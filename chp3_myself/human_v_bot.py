
# tag::play_against_your_bot[]
from dlgo.agent import navie
from dlgo import goboard_slow as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move, point_from_coords
from six.moves import input


def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    bot = navie.RandomBot()

    while not game.is_over():
        print(chr(27) + "[2J")
        print_board(game.board)
        if game.next_player == gotypes.Player.black:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())  # 将人工输入的落子位置解析为棋盘坐标point
            move = goboard.Move.play(point)   # 调用在goboard_slow.py的class Move（）的落子动作方法进行落子
        else:
            # 机器落子
            move = bot.select_move(game)  # navie.py中的机器落子坐标

        print_move(game.next_player, move) # 打印出落子棋手和执行的动作
        game = game.apply_move(move)  # # 把游戏动作添加到游戏状态中记录


if __name__ == '__main__':
    main()