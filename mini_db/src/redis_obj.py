"""
    Redis 数据结构封装
"""
from src.redisdb import redis_db
import logging


# base
class RedisObject(object):
    """redis 对象基类"""

    def __init__(self, redis_key, client=redis_db.client):
        self._client = client
        self._pipeline = None
        self._redis_key = redis_key
        self._redis_key_suffix = None

    @property
    def key(self):
        """获取缓存对象的key"""
        if self._redis_key_suffix:
            return f"{self._redis_key}:{self._redis_key_suffix}"
        else:
            return self._redis_key

    @property
    def client(self):
        """获取redis 客户端对象"""
        return self._pipeline or self._client

    def suffix(self, key_suffix):
        """设置key后缀，用于变化的key"""
        self._redis_key_suffix = key_suffix
        return self

    def exists(self):
        """判断缓存是否存在， 存在返回1， 不存在返回0"""
        return self.client.exists(self.key)

    def expire(self, time):
        """设置生存时间，当key过期时，生存时间为0，它将被自动删除
        :params:time 秒或timedelta对象，
        :return: 设置成功返回1"""
        return self.client.expire(self.key, time)

    def expireat(self, when):
        """EXPIREAT 与 EXPIRE类似，都用于为key设置生存时间。
        不同在于EXPIREAT命令接收时间参数UNITX时间戳(unix timstemp)"""
        return self.client.expireat(self.key, when)

    def ttl(self):
        """秒为单位，返回给定的key的剩余生存时间
        :return: key不存在，返回-2，key存在但没有设置剩余生存时间时，返回-1，
        否则以秒为单位，返回剩余生存时间"""
        return self.client.ttl(self.key)

    def pexpire(self, time):
        """这个命令和EXPIRE命令类似，但它以毫秒为单位设置key生存时间，不像EXPIRE命令以秒为单位
        :params time: 毫秒或者timedelta对象
        :return: 设置成功返回1"""
        return self.client.pexpire(self.key, time)

    def pexpireat(self, when):
        """这个命令与EXPIREAT类型，但它以毫秒为单位 key 过期unix时间戳，而不是像EXPIREAT以秒为单位
        :param when:时间戳或者datetime对象
        :return: 设置成功返回1
        """
        return self.client.pexpireat(self.key, when)

    def pttl(self):
        """这个命令类似TTL命令，但它以毫秒为单位返回key剩余生存时间， 而不是像TTL为秒
        :return: 当key不存在时，返回-2， 当key存在但没有设置剩余生存时间时，返回-1.否则返回剩余生存时间的毫秒单位"""
        return self.client.pttl(self.key)

    def persist(self):
        """移除给定生存时间，变成永久存在的对象
        :return: 当生存时间移除成功时，返回1，"""
        return self.client.persist(self.key)

    def type(self):
        """返回所存储的值的类型
        :return:none (key不存在)string(字符串)list(列表)set(集合)zset(有序集)hash(哈希表)"""
        return self.client.type(self.key)

    def delete(self):
        """删除缓存数据
        :return:被删除key的数量"""
        return self.client.delete(self.key)

    def pipeline(self):
        """开启管道"""
        self._pipeline = self.client.pipeline()

    def execute(self):
        """管道执行"""
        self._pipeline.execute()
        self._pipeline = None

    @staticmethod
    def keys(pattern='*', client=redis_db.client):
        """取以key开头的所有值"""
        return client.keys(pattern)


