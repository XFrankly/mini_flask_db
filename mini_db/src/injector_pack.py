from injector import Module, provider, inject, Injector, singleton
import sqlite3

sql_query = 'SELECT key, value FROM data ORDER BY key'
sql_create = 'CREATE TABLE IF NOT EXISTS data (key PRIMARY KEY, value)'
sql_insert = 'INSERT OR REPLACE INTO data VALUES ("hello", "world")'


class RequestHandler(object):
    @inject
    def __init__(self, db:sqlite3.Connection):    # 功能参数的类型注释（也称为类型提示）的标准。该PEP向Python添加了语法，用于注释变量的类型，包括类变量和实例变量
        # 像函数注释一样，Python解释器不会在变量注释中附加任何特殊含义，而仅将它们存储在__annotations__类或模块的 属性中
        self._db = db
    def get(self):
        cursor = self._db.cursor()
        res = cursor.execute(sql_query)
        return res.fetchall()

class configuration(object):
    def __init__(self, conn_str):
        self.connection_string = conn_str

# class Configure_for_testing(object):
#     @staticmethod
def configure_binder(binder):
    conf = configuration(":memory:")
    binder.bind(configuration, to=conf, scope=singleton)

class data_base_module(Module):
    """配置注册器 和 提供者"""
    # def __init__(self, configuration):
    #     self.conf = configuration
    @provider
    # @singleton
    def provide_sqlite_connection(self, configuration:configuration)->sqlite3.Connection:
        # if not configuration:
        #     configuration = self.conf
        conn = sqlite3.connect(configuration.connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_create)
        cursor.execute(sql_insert)
        print(f"conn:{conn}, {conn==True}")
        return conn

def main():
    """初始化一个Injector并使用它实例化一个RequestHandler实例。首先，该方法可传递地构造一个sqlite3.Connection对象，
    并依次构造所需的Configuration字典，然后实例化我们的RequestHandler"""
    db_obj = data_base_module()
    print(f"db obj:{db_obj}")
    db_obj2 = data_base_module()
    print(f"sing:{db_obj is db_obj2}, db_obj2:{db_obj2}, dir1:{dir(db_obj) }, \n dir2:{dir(db_obj2)} \n {db_obj2.__dict__ == db_obj.__dict__}")
    # print(f"{db_obj2.provide_sqlite_connection() is db_obj.provide_sqlite_connection()}")
    injec = Injector([configure_binder, db_obj])  # configure_binder,
    handler = injec.get(RequestHandler)
    print(f'handler:{handler}')
    tp = tuple(map(str, handler.get()[0]))
    print(f'result:{handler}, get:{handler.get()}, returns:{tp}')
    return tp


if __name__ == '__main__':
    main()