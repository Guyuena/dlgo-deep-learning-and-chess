import numpy as np

"""通过列表创建数组"""
a = np.array([1, 2, 3])
print(a)
b = [1, 2, 3, 4, 5]
c = np.array(b)
print(b)
print(c)

"列表的列表创建数组"
a = np.array([[1, 2], [3, 4]])
print(a)

a = np.array([[1, 2], [3, 4]])
print(a)
print('\n')

"数组属性实验验证测试"
a = np.arange(24)
print(a)
print(a.ndim)  # a 现只有一个维度
# 现在调整其大小
b = a.reshape(2, 4, 3)  # b 现在拥有三个维度
print(b)
print("array.ndim: =", b.ndim)  # ndim:秩，即轴的数量或维度的数量
print("array.shape: = ", b.shape)  # shape: 数组的维度，对于矩阵，n 行 m 列
print("array.dtype:=", b.dtype)  # ndarray 对象的元素类型
print("array.itemsize:=", b.itemsize)  # ndarray 对象中每个元素的大小，以字节为单位
print("array.flags：=", b.flags)  # ndarray 对象的内存信息
print("array.data:=", b.data)  # 包含实际数组元素的缓冲区，由于一般通过数组的索引获取元素，所以通常不需要使用这个属性。

"调整数组大小。"
b.shape = (2, 2, 6)
print(b)
print("b.shape: = ", b.shape)

#  NumPy 也提供了 reshape 函数来调整数组大小。

c = b.reshape(3, 4, 2)
print(c)
print("c.shape: = ", c.shape)

"NumPy 从已有的数组创建数组"
#  numpy.asarray
#  numpy.asarray(a, dtype = None, order = None)

"NumPy 从数值范围创建数组"
# numpy.arange
# numpy 包中的使用 arange 函数创建数值范围并返回 ndarray 对象，函数格式如下：
#
#  numpy.arange(start, stop, step, dtype)
print('\n')
x = np.arange(5)
print(x)
x = np.arange(5, dtype=float)
print(x)
x = np.arange(10, 20, 2)
print(x)

"等差数列数组"
# numpy.linspace 函数用于创建一个一维数组，数组是一个等差数列构成的，格式如下：
#                   np.linspace(start, stop, num=n, endpoint=True, retstep=False, dtype=None)
# endpoint	该值为 true 时，数列中包含stop值，反之不包含，默认是True
# retstep	如果为 True 时，生成的数组中会显示间距，反之不显示。

a = np.linspace(1, 10, 10)  # 设置起始点为 1 ，终止点为 10，数列个数为 10。
print("等差数列a: = ", a)

# 将 endpoint 设为 false，不包含终止值：
a = np.linspace(10, 20, 5, endpoint=False)
print(a)
print('\n')

a = np.linspace(1, 10, 10, retstep=True)
print(a)

# 拓展例子
b = np.linspace(1, 10, 10).reshape([10, 1])  # 改变数组形状
print(b)

"numpy.logspace  等比数列数组"
# numpy.logspace 函数用于创建一个于等比数列。格式如下：
#
# np.logspace(start, stop, num=50, endpoint=True, base=10.0, dtype=None)
# 对数log的底数。

# 默认底数是 10
a = np.logspace(1.0, 2.0, num=10)
print(a)

# 将对数的底数设置为 2 :
a = np.logspace(0, 9, 10, base=2)
print(a)
print('\n')

"  NumPy 切片和索引  "
print('NumPy 切片和索引')
a = np.arange(10)
s = slice(2, 7, 2)  # 从索引 2 开始到索引 7 停止，间隔为2
print(a[s])
"冒号 : 的解释：如果只放置一个参数，如 [2]，将返回与该索引相对应的单个元素。" \
"如果为 [2:]，表示从该索引开始以后的所有项都将被提取。如果使用了两个参数，如 [2:7]，那么则提取两个索引(不包括停止索引)之间的项。"

"多维数组索引、切片"
print('\n')
a = np.array([[1, 2, 3], [3, 4, 5], [4, 5, 6]])
print('a.shape:=', a.shape)
print('a.ndims:=', a.ndim)
print(a)
# 从某个索引处开始切割
print('从数组索引 a[1:] 处开始切割')
print(a[1:])
print('\n')

"   切片还可以包括省略号 …，来使选择元组的长度与数组的维度相同。 如果在行位置使用省略号，它将返回包含行中元素的 ndarray。   "
a = np.array([[1, 2, 3], [3, 4, 5], [4, 5, 6]])
print(a)
print('a.shape:=', a.shape)
print('a.ndims:=', a.ndim)
print('第2列元素 a[..., 1]：',a[..., 1])  # 第2列元素
print('第2行元素 a[1, ...]：',a[1, ...])  # 第2行元素
print('第2列及剩下的所有元素 a[..., 1:]:',a[..., 1:])  # 第2列及剩下的所有元素
print('\n')
