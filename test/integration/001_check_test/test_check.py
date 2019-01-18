import subprocess
from test.integration.base import DBTIntegrationTest

class MySlickTest(DBTIntegrationTest):

    def test_test(self):
        x = subprocess.Popen("dbt --help", shell=True, stdout=subprocess.PIPE).stdout.read()
        print(x.decode('UTF-8'))
        print('HOWDY')
        assert True
