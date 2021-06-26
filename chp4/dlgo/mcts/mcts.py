# import math
# import random
#
# from dlgo.agent.base import Agent
# from dlgo.agent import mcts_navie
# from dlgo.gotypes import Player
# from dlgo.utils import point_from_coords
#
#
#
# __all__ = [
#     'MCTSAgent',
# ]
# """
# 每次蒙特卡洛算法分三步：
#
#      1.在蒙特卡洛树中添加一个新的棋盘盘面。
#
#      2.从那个位置模拟一个随机对局。
#
#      3.更新树的关于随机游戏结果的统计数据。
# """
#
#
# def fmt(x):
#     if x is Player.black:
#         return 'B'
#     if x is Player.white:
#         return 'W'
#     if x.is_pass:
#         return 'pass'
#     if x.is_resign:
#         return 'resign'
#     return point_from_coords(x.point)
#
#
# def show_tree(node, indent='', max_depth=3):
#     if max_depth < 0:
#         return
#     if node is None:
#         return
#     if node.parent is None:
#         print('%sroot' % indent)
#     else:
#         player = node.parent.game_state.next_player
#         move = node.move
#         print('%s%s %s %d %.3f' % (
#             indent, fmt(player), fmt(move),
#             node.num_rollouts,
#             node.winning_frac(player),
#         ))
#     for child in sorted(node.children, key=lambda n: n.num_rollouts, reverse=True):
#         show_tree(child, indent + '  ', max_depth - 1)
#
#
# # tag::mcts-node[]
# """
#     MCTS数据结构：蒙特卡洛树节点
#
#     game_state--当前树中此节点的游戏状态（棋盘局面和当前玩家）。
#     parent-导致这一局面的父节点。您可以将父级设置为None以指示树的根。
#     move-最后一个直接导致产生这个节点的落子。
#     children-树中所有子节点的列表。
#     win_counts和num_rollouts-关于从这个节点开始的统计信息。
#     unvisited_moves--该局面下合法但不属于树中节点的落子位置。每当向树中添加一个新节点时，就从unvisited_moves中调出一个落子位置，为它生成一个新的MCTS节点，并且将其添加到children中。
#
# """
#
#
# class MCTSNode(object):
#     # 构造与初始化
#     def __init__(self, game_state, parent=None, move=None):
#         self.game_state = game_state  # 搜索树当前节点的游戏状态（即棋局以及下一回合执子方）
#         self.parent = parent  # 当前MCTSNode节点的父节点
#         "触发当前棋局的上一步动作"
#         self.move = move  # 触发当前棋局的上一步动作
#         self.win_counts = {  # 展示黑白胜利的统计  推演的统计信息
#             Player.black: 0,
#             Player.white: 0,
#         }
#         self.num_rollouts = 0  # 表示当前推演的轮数
#         self.children = []  # 当前节点的所有的子节点的存储列表
#         self.unvisited_moves = game_state.legal_moves()  # 未加入到树中节点的合法落子
#
#     # end::mcts-node[]
#
#     """ 更新蒙特卡洛树某个节点  MCTS树节点可以通过下面两种方式进行修改 """
#
#     def add_random_child(self):  # 随机增加一个未加入树的子节点
#         index = random.randint(0, len(self.unvisited_moves) - 1)  # 先随机生成一个int整数
#         new_move = self.unvisited_moves.pop(index)  # 根据随机索引值来在没有生成树节点的列表中抽取一个节点作为新的搜索节点
#         new_game_state = self.game_state.apply_move(new_move)  # 加入到游戏状态中
#         new_node = MCTSNode(new_game_state, self, new_move)
#         self.children.append(new_node)  # 将新节点加入成为该节点的子节点
#         return new_node
#
#     # 统计胜者  对照书本上图4-13看,就是统计当前节点黑白棋子各在当前棋局下的获胜次数
#     def record_win(self, winner):
#         self.win_counts[winner] += 1
#         self.num_rollouts += 1
#
#     # tag::mcts-readers[]
#     """"三个辅助方法，用于访问树节点的有用的属性
#             三种方便的方法来访问树节点的有用属性：
#             can_add_child表明这个局面是否还有任何尚未添加到树中的合法落子点。
#             is_terminal报告游戏是否在此节点结束；如果是，则无法进一步搜索。
#             winning_frac返回给定棋手在一次试验赢的概率。
#
#     """
#
#     def can_add_child(self):
#         # 检测当前棋局中是否还有合法动作尚未添加到树中
#         return len(self.unvisited_moves) > 0  # 返回Ture or  False
#
#     def is_terminal(self):
#         # 是否到达终盘，终盘就停止搜索
#         return self.game_state.is_over()  # 返回Ture or  False
#
#     def winning_frac(self, player):
#         return float(self.win_counts[player]) / float(self.num_rollouts)  # 返回某一方在推演中获胜的比率
#
#
# # end::mcts-readers[]
#
#
# """
#     MCTS蒙特卡洛算法
#     您首先要创建一棵新树。根节点为当前棋局盘面，然后你反复进行试验。在这种实现中，您每个回合重复固定的轮数；其他的实现中运行的时间长度是固定的。
# """
#
#
# # class MCTSAgent(agent.Agent):
# class MCTSAgent(Agent):
#     # 构造函数以及初始化
#     def __init__(self, num_rounds, temperature):
#         Agent.__init__(self)
#         self.num_rounds = num_rounds  # 轮数
#         self.temperature = temperature  # 参数C  温度
#
#     """
#         用当前游戏状态作为根节点来创建一颗搜索树，接着反复生成新的推演
#     """
#
#     def select_move(self, game_state):  # 负责挑选可供继续搜索的最佳分支
#         root = MCTSNode(game_state)  # 树的根节点
#         # tag::mcts-rounds[]
#         for i in range(self.num_rounds):  # 循环轮数
#             node = root
#             while (not node.can_add_child()) and (not node.is_terminal()):  # 一直搜索到游戏在节点结束  只要还能继续加入子节点，不是终结，就跳过这条的服务语句
#                 node = self.select_child(node)  # 后面来实现
#             if node.can_add_child():  # 在前面的判断通过下，把新的孩子节点加入到新树中.
#                 '''找到合适的节点后，使用add_random_child()来选择后续动作，并添加到搜索树中'''
#                 node = node.add_random_child()  # 树中的新节点是随机游戏的起点  此时node是一个新建的 MCTSNode，还没包含任何推演
#             """从当前新建的节点node开始使用simulate_random_game()进行推演"""
#             winner = self.simulate_random_game(node.game_state)  # 从当前局面进行模拟对局，得出胜者
#             while node is not None:  # 从当前节点进行回溯更新当前及祖先胜者次数
#                 node.record_win(winner)
#                 node = node.parent
#         scored_moves = [
#             (child.winning_frac(game_state.current_player), child.move, child.num_rollouts)
#             for child in root.children
#         ]
#         scored_moves.sort(key=lambda x: x[0], reverse=True)
#         for s, m, n in scored_moves[::]:
#             print('%s - %.3f (%d)' % (m, s, n))
#         # end::mcts-rounds[]
#
#         # tag::mcts-selection[]
#         # Having performed as many MCTS rounds as we have time for, we
#         # now pick a move.
#         """从根节点的诸多孩子节点中根据获胜几率选择最佳下法"""
#         best_move = None
#         best_pct = -1.0
#         for child in root.children:
#             child_pct = child.winning_frac(game_state.next_player)
#             if child_pct > best_pct:
#                 best_pct = child_pct
#                 best_move = child.move
#         print('Select move %s with win pct %.3f' % (best_move, best_pct))
#         return best_move
#
#     # end::mcts-selection[]
#
#     # 计算UCT分值
#     def get_UCT_score(child_rollout, parent_rollout, win_prc, temperature):
#         exploration = math.sqrt(math.log(parent_rollout) / child_rollout)
#         return win_prc + temperature * exploration
#
#     # tag::mcts-uct[]
#
#     def select_child(self, node):
#         """Select a child according to the upper confidence bound for
#         trees (UCT) metric.
#         根据树的置信上限 (UCT) 指标选择一个子节点
#         """
#         # 获得其孩子节点试验的总数,即为父节点的试验次数
#         total_rollouts = sum(child.num_rollouts for child in node.children)
#         log_rollouts = math.log(total_rollouts)
#
#         # 遍历该节点的孩子节点，获得最佳分数的孩子
#         best_score = -1
#         best_child = None
#         # Loop over each child.
#         for child in node.children:
#             # 获得该孩子节点的UCT分数
#             win_percentage = child.winning_frac(node.game_state.next_player)
#             exploration_factor = math.sqrt(log_rollouts / child.num_rollouts)
#             uct_score = win_percentage + self.temperature * exploration_factor
#             # Check if this is the largest we've seen so far.
#             if uct_score > best_score:
#                 best_score = uct_score
#                 best_child = child
#         return best_child
#
#     # end::mcts-uct[]
#
#     @staticmethod
#     def simulate_random_game(game):
#         bots = {
#             Player.black: mcts_navie.FastRandomBot(),
#             Player.white: mcts_navie.FastRandomBot(),
#
#         }
#         while not game.is_over():
#             bot_move = bots[game.next_player].select_move(game)
#             game = game.apply_move(bot_move)
#         return game.winner()



