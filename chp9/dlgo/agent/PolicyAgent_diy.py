import numpy as np

from dlgo import kerasutil, encoders, goboard
from dlgo.agent import policy_gradient_loss
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye


class PolicyAgent(Agent):

    def __init__(self, model, encoder):
        super().__init__()
        # eras顺序模型实例
        self.model = model
        # 编码器
        self.encoder = encoder

        # 返回整个棋盘预测概率分布
    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_tensor = np.array([encoded_state])
        return self.model.predict(input_tensor)[0]

        # 裁剪概率分布
    def clip_probs(original_probs):
        min_p = 1e-5
        max_p = 1 - min_p
        clipped_probs = np.clip(original_probs, min_p, max_p)
        # 确保结果仍然是有效的概率分布
        clipped_probs = clipped_probs / np.sum(clipped_probs)
        return clipped_probs

    def select_move(self, game_state):

        board_tensor = self._encoder.encode(game_state)
        x = np.array([board_tensor])
        num_moves = self._encoder.board_width * self._encoder.board_height
        move_probs = self._model.predict(x)[0]
        if np.random.random() < self._temperature:
            # Explore random moves.
            move_probs = np.ones(num_moves) / num_moves
        else:
            # Follow our current policy.
            """调用Keras的预测函数会输出批量的预测结果，因此把整个棋盘包装成一个数组，然后从结果数组中选取第一项"""


        # Prevent move probs from getting stuck at 0 or 1.
        eps = 1e-5
        move_probs = np.clip(move_probs, eps, 1 - eps)
        # Re-normalize to get another probability distribution.
        move_probs = move_probs / np.sum(move_probs)

        # Turn the probabilities into a ranked list of moves.
        candidates = np.arange(num_moves)
        ranked_moves = np.random.choice(
            candidates, num_moves, replace=False, p=move_probs)
        for point_idx in ranked_moves:
            point = self._encoder.decode_point_index(point_idx)
            if game_state.is_valid_move(goboard.Move.play(point)) and \
                    not is_point_an_eye(game_state.board,
                                        point,
                                        game_state.next_player):
                if self._collector is not None:
                    self._collector.record_decision(
                        state=board_tensor,
                        action=point_idx
                    )
                return goboard.Move.play(point)
        # No legal, non-self-destructive moves less.
        return goboard.Move.pass_turn()


    def serialize(self, h5file):
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self._encoder.name()
        h5file['encoder'].attrs['board_width'] = self._encoder.board_width
        h5file['encoder'].attrs['board_height'] = self._encoder.board_height
        h5file.create_group('model')
        kerasutil.save_model_to_hdf5_group(self._model, h5file['model'])


     #   反序列化来解析、获得模型
    def load_policy_agent(h5file):
        model = kerasutil.load_model_from_hdf5_group(
            h5file['model'],
            custom_objects={'policy_gradient_loss': policy_gradient_loss})
        encoder_name = h5file['encoder'].attrs['name']
        if not isinstance(encoder_name, str):
            encoder_name = encoder_name.decode('ascii')
        board_width = h5file['encoder'].attrs['board_width']
        board_height = h5file['encoder'].attrs['board_height']
        encoder = encoders.get_encoder_by_name(
            encoder_name,
            (board_width, board_height))
        return PolicyAgent(model, encoder)  # 重建代理