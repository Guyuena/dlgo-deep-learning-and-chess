import numpy as np

__all__ = [
    'ExperienceCollector',
    'ExperienceBuffer',
    'combine_experience',
    'load_experience',
]
# 经验数据包含三个部分：状态、行动和回报。为了有效组织这三个部分，您可以创建一个单独的数据结构，将它们放在一起。
# ExperienceBuffer类是一个经验数据集的最小容器。它有三个属性：状态、行动和奖励。所有这些都被表示为NumPy数组；
# 您的代理将负责编码它的状态和动作作为数据结构。ExperienceBuffer只是一个容器，用来传递数据集。在这种实现中，没有任何特定的策略梯度学习


class ExperienceCollector:
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.advantages = []
        self._current_episode_states = []
        self._current_episode_actions = []
        self._current_episode_estimated_values = []

        # begin_episode和complete_episode，这两种方法被自我游戏驱动程序调用，以指示一个简单游戏的开始和结束。
        # record_decision，它被代理调用以指示它选择的单个操作。
        # to_buffer将ExperienceCollector所记录的所有内容打包并返回ExperienceBuffer。自我对弈驱动程序将在自我游戏会话结束时调用它。



    def begin_episode(self):
        self._current_episode_states = []
        self._current_episode_actions = []
        self._current_episode_estimated_values = []

    def record_decision(self, state, action, estimated_value=0):
        # 把一次决策存储到当前期中；
        # 代理对象负责对棋局的状态和动作进行编码
        self._current_episode_states.append(state)
        self._current_episode_actions.append(action)
        self._current_episode_estimated_values.append(estimated_value)

    def complete_episode(self, reward):
        num_states = len(self._current_episode_states)
        self.states += self._current_episode_states
        self.actions += self._current_episode_actions
        self.rewards += [reward for _ in range(num_states)]  # 将最后的收获分摊到本局所有的动作

        for i in range(num_states):
            advantage = reward - self._current_episode_estimated_values[i]
            self.advantages.append(advantage)

        self._current_episode_states = []
        self._current_episode_actions = []
        self._current_episode_estimated_values = []

    def to_buffer(self): # 把累计数据转换为numpy数组
        return ExperienceBuffer(
            states=np.array(self.states),
            actions=np.array(self.action),
            rewards=np.array(self.rewards)
        )


class ExperienceBuffer:
    def __init__(self, states, actions, rewards, advantages):
        self.states = states
        self.actions = actions
        self.rewards = rewards
        self.advantages = advantages

    def serialize(self, h5file):
        h5file.create_group('experience')
        h5file['experience'].create_dataset('states', data=self.states)
        h5file['experience'].create_dataset('actions', data=self.actions)
        h5file['experience'].create_dataset('rewards', data=self.rewards)
        h5file['experience'].create_dataset('advantages', data=self.advantages)


def combine_experience(collectors):
    combined_states = np.concatenate([np.array(c.states) for c in collectors])
    combined_actions = np.concatenate([np.array(c.actions) for c in collectors])
    combined_rewards = np.concatenate([np.array(c.rewards) for c in collectors])
    combined_advantages = np.concatenate([
        np.array(c.advantages) for c in collectors])

    return ExperienceBuffer(
        combined_states,
        combined_actions,
        combined_rewards,
        combined_advantages)


def load_experience(h5file):
    return ExperienceBuffer(
        states=np.array(h5file['experience']['states']),
        actions=np.array(h5file['experience']['actions']),
        rewards=np.array(h5file['experience']['rewards']),
        advantages=np.array(h5file['experience']['advantages']))
