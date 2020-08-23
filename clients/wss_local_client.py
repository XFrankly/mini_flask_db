import  urllib.request as Request
import urllib.parse
import urllib
import os
import time
import json
import traceback
import hmac
import ssl
import logging as logger



def websocket_sends(url, message, hmac_key=None, group='default'):
    print(hmac_key)
    sig = hmac_key and hmac.new(hmac_key, message).hexdigest() or ''
    ssl._create_default_https_context = ssl._create_unverified_context
    params = urllib.parse.urlencode(
        {'message': message, 'signature': sig, 'group': group})
    # 加载ca私钥
    # ca_file = os.path.join(os.path.abspath('../'), "private", "localhost.pem")   # localhost.pem
    # print(f"'ca_file:{ca_file}")
    f = urllib.request.urlopen(url=url, data=params.encode())   # , cafile=ca_file
    data = f.read()
    f.close()
    return data

if __name__ == '__main__':
    host = 'http://localhost'
    port = '80'
    # ========================================
    url_path = "/realtime/11/22/33"
    urls = f"{host}:{port}{url_path}"
    websocket_sends(urls, message="H12", hmac_key=None)





