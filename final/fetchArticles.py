import json
import requests
import math, re
import csv

from tfidf import keywords_byID

requests.packages.urllib3.disable_warnings()
cookie = '__auc=6dc9ccdd17143b13780f7882a84; __gads=ID=4a1a6db174d6b764:T=1585978677:S=ALNI_MYhw2OFmwPMXG1d6oDGLtOSaoaUBw; _gid=GA1.2.1722273152.1586581391; dcard=eyJ0b2tlbiI6bnVsbCwiX2V4cGlyZSI6MTU4OTE3NTA2NjgzNCwiX21heEFnZSI6MjU5MjAwMDAwMH0=; dcard.sig=V23CgwwWlQwERJ_4oClxCfx3eJo; dcsrd=u5srf5XIcfZBSFOWoTUlB9A1; dcsrd.sig=ILdWwvOz55JmB6jAgNThu9LMRwA; __asc=7bc8218c171681f2a3a6d824441; _gat=1; amplitude_id_bfb03c251442ee56c07f655053aba20fdcard.tw=eyJkZXZpY2VJZCI6ImU0Njc2NzQ5LTQyZWUtNDFhNS04ZWE4LTA5N2JkMzhhOWZkMlIiLCJ1c2VySWQiOiI1OTk2MDgxIiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNTg2NTg5ODA1ODU3LCJsYXN0RXZlbnRUaW1lIjoxNTg2NTg5ODIxMTk2LCJldmVudElkIjozNiwiaWRlbnRpZnlJZCI6MjIsInNlcXVlbmNlTnVtYmVyIjo1OH0=; __cfduid=d9fff663f1a6dd3065426909f15752fcb1586589920; _ga=GA1.1.2128013235.1585978618; _ga_C3J49QFLW7=GS1.1.1586589804.10.1.1586589846.0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'cookie': cookie,
    # 'X-CSRF-Token': token,
    'Connection':'close'
}
dcard_api = 'https://www.dcard.tw/service/api/v2/'
RETRIES = 3

def url_to_json(url):
  for i in range(RETRIES):
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == requests.codes.ok:
      json_file = response.json()
      response.close()
      return json_file
    elif response.status_code == 404:
      return None
    else:
      print('status error:',  response.status_code)
      continue
      # response.raise_for_status()
    response.close()
  print('EXCEED RETRIES: ', url)