import math
import random

# from dlgo import agent
# from dlgo.gotypes import Player
# from dlgo.utils import point_from_coords

from dlgo.agent.base import Agent
from dlgo.mcts import mcts_navie
from dlgo.gotypes import Player
from dlgo.utils import point_from_coords

__all__ = [
    'MCTSAgent',
]


def fmt(x):
    if x is Player.black:
        return 'B'
    if x is Player.white:
        return 'W'
    if x.is_pass:
        return 'pass'
    if x.is_resign:
        return 'resign'
    return point_from_coords(x.point)


def show_tree(node, indent='', max_depth=3):
    if max_depth < 0:
        return
    if node is None:
        return
    if node.parent is None:
        print('%sroot' % indent)
    else:
        player = node.parent.game_state.next_player
        move = node.move
        print('%s%s %s %d %.3f' % (
            indent, fmt(player), fmt(move),
            node.num_rollouts,
            node.winning_frac(player),
        ))
    for child in sorted(node.children, key=lambda n: n.num_rollouts, reverse=True):
        show_tree(child, indent + '  ', max_depth - 1)


# tag::mcts-node[]
class MCTSNode(object):
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            Player.black: 0,
            Player.white: 0,
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = game_state.legal_moves()
# end::mcts-node[]

# tag::mcts-add-child[]
    def add_random_child(self):
        index = random.randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index)
        new_game_state = self.game_state.apply_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node
