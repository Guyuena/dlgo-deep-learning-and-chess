import copy

from dlgo.goboard_slow import GameState
from dlgo.gotypes import Player
from dlgo.gotypes import Point
from dlgo.scoring import compute_game_result
from dlgo import zobrist  # 导入哈希值

__all__ = [
    'Board',
    'GameState',
    'Move',
]


class IllegalMoveError(Exception):
    pass


# 棋盘走棋逻辑设计
"加入哈希值来加速棋盘"

#  棋链  start
# 棋链用来检查一组相同颜色的相连棋子和它们的气
class GoString():
    def __init__(self, color, stones, liberties):  # 棋链是一系列颜色相同且相连的棋子
        """颜色、棋子、气  棋链的属性参数"""
        self.color = color
        # 修改为不可变实例
        self.stones = frozenset(stones)  # 棋子集合        set是一个无序且不重复的元素集合  比如一堆无序且带有重复的数据集合，经set处理后只剩下不重复的数据
        self.liberties = frozenset(liberties)  # 空点(气数)集合

    # 减少气数
    # 修改
    """棋链所具备的方法"""
    # 减少气数
    # 修该版
    def without_liberty(self, point):
        new_liberties = self.liberties - set([point])
        return GoString(self.color, self.stones, new_liberties)

    # 增加气数
    # 增加一口气，实际上就是增加空点集合中的一个空点
    def with_liberty(self, point):
        new_liberties = self.liberties | set([point])
        return GoString(self.color, self.stones, new_liberties)

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
            (self.liberties | go_string.liberties) - combined_stones)  # 该棋链的气数

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

    # 添加
    def __deepcopy__(self, memodict={}):
        return GoString(self.color, self.stones, copy.deepcopy(self.liberties))


# 棋盘的棋链
# Gostring(): 跟踪、维护气数
# 多个棋子连成一片，形成棋链

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
"包含哈希值的围棋棋盘"
class Board():
    def __init__(self, num_rows, num_cols):  # 初始化空网格
        # 一个棋盘用特定大小的行和列以及一个空的棋子串集合来初始化
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}  # 存储所有棋盘上的棋子串
        # 哈希值  加速棋盘
        self._hash = zobrist.EMPTY_BOARD

    # 落子方法
    # 加入哈希值
    """
    落子需要的策略算法：place_stone()：
        1、合并任何同色且相邻的棋链
        2、减少对方的所有相邻棋链的气
        3、如果对方的某条棋链气数为零，则需要提走他们
    """
    # place_stone  开始
    def place_stone(self, player, point):
        # 用来让程序测试这个condition，如果condition为false，那么raise一个AssertionError出来
        assert self.is_on_grid(point)  # 确保位置在棋盘内
        if self._grid.get(point) is None:  # 确保给定位置没有被占据
            # print('Illegal play on %s' % str(point))
            i = 0
        assert self._grid.get(point) is None
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

        # 将当前落子与棋盘上相邻的棋子合并成一片
        # 此处加入哈希
        """落子的策略"""
        new_string = GoString(player, [point], liberties)  # <1> 落子没变
        for same_color_string in adjacent_same_color:  # <2>合并任何相邻的相同颜色的棋链。
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        self._hash ^= zobrist.HASH_CODE[point, player]  # <3> 应用此落子点对应的玩家的哈希码
        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.without_liberty(point)  # <4> 减少对手棋子的气
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                self._remove_string(other_color_string)  # <5>  对手棋子气数为0，

    # <1> Until this line `place_stone` remains the same.
    # <2> You merge any adjacent strings of the same color. 合并任何相邻的相同颜色的棋链。
    # <3> Next, you apply the hash code for this point and player
    # <4> Then you reduce liberties of any adjacent strings of the opposite color.
    # <5> If any opposite color strings now have zero liberties, remove them.
    # end::apply_zobrist[]
    # 需提走一颗棋，需要再次应用它的哈希值

    # place_stone()  结束


    def _replace_string(self, new_string):  # <1>  辅助更新棋盘网络
        for point in new_string.stones:
            self._grid[point] = new_string

        # 删除棋子串
        # 删除棋子串，并将该棋子串上每个点相邻的棋子串的气增加

    def _remove_string(self, string):
        for point in string.stones:

            for neighbor in point.neighbors():  # <2>  提走一条棋链，为其他链释放新的气
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None  # 将该点映射的棋子串置为空

            self._hash ^= zobrist.HASH_CODE[point, string.color]  # <3> 逆用哈希值来实现提子

    # 判断交叉点是否在棋盘内
    def is_on_grid(self, point):
        # 返回ture or false
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

        # 遍历相同颜色邻接棋盘块集合，执行合并操作
        # for same_color_string in adjecent_same_color:
        #     new_string = new_string.merged_with(same_color_string)
        #
        # # 对新形成的棋子串将每个棋子都实现棋子与该串的映射，即字典
        # for new_string_point in new_string.stones:  # 访问棋盘某个点时返回与该棋子相邻的所以棋子集合
        #     self._grid[new_string_point] = new_string
        #
        # # 当该点被占据前，它属于反色棋子的自由点，占据后就不再属于反色棋子自由点
        # for other_color_string in adhecent_opposite_color:
        #     other_color_string.remove_liberty(point)
        #
        # # 对于不同颜色的邻接棋盘块集合，由于该点被占据而气变少了，因此需要减掉,如果气变0了就要从棋盘上拿掉
        # for other_color_string in adhecent_opposite_color:
        #     # 如果落子后，相邻反色棋子的所有自由点都被堵住，对方棋子被吃掉
        #     if other_color_string.num_liberties == 0:
        #         self._remove_string(other_color_string)
        # 添加

    def __deepcopy__(self, memodict={}):
        copied = Board(self.num_rows, self.num_cols)
        # Can do a shallow copy b/c the dictionary maps tuples
        # (immutable) to GoStrings (also immutable)
        copied._grid = copy.copy(self._grid)
        copied._hash = self._hash
        return copied

    """返回当前棋盘的哈希值"""
    # tag::return_zobrist[]
    def zobrist_hash(self):
        return self._hash