# String
class RedisString(RedisObject):
    """Redis String 结构"""

    def get(self):
        """返回key所关联的字符串值
        :return:当key不存在时，返回None，否则返回key的值"""
        return self.client.get(self.key)

    def strlen(self):
        """返回key所存储的字符串值的长度
        :return:字符串值的长度,当key不存在时，返回0"""
        return self.client.strlen(self.key)

    def getset(self, value):
        """将给定key值设置为value，并返回key的旧值（old value）
        :param value:
        :return 返回给定key的旧值，当key没有旧值时，即key不存在，返回None"""
        return self.client.getset(self.key, value)

    def set(self, value, ex=None, px=None, nx=False, xx=False):
        """将字符串value关联到key，如果key已经持有其他值，SET覆盖旧值，无视类型。 如果原本带有生存时间TTL
        当SET命令成功在带有TTL的键执行，原有的TTL将被清除。
        :params ex: second 设置键的过期时间为second秒。SET key value EX second效果等同于SETEX key second value
        :PX millisecond: 设置键的过期时间为millisecond 毫秒。 SET key value PX millisecond 效果等同于 PSETEX key millisecond value
        :NX: 只有键不存在时，才对键进行设置操作。SET key value NX 效果等同于 SENTNX key value
        XX: 只在键存在时，才对键进行设置操作"""
        return self.client.set(self.key, value, ex, px, nx, xx)

    def setnx(self, value):
        """将key值设为value，当且仅当key不存在
        :return: 设置成功返回1"""
        return self.client.setnx(self.key, value)

    def setex(self, time, value):
        """将值value关联到key，并将key生存时间设为seconds（以秒为单位）
        如果key已经存在，SETEX命令将覆盖旧值"""
        return self.client.setex(self.key, time, value)

    def psetex(self, time_ms, value):
        """此命令与 SETEX 相似，但它以毫秒为单位设置key生存时间，而不似SETEX的 秒单位"""
        return self.client.psetex(self.key, time_ms, value)

    def setrange(self, offset, value):
        """用value 参数覆盖 overwrite 给定的key所存储的字符串值，从偏移量 offset 开始
        :return: 被SETRANGE修改后，字符串的长度"""
        return self.client.setrange(self.key, offset, value)

    def getrange(self, start, end):
        """返回key中字符串值的 子字符串，字符串的截取范围由start 和 end两个偏移量决定(包括start，end)
        负数偏移量表示从字符串最后开始计数， -1表示最后一个字符，依此类推
        :return: 截取的子字符串
        """
        return self.client.getrange(self.key, start, end)

    def append(self, value):
        """如果key已经存在并是一个字符串，APPEND命令将value追加到key 原值的 末尾。
        如果key不存在，APPEND将给定的key 设为value，就像执行SET key value
        :return: 追加 value 之后， key中字符串的长度"""
        return self.client.append(self.key, value)

    def setbit(self, offset, value):
        """对 key 所存储的字符串值，设置或清除指定偏移量上的位（bit）， 位的设置或清除取决于value参数，可以是0 或1
        :return: 指定偏移量原来存储的位"""
        return self.client.setbit(self.key, offset, value)

    def getbit(self, offset):
        """对key所存储的字符串值，获取指定偏移量上的位（bit）
        当offset比字符串值长度大， 或key不存在， 返回0
        :return: 字符串指偏移量上的位（bit）
        """
        return self.client.getbit(self.key, offset)

    def decr(self, decrement=1):
        """将key所存储的值减去减量 decrement，默认值 1
        :return: 执行DECR命令后的key 值"""
        return self.client.decr(self.key, decrement)

    def incr(self, incrment=1):
        """将key所存储的值加上增量increment。 默认位1"""
        return self.client.incr(self.key, incrment)


