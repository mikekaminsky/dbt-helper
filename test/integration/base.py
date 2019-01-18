import unittest
from dbt.adapters.factory import get_adapter
import psycopg2

class DBTIntegrationTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DBTIntegrationTest, self).__init__(*args, **kwargs)

        connection = psycopg2.connect(
            dbname='dbt',
            user='root',
            password='password',
            host='database',
            port=5432
        )
        self.conn = connection

    def setUp(self):
        schema = 'my_test_schema'
        self.run_sql('CREATE SCHEMA IF NOT EXISTS {}'.format(schema))
        self.run_sql('DROP SCHEMA IF EXISTS {} CASCADE'.format(schema))

    def tearDown(self):
        schema = 'my_test_schema'
        self.run_sql('CREATE SCHEMA IF NOT EXISTS {}'.format(schema))
        self.run_sql('DROP SCHEMA IF EXISTS {} CASCADE'.format(schema))

    def run_sql(self, query, fetch='None'):

        if query.strip() == "":
            return

        # sql = self.transform_sql(query)
        sql = query
        # if self.adapter_type == 'bigquery':
            # return self.run_sql_bigquery(sql, fetch)

        conn = self.conn
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql)
                conn.commit()
                if fetch == 'one':
                    return cursor.fetchone()
                elif fetch == 'all':
                    return cursor.fetchall()
                else:
                    return
            except BaseException as e:
                conn.rollback()
                print(query)
                print(e)
                raise e
