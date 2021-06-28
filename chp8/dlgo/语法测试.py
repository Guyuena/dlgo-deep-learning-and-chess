# glob.glob(): 返回所有匹配的文件路径列表。它只有一个参数pathname，定义了文件路径匹配规则，这里可以是绝对路径，也可以是相对路径。
# glob.iglob()：获取一个可编历对象，使用它可以逐个获取匹配的文件路径名。与glob.glob()的区别是：glob.glob同时获取所有的匹配路径，而glob.iglob一次只获取一个匹配路径
import glob

for xmlPath in glob.glob('D:/电脑壁纸' + "/*.jpg"):  # 解释：遍历指定文件夹下所有文件或文件夹
    None

# 获取指定目录下的所有图片
print(glob.glob(r"D:/电脑壁纸/*.jpg"))

# 获取上级目录的所有.py文件
print(glob.glob(r'./*.py'))  # 相对路径

# 目录中的.py文件
f = glob.iglob(r'./*.py')
print(f)
for py in f:
    print(py)
# 总结：python的glob模块可以对文件夹下所有文件进行遍历，并保存为一个list列表


"""yield生成器"""


# 在 Python 中，使用了 yield 的函数被称为生成器（generator）。
# 跟普通函数不同的是，生成器是一个返回迭代器的函数，只能用于迭代操作，更简单点理解生成器就是一个迭代器。
def fab(max):
    n, a, b = 0, 0, 1
    while n < max:
        yield b  # 使用 yield
        # print b
        a, b = b, a + b
        n = n + 1


for n in fab(5):
    print(n)
print('\n')
# 简单地讲，yield 的作用就是把一个函数变成一个 generator，带有 yield 的函数不再是一个普通函数，Python 解释器会将其视为一个 generator，
# 调用 fab(5) 不会执行 fab 函数，而是返回一个 iterable 对象！在 for 循环执行时，每次循环都会执行 fab 函数内部的代码，执行到 yield b 时，
# fab 函数就返回一个迭代值，下次迭代时，代码从 yield b 的下一条语句继续执行，而函数的本地变量看起来和上次中断执行前是完全一样的，
# 于是函数继续执行，直到再次遇到 yield。


# 在 Python 中，使用了 yield 的函数被称为生成器（generator）。
# 跟普通函数不同的是，生成器是一个返回迭代器的函数，只能用于迭代操作，更简单点理解生成器就是一个迭代器。
# 在调用生成器运行的过程中，每次遇到 yield 时函数会暂停并保存当前所有的运行信息，返回 yield 的值, 并在下一次执行 next() 方法时从当前位置继续运行。


# import sys
# def fibonacci(n):  # 生成器函数 - 斐波那契
#     a, b, counter = 0, 1, 0
#     while True:
#         if (counter > n):
#             return
#         yield a
#         a, b = b, a + b
#         counter += 1
#
#
# f = fibonacci(10)  # f 是一个迭代器，由生成器返回生成
# while True:
#     try:
#         print(next(f), end=" ")
#     except StopIteration:
#         sys.exit()

"迭代器"
# 迭代是Python最强大的功能之一，是访问集合元素的一种方式。
# 迭代器是一个可以记住遍历的位置的对象。
# 迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。迭代器只能往前不会后退。
"迭代器有两个基本的方法：iter() 和 next()。"
# 字符串，列表或元组对象都可用于创建迭代器：

# 实例(Python 3.0+)
list1 = [1, 2, 3, 4]
it = iter(list1)  # 创建迭代器对象
print(list1)
print(next(it))  # 输出迭代器的下一个元素
print(next(it))
print('\n')

# 迭代器对象可以使用常规for语句进行遍历：
list = [1, 2, 3, 4]
it = iter(list)  # 创建迭代器对象
for x in it:
    print(x, end=" ")
print('\n')
# 也可以不用 iter() 来遍历
"但是不使用 iter()来创建迭代器，不能使用next()的方法"
list = [1, 2, 3, 4]
for x in list:
    print(x, end=" ")

#
# python路径拼接os.path.join()函数的用法
# os.path.join()函数：连接两个或更多的路径名组件
#
#                1.如果各组件名首字母不包含’/’，则函数会自动加上
# 　　　　　　　　　2.如果有一个组件是一个绝对路径，则在它之前的所有组件均会被舍弃
# 　　　　　　　　　3.如果最后一个组件为空，则生成的路径以一个’/’分隔符结尾

import os

Path1 = 'home'
Path2 = 'develop'
Path3 = 'code'

Path10 = Path1 + Path2 + Path3
Path20 = os.path.join(Path1, Path2, Path3)
print('Path10 = ', Path10)
print('Path20 = ', Path20)

"pythonde 装饰器"


# Python中的装饰器（就是以“@”开头的那玩意，下面接着函数定义）。
# 究竟什么是装饰器？没啥特别的。装饰器只是一种接受函数（就是那个你用“@”符号装饰的函数）的函数，并返回一个新的函数。
# 当你装饰一个函数，意味着你告诉Python调用的是那个由你的装饰器返回的新函数，而不仅仅是直接返回原函数体的执行结果
# 装饰器(Decorators)是 Python 的一个重要部分。简单地说：他们是修改其他函数的功能的函数。他们有助于让我们的代码更简短，也更Pythonic（Python范儿）
def simple_decorator(f):
    # This is the new function we're going to return
    # This function will be used in place of our original definition
    def wrapper():
        print("Entering Function")
        f()  # 就是传进来的函数hello()
        print("Exited Function")

    return wrapper


@simple_decorator
def hello():
    print("Hello World")


hello()

# 使用了@ 装饰器，使用simple_decorator这个函数来装饰函数hello(),
# 在使用hello()函数时，hello()就是simple_decorator这个函数的参数，传入，
# 执行是simple_decorator-->hello


"""Flask–路由 """
import os

from flask import Flask  # Flask是一个使用 Python 编写的轻量级 Web 应用框架
from flask import jsonify
from flask import request
from flask import url_for


# 访问地址 : http://127.0.0.1:5000/info/1



