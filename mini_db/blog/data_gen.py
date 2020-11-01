from dataclasses import dataclass  # 装饰器定义 类为数据类
from dataclasses import asdict    # 将数据类实例 转换 为字典，factory函数的 dict_factory
from dataclasses import field, fields   # 返回 Field定义该数据类的字段的对象的元组，可以接受 数据类或 实例数据类。如果未传递数据类或实例，引发Typeerror
from typing import List


@dataclass
class Point:
     x: int
     y: int

@dataclass
class C:
    mylist: list
    z: int = field(repr=False, default=10)
    t: int = 20
    p: int = 0
    def get_x(self):
        self.p:int=self.z + self.t
@dataclass
class PackData(object):
    datas: list
    packed: dict = field(default_factory=dict)

    def packing(self):
        for data in self.datas:
            print(f"data:{data}")
            for k, v in asdict(data).items():
                self.packed[k] = v

#############=++++++++++injector+++++++++++++++++##################
from injector import Module, provider, inject, Injector, singleton
class configuration(object):
    def __init__(self, conn_str):
        self.connection_string = conn_str
def configure_binder(binder):
    conf = configuration(":memory:")
    binder.bind(configuration, to=conf, scope=singleton)


if __name__ == '__main__':
    # print(f"{GenPeople()}")
    # p1 = GenPeople('LJack', 'fJack', 122.21)
    # print(p1)
    # sg = SubGenPeople([p1, GenPeople('KJack', 'Kfood', 222.1)])
    # print(sg)

    p = Point(10, 20)
    print(type(asdict(p)),  asdict(p) )
    print(type(p), p, type(p.__dict__), p.__dict__)
    assert asdict(p) == {'x': 10, 'y': 20}

    p0 = Point(0, 0)
    p1 = Point(10, 4)
    c = C([p0, p1])
    c.get_x()
    print(asdict(c))
    # assert asdict(c) == {'mylist': [{'x': 0, 'y': 0}, {'x': 10, 'y': 4}]}

    pp = PackData([p0, p1])
    pp.packing()
    print(pp)
    print(asdict(pp))


