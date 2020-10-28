import logging
from logging.handlers import BaseRotatingHandler
import codecs
import os
import time
import traceback
from io import StringIO
import zmq
from tornado.options import options
from __path__ import project_path

log_root = os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 'log')


def ret_log_dir(log_root=log_root):
    """按月份产生日志目录"""
    if not os.path.exists(log_root):
        os.mkdir(log_root)
    log_root_dir = os.path.join(log_root, 'log')
    if not os.path.exists(log_root_dir):
        os.mkdir(log_root_dir)
    log_month_dir = os.path.join(log_root_dir, time.strftime('%Y%m', time.localtime()))
    if not os.path.exists(log_month_dir):
        os.mkdir(log_month_dir)
    return log_month_dir


# global params
game_log_id = 999
log_dir = f'{project_path}/logs'
log_format = '[%(asctime)s] [%(filename)s:%(lineno)s] [%(levelname)s] [%(process)d] [%(funcName)s] [%(thread)d] [%(name)s] %(message)s'


class RotatingProcessSafeFileHandler(BaseRotatingHandler):
    """
    - Rotate at midnight
    - Rotate at size enough
    - Multi process safe
    - Rotate at midnight and size enough only
    """

    def __init__(self, filename, encoding=None, delay=False, utc=False, mode='a', maxBytes=0, backupCount=0,
                 logPath=None, *args, **kwargs):
        self.utc = utc
        self.suffix = '%Y%m%d'
        self.filename = filename
        self.log_path = logPath
        self.baseFilename = self._handler_date_path(self.filename)
        self.currentFileName = self._compute_fn()

        if maxBytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, self.baseFilename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    def _handler_date_path(self, filename):
        """判断日志写入路径"""
        if str(time.strftime('%Y%m', time.localtime())) not in str(self.log_path):
            self.log_path = log_dir
        return os.path.join(self.log_path, filename)

    def shouldRollover(self, record):
        """判断是否翻转日志"""
        # 检查更新日志写入路径
        self.baseFilename = self._handler_date_path(self.filename)

        if self.currentFileName != self._compute_fn():
            return True  # 先判断是否有日志名称在路径中
        if self.stream is None:  # delay 已设置
            self.stream = self._open()
        if self.maxBytes > 0:  # 是否翻转
            msg = '%s\n' % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return True  # 再判断是否日志大小符合翻转条件
        # 以上条件都不满足
        return False

    def doRollover(self):
        """
        执行翻转日志文件
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # 写入文件名为当前日志文件名
        self.currentFileName = self._compute_fn()
        # 日志流按大小翻转
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename('%s.%d' % (self.currentFileName, i))
                dfn = self.rotation_filename(f"{self.currentFileName}.{i + 1}")
                if os.pardir.expandtabs(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.currentFileName + '.1')
            if os.path.exists(dfn):
                os.remove(dfn)
            # await self.rotate(self.currentFileName, dfn)   #异步解决冲突
            self.rotata(self.currentFileName, dfn)
        if not self.delay:
            self.stream = self._open()

    def _compute_fn(self):
        """返回基本日志文件名+ 后缀格式"""
        return self.baseFilename + '.' + time.strftime(self.suffix, time.localtime())

    def _open(self):
        """以当前文件名打开文件操作流"""
        if self.encoding is None:
            stream = open(self.currentFileName, self.mode)  # 打开文件操作流
        else:
            stream = codecs.open(self.currentFileName, self.mode, self.encoding)
        # simulate file name structure of 'logging.TimedRotatingFileHandler'
        if os.path.exists(self.baseFilename):
            try:
                os.remove(self.baseFilename)
            except OSError as rerror:
                print(f"os remove error msg:{rerror}")
        return stream


class ZMQHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.tcp_url = 'tcp://{0}:{1}'.format(host, port)
        context = zmq.Context()
        self.zq = context.socket(zmq.PUSH)
        self.zq.connect(self.tcp_url)

    def emit(self, record):
        try:
            self.zq.send_pyobj(record, flags=zmq.NOBLOCK, protocol=4)
        except Exception as err:
            fp = StringIO()
            traceback.print_exc(file=fp)
            error = fp.getvalue()
            logging.warning('WARNING')


class ZMQListener(object):
    def __init__(self, host, port, *handlers, respect_handler_level=False):
        self.tcp_url = "tcp://{0}:{1}".format(host, port)
        self.handlers = handlers
        self.respect_handler_level = respect_handler_level
        self.context = None
        self.zq = None
        self.connect()

    def connect(self):
        self.context = zmq.Context()
        self.zq = self.context.socket(zmq.PULL)
        self.zq.bind(self.tcp_url)

    def close(self):
        self.zq.close()
        self.context.term()
        self.context = None
        self.zq = None

    def handle(self, record):
        """Handle a record"""
        for handler in self.handlers:
            if not self.respect_handler_level:
                process = True
            else:
                process = record.levelno >= handler.level
            if process:
                handler.handle(record)

    def run(self):
        while 1:
            try:
                record = self.zq.recv_pyobj(flags=zmq.NOBLOCK)
                if record.msg == 'EOF':
                    break
                self.handle(record)
            except zmq.ZMQError:
                time.sleep(1)
            except Exception as e:
                print(e)


class LOG:
    @staticmethod
    def ret_handlers():
        """return handler list"""
        each_log_size = 10 ** 7  # log文件翻转单位字节， 7次， 10000000 bytes 10M
        log_handlers = []
        # msg The result of record.getMessage()
        logging.default_msec_format = '%s, %06d'
        formatter = logging.Formatter(log_format)
        stream_console = logging.StreamHandler()
        stream_console.setLevel(logging.DEBUG)
        stream_console.setFormatter(formatter)
        stream_console.terminator = '\n'
        log_handlers.append(stream_console)

        # debug 级别日志以上
        file_debug_name = "{0}.{1}.debug.log".format(options.logger_port, f"{game_log_id}")
        file_info_name = file_debug_name.replace('debug', 'info')

        # 费用日志
        file_fee_name = "{0}.{1}.fee.log".format(options.logger_port, f"{game_log_id}")
        # FATAL级别以上的记录fee信息
        file_fee_handler = RotatingProcessSafeFileHandler(filename=file_fee_name, maxBytes=each_log_size,
                                                          backupCount=5,
                                                          logPath='../logs')

        file_fee_handler.setLevel(logging.DEBUG)
        file_fee_handler.formatter = formatter
        # 添加过滤器，info以上的日志独立存储
        fee_filter = logging.Filter()
        fee_filter.filter = lambda record: record.levelno >= logging.FATAL
        file_fee_handler.addFilter(fee_filter)  # 添加info filter 到file handler
        log_handlers.append(file_fee_handler)
        # 传入日志名称和目录，在handler实时检查写入目录
        file_debug_handler = RotatingProcessSafeFileHandler(filename=file_debug_name, maxBytes=each_log_size,
                                                            backupCount=5, logPath='../logs')
        file_debug_handler.setLevel(logging.DEBUG)
        file_debug_handler.formatter = formatter

        # 添加过滤器，info以下的日志存储一次
        log_debug_filter = logging.Filter()
        log_debug_filter.filter = lambda record: logging.DEBUG <= record.levelno < logging.INFO
        file_debug_handler.addFilter(log_debug_filter)
        log_handlers.append(file_debug_handler)
        # info 级别以上
        file_info_handler = RotatingProcessSafeFileHandler(filename=file_info_name, maxBytes=each_log_size,
                                                           backupCount=5, logPath="../logs")
        file_info_handler.formatter = formatter
        # 添加过滤器，info以上日志独立存储
        log_filter = logging.Filter()
        log_filter = lambda record: logging.INFO <= record.levelno <= logging.ERROR
        file_info_handler.addFilter(log_filter)
        log_handlers.append(file_info_handler)
        return log_handlers

    @staticmethod
    def ret_logger(mod_name=None):
        """

        """
        log_name = str(f"{'.'.join([str(x) for x in str(__file__).split(os.sep)[-2:]])[:-3]}")  # 模块文件名
        # 方法中没有传入名称，类定义中获取，否则取当前模块名core.logger
        # fun_param -> class_param -> module_name
        logger = logging.getLogger(log_name) if not mod_name else logging.getLogger(str(mod_name))
        zmq_handler = ZMQHandler('127.0.0.1', 8981)
        logger.setLevel(logging.DEBUG)
        logger.propagate = 0  # record 不向root logging传递
        logger.addHandler(zmq_handler)
        return logger


logger = LOG.ret_logger(__name__)
print(f"defaule logger name:{logger.name}")