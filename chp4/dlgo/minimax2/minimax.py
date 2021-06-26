'''
   实现极大极小算法的一个小例子：井字棋
'''
import random
from dlgo.agent.base import Agent
import enum


# 游戏的三种状态
class GameResult(enum.Enum):
    loss = 1
    draw = 2
    win = 3


# 根据对手最好结果反推自己
def reverse_game_result(game_result):
    if game_result == GameResult.loss:
        return game_result.win
    if game_result == GameResult.win:
        return game_result.loss
    return GameResult.draw


# 得到游戏的最佳结果
def best_result(game_state):
    if game_state.is_over():
        if game_state.next_player == game_state.winner():
            return GameResult.win
        elif game_state.winner() is None:
            return GameResult.draw
        else:
            return GameResult.loss
    best_result_so_far = GameResult.loss
    for candidate_move in game_state.legal_moves():
        next_state = game_state.apply_move(candidate_move)  # <1>
        opponent_best_result = best_result(next_state)  # <2>
        our_result = reverse_game_result(opponent_best_result)  # <3>
        if our_result.value > best_result_so_far.value:  # <4>
            best_result_so_far = our_result
    return best_result_so_far

# 使用极小极大算法的AI
class MiniMaxAgent(Agent):
    def select_move(self,game_state):
        winning_moves = []  # 赢棋落子点集合
        drawing_moves = []  # 平局落子点
        losing_moves = []  # 输棋落子点
        for possible_move in  game_state.legal_moves():
            next_state = game_state.apply_move(possible_move)
            opponent_best_result = best_result(next_state)  # 查看对手在我落子后的最好结果
            if opponent_best_result == GameResult.loss:  # 对手必输
                winning_moves.append(possible_move)
            elif opponent_best_result == GameResult.draw: # 对手最好是平局
                drawing_moves.append(possible_move)
            else:
                losing_moves.append(possible_move)
        # 有必胜招法，就随机选一种去下
        if winning_moves:
            return random.choice(winning_moves)
        elif drawing_moves:
            return random.choice(drawing_moves)
        else:
            return random.choice(losing_moves)