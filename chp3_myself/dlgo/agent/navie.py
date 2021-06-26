import random
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.gotypes import Point
from dlgo.goboard_slow import Move


# 一个随机的围棋机器人
class RandomBot(Agent):
    def select_move(self, game_state):
        # choose a random vaild move that preserves our own eyes
        candidates = []  # 候选
        # 随机生成一个 行数和列数，组成一个落子坐标
        for r in range(1, game_state.board.num_rows + 1):  # 行
            for c in range(1, game_state.board.num_cols + 1):  # 列
                candidate = Point(row=r, col=c)
                # 判断这个坐标是否有效，并且不能是落子眼eyes中
                if game_state.is_valid_move(Move.play(candidate)) and \
                        not is_point_an_eye(game_state.board,
                                            candidate,
                                            game_state.next_player):
                    candidates.append(candidate)  # 落子坐标有效，就加入候选坐标列表中
        if not candidates:  # 如果无子可下了，就跳过
            return Move.pass_turn()
        return Move.play(random.choice(candidates))  # 把随机有效坐标进行棋盘落子动作