# ArrayList
class RedisList(RedisObject):
    """Redis ArrayList 结构"""

    def lpop(self):
        """移除并返回列表key的头元素"""
        return self.client.lpop(self.key)

    def rpop(self):
        """移除并返回列表key尾元素"""
        return self.client.rpop(self.key)

    def lpush(self, *values):
        """将一个或多个值 value插入列表key的表头
        :return:执行LPUSH命令后，列表长度"""
        return self.client.lpush(self.key, *values)

    def rpush(self, *values):
        """将一个，多个值value插入到列表key表尾 （最右边）"""
        return self.client.rpush(self.key, *values)

    def lpushx(self, value):
        """将值value插入到列表key的表头，只有当key 粗壮并是一个列表 和 LPUSH 命令相反。
        当key不存在，LPUSHX命令啥也不做
        :return: 执行LPUSHX命令后，列表的长度"""
        return self.client.lpushx(self.key, value)

    def rpushx(self, value):
        """将值value 插入列表key表尾，只有当key存在并且是一个列表。
        与RPUSH相反，当key不存在，RPUSHX 什么也不做
        :return: 执行RPUSHX命令后列表长度"""
        return self.client.rpushx(self.key, value)

    def lset(self, index, value):
        """将列表key下标为index的元素的值为 value
        当index参数超出返回，或对一个空列表(key 不存在)进行LSET时，返回一个错误"""
        return self.client.lset(self.key, index, value)

    def lindex(self, index):
        """返回列表key中，下表为index的元素，下标从0开始"""
        return self.client.lindex(self.key, index)

    def lrange(self, start, end):
        """返回列表key中指定区间的元素，区间以偏移量start， stop指定"""
        return self.client.lrange(self.key, start, end)

    def llen(self):
        """返回列表key的长度，如果key不存在，则key被解释为一个空列表，返回0"""
        return self.client.llen(self.key)

    def lrem(self, value, num=0):
        """根据参数 num 的值， 移除列表中与参数value相等 的元素
        num > 0: 从表头开始向表尾搜索，移除与value相等的元素，数量为num
        num < 0: 从表尾开始向表头搜索，移除与value 相等的元素，数量为num绝对值
        num = 0: 移除表中所有与value向等的值
        :return: 被移除元素的数量
        """
        return self.client.lrem(self.key, num, value)


# HashMap
class RedisMap(RedisObject):
    """Redis HashMap 结构"""

    def hexists(self, key):
        """查看hash 表 key中，给定域field是否存在
        :return:如果hash表含有给定域，返回1"""
        return self.client.hexists(self.key, key)

    def hget(self, key):
        """返回哈希表key中给定域field的值"""
        return self.client.hget(self.key, key)

    def hset(self, key, value):
        """将哈希表key中的域 field值设为value
        如果key不存在，新的哈希表 将被创建并进行HSET操作
        如果域field 已经存在哈希表中，旧值将被覆盖
        :return: 如果field 时哈希表中一个新建域，并且值设置成功。返回1. 如果field已经存在，且新值覆盖了旧值，返回0"""
        return self.client.hset(self.key, key, value)

    def hsetnx(self, key, value):
        """将哈希表key中的域 field值设置为value， 只有当域field不存在时。
        若域field已经存在，该操作无效。
        如果key不存在，一个新的哈希表被创建并执行HSETTNX
        :return: 设置成功返回 1"""
        return self.client.hsetnx(self.key, key, value)

    def hmget(self, keys, *args):
        """返回哈希表 key中，一个或多个给定域的值
        :return:一个包含多个给定域的关联值的表。表值的排列顺序和给定域参数请求顺序一样。"""
        return self.client.hmget(self.key, keys, *args)

    def hmset(self, mapping):
        """同时将多个field0value对设置到哈希表 key中，此命令将覆盖哈希表已存在的域。
        如果key不存在，一个空哈希表被创建并执行 HMSET操作"""
        logging.debug(f"redis_hmset_mapping:{mapping}")
        return self.client.hmset(self.key, mapping)

    def hdel(self, *keys):
        """删除哈希表 key 的一个或多个指定域，不存在的域将被忽略"""
        self.client.hdel(self.key, *keys)

    def hgetall(self):
        """返回 哈希表key中，所有域和值
        返回值中，紧跟每个域名 field name 之后的时域的值 value
        所以返回值的长度时哈希表大小的两倍"""
        return self.client.hgetall(self.key)

    def hkeys(self):
        """返回哈希表key中所有的域"""
        return self.client.hkeys(self.key)

    def hvals(self):
        """返回哈希表 key 中所有域的值"""
        return self.client.hvals(self.key)

    def hlen(self):
        """返回哈希表key中域的数量
        :return:哈希表域的数量"""
        return self.client.hlen(self.key)

    def hincrby(self, key, amount=1):
        """为哈希表key中的域field值加上增量 increment
        增量也可以为负数，相当于对给定域进行减法操作
        如果key不存在，一个新的哈希表被创建并执行HINCRBY命令
        如果域field不存在，那么在执行命令前，该域的值被初始化为0
        对一个存储字符串值的域field 执行HINCRBY命令将造成一个错误
        本操作的值被限制在 64 位(bit)由符号数字表示之内
        :return: 执行HINCRBY之后，哈希表key中域field的值"""
        return self.client.hincrby(self.key, key, amount)

    def hscan(self, cursor=0, match=None, count=None):
        """ 增量地带哈希键中的键值对"""
        cursor, data = self.client.hscan(self.key, cursor, match, count)
        while cursor != 0 and not data:
            cursor, data = self.client.hscan(self.key, cursor, match, count)
        return cursor, data


