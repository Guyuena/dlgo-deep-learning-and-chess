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


# 棋盘的棋链
# Gostring(): 跟踪、维护气数
# 多个棋子连成一片，形成棋链
class GoString():
    def __init__(self, color, stones, liberties):  # 棋链是一系列颜色相同且相连的棋子
        # 颜色、棋子、气  棋链的属性参数
        self.color = color
        self.stones = set(stones)  # 棋子集合        set是一个无序且不重复的元素集合
        self.liberties = set(liberties)  # 空点(气数)集合

    # 减少气数
    def remove_liberty(self, point):
        self.liberties.remove(point)

    # 增加气数
    # 增加一口气，实际上就是增加空点集合中的一个空点
    def add_liberty(self, point):
        self.liberties.add(point)

    # 当落子把两颗棋子连起来时，调用该方法
    # 连接棋子串(要求棋子串颜色要相同）
    # 合并后的气应该是两个棋子串合并前的气之和减去两个棋子串的棋子个数之和
    def merged_with(self, go_string):  # 返回新的棋链，包含两条棋链的所有棋子
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

        assert go_string.color == self.color  # 判断颜色是否一致
        combined_stones = self.stones | go_string.stones  # 颜色一致，相连成棋链
        # 返回棋链
        return GoString(
            self.color,  # 该棋链的棋子颜色
            combined_stones,  # 该棋链的棋子集合set
            (self.liberties | go_string.liberties) - combined_stones)# 该棋链的气数

    # 参考书中图3-1来解释：(self.liberties | go_string.liberties) - combined_stones
    # 试想在第二行两个分离的黑棋中落一个黑棋，那么左边单个黑棋和右边两个黑棋就会连成一片，左边黑棋与落在中间黑棋连接成片时，
    # 它的自由点集合要减去中间落入的黑棋，同理右边两个黑棋的自由点也要减去落在中间黑棋所占据的位置，
    # 这就是为何要执行语句(self.liberties | go_string.liberties) - combined_stones。
    @property  # 创建只读属性，
    def num_liberties(self):  # 调用num_liberties来得到任意时刻的棋子串的气
        return len(self.liberties)  # 返回任一棋链所拥有的气数

    def __eq__(self, other):  # 判断两个棋子串是否相等
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

@----在围棋棋盘上落子和吃子
在讨论了棋子和棋子串之后，下一步自然就是讨论如何在棋盘上放置棋子。使用GoString类，放置棋子的算法看起来像这样：
    1.合并同一颜色的任意相邻棋子串
    2.减少任何颜色相反的相邻棋子串的气。
    3.如果任何相反的颜色棋子串没气了，请把它从棋盘上拿掉。
    此外，如果新形成的棋子串没有气，则不能下进去