# end::return_zobrist[]
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

    # 书上没有，参考源码后添加
    def __str__(self):
        if self.is_pass:
            return 'pass'
        if self.is_resign:
            return 'resign'
        return '(r %d, c %d)' % (self.point.row, self.point.col)


"""面代码只是拥有表示下棋时的一下基本概念，并不包含逻辑，接下来我们要编写围棋的规则及逻辑代码"""

# 落子和棋盘都完成了，由于每次落子到棋盘上后，棋局的状态会发生变化，接下来我们完成棋盘状态的检测和落子法性检测，
# 状态检测会让程序得知以下信息：各个棋子的摆放位置；轮到谁落子；落子前的棋盘状态，以及最后一次落子信息，以及落子后棋盘的状态变化：

# 棋盘状态的检测和落子检测  GameState类包括棋盘上的所有棋子，以及跟踪轮到谁下以及先前的游戏状态

"""    GameState类中来捕获游戏的当前状态。粗略地说，GameState类应该能够获取棋盘盘面，知晓落子方，获悉上一个游戏状态，以及知道上一个操作   """

# GameState  start
class GameState():
    # 用哈希值初始化游戏状态
    def __init__(self, board, next_player, previous, move):
        self.board = board  # 棋盘
        self.next_player = next_player  # 下一手
        self.previous_state = previous  # 前一游戏状态
        # 使用 previous_state来存储哈希值
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())})
        self.last_move = move  # 最新动作

    def apply_move(self, move): # 执行落子后，返回新的GameState对象
        if move.is_play:
            next_board = copy.deepcopy(self.board)  # 将落子前的盘面进行深度拷贝
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board

        return GameState(next_board, self.next_player.other, self, move)

    # 新开一局游戏
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    """
    三个规则：
        你想落的交叉点必须是空的
        落下这个子后不会造成自吃
        打劫时未找劫财不可直接提回
    """

    # # 判别有无自吃
    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)  # 深度拷贝为了思考过程不会影响原有棋局
        # 先落子，完成吃子后再判断是否是自己吃自己
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    # 判断当前游戏状态是否违反了劫争规则
    """  劫争  """
    @property  # python用来修饰方法的。 作用: 我们可以使用@property装饰器来创建只读属性,@property装饰器会将方法转换为相同名称的只读属性
    def situation(self):
        return (self.next_player, self.board)

    # 加入棋子哈希值
    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states # 遍历，检查历史棋局状态

    # 在给定游戏状态下，判断这个动作是否合法
    def is_valid_move(self, move):
        if self.is_over():
            return False

        if move.is_pass or move.is_resign:
            return True

        return (self.board.get(move.point) is None and
                not self.is_move_self_capture(self.next_player, move) and
                not self.does_move_violate_ko(self.next_player, move))
    # 判断棋局有无结束
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


    # 书上没有的，根据源码添加 start
    def legal_moves(self):
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # These two moves are always legal.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    def winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner

    # 书上没有的，根据源码添加 end
