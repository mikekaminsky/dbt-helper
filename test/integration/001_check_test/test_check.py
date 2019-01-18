import subprocess

def test():
    x = subprocess.Popen("dbt --help", shell=True, stdout=subprocess.PIPE).stdout.read()
    print(x.decode('UTF-8'))
    print('HOWDY')
    assert True
