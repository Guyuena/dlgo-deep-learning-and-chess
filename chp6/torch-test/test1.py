import torch

print(torch.__version__)

"""通过列表创建tensor"""
t1 = torch.tensor([1, 2, 3, 4, 5])
print(t1.type())
print(t1.dtype)  # 打印该tensor的元素的数据类型
print(t1)

"""通过元组创建 """
t2 = torch.tensor((1, 2, 3, 4, 5))
print(t2.type())
print(t2.dtype)  # 打印该tensor的元素的数据类型
print(t2)

""" 通过array数组创建张量"""
import numpy as np

a1 = np.array((1, 2, 3, 4, 5))
print(type(a1))
print(a1)
t3 = torch.tensor(a1)
print(t3.type())
print(t3)
print('\n')

"""维度与形状"""
t4 = torch.tensor([1, 2, 3, 4, 5])
print(t4.type())
print(t4.dtype)  # 打印该tensor的元素的数据类型
print(t4.ndim)  # 张量维度信息
print(t4.shape)  # 张量形态size信息
print(t4.size())  # 张量形态size信息
print(len(t4))  # 返回有几个（N）维的元素
print(t4.numel())  # 返回总共拥有几个数
print(t4)

"""使用”序列“的”序列“创建二维数组"""

# 使用list的list创建二维数组

t5 = torch.tensor([[1, 2], [3, 4]])
print(t5.type())
print(t5.dtype)  # 打印该tensor的元素的数据类型
print("张量的维度 ", t5.ndim)  # 张量维度信息
print("张量的形状 N行*N列 ", t5.shape)  # 张量形态size信息
print("张量的size形状 N行*N列 ", t5.size())  # 张量形态size信息
print('张量拥有在维度上的张量单元个数 ', len(t5), "表示有这么多个 N-1维的张量构成")  # 返回有几个（N-1）维的元素
print("张量拥有的所有元素个数 ", t5.numel())  # 返回总共拥有几个数
print(t5)

# 零维张量

t6 = torch.tensor(123)
print("张量的维度 ", t6.ndim)  # 张量维度信息
print(t6)
print('\n')

# 高维数组创建张量
a2 = np.array([[1, 2, 3], [4, 5, 6]])
print(a2)
a3 = np.array([[7, 8, 9], [10, 11, 12]])
print(a3)
t7 = torch.tensor([a2, a3])  # 使用两个相同形状二维数组构建三维张量

print("张量的维度 ", t7.ndim)  # 张量维度信息
print("张量的形状 ", t7.shape)  # 张量形态size信息 这里高维这里信息是 N个 m行s列的矩阵的张量
print("张量的形状信息shape[0] ", t7.shape[0])
print("张量的size形状  ", t7.size())  # 张量形态size信息
print('张量拥有在维度上的张量单元个数 ', len(t7))  # 返回有几个（N-1）维的元素
print("张量拥有的所有元素个数 ", t7.numel())  # 返回总共拥有几个数
print(t7)
print('\n')

"""张量的形状的变化"""

# flatten  任意维度张量展为一维张量

t8 = t7.flatten()
print("t8", t8)
print(t8.ndim)
print('\n')
# reshape() 任意变形

t9 = t8.reshape(2, 6)  # 二维，每个维度6个单元元素
print("t9", t9)
print(t9.size())
print(t9.ndim)
print('\n')

t10 = t8.reshape(2, 2, 3)  # 三维
print("t10", t10)
print(t8.size())
print(t10.ndim)
print(t10[0][0])
print(t10[0][0].ndim)
print('\n')

t11 = t8.reshape(2, 1, 3, 2)  # 四维
print("t11", t11)
print(t8.size())
print(t11.ndim)
print(t11[0][0])
print(t11[0][0].ndim)
print('\n')

t12 = t8.reshape(3, 1, 2, 2)  # 四维
print("t12", t12)
print(t8.size())
print(t12.ndim)
print(t12[0][0])
print(t12[0][0].ndim)
print('\n')

