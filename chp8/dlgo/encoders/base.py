# tag::importlib[]
import importlib
# end::importlib[]

__all__ = [
    'Encoder',
    'get_encoder_by_name',
]


# tag::base_encoder[]
"""编码器接口"""
class Encoder:
    def name(self):  # <1># 把模型正在使用的编码器名称输出到日志中或存储下来
        raise NotImplementedError()

    def encode(self, game_state):  # <2> # 把棋盘棋盘转化成数字数据
        raise NotImplementedError()

    def encode_point(self, point):  # <3> # 将围棋棋盘点转换为整数索引
        raise NotImplementedError()

    def decode_point_index(self, index):  # <4> # 将整数索引转换为围棋棋盘落子点
        raise NotImplementedError()

    def num_points(self):  # <5>   #围棋棋盘上的交叉点的数目 - 棋盘宽度乘以棋盘高度
        raise NotImplementedError()

    def shape(self):  # <6>  # 已经编码的棋盘结构外形
        raise NotImplementedError()

# <1> Lets us support logging or saving the name of the encoder our model is using.
# <2> Turn a Go board into a numeric data.
# <3> Turn a Go board point into an integer index.
# <4> Turn an integer index back into a Go board point.
# <5> Number of points on the board, i.e. board width times board height.
# <6> Shape of the encoded board structure.
# end::base_encoder[]


# tag::encoder_by_name[]
"""通过名字返回相应的编码器"""
def get_encoder_by_name(name, board_size):  # <1> 根据编码器名字来构建它的实例
    if isinstance(board_size, int):
        board_size = (board_size, board_size)  # <2>
    module = importlib.import_module('dlgo.encoders.' + name)  # 获取名字对应的模块
    constructor = getattr(module, 'create')  # <3>  # 每个编码器的实现类都必须提供一个“create”函数来创建新的实例
    return constructor(board_size)

# <1> We can create encoder instances by referencing their name.
# <2> If board_size is one integer, we create a square board from it.
# <3> Each encoder implementation will have to provide a "create" function that provides an instance.
# end::encoder_by_name[]