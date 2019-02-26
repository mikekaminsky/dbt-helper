import os
import re
import networkx as nx
import argparse
import sys


REG_BLOCK_COMMENT = re.compile("(/\*)[\w\W]*?(\*/)", re.I)
REG_LINE_COMMENT = re.compile("(--.*)", re.I)
REG_BRACKETS = re.compile('\[|\]|\)|"', re.I)
REG_PARENTS = re.compile("(?<=join\s)+[\S\.\"']+|(?<=from\s)+[\S\.\"']+", re.I)
REG_CTES = re.compile("(\S+)\sas\W*\(", re.I)


class ShowDependenciesTask:
    def __init__(self, args):
        self.args = args
        if self.args.command == "show_upstream":
            self.direction = "upstream"
        elif self.args.command == "show_downstream":
            self.direction = "downstream"
        else:
            raise

    def create_query_dict(self):
        sql_files = []
        for dp, dn, filenames in os.walk("./models"):
            for fn in filenames:
                if os.path.splitext(fn)[1] == ".sql":
                    full_path = os.path.join(dp, fn)
                    sql_files.append(full_path)

        query_list = []
        for sql_file in sql_files:
            with open(sql_file, "r") as f:
                query = f.read()
            if not query.strip() == "":
                d = {}
                d["name"] = os.path.splitext(os.path.basename(sql_file))[0]
                d["sql"] = query
                d["tpe"] = "view"
                query_list.append(d)

        return query_list

    def clean_sql(self, sql):
        c_sql = sql.lower()  # lowercase everything (for easier match)
        c_sql = REG_BLOCK_COMMENT.sub("", c_sql)  # remove block comments
        c_sql = REG_LINE_COMMENT.sub("", c_sql)  # remove line comments
        c_sql = " ".join(c_sql.split())  # replace \n and multi space w space
        return c_sql

    # this returns the unique set of parents per query
    def get_parents(self, c_sql):
        raw_parents = REG_PARENTS.findall(c_sql)
        parents = set([x for x in raw_parents if "generate_series" not in x])
        return parents

    # this returns the unique set of ctes per query, to exclude from parents
    def get_ctes(self, c_sql):
        ctes = set(REG_CTES.findall(c_sql))
        return ctes

    # this traverses an arbitrary tree (parents or children) to get all ancestors or descendants
    def traverse_tree(self, node, d_tree, been_done=set()):
        tree_outputs = set(d_tree.get(node, set()))  # direct relatives
        for key in d_tree.get(node, set()):  # 2nd step relatives
            if not key in been_done:
                been_done.add(key)  # to break any circular references
                tree_outputs = tree_outputs.union(
                    self.traverse_tree(key, d_tree, been_done)
                )
        return tree_outputs

    # this reverses a parent tree to a child tree
    def get_child_dict(self, parent_dict):
        child_dict = {}
        for node in parent_dict:
            for parent in parent_dict[node]:
                if not parent in child_dict.keys():
                    child_dict[parent] = set([node])
                else:
                    child_dict[parent].add(node)
        return child_dict

    def get_node_set(self, parent_dict, focal_set):

        downstream_dict = {}  # intended to store all descendants (any generation)
        upstream_dict = {}  # intended to store all ancestry (any generation)
        node_set = set()

        # reverse parent dict to child so we can look for descendants
        child_dict = self.get_child_dict(parent_dict)  # immediate children

        # build descendant dict
        for node in child_dict:
            downstream_dict[node] = self.traverse_tree(
                node, child_dict, been_done=set()
            )

        # build ancestor dict
        for node in parent_dict:
            upstream_dict[node] = self.traverse_tree(node, parent_dict, been_done=set())

        for focal_node in focal_set:
            if self.direction == "upstream":
                node_set = upstream_dict.get(focal_node, set())
            else:
                node_set = downstream_dict.get(focal_node, set())
            node_set.add(focal_node)

        return node_set

    def get_node_info(self):
        node_info_dict = {}  # intended to store direct node type
        parent_dict = {}  # intended to store parent data

        query_dict = self.create_query_dict()
        for row in query_dict:

            object_name = row["name"]
            object_type = row["tpe"]
            sql = row["sql"]

            # clean the sql
            c_sql = self.clean_sql(sql)

            # get the set of parents
            parents = self.get_parents(c_sql)

            # get set of ctes to exclude from parents
            ctes = self.get_ctes(c_sql)

            # remove CTES from parent dict
            for cte in ctes:
                parents.discard(cte)

            # get rid of brackets in views
            c_parents = set()
            for parent in parents:
                if not parent[:1] == "(":
                    c_parents.add(REG_BRACKETS.sub("", parent))

            # add the object name and type and direct parents to the dict
            node_info_dict[object_name] = object_type
            parent_dict[object_name] = c_parents
        return (parent_dict, node_info_dict)

    def build_d_graph(self, parent_dict, node_set, node_type_dict):

        # if focus_objct is specified, only the branches related to that object will be returned
        # if direction is specified, only ancestors or only descedents will be shown
        G = nx.DiGraph()  # initialize directional graph object

        for node in node_set:

            # Add color nodes
            if node_type_dict.get(node, None) == "view":
                G.add_node(node, color="green")
            elif node_type_dict.get(node, None) == "chart":
                G.add_node(node, color="blue")
            elif node_type_dict.get(node, None) == "csv":
                G.add_node(node, color="red")

            # add edges and non-color nodes
            for parent in parent_dict.get(node, set()):
                G.add_edge(parent, node)
        return G

    def display_deps(self, viz_dict):
        rev = self.direction == "downstream"
        layers = sorted([*viz_dict], reverse=rev)
        print("-" * 80)
        for layer in layers:
            print(" | ".join(viz_dict[layer]).center(80))
            print("-" * 80)

    def subset_dict(self, d, nodes):
        out_d = {}
        for k, v in d.items():
            if k in nodes:
                dep_set = set()
                for n in d[k]:
                    if n in nodes:
                        dep_set.add(n)
                out_d[k] = dep_set
        return out_d

    def run(self, args):
        parent_dict, node_info_dict = self.get_node_info()

        focal_set = set([self.args.model_name])

        node_set = self.get_node_set(parent_dict, focal_set)

        parent_subset_dict = self.subset_dict(parent_dict, node_set)

        G = self.build_d_graph(parent_subset_dict, node_set, node_info_dict)

        viz_dict = {}

        def update_viz_dict(G, current_node, level=0):
            if len(G.nodes()) == 0:
                # if len(G.nodes()) == 1:
                viz_dict[0] = focal_set
                return
            if level in viz_dict:
                viz_dict[level].append(current_node)
            else:
                viz_dict[level] = [current_node]
            if self.direction == "upstream":
                if G.predecessors(current_node) == []:
                    return
                for pred in G.predecessors(current_node):
                    update_viz_dict(G, pred, level + 1)
            if self.direction == "downstream":
                if G.successors(current_node) == []:
                    return
                for pred in G.successors(current_node):
                    update_viz_dict(G, pred, level + 1)

        update_viz_dict(G, self.args.model_name)

        self.display_deps(viz_dict)
