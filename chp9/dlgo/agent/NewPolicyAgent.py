from dlgo.encoders.ElevenEncoder import ElevenEncoder
from keras.models import Sequential
from dlgo.networks.large import layers
from keras.layers import Dense
from keras.layers import Activation
from dlgo.agent.PolicyAgent_diy  import PolicyAgent

board_size = 19
encoder = ElevenEncoder(board_size)
# 构建顺序神经网络
model = Sequential()
for layer in layers(encoder.shape()):
    model.add(layer)
# 添加一个输出层，该层将在返回棋盘上点的概率分布
model.add(Dense(encoder.num_points()))
model.add(Activation('softmax'))
new_agent = PolicyAgent(model, encoder)
