



"""
    测试：# nametuple命名元组 2021-06-18
"""

import collections
# 通过namedtuple创建的一个元组的子类
# 新建一个元组子类，这个子类名为User，有两个属性值 name和id
# User1就是新建的元组子类，可以用来例化对象
User1 = collections.namedtuple('User', 'name age id')
user = User1('tester', '22', '464643123')

print(user)

u2=User1('tester2','23','sdfsdf')
print(u2)



# set的运算

c1 = set("asfdsgldf")
print(c1)
c2 = set("asfdsgldfkhj")

c3 = c2-c1
print(c3)

