import copy
import numpy as np
from dlgo.gotypes import Player
from dlgo.gotypes import Point
from dlgo.scoring import compute_game_result

__all__ = [
    'Board',
    'GameState',
    'Move',
]


class IllegalMoveError(Exception):
    pass


" 动作： 落子、跳过、认输, 对动作编码 "


# 棋手可能做出的三种棋局动作
class Move():
    def __init__(self, point=None, is_pass=False, is_resign=False):
        # 用来让程序测试这个condition，如果condition为false，那么raise一个AssertionError出来
        assert (point is not None) ^ is_pass ^ is_resign
        # 是否轮到我下
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    """ classmethod 修饰符对应的函数不需要实例化，不需要 self 参数，但第一个参数需要是表示自身类的 cls 参数，可以来调用类的属性，类的方法，实例化对象等。"""

    @classmethod
    def play(cls, point):  # 棋盘上落下一颗子
        return Move(point=point)

    # 让对方继续下
    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    # 投子认输
    @classmethod
    def resign(cls):
        return Move(is_resign=True)


"""面代码只是拥有表示下棋时的一下基本概念，并不包含逻辑，接下来我们要编写围棋的规则及逻辑代码"""


# 棋盘的棋链
# Gostring(): 跟踪、维护气数
# 多个棋子连成一片，形成棋链
class GoString():
    def __init__(self, color, stones, liberties):  # 棋链是一系列颜色相同且相连的棋子
        # 颜色、棋子、气  棋链的属性参数
        self.color = color
        self.stones = set(stones)  # """set是一个无序且不重复的元素集合"""
        self.liberties = set(liberties)

    "棋链的操作方法"

    # 减少气数
    def remove_liberty(self, point):
        self.liberties.remove(point)

    # 增加气数
    def add_liberty(self, point):
        self.liberties.add(point)

    # 当落子把两颗棋子连起来时，调用该方法
    def merge_with(self, go_string):  # 返回新的棋链，包含两条棋链的所有棋子
        # 落子之后，两片相邻棋子可能会合成一片
        """
                假设*代表黑棋，o代表白棋，x代表没有落子的棋盘点，当前棋盘如下：
                x  x  x  x  x  x
                x  *  x! *  o  *
                x  x  x  *  o  x
                x  x  *  x  o  x
                x  x  *  o  x  x
                注意看带!的x，如果我们把黑子下在那个地方，那么x!左边的黑棋和新下的黑棋会调用当前函数进行合并，
                同时x!上方的x和下面的x就会成为合并后相邻棋子共同具有的自由点。同时x!原来属于左边黑棋的自由点，
                现在被一个黑棋占据了，所以下面代码要把该点从原来的自由点集合中去掉
        """

        assert go_string.color == self.color  # 棋子颜色是否一致
        combined_stones = self.stones | go_string.stones  # 合并棋链，就是把当前落子棋子与棋链做或运算
        print(type(combined_stones))
        print(combined_stones)
        # 返回合并后的棋链（棋子颜色、棋子数、棋链拥有的自由点数（气数））
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

        # 参考书中图3-1来解释：(self.liberties | go_string.liberties) - combined_stones
        # 试想在第二行两个分离的黑棋中落一个黑棋，那么左边单个黑棋和右边两个黑棋就会连成一片，左边黑棋与落在中间黑棋连接成片时，
        # 它的自由点集合要减去中间落入的黑棋，同理右边两个黑棋的自由点也要减去落在中间黑棋所占据的位置，
        # 这就是为何要执行语句(self.liberties | go_string.liberties) - combined_stones。

    @property  # 创建只读属性，
    def num_liberties(self):  # 获取任意交叉点的气数
        return len(self.liberties)

    def __eq__(self, other):  # 是否相等
        return isinstance(other, GoString) and \
                self.color == other.color and \
                self.stones == other.stones and \
                self.liberties == other.liberties


# 新建棋盘  Board类负责落子和吃子的逻辑

"""
在实现GameState类之前，我们先实现Board类。您的第一个想法可能是创建一个19×19数组，
跟踪棋盘中每个交叉点的状态，这是一个很好的起点。现在，要考虑一个算法去检测什么时候需要从棋盘上拿掉棋子。
回想一下，一块棋子的气是由它的上下左右邻接空点的数量来定义的。如果所有四个相邻的点都被另一种颜色的棋子占据，
棋子就会没气而死掉。对于连接棋子后形成的连接块，这情况就比较复杂了。例如，下了黑棋后，你必须检查所有相邻的白棋，
看看黑色吃掉任何棋子，如果吃掉的话，你就必须要拿掉这个棋子。具体来说，你必须要检查以下几点：
1--你要去看邻接棋子是否还有留下的气
2--你要去检查任何一个邻接棋子的邻接棋子还有留下的气
3--再去检测邻接棋子的邻接棋子的邻接棋子等等


"""


