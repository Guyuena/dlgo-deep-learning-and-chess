# tag::generate_mcts_imports[]
import argparse
import numpy as np

from dlgo.encoders import get_encoder_by_name
from dlgo import goboard_fast as goboard
from dlgo import mcts
from dlgo.utils import print_board, print_move

"使用MCTS蒙特卡洛算法来生成棋局"


# tag::generate_mcts[]
def generate_game(board_size, rounds, max_moves, temperature): # 棋盘大小  ， 推演轮数、最大落子次数、蒙特卡洛搜索活跃度
    boards, moves = [], []  # <1> boards   保存编码后的棋局状态，moves保存编码后的落子动作

    encoder = get_encoder_by_name('oneplane', board_size)  # <2>  按名字来例化一个编码器

    game = goboard.GameState.new_game(board_size)  # <3> 新开一局游戏

    "棋手使用蒙特卡洛树搜索的方法"
    bot = mcts.MCTSAgent(rounds, temperature)  # <4>  例化蒙特卡洛棋手机器人

    num_moves = 0
    while not game.is_over():
        print_board(game.board)
        move = bot.select_move(game)  # <5> 机器人的选择下一步动作
        if move.is_play:
            boards.append(encoder.encode(game))  # <6> 保存编码状态

            move_one_hot = np.zeros(encoder.num_points())
            move_one_hot[encoder.encode_point(move.point)] = 1
            moves.append(move_one_hot)  # <7>

        print_move(game.next_player, move)
        game = game.apply_move(move)  # <8>
        num_moves += 1
        if num_moves > max_moves:  # <9>
            break

    return np.array(boards), np.array(moves)  # <10>  棋盘数组  、 执行动作


# <1> In `boards` we store encoded board state, `moves` is for encoded moves.
# <2> We initialize a OnePlaneEncoder by name with given board size.
# <3> An new game of size `board_size` is instantiated.
# <4> A Monte Carlo tree search agent with specified number of rounds and temperature will serve as our bot.
# <5> The next move is selected by the bot.
# <6> The encoded board situation is appended to `boards`.
# <7> The one-hot-encoded next move is appended to `moves`.
# <8> Afterwards the bot move is applied to the board.
# <9> We continue with the next move, unless the maximum number of moves has been reached.
# end::generate_mcts[]


# tag::generate_mcts_main[]
def main():
    # python 中断指令参数列表
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', '-b', type=int, default=9)  # 棋盘大小
    parser.add_argument('--rounds', '-r', type=int, default=1000)   # 蒙特卡洛搜索轮数
    parser.add_argument('--temperature', '-t', type=float, default=0.8)  # 蒙特卡洛搜索活跃度
    parser.add_argument('--max-moves', '-m', type=int, default=60,
                        help='Max moves per game.')  # 最大落子动作次数
    parser.add_argument('--num-games', '-n', type=int, default=10)  # 多少局游戏测试
    parser.add_argument('--board-out')  # 特征输出配置文件名
    parser.add_argument('--move-out')   # 标签文件名

    args = parser.parse_args()  # <1>  # 此应用程序允许通过命令行参数自定义
    xs = []
    ys = []

    for i in range(args.num_games):
        print('Generating game %d/%d...' % (i + 1, args.num_games))
        # 如执行指令：  python generate_mcts_games.py -n 20 --board-out features.npy  --move-out labels.npy
        # 生成游戏
        x, y = generate_game(args.board_size,
                             args.rounds,
                             args.max_moves,
                             args.temperature)  # <2>根据给定的棋局数量来生成相应的棋局数据
        xs.append(x)
        ys.append(y)
    # np.concatenate() 能够一次完成多个数组的拼接。
    x = np.concatenate(xs)  # <3> 当所有棋局都生成后，为棋局添加相应的特征与标签
    y = np.concatenate(ys)

    np.save(args.board_out, x)  # <4> 保存特征与标签文件
    np.save(args.move_out, y)


if __name__ == '__main__':
    main()

# <1> This application allows some customization via command line arguments.
# <2> For the specified number of games we generate game data.
# <3> After all games have been generated, we concatenate features and labels, respectively.
# <4> We store feature and label data to separate files, as specified by the command line options.
# end::generate_mcts_main[]层 pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ tensorflow-gpu==1.8.0
