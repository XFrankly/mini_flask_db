"""
    流的异步处理, 1,2
    子进程的创建使用 3~4...
    锁 5~...
    ~~~~~~~~~~~~~~~~~~~~~~~~~
# py3.6 源码 Lib/asyncio/streams.py
"""

import asyncio


@asyncio.coroutine
def handle_echo(reader, writer):
    """
    基于asyncio.start_server 的TCP回显服务器

    """
    data = yield from reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print(f"Received:{message} from {addr}")
    print(f"Send:{message}")

    writer.write(data)
    yield from writer.drain()  # 返回的可选Future内容。 让基础传输的写缓冲区有机会被刷新
    print(f'Close the client socket')
    writer.close()


def handle_main():
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', 887, loop=loop)
    server = loop.run_until_complete(coro)

    # Server requests until Ctrl+C is pressed
    print(f"Serviing on {server.sockets[0].getsockname()}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print(f"Ctrl+C quit")
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


#################++++++++++++++2,注册开放式服务等待使用流数据+++++++++++################
from socket import socketpair


# @asyncio.coroutine   # 如果封装在类中，只能使用类方法
class WaitForData():

    @classmethod  # 后执行classmethod
    @asyncio.coroutine  # 先执行异步定义
    def wait_data(cls, loop):
        # Create a pair of connected sockets
        rsock, wsock = socketpair()

        # Register the open socket to wait for data
        reader, writer = yield from asyncio.open_connection(sock=rsock, loop=loop)

        # Simulate the reception of data from the network
        loop.call_soon(wsock.send, 'aaa'.encode())

        # Wait for data
        data = yield from reader.read(100)

        # Got data, we are done close the socket
        print(f"Received:{data.decode()}")
        writer.close()

        # Close the second socket
        wsock.close()

    @asyncio.coroutine
    def wait_for_data(self, loop):
        # Create a pair of connected sockets
        rsock, wsock = socketpair()

        # Register the open socket to wait for data
        reader, writer = yield from asyncio.open_connection(sock=rsock, loop=loop)

        # Simulate the reception of data from the network
        loop.call_soon(wsock.send, 'aaa'.encode())

        # Wait for data
        data = yield from reader.read(100)

        # Got data, we are done close the socket
        print(f"Received:{data.decode()}")
        writer.close()

        # Close the second socket
        wsock.close()


# send sock data
def send_loop_data_main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(WaitForData().wait_data(loop))
    loop.run_until_complete(WaitForData().wait_for_data(loop))
    loop.close()


###########+++++++++++++3,subprocess-子进程使用传输和协议++++++++++++++####################
import sys


class DateProtocol(asyncio.SubprocessProtocol):  #  connection_made
    """子流程协议的示例，用于获取子流程的输出并等待子流程退出。 传输和协议，AbstractEventLoop.subprocess_exec()创建"""

    def __init__(self, exit_future):
        self.exit_future = exit_future
        self.output = bytearray()

    def pipe_data_received(self, fd: int, data) -> None:
        self.output.extend(data)

    def process_exited(self) -> None:
        self.exit_future.set_result(True)


@asyncio.coroutine
def get_date(loop):
    code = 'import datetime; print(datetime.datetime.now())'
    exit_future = asyncio.Future(loop=loop)

    # Create the subprocess controlled by the protocol DateProtocol,
    # redirect the standard output into a pipe
    create = loop.subprocess_exec(lambda: DateProtocol(exit_future),
                                  sys.executable, '-c', code,
                                  stdin=None, stderr=None)
    transport, protocol = yield from create

    # Wait for the subprocess exit using the process_exited() method
    # of the protocol
    yield from exit_future

    # Close the stdout pipe
    transport.close()

    # Read the output which was collected by the pipe_data_received()
    # method of the protocol
    print(f"{type(protocol), dir(protocol)}")
    data = bytes(protocol.output)
    return data.decode('ascii').rstrip()


def main_loop():
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    date = loop.run_until_complete(get_date(loop))
    print(f"Current date:{date}")
    loop.close()


########+++++++++++++++++4,子进程使用流+++++++++++++++++++###########################
@asyncio.coroutine
def get_dates():
    """
    子流程使用流create_subprocess_exec()函数创建
    """
    code = "import datetime;print(datetime.datetime.now())"
    # Create the subprocess, redirect the standard output into pipe
    create = asyncio.create_subprocess_exec(sys.executable, '-c', code, stdout=asyncio.subprocess.PIPE)
    proc = yield from create
    # Read one line of output
    date = yield from proc.stdout.readline()
    line = date.decode('ascii').rstrip()
    # Wait for the subprocess exit
    yield from proc.wait()
    return line


def stream_main():
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    date = loop.run_until_complete(get_dates())
    print(f"Current date:{date}")
    loop.close()

########++++++++++++++5,Lock++++++++++++++++++####################

from redlock import RedLock   # 分布式锁



#######++++++++++++++6, 进度条 +++++++++++++++#######################

import decimal
import asyncio, time
from pprint import pprint, pformat
import os
# os.fdopen(sys.stdout.fileno(), 'w', 0)
class Unbuffered(object):
    # 将sys.stdout替换为包装器之类的其他流，该流在每次调用后进行刷新,即不缓冲
    # https://eklitzke.org/stdout-buffering
    # 您可以使用iter()而不是while循环：for line in iter(pipe.readline, ''):。您不需要在Python 3上for line in pipe:尽快生成它

   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       """__getattr__允许它与任何流一起使用，而不仅仅是您打算使用的任何特定类"""
       return getattr(self.stream, attr)

async def process_print(x):
    # x = int(input('请输入进度条长:'))
    # 通过if语句判断输入的数值是否大于0，大于0执行if内代码块，
    # 否则执行else的代码块打印输出错误提示
    if x < 0:
        print(f"input int bigger than 0")
        return False
    for a in range(x):
        # python的print（）函数默认换行打印输出，
        # 若不换行输出需要加上" end='' " 如代码所示

        if a == x - 1:
            print(f"100%", end='')
        elif a == 0:
            print(f"0%", end='')
        else:
            # print(a % x, x % a)
            y = decimal.Decimal(a)/ decimal.Decimal(x)
            print('.', end='') if y*100 % 30 != 0 else print(f"{y* 100}%", end='')
        await asyncio.sleep(0.1)
    # print('')

    return True


if __name__ == '__main__':
    pass
    # handle_main()

    # 2
    # send_loop_data_main()
    # 3
    # main_loop()

    # 4
    # stream_main()

    # 5 dev fab
    # do_fab()
    import sys

    sys.stdout = Unbuffered(sys.stdout)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([process_print(100)]))

    print('\n')
    # 6, compare with print for
    for i in range(100):
        print(f".", end='')
        time.sleep(0.1)


