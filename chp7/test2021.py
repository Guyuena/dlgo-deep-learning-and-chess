from dlgo.data.parallel_processor import GoDataProcessor   # 训练数据处理器
from dlgo.encoders.oneplane import OnePlaneEncoder  # 编码器
from dlgo.networks.small import layers   # 待训练的网络


from tensorflow import keras
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import ModelCheckpoint  # 模型检查点
# from keras.optimizers import SGD  # 报错
from tensorflow.keras.optimizers import SGD





if __name__ == '__main__':
    print('当前keras版本',keras.__version__)

    # 进行配置，每个GPU使用90%上限现存
    # os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 使用编号为0，1号的GPU
    # # config = tf.ConfigProto()
    # config = tf.compat.v1.ConfigProto()
    # config.gpu_options.per_process_gpu_memory_fraction = 0.9  # 每个GPU上限控制在90%以内
    # session = tf.compat.v1.Session(config=config)
    # # 设置session
    # KTF.set_session(session)






    go_board_rows, go_board_cols = 19, 19
    num_classes = go_board_rows * go_board_cols
    num_games = 100  # 100盘游戏

    encoder = OnePlaneEncoder((go_board_rows, go_board_cols))  # 创建棋盘，与编码器大小一致
    processor = GoDataProcessor(encoder=encoder.name())  # 围棋数据处理器
    generator = processor.load_go_data('train', num_games, use_generator=True)  # 数据生成器，用于训练数据
    # tf.keras.backend.set_image_data_format('channels_last')
    # temp_x_train = []
    # for i in range(len(generator)):
    #     new_x_train_row = np.moveaxis(generator[i], 0, 2)
    #     temp_x_train.append(new_x_train_row)
    # x_train = np.array(temp_x_train)

    test_generator = processor.load_go_data('test', num_games, use_generator=True)  # 数据生成器，用于测试数据

    "定义Keras神经网络"

    input_shape = (encoder.num_planes, 1, go_board_rows, go_board_cols)  # 平面数，行，列

    network_layer = layers(input_shape)  # 例化small的网络
    model = Sequential()  # 序列化的网络
    for layer in network_layer:  # 遍历，逐个加入
        model.add(layer)

    model.add(Dense(num_classes, activation='softmax'))  # 最后一个稠密层（全连接层）

    sgd = SGD(learning_rate=0.1, momentum=0.9, decay=0.01)  # 初始化 sgd

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

    "用生成器拟合Keras模型并评估"

    epochs = 5
    batch_size = 128
    # 训练
    # fit_generator 需要指定参数 generator、epochs(训练迭代周期数)、 steps_per_epoch（每个迭代周期训练步数）  三个基本参数
    # 还要添加参数： validation_data（验证数据生成器） validation_steps（每个迭代周期中的验证的步数）
    # model.fit_generator(
    model.fit(
        # generator=generator.generate(batch_size, num_classes),
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