import h5py

from keras.models import Sequential
from keras.layers import Dense

from dlgo.agent.predict_diy import DeepLearningAgent, load_prediction_agent
from dlgo.data.parallel_processor import GoDataProcessor
from dlgo.encoders.sevenplane import SevenPlaneEncoder
from dlgo.httpfrontend import get_web_app
from dlgo.networks import large

go_board_rows , go_board_cols = 19,19
nb_classes = go_board_rows * go_board_cols
encoder = SevenPlaneEncoder((go_board_rows,go_board_cols))  # 例化编码器
processor = GoDataProcessor(encoder=encoder.name())  # 例化sgf数据处理器

X ,y = processor.load_go_data(num_samples=100)  # 从围棋数据中加载特征和标签

load_prediction_agent
"""准备好数据特征和标签后，创建神经网络，并训练"""

input_shape = (encoder.num_planes,go_board_rows, go_board_cols)
model = Sequential()
network_layers = large.layers(input_shape)
for layer in network_layers:  # 从定义的网络large中提取出各个层，并添加到序列网络sequential中
    model.add(layer)
model.add(Dense(nb_classes, activation='softmax'))  # 添加稠密层（全连接层）
# 配置训练方法   损失函数模型、优化器模型、评判指标类型
model.compile(loss='categorical_crossentropy',
              optimizer='adadelta',
              metrics=['accuracy']
              )

# 训练数据喂入
model.fit(X, y, batch_size=8, epochs=20, verbose=1)


"保存模型"
deep_learning_robot = DeepLearningAgent(model,encoder)
deep_learning_robot.serialize("./deep_robot.h5")


