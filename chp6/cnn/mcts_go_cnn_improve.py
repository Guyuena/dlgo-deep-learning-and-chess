from __future__ import print_function

# tag::mcts_go_cnn_simple_preprocessing[]
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D

"加入Conv2D"
"按书上的源码来，加入了池化层，dropout失活层"
np.random.seed(123)
# X = np.load('features.npy')
# Y = np.load('labels.npy')
X = np.load('../generate_games/features-200.npy')  # 将数据加载到numpy数组中
# 加载标签(当前局面的落子）
Y = np.load('../generate_games/labels-200.npy')
samples = X.shape[0]
size = 9
input_shape = (size, size, 1)  # <2>
X = X.reshape(samples, size, size, 1)  # <3>
train_samples = int(0.9*samples)
X_train, X_test = X[:train_samples], X[train_samples:]
Y_train, Y_test = Y[:train_samples], Y[train_samples:]

# <1> We import two new layers, a 2D convolutional layer and one that flattens its input to vectors.
# <2> The input data shape is 3-dimensional, we use one plane of a 9x9 board representation.
# <3> We then reshape our input data accordingly.
# end::mcts_go_cnn_simple_preprocessing[]

# tag::mcts_go_cnn_simple_model[]
"网络搭建"
# 书上源码
model = Sequential()
# 第一层
model.add(Conv2D(filters=48,  # <1>
                 kernel_size=(3, 3),  # <2>
                 activation='sigmoid',
                 padding='same',
                 input_shape=input_shape))
# 第二层
model.add(Dropout(rate=0.5)) # dropout 丢弃，通过丢弃神经元对网络进行正则化  指定丢弃率 rate
model.add(Conv2D(48, (3, 3), padding='same', activation='relu'))  #  卷积
model.add(MaxPooling2D(pool_size=(2, 2)))  # 池化
model.add(Dropout(rate=0.5))  # dropout层
model.add(Flatten())  # 展平
model.add(Dense(512, activation='relu'))  # 稠密层
model.add(Dropout(rate=0.5))  # dropout层
model.add(Dense(size * size, activation='sigmoid'))  # <5>
model.summary()

model.compile(loss='mean_squared_error',
              optimizer='sgd',
              metrics=['accuracy'])

model.fit(X_train, Y_train,
          batch_size=64,
          epochs=50,
          verbose=1,
          validation_data=(X_test, Y_test))

score = model.evaluate(X_test, Y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
# end::mcts_go_cnn_eval[]


"尝试预测"
# 表示棋盘的矩阵
test_board = np.array([[
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, -1, 1, -1, 0, 0, 0, 0,
    0, 1, -1, 1, -1, 0, 0, 0, 0,
    0, 0, 1, -1, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
]])

test_board = test_board.reshape(1, size, size, 1)

# 输出一个棋盘局面下的预测值
move_prob = model.predict(test_board)[0]
i = 0
for row in range(9):
    row_formatted = []
    for cow in range(9):
        row_formatted.append('{:.3f}'.format(move_prob[i]));
        i += 1
    print(' '.join(row_formatted))
