# 从SGF文件中重放游戏记录。原来的SGF文件编码游戏移动与字符串，
# 如B[ee]。Sgf_game类解码这些字符串并将它们作为Python元组返回。
# 你就可以将这些落子应用到GameState对象以重建游戏


# 先从新的gosgf模块导入Sgf_game类
import dlgo
from dlgo.gosgf.sgf import Sgf_game
from dlgo.goboard_fast import GameState, Move
from dlgo.gotypes import Point
from dlgo.utils import print_board

# 从SGF文件中重放游戏记录。原来的SGF文件编码游戏移动与字符串，如B[ee]。Sgf_game类解码这些字符串并将它们作为Python元组返回。
# 你就可以将这些落子应用到GameState对象以重建游戏

# 定义示例SGF字符串，此内容稍后会来自下载的数据
sgf_content = "(;GM[1]FF[4]SZ[9];B[ee];W[ef];B[ff]" + ";W[df];B[fe];W[fc];B[ec];W[gd];B[fb])"

# 使用from_string方法，您可以创建一个SGF_game
print(type(sgf_content))
print(sgf_content)
sgf_game = Sgf_game.from_string(sgf_content)
game_state = GameState.new_game(19)

# 重复游戏的主要顺序，你忽略了棋局变化和评论
for item in sgf_game.main_sequence_iter():
    # 这个主序列中的项是(颜色，落子)对，其中"落子"是一对坐标。
    color, move_tuple = item.get_move()
    if color is not None and move_tuple is not None:
        row, col = move_tuple
        point = Point(row + 1, col + 1)
        move = Move.play(point)
        # 将读出的落子应用到棋盘上
        game_state = game_state.apply_move(move)
        print_board(game_state.board)
