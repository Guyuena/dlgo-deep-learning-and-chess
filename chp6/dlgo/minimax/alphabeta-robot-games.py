from __future__ import print_function
from dlgo.minimax.alphabeta import AlphaBetaAgent
from dlgo.gotypes import Player, Point
from dlgo.utils import print_move, print_board, point_from_coords
from dlgo.minimax.depthprune import DepthPrunedAgent
from dlgo import goboard, gotypes
from six.moves import input
import time
"""":argument
    加入剪枝的游戏机器对弈脚本

"""


# 用棋盘上黑白棋子数目来评估棋盘---最简单的评估
def capture_diff(game_state):
    black_num = 0
    white_num = 0

    # 遍历棋盘获得黑白棋子个数
    for r in range(1, game_state.board.num_rows):
        for c in range(1, game_state.board.num_cols):
            point = Point(row=r, col=c)
            color = game_state.board.get(point)
            if color == Player.black:
                black_num += 1
            elif color == Player.white:
                white_num += 1

    # 根据当前的落子方得出局面相应的评估
    diff = black_num - white_num
    if game_state.next_player == Player.black:
        return diff
    else:
        return -1 * diff


# "人机对战 start"
# def main():
#     # 建一个5*5的棋盘
#     game = goboard.GameState.new_game(5)
#     bot = AlphaBetaAgent(2, capture_diff)  # 注意例化时的参数类型
#
#     while not game.is_over():
#         print_board(game.board)
#         if game.next_player == Player.black:
#             human_input = input('-- ')
#             point = point_from_coords(human_input)
#             move = goboard.Move.play(point)
#         else:
#             # 计算一下AI的思考时间
#             start_time = time.time()
#             move = bot.select_move(game)
#             end_time = time.time()
#             print("AI思考时间：" + str(end_time - start_time) + "秒")
#         print_move(game.next_player, move)
#         game = game.apply_move(move)
#
#
# if __name__ == '__main__':
#     main()
#
# "人机对战 end"


# 机器人对战机器人            为了显示方便去吧 goboard.py的这条语句注释掉  print('Illegal play on %s' % str(point)) 并用语句代替
def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    bots = {
        gotypes.Player.black: AlphaBetaAgent(2, capture_diff),  # 特别注意AlphaBetaAgent的例化参数eval_fn： 这个参数是个函数，也就是评估函数，把函数当参数
        gotypes.Player.white: AlphaBetaAgent(2, capture_diff),
    }
    while not game.is_over():
        time.sleep(0.3)  # <1> 0.3s休眠

        print(chr(27) + "[2J")  # <2> 每次落子前都清除屏幕
        print_board(game.board)
        start_time = time.time()
        bot_move = bots[game.next_player].select_move(game)
        end_time = time.time()
        print("AI思考时间：" + str(end_time - start_time) + "秒")
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
    print("游戏结束")


if __name__ == '__main__':
    main()