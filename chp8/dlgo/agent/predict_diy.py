import numpy as np

from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo import goboard
from dlgo import encoders
from dlgo import goboard
from dlgo import kerasutil


class DeepLearningAgent(Agent):

    def __init__(self, model, encoder):
        Agent.__init__(self)
        self.model = model
        self.encoder = encoder

    # 返回整个棋盘预测概率分布
    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_tensor = np.array([encoded_state])
        return self.model.predict(input_tensor)[0]

    def select_move(self, game_state):
        num_moves = self.encoder.board_width * self.encoder.board_height
        # 获得预测概率分布
        move_probs = self.predict(game_state)

        # 大幅拉开可能点与非可能点之间的距离
        move_probs = move_probs ** 3
        eps = 1e-6
        # 防止落子概率卡在0或1
        move_probs = np.clip(move_probs, eps, 1 - eps)
        # 重新得到另一个概率分布
        move_probs = move_probs / np.sum(move_probs)

     # 把概率转成一个排序列表
        candidates = np.arange(num_moves)
        # 按照落子概率进行采样，不允许取相同的落子
        ranked_moves = np.random.choice(candidates, num_moves, replace=False, p=move_probs)
        # 从最高层开始，找到一个有效的落子，不会减少视野空间
        for point_index in ranked_moves:
            point = self.encoder.decode_point_index(point_index)
            if game_state.is_valid(goboard.Move.play(point)) and \
                    not is_point_an_eye(game_state.board, point, game_state.current_player):
                return goboard.Move.play(point)
        return goboard.Move.pass_turn()


# 训练了一个深度学习模型，并创建了一个代理，然后你坚持下去。稍后，这个代理将被反序列化成了服务，
# 这样人类玩家或其他机器人就可以对抗它。要执行序列化步骤，就需要序列化Keras的格式。当您持久化Keras模型时，
# 它将以HDF5进行存储，这是一种有效的序列化格式。HDF5文件包含灵活的组，用于存储元信息和数据。对于任何一个Keras模型，
# 您可以调用model.save（“model_path.h5”）将完整模型（即神经网络体系结构和所有权重）持久化为本地文件model_path.h5

    """序列化模型"""
    def serialize(self, h5file):
        # 先创建一个编码器组
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self.encoder.name()
        h5file['encoder'].attrs['board_width'] = self.encoder.board_width
        h5file['encoder'].attrs['board_height'] = self.encoder.board_height
        # 再创建一个模型组
        h5file.create_group('model')
        kerasutil.save_model_to_hdf5_group(self.model, h5file['model'])

    """在序列化模型之后，您还需要知道如何从HDF5文件去加载它。"""

    # 从序列化的文件中加载模型
def load_prediction_agent(h5file):
    # 加载模型
    model = kerasutil.load_model_from_hdf5_group(h5file['model'])
    # 加载编码器
    encoder_name = h5file['encoder'].attrs['name']
    if not isinstance(encoder_name, str):
        encoder_name = encoder_name.decode('ascii')   # 编解码格式
        # encoder_name = encoder_name.decode('ascii')
        # encoder_name = encoder_name.decode('utf-8')  # 因为
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = encoders.get_encoder_by_name(
        encoder_name, (board_width, board_height))
    return DeepLearningAgent(model, encoder)


