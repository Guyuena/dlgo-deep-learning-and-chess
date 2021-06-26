
# tag::oneplane_imports[]
import numpy as np

from dlgo.encoders.base import Encoder
from dlgo.goboard import Point
# end::oneplane_imports[]


"""实现编码器
    使用单平面围棋棋盘编码器对游戏状态进行编码
"""

# tag::oneplane_encoder[]
# 使用1表示下一回合落子方，并用-1表示对手。将把这种编码称为OnePlaneEncoder
class OnePlaneEncoder(Encoder):
    # 初始化
    def __init__(self, board_size): # 传入棋盘大小·
        self.board_width, self.board_height = board_size
        self.num_planes = 1  # 平面数量

    def name(self):  # <1>  可以应oneplane来指代这个编码器
        return 'oneplane'


    # 把棋盘棋盘转化成数字数据,编码成三维矩阵
    # 重写 Encoder类的encode()方法
    def encode(self, game_state):  # <2>
        board_matrix = np.zeros(self.shape())  # 棋盘矩阵
        next_player = game_state.next_player
        for r in range(self.board_height):
            for c in range(self.board_width):
                p = Point(row=r + 1, col=c + 1)
                go_string = game_state.board.get_go_string(p)
                if go_string is None:
                    continue
                # 是当前落子方，编码为1
                if go_string.color == next_player:
                    board_matrix[0, r, c] = 1
                else:   # 不是当前落子方，编码为-1
                    board_matrix[0, r, c] = -1
        return board_matrix

# <1> We can reference this encoder by the name "oneplane".
# <2> To encode, we fill a matrix with 1 if the point contains one of the current player's stones, -1 if the point contains the opponent's stones and 0 if the point is empty.
# end::oneplane_encoder[]

# tag::oneplane_encoder_2[]
    # 将围棋棋盘点转换为整数索引
    def encode_point(self, point):  # <1>
        return self.board_width * (point.row - 1) + (point.col - 1)

    # 将整数索引转换为围棋棋盘落子点
    def decode_point_index(self, index):  # <2>
        row = index // self.board_width
        col = index % self.board_width
        return Point(row=row + 1, col=col + 1)

    # 围棋棋盘上的交叉点的数目 --》 棋盘宽度乘以棋盘高度
    def num_points(self):
        return self.board_width * self.board_height

    # 已经编码的棋盘结构外形
    def shape(self):
        return self.num_planes, self.board_height, self.board_width

# <1> Turn a board point into an integer index.
# <2> Turn an integer index into a board point.
# end::oneplane_encoder_2[]


# tag::oneplane_create[]
"""实例化oneplane编码器"""
def create(board_size):
    return OnePlaneEncoder(board_size)
# end::oneplane_create[]
