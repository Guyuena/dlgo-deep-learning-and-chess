from dlgo.data.parallel_processor import GoDataProcessor
from dlgo.encoders.oneplane import  OnePlaneEncoder
from dlgo.networks import small


from keras.models import Sequential
from keras.layers.core import Dense
from keras.callbacks import ModelCheckpoint  # 存储进度

if __name__ == '__main__':
    go_board_rows, go_board_cols = 19, 19
    num_classes = go_board_rows * go_board_cols
    num_games = 100

    # 创建OnePlane编码器
    encoder = OnePlaneEncoder((go_board_rows, go_board_cols))

    # 初始化围棋数据进程
    processor = GoDataProcessor(encoder=encoder.name())

    # 创建训练数据生成器
    generator = processor.load_go_data('train', num_games, use_generator=True)
    # 创建测试数据生成器
    test_generator = processor.load_go_data('test', num_games, use_generator=True)

    input_shape = (encoder.num_planes, go_board_rows, go_board_cols)
    network_layers = small.layers(input_shape)
    model = Sequential()
    for layer in network_layers:
        model.add(layer)
    model.add(Dense(num_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    # end::train_generator_model[]

    # tag::train_generator_fit[]
    epochs = 5
    batch_size = 128
    model.fit_generator(generator=generator.generate(batch_size, num_classes),  # <1>
                        epochs=epochs,
                        steps_per_epoch=generator.get_num_samples() / batch_size,  # <2>
                        validation_data=test_generator.generate(batch_size, num_classes),  # <3>
                        validation_steps=test_generator.get_num_samples() / batch_size,  # <4>
                        # callbacks=[ModelCheckpoint('../checkpoints/small_model_epoch_{epoch}.h5')]
                        callbacks=[ModelCheckpoint('../checkpoints/small_model_epoch_{epoch}.h5')]
                        )  # <5>

    model.evaluate_generator(generator=test_generator.generate(batch_size, num_classes),
                             steps=test_generator.get_num_samples() / batch_size)  # <6>


