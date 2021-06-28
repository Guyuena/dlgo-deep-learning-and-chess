"""
围棋机器人的统一接口
所有机器人都要根据当前游戏状态选择一个动作
当然，在这个方法内部可能调用其他复杂的方法
"""

# class Agent:
#     def __init__(self):
#         pass
#
#     def select_move(self, game_state0):
#         raise NotImplementedError
__all__ = [
    'Agent',
]

"围棋棋手代理的基类，后面的所有机器棋手代理人都继承该基类"
"主要是要在各自的棋手代理机器人中实现select_move()落子决策动作"
"机器人的统一接口"


# tag::agent[]
class Agent:
    def __init__(self):
        pass

    # 根据棋盘盘面状态去选择相应落子
    def select_move(self, game_state):
        raise NotImplementedError()  # 预留一个借口先不实现，让子类去实现  在navie子类中实现该方法

    # end::agent[]

    def diagnostics(self):
        return {}
