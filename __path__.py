import os
import time
from datetime import datetime

project_path = os.path.join(os.path.dirname(__file__))  # 项目所在路径 os.path.join(os.path.dirname(__file__), os.pardir)
log_root = os.path.join(os.path.join(os.path.dirname(__file__), '.'), 'root_log')
# 数据文件目录
data_path = f'{project_path}/data/{datetime.now().year}{datetime.now().month}'
if not os.path.exists(data_path):
    os.mkdir(data_path)
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


if __name__ == '__main__':
    print(f"project path:{project_path}")
    print(f"log path root:{log_root}")
    print(f"log path month:{ret_log_dir()}")

    # start_path = """D:\\workspace\\rent_food\\templates\\start.html"""
    # print(f"start.html {os.path.exists(start_path)}")