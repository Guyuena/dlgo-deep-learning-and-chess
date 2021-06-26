"""
围棋机器人的统一接口
所有机器人都要根据当前游戏状态选择一个动作
当然，在这个方法内部可能调用其他复杂的方法
"""


class Agent:
    def __init__(self):
        pass

    def select_move(self, game_state0):
        raise NotImplementedError
