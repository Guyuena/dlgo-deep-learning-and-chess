from __future__ import print_function
# tag::bot_vs_bot[]
from dlgo.agent.navie import RandomBot
from dlgo import goboard_slow as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move
import time


"""":argument
    机器自对弈脚本

"""

def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    bots = {
        gotypes.Player.black: RandomBot(),
        gotypes.Player.white: RandomBot(),
    }
    while not game.is_over():
        time.sleep(0.3)  # <1> 0.3s休眠

        print(chr(27) + "[2J")  # <2> 每次落子前都清除屏幕
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
    print("游戏结束")


if __name__ == '__main__':
    main()

