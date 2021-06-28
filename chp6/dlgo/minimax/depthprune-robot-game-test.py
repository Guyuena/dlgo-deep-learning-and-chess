'''
   人与使用深度剪枝的极小极大AI对弈,默认人拿黑棋
   考虑到变化还是太多，所以棋盘设为5*5
'''

from dlgo.gotypes import Player, Point
from dlgo.utils import print_move, print_board, point_from_coords
from dlgo.minimax.depthprune import DepthPrunedAgent
from dlgo import goboard
# from dlgo import goboard_slow as goboard
from six.moves import input
import time


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


def main():
    # 建一个5*5的棋盘
    game = goboard.GameState.new_game(5)
    bot = DepthPrunedAgent(2, capture_diff)  # 注意例化时的参数类型

    while not game.is_over():
        print_board(game.board)
        if game.next_player == Player.black:
            human_input = input('-- ')
            point = point_from_coords(human_input)
            move = goboard.Move.play(point)
        else:
            # 计算一下AI的思考时间
            start_time = time.time()
            move = bot.select_move(game)
            end_time = time.time()
            print("AI思考时间：" + str(end_time - start_time) + "秒")
        print_move(game.next_player, move)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()