# end::mcts-add-child[]

# tag::mcts-record-win[]
    def record_win(self, winner):
        self.win_counts[winner] += 1
        self.num_rollouts += 1
# end::mcts-record-win[]

# tag::mcts-readers[]
    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.game_state.is_over()

    def winning_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)
# end::mcts-readers[]


class MCTSAgent(Agent):
    def __init__(self, num_rounds, temperature):
        Agent.__init__(self)
        self.num_rounds = num_rounds
        self.temperature = temperature   # 蒙特卡洛搜索树的活跃度

# tag::mcts-signature[]
    def select_move(self, game_state):
        root = MCTSNode(game_state)
# end::mcts-signature[]

# tag::mcts-rounds[]
        for i in range(self.num_rounds):
            node = root
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            # Add a new child node into the tree.
            if node.can_add_child():
                node = node.add_random_child()

            # Simulate a random game from this node.
            winner = self.simulate_random_game(node.game_state)

            # Propagate scores back up the tree.
            while node is not None:
                node.record_win(winner)
                node = node.parent
# end::mcts-rounds[]

        scored_moves = [
            (child.winning_frac(game_state.next_player), child.move, child.num_rollouts)
            for child in root.children
        ]
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        # for s, m, n in scored_moves[:10]:
        """这里设置可以打印输出多少个搜索树节点结果，超过这个树也只能输出这么多个，少于就是例化输入多少就输出多少"""
        print('蒙特卡洛搜素结果：  ')
        for s, m, n in scored_moves[:50]:
            print('%s - %.3f (%d)' % (m, s, n))

# tag::mcts-selection[]
        # Having performed as many MCTS rounds as we have time for, we
        # now pick a move.
        best_move = None
        best_pct = -1.0

        for child in root.children:
            child_pct = child.winning_frac(game_state.next_player)
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.move
        print('蒙特卡洛搜素选择落子： %s with win pct %.3f' % (best_move, best_pct))
        # print('Select move %s with win pct %.3f' % (best_move, best_pct))
        return best_move
# end::mcts-selection[]

# tag::mcts-uct[]
    def select_child(self, node):
        """Select a child according to the upper confidence bound for
        trees (UCT) metric.
        """
        total_rollouts = sum(child.num_rollouts for child in node.children)
        log_rollouts = math.log(total_rollouts)

        best_score = -1
        best_child = None
        # Loop over each child.
        for child in node.children:
            # Calculate the UCT score.
            win_percentage = child.winning_frac(node.game_state.next_player)
            exploration_factor = math.sqrt(log_rollouts / child.num_rollouts)
            uct_score = win_percentage + self.temperature * exploration_factor
            # Check if this is the largest we've seen so far.
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        return best_child
# end::mcts-uct[]

    @staticmethod
    def simulate_random_game(game):
        bots = {
            Player.black: mcts_navie.FastRandomBot(),
            Player.white: mcts_navie.FastRandomBot(),
        }
        while not game.is_over():
            bot_move = bots[game.next_player].select_move(game)
            game = game.apply_move(bot_move)
        return game.winner()
