from __future__ import print_function
# tag::bot_vs_bot[]
from dlgo.agent.navie import RandomBot
# from dlgo import goboard_slow as goboard
from dlgo import goboard as goboard  # 哈希值加速后的棋局博弈
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
        gotypes.Player.black: RandomBot(),  # 机器人棋手执黑
        gotypes.Player.white: RandomBot(),  # 机器人棋手执白
    }
    while not game.is_over():
        time.sleep(1)  # <1> 1s休眠

        print(chr(27) + "[2J")  # <2> 每次落子前都清除屏幕
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)  # 机器人一人一次使用机器生成棋盘落子坐标
        print_move(game.next_player, bot_move)  # 打印当前棋手和棋手动作
        game = game.apply_move(bot_move)   # 把游戏动作添加到游戏状态中记录
    print("游戏结束")


if __name__ == '__main__':
    main()

