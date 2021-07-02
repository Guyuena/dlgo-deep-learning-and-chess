from __future__ import print_function

# tag::mcts_go_cnn_preprocessing[]

# """加载并预处理先前存储的围棋棋谱数据"""
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D

np.random.seed(123)  # 设置一个固定的随机种子，以确保这个脚本可以严格重现

# 加载特征(就是局面)
X = np.load('../generate_games/features-200.npy')  # 将数据加载到numpy数组中

# 加载标签(当前局面的落子）
Y = np.load('../generate_games/labels-200.npy')

# X.shape == n * board_size * board_size
samples = X.shape[0]

"""书上的源码，与作者修改后的有些不一样"""
board_size = 9 * 9

# 输入数据形状是三维的；您使用一个平面表示9×9的棋盘
X = X.reshape(samples, board_size)
Y = Y.reshape(samples, board_size)
train_samples = int(0.9 * samples)

# 拿出90%用来训练,10%用于测试
X_train, X_test = X[:train_samples], X[train_samples:]
Y_train, Y_test = Y[:train_samples], Y[train_samples:]

# """下面注释的代码是作者的源码"""
# size = 9
# input_shape = (size, size, 1)
#
# X = X.reshape(samples, size, size, 1)
#
# train_samples = 10000
# X_train, X_test = X[:train_samples], X[train_samples:]
# Y_train, Y_test = Y[:train_samples], Y[train_samples:]
# end::mcts_go_cnn_preprocessing[]

# tag::mcts_go_cnn_model[]
# """在生成的围棋棋谱数据上运行Keras多层感知机"""
# 下面是书上源码
model = Sequential()
model.add(Dense(1000, activation='sigmoid', input_shape=(board_size,)))
model.add(Dense(500, activation='sigmoid'))
model.add(Dense(board_size, activation='sigmoid'))
model.summary()

model.compile(loss='mean_squared_error',
              optimizer='sgd',
              metrics=['accuracy'])  # accuracy指标用来度量模型得分最高的预测输出与数据真实标签之间匹配的频率
# 该accuracy就是大家熟知的最朴素的accuracy。比如我们有6个样本，其真实标签y_true为[0, 1, 3, 3, 4, 2]，
# 但被一个模型预测为了[0, 1, 3, 4, 4, 4]，即y_pred=[0, 1, 3, 4, 4, 4]，那么该模型的accuracy=4/6=66.67%。

model.fit(X_train, Y_train,
          batch_size=64,
          epochs=5,
          verbose=1,
          validation_data=(X_test, Y_test))

# 评分包括损失值和你的精确值
score = model.evaluate(X_test, Y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

# "评估这个模型"
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


# 输出一个棋盘局面下的预测值
move_prob = model.predict(test_board)[0]
i = 0
for row in range(9):
    row_formatted = []
    for cow in range(9):
        row_formatted.append('{:.3f}'.format(move_prob[i]));
        i += 1
    print(' '.join(row_formatted))









# """下面注释的是作者的GitHub源码"""
# model = Sequential()
# model.add(Conv2D(32, kernel_size=(3, 3),
#                  activation='relu',
#                  input_shape=input_shape))
# model.add(Dropout(rate=0.6))
# model.add(Conv2D(64, (3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(rate=0.6))
# model.add(Flatten())
# model.add(Dense(128, activation='relu'))
# model.add(Dropout(rate=0.6))
# model.add(Dense(size * size, activation='softmax'))
# model.summary()
#
# model.compile(loss='categorical_crossentropy',
#               optimizer='sgd',
#               metrics=['accuracy'])
# # end::mcts_go_cnn_model[]
#
# # tag::mcts_go_cnn_eval[]
# model.fit(X_train, Y_train,
#           batch_size=64,
#           epochs=5,
#           verbose=1,
#           validation_data=(X_test, Y_test))
# score = model.evaluate(X_test, Y_test, verbose=0)
# print('Test loss:', score[0])
# print('Test accuracy:', score[1])
# # end::mcts_go_cnn_eval[]
