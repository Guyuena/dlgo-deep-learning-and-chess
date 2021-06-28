from dlgo.gotypes import Point

"""
需要明确的是，我们防止是填真眼，真眼除需要上下左右都是同色棋外，还需要一些条件：
    1 在中央只要眼的东北、东南、西南、西北有三个同色棋即可
    2 角部与边上的点的斜对角同色棋保持和棋盘外的角数目为4且棋盘内的斜对角有同色棋即可
"""
__all__ = [
    'is_point_an_eye',
]

"检测落子是否为眼的工具函数"


# 判断棋盘上某个点是否为眼
def is_point_an_eye(board, point, color):
    if board.get(point) is not None:  # 眼必须是一个空点
        return False
    # 判断点是否为眼
    for neighbor in point.neighbors():  # 遍历空点的所有相邻的点，且都必须是己方的棋子
        # 检测邻接点全是己方棋子
        if board.is_on_grid(neighbor):
            neighbor_color = board.get(neighbor)
            if neighbor_color != color:
                return False
    # 判断是否为真  , 四个对角线位置至少三个被己方棋子占据
    friendly_corners = 0
    off_board_corners = 0
    corners = [  # 斜对角集合
        Point(point.row - 1, point.col - 1),
        Point(point.row - 1, point.col + 1),
        Point(point.row + 1, point.col - 1),
        Point(point.row + 1, point.col + 1),
    ]
    # for corner in corners:
    #     if board.is_on_grid(corner):
    #         corner_color = board.get(corner)
    #         if corner_color == color:
    #             friendly_corners += 1
    #     else:
    #         off_board_corners += 1
    # if off_board_corners > 0:
    #     return off_board_corners + friendly_corners == 4  # <4>
    # return friendly_corners >= 3  # <5>
    # for corner in corners:

    """"
        特别--特别注意下面的if-else的逻辑关系，
        一定要正确使用这几个逻辑判断，注意代码的缩进关系
    
    """
    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
        else:
            off_board_corners += 1
    if off_board_corners > 0:  # 点在边角
        return off_board_corners + friendly_corners == 4
    return friendly_corners >= 3
