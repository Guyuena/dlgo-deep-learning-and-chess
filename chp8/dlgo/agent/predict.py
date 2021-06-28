# tag::dl_agent_imports[]
import numpy as np

from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo import encoders
from dlgo import goboard
from dlgo import kerasutil

# end::dl_agent_imports[]
__all__ = [
    'DeepLearningAgent',
    'load_prediction_agent',
]

# tag::dl_agent_init[]
"创建一个深度学习的落子预测AI代理的定义 "

"""按照第3章中得到的随机落子AI的概念创建深度学习机器人"""


class DeepLearningAgent(Agent):
    # 初始化  例化的时候传入参数对应的网路模型和棋盘棋局编码器
    def __init__(self, model, encoder):
        Agent.__init__(self)
        self.model = model  # 模型用于预测下一步动作
        self.encoder = encoder  # 编码器将棋盘状态转换为特征

    # end::dl_agent_init[]
    # 使用编码器将棋盘撞他转换为特征，然后使用该模型去预测下一步落子。实际上，您将使用该模型去计算所有可能的概率分布。
    # tag::dl_agent_predict[]
    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)  # 编码器编码游戏状态，将棋盘状态转换为特征
        input_tensor = np.array([encoded_state])  # 把编码结果转换为numpy的数组
        """调用Keras的预测函数会输出批量的预测结果，因此把整个棋盘包装成一个数组，然后从结果数组中选取第一项"""
        return self.model.predict(input_tensor)[0]  # 把input_tensor参数输入到对应的网络模型中进行预测

    def select_move(self, game_state):
        num_moves = self.encoder.board_width * self.encoder.board_height

        # 获得预测概率分布
        move_probs = self.predict(game_state)
        # end::dl_agent_predict[]

        # tag::dl_agent_probabilities[]
        """裁剪概率分布"""
        # 调整概率分布
        move_probs = move_probs ** 3  # <1>大幅拉开可能点与非可能点之间的距离
        eps = 1e-6
        move_probs = np.clip(move_probs, eps, 1 - eps)  # <2>  裁剪概率分布   防止落子概率卡在0或1
        move_probs = move_probs / np.sum(move_probs)  # <3>  重新归一化以获得另一个概率分布。确保结果仍是有效的概率分布
        # <1> Increase the distance between the move likely and least likely moves.
        # <2> Prevent move probs from getting stuck at 0 or 1
        # <3> Re-normalize to get another probability distribution.
        # end::dl_agent_probabilities[]

        # tag::dl_agent_candidates[]
        """从已排序的候选动作列表中选择下一步动作"""
        candidates = np.arange(num_moves)  # <1>   # 把概率转成一个排序列表
        ranked_moves = np.random.choice(   # <2> # 潜在候选落子动作中，按照落子概率进行采样，不允许取相同的落子
            candidates, num_moves,
            replace=False,
            p=move_probs)

        # 从最高层开始，找到一个有效的落子，不会减少眼（围棋中的眼）的合法动作
        for point_idx in ranked_moves:
            point = self.encoder.decode_point_index(point_idx)
            if game_state.is_valid_move(goboard.Move.play(point)) and \
                    not is_point_an_eye(game_state.board, point, game_state.next_player):  # <3>
                return goboard.Move.play(point)
        return goboard.Move.pass_turn()  # <4>  无法找到不导致自吃的回合动作，选择跳过

    # <1> Turn the probabilities into a ranked list of moves.
    # <2> Sample potential candidates
    # <3> Starting from the top, find a valid move that doesn't reduce eye-space.
    # <4> If no legal and non-self-destructive moves are left, pass.
    # end::dl_agent_candidates[]

    # 训练了一个深度学习模型，并创建了一个代理，然后你坚持下去。稍后，这个代理将被反序列化成了服务，这样人类玩家或其他机器人就可以对抗它。
    # 要执行序列化步骤，就需要序列化Keras的格式。当您持久化Keras模型时，它将以HDF5进行存储，这是一种有效的序列化格式。
    # HDF5文件包含灵活的组，用于存储元信息和数据。对于任何一个Keras模型，
    # 您可以调用model.save（“model_path.h5”）将完整模型（即神经网络体系结构和所有权重）持久化为本地文件model_path.h5。
    # 你唯一需要的就是在保持像这样的Keras模型之前，先安装Python库h5py

    """存储Keras模型
        存储DeepLearningAgent的实例，方便以后调用
    """

    # tag::dl_agent_serialize[]

    # 序列化模型 序列化一个深度学习代理的实例 DeepLearningAgent
    def serialize(self, h5file):
        # 先创建一个编码器组
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self.encoder.name()
        h5file['encoder'].attrs['board_width'] = self.encoder.board_width
        h5file['encoder'].attrs['board_height'] = self.encoder.board_height

        # 再创建一个模型组
        h5file.create_group('model')
        kerasutil.save_model_to_hdf5_group(self.model, h5file['model'])  #保存


# end::dl_agent_serialize[]


# tag::dl_agent_deserialize[]

# 从序列化的文件中加载模型
"""从hsfile文件中反序列化DeepLearningAgent的实例，方便以后调用
"""
def load_prediction_agent(h5file):
    # 加载模型
    model = kerasutil.load_model_from_hdf5_group(h5file['model'])
    # 加载编码器
    encoder_name = h5file['encoder'].attrs['name']
    if not isinstance(encoder_name, str):
        encoder_name = encoder_name.decode('ascii')
        # encoder_name = encoder_name.decode('utf-8')
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = encoders.get_encoder_by_name(
        encoder_name, (board_width, board_height))
    return DeepLearningAgent(model, encoder)
# tag::dl_agent_deserialize[]
