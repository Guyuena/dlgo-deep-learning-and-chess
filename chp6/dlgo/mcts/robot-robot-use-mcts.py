from __future__ import print_function
# tag::bot_vs_bot[]
from dlgo.agent.navie import RandomBot
from dlgo import goboard as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move
import time
from  dlgo.mcts.mcts import MCTSAgent  # 导入蒙特卡洛树代理


"""":argument
    机器自对弈脚本   加入了蒙特卡洛树搜索的游戏测试

"""

def main():
    board_size = 19
    game = goboard.GameState.new_game(board_size)
    bots = {
        # gotypes.Player.black: RandomBot(),
        # gotypes.Player.white: RandomBot(),
        gotypes.Player.black: MCTSAgent(10,2),  # 使用 蒙特卡洛搜索
        gotypes.Player.white: MCTSAgent(10,2),  # 使用 蒙特卡洛搜索
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

