from urllib.request import urlopen
import json
import requests

def get_token():
    header = {'content-type':'application/json'}
    try:
        response = requests.get('http://iot.embsky.com/api/1.0/token', headers=header, auth=('liu642586221@2980.com', 'liujinsheng'), timeout=1)
    except:
        print('timeout1')
        return
    s = response.content.decode('utf-8')
    data = json.loads(s)
    return data['token']

def upload_data(token, dev_id, sen_id, value):
    header = {'content-type':'application/json'}
    auth = (token, '')
    url = 'http://iot.embsky.com/api/1.0/device/{}/sensor/{}/data'
    url = url.format(dev_id, sen_id)
    d = {'data':value}
    try:
        response = requests.post(url, headers=header, auth=auth, data=json.dumps(d), timeout=1)
        print(response.content)
    except:
        print('timeout3')
        return

import time
token = get_token()
temp = 22.5
while True:
    temp += 1.3
    upload_data(token, 434, 906, temp)
    time.sleep(11)
    if temp > 50:
        temp = 22.5

#测试
#upload_data(get_token(), 20, 68, 1)
#status = get_status(get_token(), 20, 68)
#print(status)
#ht = get_hum_temp()
#print(ht)
#token = get_token()
#print(token)
