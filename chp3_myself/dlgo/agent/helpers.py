from dlgo.gotypes import Point
# 判断棋盘上某个点是否为眼
def is_point_an_eye(board, point, color):
    if board.get(point) is not None:  # 眼必须是一个空点
        return False

    for neighbor in point.neighbors():  # 所有相邻的点都必须是己方的棋子
        # 检测邻接点全是己方棋子
        if board.is_on_grid(neighbor):
            neighbor_color = board.get(neighbor)
            if neighbor_color != color:
                return False
    # 四个对角线位置至少三个被己方棋子占据
    friendly_corners = 0
    off_board_corners = 0
    corners = [
        Point(point.row - 1, point.col - 1),
        Point(point.row - 1, point.col + 1),
        Point(point.row + 1, point.col - 1),
        Point(point.row + 1, point.col + 1),
    ]
    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
            else:
                off_board_corners += 1
        if off_board_corners > 0:
            return off_board_corners + friendly_corners == 4

        return friendly_corners >= 3