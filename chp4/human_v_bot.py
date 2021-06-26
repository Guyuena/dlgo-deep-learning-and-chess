
# tag::play_against_your_bot[]
from dlgo.agent import navie
# from dlgo import goboard_slow as goboard
from dlgo import goboard as goboard  # 加入哈希的人机对弈


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
            point = point_from_coords(human_move.strip())
            move = goboard.Move.play(point)
        else:
            move = bot.select_move(game)
        print_move(game.next_player, move)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()