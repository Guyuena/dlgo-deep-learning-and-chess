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
list1 = [1,2,3,4]
it = iter(list1)    # 创建迭代器对象
print(list1)
print(next(it))   # 输出迭代器的下一个元素
print(next(it))
print('\n')

# 迭代器对象可以使用常规for语句进行遍历：
list=[1,2,3,4]
it = iter(list)    # 创建迭代器对象
for x in it:
    print (x, end=" ")
print('\n')
# 也可以不用 iter() 来遍历
"但是不使用 iter()来创建迭代器，不能使用next()的方法"
list=[1,2,3,4]
for x in list:
    print (x, end=" ")



"""将字符串处理成只有ASCII字符"""
import unicodedata, sys

print()

a = 's\u00f1o'
print(a)
print(ascii(a))
b = unicodedata.normalize('NFD', a)
print(b)
print(ascii(b))

print()


result1 = a.encode('ascii', 'ignore').decode('ascii')
print(result1)
result = b.encode('ascii', 'ignore').decode('ascii')  # 这里的ascii可以改成你想处理成的任何编码格式
print(result)

from dlgo.data.parallel_processor import GoDataProcessor   # 训练数据处理器
from dlgo.encoders.oneplane import OnePlaneEncoder  # 编码器
from dlgo.networks.small import layers   # 待训练的网络