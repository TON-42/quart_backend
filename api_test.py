import requests

ENDPOINT = 'http://127.0.0.1:8080'

def hello_test():
  res = requests.get(ENDPOINT+'/hello', timeout=1)
  print(res.json)

hello_test()