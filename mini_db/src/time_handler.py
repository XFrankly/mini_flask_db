# coding:utf-8

import sys
from datetime import datetime
from __path__ import project_path
from commp.src.logger import logger

sys.path.append('.')

__this_module = 'DataAnysis'
_date = str(datetime.now())[:10]
t_log = logger


class HandlerTimer(object):

    @staticmethod
    def format_date_type(date_str=None):
        """if 2019-01-25 00:04:01.292 ret 2019-01-25 00:04:01.292000 :return"""
        if date_str is None:
            return str(datetime.now())
        date_str = str(date_str)
        if '.' not in date_str:
            date_str = date_str + '.'
        if len(date_str) > 26:
            return str(date_str)[26:]
        if len(date_str) < 26:
            n = 26 - len(date_str)
            date_str += '0' * (n - 1)
            date_str = str(date_str) + '1'
        return date_str

    @staticmethod
    def format_time_type(time_str=None):
        """if 2019-01-25 00:04:01.292 ret 2019-01-25 00:04:01.292000 :return"""
        if time_str is None:
            return "0:00:00.000001"
        time_str = str(time_str)
        if '.' not in time_str:
            time_str = time_str + '.'
        if len(time_str) < 14:
            n = 14 - len(time_str)
            time_str += '0' * (n - 1)
            time_str = str(time_str) + '1'
        else:
            return "0:00:00.000001"
        assert isinstance(datetime.strptime(time_str, '%H:%M:%S.%f'), datetime) is True
        return time_str

    @staticmethod
    def get_time():
        """ret (datetime.datetime(2019, 1, 26, 16, 5, 42, 737881), '20190126160', '20190126160542.7378811') :return"""
        time1 = datetime.now()
        time = str(time1)
        time_str = time
        new_str = ''
        for i in range(len(time_str)):
            new_str = time_str.replace('-', '').replace(':', '').replace(' ', '').replace('.', '')
        hour_str = new_str[:-11]
        return time1, hour_str, new_str

    def get_str_time_info_line(self, line_str):
        """get time str from log if 2019-01-25 00:04:01.292 ret 2019-01-25 00:04:01.292000 :return"""
        list_str = line_str.split(' ')
        try:
            time_str = list_str[0] + ' ' + list_str[1]
        except IndexError as msg:
            t_log.warning("get time str from line {} failed msg:{}".format(line_str, msg))
            return None
        print(len(time_str), time_str)
        time_str = self.format_date_type(time_str)
        return time_str

    @staticmethod
    def get_start_ends(CaseID=None, millTime=1000):
        timeList = ['2019-01-25 00:00:03.154', '2019-01-25 00:44:41.289']

    def ret_strp_time(self, t):
        """ ret datetime.datetime(2019, 1, 25, 0, 0, 3, 250000) :return"""
        t = self.format_date_type(t)
        try:
            strp_time = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError as e:
            t_log.warning("format time error {}".format(e))
            raise ValueError
        else:
            return strp_time

    @staticmethod
    def reduce_time(t1, t0):
        """ ret datetime.datetime t1 reduce t0 :return"""
        return datetime.strptime(t1, '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t0, '%Y-%m-%d %H:%M:%S.%f')

    def avg_time(self, time_lis=None):
        """ ret datetime.datetime t1 reduce t0 :return"""
        if not time_lis:
            raise ValueError(time_lis)
        # t_log.warning("get time lis {}".format(time_lis))
        total_time = float(0.0)
        for timer in time_lis:
            timer_str = self.format_time_type(str(timer))
            total_time += float(str(timer_str)[-9:])
            # t_log.warning("sum lis total_time: {}, float timer_str:{}, lis timer:{}".format(
            #             total_time, float(str(timer_str)[-9:]), str(timer)))

        avg_time = total_time / float(len(time_lis))
        Maximum = time_lis[0]
        t_log.warning("time num lis total_time {} avg_time {}".format(total_time, avg_time))

        return {"total_time": total_time, "avg_time": avg_time, "Maximum": Maximum}

    def comp_time(self, t1, t0):
        """if t1 >= t0 ret True, else False"""
        # pick_log.warning(msg="comp t1 {} and time {}".format(t1, t0))
        return self.ret_strp_time(str(t1)) > self.ret_strp_time(str(t0))


if __name__ == '__main__':
    hand_time = HandlerTimer()
    hand_time.get_start_ends()
    with open(f'{project_path}/SisTmp/example.log', 'r') as oc_log:
        line = oc_log.readline()
        print(hand_time.get_str_time_info_line(line))
        print(hand_time.reduce_time(str(datetime.now()), hand_time.get_str_time_info_line(line)))

    print(str(datetime.now()) > str('2019-01-25 00:00:03.250000'))
    print(HandlerTimer.get_time())
    print(hand_time.format_date_type('2019-01-25 00:28:48'))
    print(hand_time.reduce_time(t1="2019-02-13 00:00:02.348000", t0="2019-02-13 00:00:02.274000"))