class Board():
    def __init__(self, num_rows, num_cols):  # 初始化空网格
        # 一个棋盘用特定大小的行和列以及一个空的棋子串集合来初始化
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}  # 存储所有棋盘上的棋子串

    # 落子方法
    def place_stone(self, player, point):
        # 用来让程序测试这个condition，如果condition为false，那么raise一个AssertionError出来

        assert self.is_on_grid(point)  # 确保位置在棋盘内
        assert self._grid.get(point) is None  # 确保给定位置没有被占据
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []

        for neighbor in point.neighbors():  # 判断落子点上下左右临界点的情况
            if not self.is_on_grid(neighbor):  # 判断是否为None的情况：
                continue
            neighbor_string = self._grid.get(neighbor)  #
            if neighbor_string is None:
                # 如果邻接点没有被占据，那么就是当前落子点的自由点
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    # 记录与棋子同色的连接棋子
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    # 记录落点与邻接点棋子不同色的棋子
                    adjacent_opposite_color.append(neighbor_string)
        # 将当前落子与棋盘上相邻的棋子合并成一片
        new_string = GoString(player, [point], liberties)
        # 合并任何同色相邻的棋链
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)

        for new_string_point in new_string.stones:
            # 访问棋盘某个点时返回与该棋子相邻的所以棋子集合
            self._grid[new_string_point] = new_string

        for other_color_string in adjacent_opposite_color:
            # 当该点被占据前，它属于反色棋子的自由点，占据后就不再属于反色棋子自由点
            other_color_string.remove_liberty(point)

        for other_color_string in adjacent_opposite_color:
            # 如果落子后，相邻反色棋子的所有自由点都被堵住，对方棋子被吃掉
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)
    # 判断交叉点是否在棋盘内
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and 1 <= point.col <= self.num_cols

    # 返回交叉点上的内容：如果该交叉点已经落子，返回对应的player对象，否则返回none
    def get(self, point):
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    # 返回交叉点的棋链
    def get_go_string(self, point):  # 返回一个交叉点上的整条棋链；如果棋链中的一颗棋子落在这个交叉点上，则返回他的Gostring对象，否则返回None
        string = self._grid.get(point)
        if string is None:
            return None
        return string



    def _remove_string(self, string):
        # 从棋盘上删除一整片连接棋子
        for point in string.stones:
            for neighbor in point.neighbors():  # 提走一条棋链可以为其他棋链增加气数
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None


# 落子和棋盘都完成了，由于每次落子到棋盘上后，棋局的状态会发生变化，接下来我们完成棋盘状态的检测和落子法性检测，
# 状态检测会让程序得知以下信息：各个棋子的摆放位置；轮到谁落子；落子前的棋盘状态，以及最后一次落子信息，以及落子后棋盘的状态变化：

# 棋盘状态的检测和落子检测  GameState类包括棋盘上的所有棋子，以及跟踪轮到谁下以及先前的游戏状态
class GameState():
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        self.last_move = move

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board

        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)

        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):  # 决定围棋比赛结束的时机
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True

        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False

        # 如果两个棋手同时放弃落子，棋局结束
        return self.last_move.is_pass and second_last_move.is_pass

    """
        接下来我们需要确定，落子时是否合法。
        因此我们需要确定三个条件，落子的位置没有被占据；落子时不构成自己吃自己；落子不违反ko原则。
        第一个原则检测很简单，我们看看第二原则：
    """

    # 自吃
    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False

        next_board = copy.deepcopy(self.board)
        # 先落子，完成吃子后再判断是否是自己吃自己
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    # 判断当前游戏状态是否违反了劫争规则
    @property
    def situation(self):
        return (self.next_player, self.board)

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False

        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board)
        past_state = self.previous_state
        # 判断ko不仅仅看是否返回上一步的棋盘而是检测能否返回以前有过的棋盘状态
        while past_state is not None:
            if past_state.situation == next_situation:
                return True
        return False

    # 在给定游戏状态下，判断这个动作是否合法
    def is_valid_move(self, move):
        if self.is_over():
            return False

        if move.is_pass or move.is_resign:
            return True

        return (self.board.get(move.point) is None and
                not self.is_move_self_capture(self.next_player, move) and
                not self.does_move_violate_ko(self.next_player, move))
