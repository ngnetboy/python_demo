# -*- coding: UTF-8 -*-

# 方法1 装饰器
class Singleton(object):
    def __init__(self, aClass):
        self.aClass = aClass
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.aClass(*args, **kwargs)
        return self.instance


@Singleton
class Persion():
    def __init__(self, name, age):
        self.name = name
        self.age = age


# 方法2 共享属性
class Persion2():
    __shared_state = {
        "name" : "netboy",
        "age" : 18
    }

    def __init__(self):
        self.__dict__ = self.__shared_state

# 方法3 元类
class Singleton2(type):
    def __init__(cls, name, bases, dict):
        super(Singleton2, cls).__init__(name, bases, dict)
        cls._instance = None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton2, cls).__call__(*args, **kwargs)
        return cls._instance

class Persion3():
    __metaclass__ = Singleton2
    name = "netboy"
'''
    def __init__(self):
        self.name = "netboy"
        self.age = 18
'''

if __name__ == "__main__":
    print("----------- decorator -------------------------")
    p1 = Persion("netboy", 18)
    p2 = Persion("goodboy", 20)

    print(p1.name, p2.name)  # ---> netboy netboy
    p2.name = "badboy"
    print(p1.name, p2.name)  # ---> badboy badboy

    print("\n----------- __dict__ -------------------------")
    p3 = Persion2()
    p3.name = "goodboy"
    p4 = Persion2()

    print(p3.name, p4.name)  # ---> goodboy goodboy


    print("\n----------- metaclass -------------------------")
    p5 = Persion3()
    p6 = Persion3()

    print(p5.name, p6.name)    # ---> netboy netboy
    Persion3.name = "goodboy"
    print(p5.name, p6.name)    #  ---> goodboy goodboy
    print(Persion3.name)       #  ---> goodboy



