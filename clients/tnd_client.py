"""
``````````````
    tornado websocket 基础子类示例代码
"""
import time
import tornado.httpclient
import tornado.websocket as ws
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
import hmac
import urllib
import ssl
import os
import urllib.parse
import urllib.request
# import websocket

class EchoWebSc(ws.WebSocketHandler):
    """
    继承WebSocketHandler，创建子类
    """
    def open(self):
        print("WebSocket opend")

    def on_message(self, message):
        self.write_message(u'You said:' + message)

    def on_close(self) -> None:
        print(f"WebSocket closed")

class Client(object):
    client_protocal = None
    def __init__(self, url, timeout, name=None):
        """
        WebSocket 客户端程序，模拟指定数量客户端连接 指定的url
        Args:
            url:
            timeout:
            name:
        """
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.wss = None

        PeriodicCallback(self.keep_alive, 20000).start()
        if name is None:
            name = 'wsc'
        self.name = 'wsc_' + str(name)
        self.connect()
        self.ioloop.start()

    def start_doing(self):
        """连接开始运行"""
        self.connect()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        """

        Returns:

        """
        print(f"{self.name} trying to conn")
        try:
            self.ws = yield websocket_connect(url=self.url)
            # self.ws = yield websocket_connect(tornado.httpclient.HTTPRequest(url=self.url, ca_certs=os.path.join(os.path.abspath('.'), "minica-key.pem")))
        except Exception as e:
            print(f"connect error msg:{e}")
        else:
            print(f"{self.name} connected success")
            self.run()

    @gen.coroutine
    def run(self):
        """

        Returns:

        """
        while 1:
            msg = yield self.ws.read_message()
            if msg is None:
                print("connect closed")
                self.ws = None
                break
            else:
                time.sleep(1)
                print(f"received msg:{msg}")
                self.ws.write_message(f"at time:{str(time.time())}, {self.name} said how to work with ws.")
    def keep_alive(self):
        """

        Returns:

        """
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message(f"at {str(time.time())}, {self.name} need keep alive.")

# ===============================async
import asyncio
from concurrent.futures import ProcessPoolExecutor
def mutil_client(n):
    http_url = f'http://127.0.0.1:8091/getgamebyid/13'
    # ws_url = f"ws://127.0.0.1:5678"
    wss_url = f"wss://127.0.0.1:80/realtime/a"
    Client(url=wss_url, timeout=3, name=f"n{n}")
    # WsClient.websocket_sends(url=wss_url, message="hello,new!")

async def tasks(n):
    tasks_lis = [loop.run_in_executor(executor, mutil_client, int(info)) for info in range(n)]
    await asyncio.gather(*tasks_lis)

if __name__ == '__main__':
    # mutil process
    """
    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(max_workers=1)

    print('')
    loop.run_until_complete(tasks(2))
    """
    # single
    wss_url = f"ws://127.0.0.1:80/realtime/122/12222/33333"
    Client(url=wss_url, timeout=3, name=f"n{1}")


