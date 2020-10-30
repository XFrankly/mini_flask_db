# -*- coding: utf-8 -*-
#
# Imports
#
import sys
from sqlalchemy import create_engine, Column, String, Integer, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import BinaryExpression

import Config
import logging as g_logger

sys.path.append('.')

def check_env_sys():
    server_host, io_type, db_host, db_name, db_user, _app, debug = '', '', '', '', '', '', ''
    if len(sys.argv) < 7:
        print("usage: %s [server_host] [i3|i8|i12] [db_host] [db_name] [db_user/db_passwd] [server_app] [case_level] [debug]" % \
              sys.argv[0])
        # sys.exit(0)
        return [False]
    if len(sys.argv) == 8:
        debug = sys.argv[5]
        server_host = sys.argv[1]
        io_type = sys.argv[2]
        db_host = sys.argv[3]
        db_name = sys.argv[4]
        db_user = sys.argv[5]
        _app = sys.argv[6]
        case_level = sys.argv[7]

        if not server_host:
            print ("Not need adjust environment %s" % server_host)
            return [False]
        else:
            pass
        return [True, server_host, io_type, db_host, db_name, db_user,  _app, case_level]
'''
# README
# init DBSession by get sys argvs, if not input, get from conf/global.conf
'''

Base = declarative_base()
db_port = 3306
env_msg = check_env_sys()
if env_msg[0] is True:
    io_type = str(sys.argv[2])
    db_username = str(sys.argv[5]).split('/')[0]
    db_userpasswd = str(sys.argv[5]).split('/')[1]
    if ":" in sys.argv[3]:
        config = 'mysql+mysqlconnector://%s:%s@%s' % (db_username, db_userpasswd, '%s/%s' % (sys.argv[3], sys.argv[4]))
    else:
        config = 'mysql+mysqlconnector://%s:%s@%s' % (
        db_username, db_userpasswd, '%s:%s/%s' % (sys.argv[3], db_port, sys.argv[4]))
else:
    io_type = Config.get_global_conf('iotype_name')
    datasource = Config.get_global_conf('datasource')
    config = 'mysql+mysqlconnector://%s:%s@%s' % (datasource['username'], datasource['password'], datasource['url'])
g_logger.info(config)
engine = create_engine(config)
DBSession = sessionmaker(bind=engine)


class ApiDO(Base):
    __tablename__ = '_api'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    scope = Column(String)
    status = Column(Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


class AppDO(Base):
    __tablename__ = '_app'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Integer)
    callback = Column(String)
    accessId = Column('access_id', String)
    accessSecret = Column('access_secret', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


class AppApiDO(Base):
    __tablename__ = '_app_api'

    id = Column(Integer, primary_key=True)
    appId = Column('app_id', Integer)
    apiId = Column('api_id', Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


def init_db(username='apsara', password='apsara', url='127.0.0.1:3306/rb'):
    sql_url = 'mysql+mysqlconnector://{}:{}@{}'.format(username, password, url)
    init_engine = create_engine(sql_url)
    return sessionmaker(bind=init_engine)()


def query_object(table, condition, session):
    try:
        if type(condition) == BinaryExpression:
            data = session.query(table).filter(condition).one()
        else:
            data = session.query(table).one()
        return data
    except NoResultFound:
        # g_logger.warn('NoResultFound')
        return None
    finally:
        session.close()
#########################################################################


def queryOne(Table, condition):
    session = DBSession()
    try:
        if type(condition) == BinaryExpression:
            data = session.query(Table).filter(condition).one()
        else:
            data = session.query(Table).one()
    except NoResultFound:
        # g_logger.warn('NoResultFound')
        return None
    finally:
        session.close()
    return data


def queryAll(Table, condition=None):
    session = DBSession()
    try:
        if type(condition) == BinaryExpression:
            data = session.query(Table).filter(condition).all()
        else:
            data = session.query(Table).all()
    finally:
        session.close()
    return data


def insert(record):
    session = DBSession()
    try:
        session.add(record)
        session.commit()
        insRst = record.id
        if isinstance(insRst, int):
            return insRst
    finally:
        session.close()


def delete(Table, condition):
    session = DBSession()
    try:
        delRst = session.query(Table).filter(condition).delete()
        session.commit()
        if delRst == 1:
            return delRst
    finally:
        session.close()


def update(Table, condition, dicData):
    session = DBSession()
    try:
        upRst = session.query(Table).filter(condition).update(dicData)
        session.commit()
        if isinstance(upRst, int):
            return upRst
    finally:
        session.close()


def updateAll(Table,dicData):
    session = DBSession()
    try:
        rst = session.query(Table).update(dicData)
        session.commit()
        if isinstance(rst, int):
            return rst
    finally:
        session.close()


def get_dom_info(domain_name=None):

    pass


def get_db_conf(ioType=None):
    if ioType is None:
        return None
    g_logger.info("query db info about ioType %s" % ioType)



def get_hmac_key(app=None):
    if app is None:
        return None
    APP_INFO = queryOne(AppDO, AppDO.accessId == app)
    if not APP_INFO:
        raise AssertionError("app {} query error: {}".format(app, APP_INFO))
    __access_public_HMAC_key = APP_INFO.accessSecret
    if not __access_public_HMAC_key:
        return None
    else:
        g_logger.info("app {} query Success: {}".format(app, __access_public_HMAC_key))
        return __access_public_HMAC_key


if __name__ == '__main__':
    g_logger.info('api: %d' % len(queryAll(ApiDO)))

    app_pub_key = get_hmac_key(app="sigma_admin")
    g_logger.info('app_pub_key: %s' % app_pub_key)
