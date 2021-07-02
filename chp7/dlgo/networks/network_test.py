from dlgo.data.parallel_processor import GoDataProcessor  # 训练数据处理器
from dlgo.encoders.oneplane import OnePlaneEncoder  # 编码器
from dlgo.networks.small import layers  # 待训练的网络
import tensorflow as tf
from tensorflow import keras
# import keras
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import ModelCheckpoint  # 模型检查点
# from keras.optimizers import SGD  # 报错
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.optimizers import Adadelta

if __name__ == '__main__':
    print('当前keras版本', keras.__version__)
    # 训练和测试数据建立  start
    go_board_rows, go_board_cols = 19, 19
    num_classes = go_board_rows * go_board_cols
    num_games = 100  # 100盘游戏
    encoder = OnePlaneEncoder((go_board_rows, go_board_cols))  # 创建棋盘，与编码器大小一致
    processor = GoDataProcessor(encoder=encoder.name())  # 围棋数据处理器
    generator = processor.load_go_data('train', num_games, use_generator=True)  # 数据生成器，用于训练数据
    test_generator = processor.load_go_data('test', num_games, use_generator=True)  # 数据生成器，用于测试数据
    # 训练和测试数据建立  end

    # "定义Keras神经网络"  start
    input_shape = (encoder.num_planes, 1, go_board_rows, go_board_cols)  # 平面数，行，列
    network_layer = layers(input_shape)  # 例化small的网络
    # model = Sequential()  # 序列化的网络
    model = tf.keras.models.Sequential()  # 序列化的网络
    for layer in network_layer:  # 遍历，逐个加入
        model.add(layer)
    model.add(Dense(num_classes, activation='softmax'))  # 最后一个稠密层（全连接层）
    sgd = SGD(learning_rate=0.1, momentum=0.9, decay=0.01)  # 初始化 sgd
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    # "定义Keras神经网络"  end


    # "用生成器拟合Keras模型并评估"

    epochs = 5
    batch_size = 2
    # 训练
    # fit_generator 需要指定参数 generator、epochs(训练迭代周期数)、 steps_per_epoch（每个迭代周期训练步数）  三个基本参数
    # 还要添加参数： validation_data（验证数据生成器） validation_steps（每个迭代周期中的验证的步数）
    model.fit_generator(
        # model.fit_generator(
        generator=generator.generate(batch_size, num_classes),
        epochs=epochs,
        steps_per_epoch=generator.get_num_samples() / batch_size,
        validation_data=test_generator.generate(batch_size, num_classes),
        validation_steps=test_generator.get_num_samples() / batch_size,
        # 回调函数 在训练过程中跟踪和返回额外信息
        # 利用回调来触发ModelCheckpoint工具
        callbacks=[ModelCheckpoint('checkpoints/small_model_epoch_{epoch}.h5')]

    )
    # 评估
    model.evaluate_generator(
        generator=test_generator.generate(batch_size, num_classes),
        steps=test_generator.get_num_samples() / batch_size
    )

"报错"
# tensorflow.python.framework.errors_impl.InvalidArgumentError:  Conv2DCustomBackpropInputOp only supports NHWC.
# 是CPU不支持图片的NHWC这样的排列方式：
#
# N batch_size
# H height
# W width
# C color 层数
#
# 用GPU计算没这个问题，用CPU计算有这个问题，先记录这个问题，解决了过来填坑