# GameState  send








# import copy
# from dlgo.gotypes import Player, Point
# from dlgo.scoring import compute_game_result
# # tag::import_zobrist[]
# from dlgo import zobrist
#
# # end::import_zobrist[]
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
# # tag::fast_go_strings[]
# class GoString:
#     def __init__(self, color, stones, liberties):
#         self.color = color
#         self.stones = frozenset(stones)
#         self.liberties = frozenset(liberties)  # <1>
#
#     def without_liberty(self, point):  # <2>
#         new_liberties = self.liberties - set([point])
#         return GoString(self.color, self.stones, new_liberties)
#
#     def with_liberty(self, point):
#         new_liberties = self.liberties | set([point])
#         return GoString(self.color, self.stones, new_liberties)
# # <1> `stones` and `liberties` are now immutable `frozenset` instances
# # <2> The `without_liberty` methods replaces the previous `remove_liberty` method...
# # <3> ... and `with_liberty` replaces `add_liberty`.
# # end::fast_go_strings[]
#
#     def merged_with(self, string):
#         """Return a new string containing all stones in both strings."""
#         assert string.color == self.color
#         combined_stones = self.stones | string.stones
#         return GoString(
#             self.color,
#             combined_stones,
#             (self.liberties | string.liberties) - combined_stones)
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
#
#     def __deepcopy__(self, memodict={}):
#         return GoString(self.color, self.stones, copy.deepcopy(self.liberties))
#
#
# # tag::init_zobrist[]
# class Board:
#     def __init__(self, num_rows, num_cols):
#         self.num_rows = num_rows
#         self.num_cols = num_cols
#         self._grid = {}
#         self._hash = zobrist.EMPTY_BOARD
# # end::init_zobrist[]
#
#     def place_stone(self, player, point):
#         assert self.is_on_grid(point)
#         if self._grid.get(point) is not None:
#             print('Illegal play on %s' % str(point))
#         assert self._grid.get(point) is None
#         # 0. Examine the adjacent points.
#         adjacent_same_color = []
#         adjacent_opposite_color = []
#         liberties = []
#         for neighbor in point.neighbors():
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
# # tag::apply_zobrist[]
#         new_string = GoString(player, [point], liberties)  # <1>
#
#         for same_color_string in adjacent_same_color:  # <2>
#             new_string = new_string.merged_with(same_color_string)
#         for new_string_point in new_string.stones:
#             self._grid[new_string_point] = new_string
#
#         self._hash ^= zobrist.HASH_CODE[point, player]  # <3>
#
#         for other_color_string in adjacent_opposite_color:
#             replacement = other_color_string.without_liberty(point)  # <4>
#             if replacement.num_liberties:
#                 self._replace_string(other_color_string.without_liberty(point))
#             else:
#                 self._remove_string(other_color_string)  # <5>
# # <1> Until this line `place_stone` remains the same.
# # <2> You merge any adjacent strings of the same color.
# # <3> Next, you apply the hash code for this point and player
# # <4> Then you reduce liberties of any adjacent strings of the opposite color.
# # <5> If any opposite color strings now have zero liberties, remove them.
# # end::apply_zobrist[]
#
#
# # tag::unapply_zobrist[]
#     def _replace_string(self, new_string):  # <1>
#         for point in new_string.stones:
#             self._grid[point] = new_string
#
#     def _remove_string(self, string):
#         for point in string.stones:
#             for neighbor in point.neighbors():  # <2>
#                 neighbor_string = self._grid.get(neighbor)
#                 if neighbor_string is None:
#                     continue
#                 if neighbor_string is not string:
#                     self._replace_string(neighbor_string.with_liberty(point))
#             self._grid[point] = None
#
#             self._hash ^= zobrist.HASH_CODE[point, string.color]  # <3>
# # <1> This new helper method updates our Go board grid.
# # <2> Removing a string can create liberties for other strings.
# # <3> With Zobrist hashing, you need to unapply the hash for this move.
# # end::unapply_zobrist[]
#
#     def is_on_grid(self, point):
#         return 1 <= point.row <= self.num_rows and \
#             1 <= point.col <= self.num_cols
#
#     def get(self, point):
#         """Return the content of a point on the board.
#         Returns None if the point is empty, or a Player if there is a
#         stone on that point.
#         """
#         string = self._grid.get(point)
#         if string is None:
#             return None
#         return string.color
#
#     def get_go_string(self, point):
#         """Return the entire string of stones at a point.
#         Returns None if the point is empty, or a GoString if there is
#         a stone on that point.
#         """
#         string = self._grid.get(point)
#         if string is None:
#             return None
#         return string
#
#     def __eq__(self, other):
#         return isinstance(other, Board) and \
#             self.num_rows == other.num_rows and \
#             self.num_cols == other.num_cols and \
#             self._hash() == other._hash()
#
#     def __deepcopy__(self, memodict={}):
#         copied = Board(self.num_rows, self.num_cols)
#         # Can do a shallow copy b/c the dictionary maps tuples
#         # (immutable) to GoStrings (also immutable)
#         copied._grid = copy.copy(self._grid)
#         copied._hash = self._hash
#         return copied
#
# # tag::return_zobrist[]
#     def zobrist_hash(self):
#         return self._hash
# # end::return_zobrist[]
#
#
# class Move:
#     """Any action a player can play on a turn.
#     Exactly one of is_play, is_pass, is_resign will be set.
#     """
#     def __init__(self, point=None, is_pass=False, is_resign=False):
#         assert (point is not None) ^ is_pass ^ is_resign
#         self.point = point
#         self.is_play = (self.point is not None)
#         self.is_pass = is_pass
#         self.is_resign = is_resign
#
#     @classmethod
#     def play(cls, point):
#         """A move that places a stone on the board."""
#         return Move(point=point)
#
#     @classmethod
#     def pass_turn(cls):
#         return Move(is_pass=True)
#
#     @classmethod
#     def resign(cls):
#         return Move(is_resign=True)
#
#     def __str__(self):
#         if self.is_pass:
#             return 'pass'
#         if self.is_resign:
#             return 'resign'
#         return '(r %d, c %d)' % (self.point.row, self.point.col)
#
#
# # tag::init_state_zobrist[]
# class GameState:
#     def __init__(self, board, next_player, previous, move):
#         self.board = board
#         self.next_player = next_player
#         self.previous_state = previous
#         if self.previous_state is None:
#             self.previous_states = frozenset()
#         else:
#             self.previous_states = frozenset(
#                 previous.previous_states |
#                 {(previous.next_player, previous.board.zobrist_hash())})
#         self.last_move = move
# # end::init_state_zobrist[]
#
#     def apply_move(self, move):
#         """Return the new GameState after applying the move."""
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
#
#     def is_move_self_capture(self, player, move):
#         if not move.is_play:
#             return False
#         next_board = copy.deepcopy(self.board)
#         next_board.place_stone(player, move.point)
#         new_string = next_board.get_go_string(move.point)
#         return new_string.num_liberties == 0
#
#     @property
#     def situation(self):
#         return (self.next_player, self.board)
#
# # tag::ko_zobrist[]
#     def does_move_violate_ko(self, player, move):
#         if not move.is_play:
#             return False
#         next_board = copy.deepcopy(self.board)
#         next_board.place_stone(player, move.point)
#         next_situation = (player.other, next_board.zobrist_hash())
#         return next_situation in self.previous_states
# # end::ko_zobrist[]
#
#     def is_valid_move(self, move):
#         if self.is_over():
#             return False
#         if move.is_pass or move.is_resign:
#             return True
#         return (
#             self.board.get(move.point) is None and
#             not self.is_move_self_capture(self.next_player, move) and
#             not self.does_move_violate_ko(self.next_player, move))
#
#     def is_over(self):
#         if self.last_move is None:
#             return False
#         if self.last_move.is_resign:
#             return True
#         second_last_move = self.previous_state.last_move
#         if second_last_move is None:
#             return False
#         return self.last_move.is_pass and second_last_move.is_pass
#
#     def legal_moves(self):
#         moves = []
#         for row in range(1, self.board.num_rows + 1):
#             for col in range(1, self.board.num_cols + 1):
#                 move = Move.play(Point(row, col))
#                 if self.is_valid_move(move):
#                     moves.append(move)
#         # These two moves are always legal.
#         moves.append(Move.pass_turn())
#         moves.append(Move.resign())
#
#         return moves
#
#     def winner(self):
#         if not self.is_over():
#             return None
#         if self.last_move.is_resign:
#             return self.next_player
#         game_result = compute_game_result(self)
#         return game_result.winner