# HashSet
class RedisSet(RedisObject):
    """Redis HashSet 结构"""

    def scard(self):
        """返回集合中元素总数量"""
        return self.client.scard(self.key)

    def sismember(self, value):
        """判断member元素是否集合key的成员"""
        return self.client.sismember(self.key, value)

    def sadd(self, *values):
        """将一个或多个member元素加入到集合key，已经存在域集合的member元素将被忽略
        加入key 不存在，则创建一个只包含member元素做成员的集合
        :return: 被添加到集合中的新元素的数量，不包括被忽略的元素"""
        return self.client.sadd(self.key, *values)

    def srem(self, *values):
        """移除集合key中的一个或多个member 元素， 不存在的member、元素将被忽略
        :return: 被成功移除的元素的数量，不包括被忽略的元素"""
        return self.client.srem(self.key, *values)

    def spop(self, count=None):
        """移除并返回集合中的一个随机元素
        :return: 被移除的随机元素"""
        return self.client.spop(self.key, count)

    def smembers(self):
        """返回集合key中所有成员，不长脑子的key被视为空集合"""
        return self.client.smembers(self.key)

    def srandmember(self, number=None):
        """如果命令执行时， 只有key参数， 那么返回集合中一个随机元素。
        如果count为正数，且小于集合基数，那么命令返回一个保护count个元素的数组。数组的元素各不同
        如果count是负数，那么命令返回一个数组，数组的元素可能会重复出现多次，而数组长度为count绝对值

        该操作和SPOP相似，但SPOP将随机元素从集合中移除并返回，而srandmember 不对集合做任何改动，仅仅返回随机元素"""
        return self.client.srandmember(self.key, number)

    def sscan(self, cursor=0, match=None, count=None):
        """增量迭代集合键中的元素"""
        cursor, data = self.client.sscan(self.key, cursor, match, count)
        while cursor != 0 and not data:
            cursor, data = self.client.sscan(self.key, cursor, match, count)
        return cursor, data


