
from __future__ import print_function
# from dlgo import goboard_slow as goboard

# tag::bot_vs_bot[]
from dlgo import goboard as goboard
from dlgo.mcts import mcts_navie

from dlgo import gotypes
from dlgo.utils import print_board, print_move, point_from_coords
from six.moves import input
from  dlgo.mcts.mcts import MCTSAgent  # 导入蒙特卡洛树代理
"测试加入 蒙特卡洛树，测试成功"

def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    # bot = navie.RandomBot()
    # bot = mcts_navie.FastRandomBot()
    bot = MCTSAgent(10, 2)  # 使用 蒙特卡洛搜索代理棋手

    while not game.is_over():
        print(chr(27) + "[2J")
        print_board(game.board)
        if game.next_player == gotypes.Player.black:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())
            move = goboard.Move.play(point)
        else:
            move = bot.select_move(game)

        print_move(game.next_player, move)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()