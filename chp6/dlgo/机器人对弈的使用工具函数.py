# from dlgo import gotypes
#
# COLS = 'ABCDEFGHJKLMNOPQRST'  # 字符串变量COLS=‘ABCDEFGHJ KLMNOPQRST’，其字符代表围棋棋盘的列
# STONE_TO_CHAR = {
#     None: ' . ',
#     gotypes.Player.black: 'x',
#     gotypes.Player.white: 'o',
# }
#
#
# def print_move(player, move):
#     if move.is_pass:
#         move_str = 'passes'
#     elif move.is_resign:
#         move_str = 'resigns'
#     else:
#         move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)
#     print('%s %s % (player, move_str)')
#
#
# def print_board(board):
#     for row in range(board.num_rows, 0, -1):
#         bump = " " if row <= 9 else " "
#         line = []
#         for col in range(1, board.num_cols + 1):
#             stone = board.get(gotypes.Point(row=row, col=col))
#             line.append(STONE_TO_CHAR[stone])
#         print('%s%d %s ' % (bump, row, ''.join(line)))
#     print('     ' + '  '.join(COLS[:board.num_cols]))
#
#
# # 将人工输入转换为棋盘坐标
# def point_from_coords(coords):
#     col = COLS.index(coords[0]) + 1
#     row = int(coords[1:])
#     return gotypes.Point(row=row, col=col)



import numpy as np
# tag::print_utils[]
from dlgo import gotypes

# 字符串变量COLS=‘ABCDEFGHJ KLMNOPQRST’，其字符代表围棋棋盘的列
COLS = 'ABCDEFGHJKLMNOPQRST'   # 棋盘列标号
STONE_TO_CHAR = {
    None: ' . ',
    # gotypes.Player.black: ' ○ ',
    # gotypes.Player.white: ' ● ',

    gotypes.Player.black: ' x ',
    gotypes.Player.white: ' o ',
}


def print_move(player, move):  # 打印落子动作状态
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resigns'
    else:
        move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)
    print('%s %s' % (player, move_str))


def print_board(board):   # 打印整个棋盘
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(gotypes.Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.num_cols]))
# end::print_utils[]


# tag::human_coordinates[]
def point_from_coords(coords):  # 就是把人工棋手输入的落子位置转为棋盘的坐标信息
    col = COLS.index(coords[0]) + 1
    row = int(coords[1:])
    return gotypes.Point(row=row, col=col)
# end::human_coordinates[]

# NOTE: MoveAge is only used in chapter 13, and doesn't make it to the main text.
# This feature will only be implemented in goboard_fast.py so as not to confuse
# readers in early chapters.
class MoveAge():
    def __init__(self, board):
        self.move_ages = - np.ones((board.num_rows, board.num_cols))

    def get(self, row, col):
        return self.move_ages[row, col]

    def reset_age(self, point):
        self.move_ages[point.row - 1, point.col - 1] = -1

    def add(self, point):
        self.move_ages[point.row - 1, point.col - 1] = 0

    def increment_all(self):
        self.move_ages[self.move_ages > -1] += 1