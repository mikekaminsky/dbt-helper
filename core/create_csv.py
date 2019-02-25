import os
import csv

sql_files = []
for dp, dn, filenames in os.walk('./models'):
    for fn in filenames:
        if os.path.splitext(fn)[1] == '.sql':
            full_path = os.path.join(dp, fn)
            sql_files.append(full_path)

query_list = []
for sql_file in sql_files:
    with open(sql_file, 'r') as f:
        query = f.read()
    if not query.strip()  == '':
        d = {}
        d['name'] = os.path.splitext(os.path.basename(sql_file))[0]
        d['sql'] = query
        d['tpe'] = 'view'
        query_list.append(d)

with open('SQLs.csv', 'w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['name','tpe','sql'])
    writer.writeheader()
    writer.writerows(query_list)

    # for key, value in query_dict.items():
       # writer.writerow([key, value])