# SortedSet
class RedisZSet(RedisObject):
    """Redis SortedSet 结构"""

    def zcard(self):
        """返回有序集中元素总数量"""
        return self.client.zcard(self.key)

    def zdd(self, mapping, nx=False, xx=False, ch=False, incr=False):
        """把一个或多个member元素及其score值加入到有序集 key中
        如果某member 已经是有序集成员，那么更新这个member的score值，并通过重新插入这个member元素，保证该member在正确位置
        :return: 被成功添加的新成员的数量， 不包括那些被更新的，已经存在的成员。"""
        return self.client.zadd(self.key, mapping, nx, xx, ch, incr)

    def zscore(self, value):
        """返回有序集key中，成员member的score值
        :return: member 成员是score值，以字符串形式表示"""
        return self.client.zscore(self.key, value)

    def zincrby(self, value, amount=1):
        """为有序集key的成员member的score值加上增量 increment
        可以通过传递一个负数值 increment，让score减去相关的值，比如ZINCRBY key -5 member， 就是让member的score减去5
        当key不存在，或member不是key的成员，ZINCRBY key increment member 等同于 ZADD key increment member
        :return: member 成员的score值，以字符串形成表示"""
        return self.client.zincrby(self.key, amount, value)

    def zrank(self, value):
        """
        返回有序集key中成员member的牌面，其中有序集成员按score值递增(从小到大)顺序排列
        排名为0的 是底， 即score值最小的成员排名 0
        :returnL如果member 是有序集 key的成员，返回member排名
        """
        return self.client.zrank(self.key, value)

    def zrevrank(self, value):
        """
        返回有序集key的成员member的排名，其中有序集成员按score值递减 从大到小的 排序
        排名以0为底， 即score最大的成员排名0
        :return: 如果member 是有序集key的成员，返回member排名
        """
        return self.client.zrevrank(self.key, value)

    def zcount(self, min_score, max_score):
        """返回有序集key中， score值在min，max之间(默认包括score值等于min或max)的成员数量"""
        return self.client.zcount(self.key, min_score, max_score)

    def zrem(self, *values):
        """移除有序集key中的一个或多个成员，不存在的成员将被忽略"""
        return self.client.zrem(self.key, *values)

    def remrangebyrank(self, min_score, max_score):
        """移除有序集key中，指定排名 rank 区间内的所有成员
        区间分别以下标参数start 和stop指出，包含start 和 stop在内
        下标参数start 和stop 都以0 为底，即以0表示有序集第一个成员，以1表示有序集第2个
        也可以用负数作为下标，以 -1 表示最后一个成员，依此类推"""
        return self.client.zremrangebyrank(self.key, min_score, max_score)

    def zremrangebuscore(self, min_score, max_score):
        """移除有序集key中，所有score值介于min和max之间 包括等于，的成员"""
        return self.client.zremrangebyscore(self.key, min_score, max_score)

    def zrange(self, start, end, desc=False, withscores=False, score_cast_func=float):
        """返回有序集key中，指定区间内的成员
        其中成员位置按score 值递增 从小到大 排序
        具有相同score值的成员按字典序 lexicographical order排列"""
        return self.client.zrange(self.key, start, end, desc, withscores, score_cast_func)

    def zrangebuscore(self, min_socre, max_score, start=None, num=None, withscores=False, socre_cast_func=float):
        """
        返回有序集key中，所有score值介于min，max之间（包括等于）的成员，有序集成员按score值递增，从小到大排序
        具有相同score值的成员按字典序lexicographical order排序（该属性是有序集提供的，不需要额外计算）
        可选LIMIT参数指定返回结果的数量及区间（类似SQL的SELECT LIMIT offset， count）注意当offset很大时，定位操作可能需要遍历整个有序集，次过程最坏复杂度O(N)
        可选WITHSCORES参数决定结果集时蛋蛋返回有序集的成员，还是将有序集成员及其score值一起返回
        """
        return self.client.zrangebyscore(self.key, min_socre, max_score, start, num, withscores, socre_cast_func)

    def zrevrange(self, start, end, withscores=False, score_cast_func=float):
        """返回有序集key中，指定区间的成员
        其中成员位置按score值递减 从大到小 排序
        具有相同score值的成员按字典序的逆序 reverse lexicographical order 排序"""
        return self.client.zrevrange(self.key, start, end, withscores, score_cast_func)

    def zrevrangebuscore(self, max_score, min_score, start=None, num=None, withscores=False, score_cast_func=float):
        """返回有序集key中，所有score值介于min，max之间（包括等于）的成员，有序集成员按score值递减，从大到小排序
        具有相同score的值成员按字典序的逆序 reverse lexicographical order 排序"""
        return self.client.zrevrangebyscore(self.key, max_score, min_score, start, num, withscores, score_cast_func)

    def zscan(self, cursor=0, match=None, count=None, score_cast_func=float):
        """增量迭代有序集合中的元素 包括元素成员和元素分值"""
        cursor, data = self.client.zscan(self.key, cursor, match, count, score_cast_func)
        while cursor != 0 and not data:
            cursor, data = self.client.zscan(self.key, cursor, match, count, score_cast_func)
        return cursor, data



if __name__ == '__main__':
    # 从redis服务 list取出数据并赋予值
    retry = RedisList(f"retry:replay:{'http://127.0.0.1:3067/replay'}")

    # 缓存操作设置
    import time
    cache = RedisMap(f"{__file__.__name__.lower()}:{time.time()}")

    # table manager
    table_manager = RedisSet(f"table:mgr:{'http://127.0.0.1:3067'}")

    # 如果不用以上封装方法，依赖第三方库直接调用
    import redis as rd
    redis = rd.Redis(host='', port='', password='', db='')
    pipe = redis.pipeline()

    raw = redis.hget('key_id', 'name')
    pipe.hset('redis_key', 'name', 'value')

    # 在其他模块导入定义的redis