"""


# 棋盘
# Board Start
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
        adjacent_same_color = []  # 相同颜色棋盘块集合
        adjacent_opposite_color = []  # 不同颜色棋盘块集合
        liberties = []  # 该点邻接空点集合
        for neighbor in point.neighbors():  # 判断落子点上下左右临界点的情况
            if not self.is_on_grid(neighbor):  # # 该点邻接的这个点不在棋盘上不用管
                continue
            neighbor_string = self._grid.get(neighbor)  # 获取这个落子点的邻接点所在的棋盘块
            if neighbor_string is None:  # 如果为空，就加入集合
                # 如果邻接点没有被占据，那么就是当前落子点的自由点
                liberties.append(neighbor)  # 落子点的气数增加
            elif neighbor_string.color == player:  # 邻点棋链的棋子颜色和当前棋手的棋子颜色一致
                if neighbor_string not in adjacent_same_color:  # 相同颜色棋子的集合里面还没保存有该棋链，则存入该棋链
                    adjacent_same_color.append(neighbor_string)  # 记录与棋子同色的连接棋子
            else:
                if neighbor_string not in adjacent_opposite_color:
                    # 记录落点与邻接点棋子不同色的棋子
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)  # 将当前落子与棋盘上相邻的棋子合并成一片
        for same_color_string in adjacent_same_color:  # <1>
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        for other_color_string in adjacent_opposite_color:  # <2>
            other_color_string.remove_liberty(point)
        for other_color_string in adjacent_opposite_color:  # <3>
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)

    # 删除棋子串
    # 删除棋子串，并将该棋子串上每个点相邻的棋子串的气增加
    def _remove_string(self, string):
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None  # 将该点映射的棋子串置为空

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

    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.num_rows == other.num_rows and \
            self.num_cols == other.num_cols and \
            self._grid == other._grid



# Board end

class Move():  # 动作： 落子、跳过、认输,对动作编码
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



# 落子和棋盘都完成了，由于每次落子到棋盘上后，棋局的状态会发生变化，接下来我们完成棋盘状态的检测和落子法性检测，
# 状态检测会让程序得知以下信息：各个棋子的摆放位置；轮到谁落子；落子前的棋盘状态，以及最后一次落子信息，以及落子后棋盘的状态变化：

# 棋盘状态的检测和落子检测  GameState类包括棋盘上的所有棋子，以及跟踪轮到谁下以及先前的游戏状态
# GameState  start
class GameState():
    def __init__(self, board, next_player, previous, move):
        self.board = board  # 当前棋盘棋局棋子布局
        self.next_player = next_player  # 下一回合执棋方
        self.previous_state = previous  # 上一回合状态状态
        self.last_move = move  # 上一步动作

    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)  # 将落子前的盘面进行深度拷贝
            next_board.place_stone(self.next_player, move.point)  # 外部调用apply_move(move)就会完成落子动作
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)
        # 在完成新的落子后，给外部调用apply_move()返回一个GameState，
        # GameState(next_board, self.next_player.other, self, move) 就是例化一个GameState对象，
        # 例化就会把next_board、next_player.other、selfmove这四个参数传入到GameState的init中完成对象参数值得配置


    # 新开一局游戏
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)  # 新开一局游戏，返回游戏状态，因为新开局，所以有两个参数为空，且这个设置为 黑子为先手

    """
    三个规则：
        你想落的交叉点必须是空的
        落下这个子后不会造成自吃
        打劫时未找劫财不可直接提回
    """

    # # 判别有无自吃
    # def is_move_self_capture(self, player, move):
    #     if not move.is_play:
    #         return False
    #     next_board = copy.deepcopy(self.board)  # 深度拷贝为了思考过程不会影响原有棋局
    #     # 先落子，完成吃子后再判断是否是自己吃自己
    #     next_board.place_stone(player, move.point)
    #     new_string = next_board.get_go_string(move.point)
    #     return new_string.num_liberties == 0
    "self-capture:自吃"
    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
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
            past_state = past_state.previous_state  # 这句漏了
        return False

    # 在给定游戏状态下，判断这个动作是否合法
    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move))

    # 判断棋局有无结束  决定游戏结束的时机
    def is_over(self):  # 决定围棋比赛结束的时机
        if self.last_move is None:
            return False
        if self.last_move.is_resign:  # 认输
            return True  # 游戏结束
        second_last_move = self.previous_state.last_move
        if second_last_move is None:  # 前两步落子动作
            return False
        # 如果两个棋手同时放弃落子，棋局结束
        return self.last_move.is_pass and second_last_move.is_pass
# GameState  send

#
# import numpy as np
# # tag::imports[]
# import copy
# from dlgo.gotypes import Player
# # end::imports[]
# from dlgo.gotypes import Point
# from dlgo.scoring import compute_game_result
#
# __all__ = [
#     'Board',
#     'GameState',
#     'Move',
# ]
#
#
# class IllegalMoveError(Exception):
#     pass
#
#
# # tag::strings[]
# class GoString():  # <1>
#     def __init__(self, color, stones, liberties):
#         self.color = color
#         self.stones = set(stones)
#         self.liberties = set(liberties)
#
#     def remove_liberty(self, point):
#         self.liberties.remove(point)
#
#     def add_liberty(self, point):
#         self.liberties.add(point)
#
#     def merged_with(self, go_string):  # <2>
#         assert go_string.color == self.color
#         combined_stones = self.stones | go_string.stones
#         return GoString(
#             self.color,
#             combined_stones,
#             (self.liberties | go_string.liberties) - combined_stones)
#
#     @property
#     def num_liberties(self):
#         return len(self.liberties)
#
#     def __eq__(self, other):
#         return isinstance(other, GoString) and \
#             self.color == other.color and \
#             self.stones == other.stones and \
#             self.liberties == other.liberties
# # <1> Go strings are stones that are linked by a chain of connected stones of the same color.
# # <2> Return a new Go string containing all stones in both strings.
# # end::strings[]
#
#
# # tag::board_init[]
# class Board():  # <1>
#     def __init__(self, num_rows, num_cols):
#         self.num_rows = num_rows
#         self.num_cols = num_cols
#         self._grid = {}
#
# # <1> A board is initialized as empty grid with the specified number of rows and columns.
# # end::board_init[]
#
# # tag::board_place_0[]
#     def place_stone(self, player, point):
#         assert self.is_on_grid(point)
#         assert self._grid.get(point) is None
#         adjacent_same_color = []
#         adjacent_opposite_color = []
#         liberties = []
#         for neighbor in point.neighbors():  # <1>
#             if not self.is_on_grid(neighbor):
#                 continue
#             neighbor_string = self._grid.get(neighbor)
#             if neighbor_string is None:
#                 liberties.append(neighbor)
#             elif neighbor_string.color == player:
#                 if neighbor_string not in adjacent_same_color:
#                     adjacent_same_color.append(neighbor_string)
#             else:
#                 if neighbor_string not in adjacent_opposite_color:
#                     adjacent_opposite_color.append(neighbor_string)
#         new_string = GoString(player, [point], liberties)
# # <1> First, we examine direct neighbors of this point.
# # end::board_place_0[]
# # tag::board_place_1[]
#         for same_color_string in adjacent_same_color:  # <1>
#             new_string = new_string.merged_with(same_color_string)
#         for new_string_point in new_string.stones:
#             self._grid[new_string_point] = new_string
#         for other_color_string in adjacent_opposite_color:  # <2>
#             other_color_string.remove_liberty(point)
#         for other_color_string in adjacent_opposite_color:  # <3>
#             if other_color_string.num_liberties == 0:
#                 self._remove_string(other_color_string)
# # <1> Merge any adjacent strings of the same color.
# # <2> Reduce liberties of any adjacent strings of the opposite color.
# # <3> If any opposite color strings now have zero liberties, remove them.
# # end::board_place_1[]
#
# # tag::board_remove[]
#     def _remove_string(self, string):
#         for point in string.stones:
#             for neighbor in point.neighbors():  # <1>
#                 neighbor_string = self._grid.get(neighbor)
#                 if neighbor_string is None:
#                     continue
#                 if neighbor_string is not string:
#                     neighbor_string.add_liberty(point)
#             self._grid[point] = None
# # <1> Removing a string can create liberties for other strings.
# # end::board_remove[]
#
# # tag::board_utils[]
#     def is_on_grid(self, point):
#         return 1 <= point.row <= self.num_rows and \
#             1 <= point.col <= self.num_cols
#
#     def get(self, point):  # <1>
#         string = self._grid.get(point)
#         if string is None:
#             return None
#         return string.color
#
#     def get_go_string(self, point):  # <2>
#         string = self._grid.get(point)
#         if string is None:
#             return None
#         return string
# # <1> Returns the content of a point on the board:  a Player if there is a stone on that point or else None.
# # <2> Returns the entire string of stones at a point: a GoString if there is a stone on that point or else None.
# # end::board_utils[]
#
#     def __eq__(self, other):
#         return isinstance(other, Board) and \
#             self.num_rows == other.num_rows and \
#             self.num_cols == other.num_cols and \
#             self._grid == other._grid
#
#
# # tag::moves[]
# class Move():  # <1>
#     def __init__(self, point=None, is_pass=False, is_resign=False):
#         assert (point is not None) ^ is_pass ^ is_resign
#         self.point = point
#         self.is_play = (self.point is not None)
#         self.is_pass = is_pass
#         self.is_resign = is_resign
#
#     @classmethod
#     def play(cls, point):  # <2>
#         return Move(point=point)
#
#     @classmethod
#     def pass_turn(cls):  # <3>
#         return Move(is_pass=True)
#
#     @classmethod
#     def resign(cls):  # <4>
#         return Move(is_resign=True)
# # <1> Any action a player can play on a turn, either is_play, is_pass or is_resign will be set.
# # <2> This move places a stone on the board.
# # <3> This move passes.
# # <4> This move resigns the current game
# # end::moves[]
#
#
# # tag::game_state[]
# class GameState():
#     def __init__(self, board, next_player, previous, move):
#         self.board = board
#         self.next_player = next_player
#         self.previous_state = previous
#         self.last_move = move
#
#     def apply_move(self, move):  # <1>
#         if move.is_play:
#             next_board = copy.deepcopy(self.board)
#             next_board.place_stone(self.next_player, move.point)
#         else:
#             next_board = self.board
#         return GameState(next_board, self.next_player.other, self, move)
#
#     @classmethod
#     def new_game(cls, board_size):
#         if isinstance(board_size, int):
#             board_size = (board_size, board_size)
#         board = Board(*board_size)
#         return GameState(board, Player.black, None, None)
# # <1> Return the new GameState after applying the move.
# # end::game_state[]
#
# # tag::self_capture[]
#     def is_move_self_capture(self, player, move):
#         if not move.is_play:
#             return False
#         next_board = copy.deepcopy(self.board)
#         next_board.place_stone(player, move.point)
#         new_string = next_board.get_go_string(move.point)
#         return new_string.num_liberties == 0
# # end::self_capture[]
#
# # tag::is_ko[]
#     @property
#     def situation(self):
#         return (self.next_player, self.board)
#
#     def does_move_violate_ko(self, player, move):
#         if not move.is_play:
#             return False
#         next_board = copy.deepcopy(self.board)
#         next_board.place_stone(player, move.point)
#         next_situation = (player.other, next_board)
#         past_state = self.previous_state
#         while past_state is not None:
#             if past_state.situation == next_situation:
#                 return True
#             past_state = past_state.previous_state
#         return False
# # end::is_ko[]
#
# # tag::is_valid_move[]
#     def is_valid_move(self, move):
#         if self.is_over():
#             return False
#         if move.is_pass or move.is_resign:
#             return True
#         return (
#             self.board.get(move.point) is None and
#             not self.is_move_self_capture(self.next_player, move) and
#             not self.does_move_violate_ko(self.next_player, move))
# # end::is_valid_move[]
#
# # tag::is_over[]
#     def is_over(self):
#         if self.last_move is None:
#             return False
#         if self.last_move.is_resign:
#             return True
#         second_last_move = self.previous_state.last_move
#         if second_last_move is None:
#             return False
#         return self.last_move.is_pass and second_last_move.is_pass
# # end::is_over[]