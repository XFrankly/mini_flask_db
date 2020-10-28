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
    ocean_host, io_type, db_host, db_name, db_user, ocean_app, debug = '', '', '', '', '', '', ''
    if len(sys.argv) < 7:
        print("usage: %s [ocean_host] [io3|io8|io12] [db_host] [db_name] [db_user/db_passwd] [ocean_app] [case_level] [debug]" % \
              sys.argv[0])
        # sys.exit(0)
        return [False]
    if len(sys.argv) == 8:
        debug = sys.argv[5]
        ocean_host = sys.argv[1]
        io_type = sys.argv[2]
        db_host = sys.argv[3]
        db_name = sys.argv[4]
        db_user = sys.argv[5]
        ocean_app = sys.argv[6]
        case_level = sys.argv[7]
        # print "get config: %s, %s, %s, %s, %s, %s, %s" % (ocean_host, io_type, db_host, db_name, db_user, ocean_app, case_level)

        if not ocean_host:
            print ("Not need adjust environment %s" % ocean_host)
            return [False]
        else:
            #if check_ip(ocean_host)[0] != 'True' or check_ip(db_host)[0] != 'True':
            #    return [False]
            #else:
            #    assert check_ip(db_host)[0] == 'True'
            pass
        return [True, ocean_host, io_type, db_host, db_name, db_user, ocean_app, case_level]
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
    __tablename__ = 'ocean_api'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    scope = Column(String)
    status = Column(Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


class AppDO(Base):
    __tablename__ = 'ocean_app'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Integer)
    callback = Column(String)
    accessId = Column('access_id', String)
    accessSecret = Column('access_secret', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


class AppApiDO(Base):
    __tablename__ = 'ocean_app_api'

    id = Column(Integer, primary_key=True)
    appId = Column('app_id', Integer)
    apiId = Column('api_id', Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


class ClusterDO(Base):
    __tablename__ = 'cluster_info'

    id = Column('cluster_id', Integer, primary_key=True)
    name = Column('name', String)
    masterId = Column('master_id', Integer)
    saleable = Column('saleable', Integer)
    useRatioMax = Column('use_ratio', Integer)
    saleRatioMax = Column('sale_ratio', Integer)
    storageDomainId = Column('storage_domain_id', Integer)
    iotypeValue = Column('iotype_value', Integer)
    schedulePolicy = Column('sched_policy', Integer)
    ssStorageId = Column('ss_storage_id', Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class storageDomainDO(Base):
    __tablename__ = 'storage_domain'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class AzoneDO(Base):
    __tablename__ = 'azone'

    azId = Column('az_id', Integer, primary_key=True)
    azoneId = Column('azone_id', String)
    network_type = Column('network_type', Integer)
    description = Column('description', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class RiverMstDO(Base):
    __tablename__ = 'river_master'

    id = Column('master_id', Integer, primary_key=True)
    name = Column('name', String)
    addr = Column('addr', String)
    ip = Column('ip', String)
    port = Column('port', Integer)
    azonId = Column('az_id', Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class oceanResourceDO(Base):
    __tablename__ = 'ocean_resource'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', String)
    name = Column('name', String)
    value = Column('value', String)
    description = Column('description', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modified', DATETIME, default=func.now())


class deviceDO(Base):
    __tablename__ = 'device'

    id = Column('id', Integer, primary_key=True)
    deviceKey = Column('device_key', String)
    clusterId = Column('cluster_id', Integer)
    deviceId = Column('device_id', Integer)
    deviceSize = Column('device_size', Integer)
    panguPath = Column('pangu_path', Integer)
    partitionName = Column('partition_name', String)
    appId = Column('app_id', String)
    status = Column('status', Integer)
    feature = Column('feature', Integer)
    srcSnapshotId = Column('src_snapshot_id', String)
    progress = Column('progress', Integer)
    userData = Column('user_data', Integer)
    iotypeValue = Column('iotype_value', Integer)
    migrationDisable = Column('migration_disable', Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class oceanVolumeDO(Base):
    __tablename__ = 'ocean_volume'

    id = Column('id', Integer, primary_key=True)
    volumeRiverId = Column('volume_river_id', String)
    volumeUuid = Column('volume_uuid', String)


class snapshotStorageDO(Base):
    __tablename__ = 'snapshot_storage'

    ssStorageId = Column('ss_storage_id', Integer, primary_key=True)
    storageType = Column('storage_type', Integer)
    snapshotType = Column('snapshot_type', Integer)
    accessId = Column('access_id', String)
    accessKey = Column('access_key', String)
    ossDomain = Column('oss_domain', String)
    ocmAddr = Column('ocm_addr', String)
    vipServer = Column('vip_server', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class snapshotDO(Base):
    __tablename__ = 'snapshot'

    id = Column('id', Integer, primary_key=True)
    deviceKey = Column('device_key', String)
    snapshotId = Column('snapshot_id', String)
    ssStorageId = Column('ss_storage_id', Integer)
    homeClusterId = Column('home_cluster_id', Integer)
    status = Column('status', Integer)
    progress = Column('progress', Integer)
    userData = Column('user_data', Integer)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModify = Column('gmt_modify', DATETIME, default=func.now())


class oceanSnapshotDO(Base):
    __tablename__ = 'ocean_snapshot'

    id = Column('id', Integer, primary_key=True)
    snapshotRiverId = Column('snapshot_river_id', Integer)
    snapshotUuid = Column('snapshot_uuid', String)
    volumeId = Column('volume_id', String)

#########################################################################


# geo logic appendix
class OceanReplicationTask(Base):
    __tablename__ = 'ocean_replication_task'

    id = Column('id', Integer, primary_key=True)
    appId = Column('app_id', Integer)
    taskId = Column('task_id', String)
    taskType = Column('task_type', String)
    isReplace = Column('is_replace', Integer)
    isMigration = Column('is_migration', Integer)
    srcVolumeKey = Column('src_volume_key', String)
    srcIoType = Column('src_io_type', String)
    srcAzone = Column('src_azone', String)
    srcCluster = Column('src_cluster', String)
    targetVolumekey = Column('target_volume_key', String)
    targetIoType = Column('target_io_type', String)
    targetAzone = Column('target_azone', String)
    targetCluster = Column('target_cluster', String)
    task_status = Column('task_status', String)
    gmtCreate = Column('gmt_create', DATETIME, default=func.now())
    gmtModified = Column('gmt_modified', DATETIME, default=func.now())


def init_db(username='apsara', password='apsara', url='100.81.252.31:3306/riverdb'):
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
    # query cluster, snapshot storage, azone
    # clusterInfo = queryOne(ClusterDO, ClusterDO.iotypeValue == 2 ** int(str(ioType)[2:]))
    clusterInfo = queryAll(ClusterDO, ClusterDO.iotypeValue == 2 ** int(str(ioType)[2:]))
    if not clusterInfo:
        raise AssertionError("ioType {} not exist at db".format(ioType))
    else:
        if len(clusterInfo) >= 2:
            name_cluster = Config.get_global_conf('cluster_name')
        else:
            name_cluster = clusterInfo[0].name
        clusterInfo = queryOne(ClusterDO, ClusterDO.name == name_cluster)
        if not clusterInfo:
            raise AssertionError("cluster info get failed with cluster name {}".format(name_cluster))
        ssStorageId = clusterInfo.ssStorageId
        oss_domain_info = queryOne(snapshotStorageDO, snapshotStorageDO.ssStorageId == ssStorageId)
    if oss_domain_info is None:
        oss_domain = str(Config.get_global_conf('oss_snapshot_domain'))
    else:
        oss_domain = oss_domain_info.ossDomain

    # query azone info with iotype and cluster
    cs_rm_id = clusterInfo.masterId
    river_info = queryOne(RiverMstDO, RiverMstDO.id == cs_rm_id)
    rm_az_id = river_info.azonId
    # print "rm_az_id:", rm_az_id, "river_info:", river_info
    azoneInfo = queryOne(AzoneDO, AzoneDO.azId == rm_az_id)
    azone_Name = azoneInfo.azoneId

    # query ocean resource
    db_ocean_region_name = queryOne(oceanResourceDO, oceanResourceDO.name == "ocean_region_name")
    db_ocean_domain_name = queryOne(oceanResourceDO, oceanResourceDO.name == "ocean_domain_name")
    if not db_ocean_region_name:
        ocean_region_name = Config.get_global_conf('ocean_region_name')
    else:
        ocean_region_name = db_ocean_region_name.value
    if not db_ocean_domain_name:
        ocean_domain_name = Config.get_global_conf('ocean_domain_name')
    else:
        ocean_domain_name = db_ocean_domain_name.value
    db_info = {"name_cluster": name_cluster, "oss_domain": oss_domain, "_azone_name": azone_Name,
            "ocean_region_name": ocean_region_name, "ocean_domain_name": ocean_domain_name}
    g_logger.info("db_info about io_type %s: %s" % (ioType, db_info))
    return {"name_cluster": name_cluster, "oss_domain": oss_domain, "_azone_name": azone_Name,
            "ocean_region_name": ocean_region_name, "ocean_domain_name": ocean_domain_name}


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
    g_logger.info('app: %d' % len(queryAll(AppDO)))
    g_logger.info('appApi: %d' % len(queryAll(AppApiDO)))
    g_logger.info('cluster: %d' % len(queryAll(ClusterDO)))
    cluster_info = queryOne(ClusterDO, ClusterDO.name == 'pangu2-ebs-test2')

    if cluster_info:
        g_logger.info('cluster info: {},{}'.format(cluster_info.name, cluster_info.schedulePolicy))
    domain_info = queryOne(storageDomainDO, storageDomainDO.name == "PUBLIC")
    print("domain_info:{}".format(domain_info))
    app_pub_key = get_hmac_key(app="sigma_admin")
    g_logger.info('app_pub_key: %s' % app_pub_key)
    all_dev_info = queryAll(deviceDO, deviceDO.deviceKey.like("{}%".format("25597-")))
    print("dev info num {}".format(len(all_dev_info)))
    ret = delete(deviceDO, deviceDO.deviceKey == "25597-12319123")
    print("del dev {}".format(ret))
    # get_io_info = get_db_conf(ioType=io_type)
    # print "get_io_info:%s" % get_io_info
    # db_vo_info = queryOne(oceanVolumeDO, oceanVolumeDO.id == '17915696402958336')
    # g_logger.info('oceanVolumeDO info: {}'.format(db_vo_info.volumeKey))
