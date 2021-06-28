from __future__ import print_function

# tag::mcts_go_cnn_preprocessing[]

"""加载并预处理先前存储的围棋棋谱数据"""
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D

np.random.seed(123)  # 设置一个固定的随机种子，以确保这个脚本可以严格重现

X = np.load('../generate_games/features-200.npy')  # 将数据加载到numpy数组中
Y = np.load('../generate_games/labels-200.npy')

# X.shape == n * board_size * board_size
samples = X.shape[0]


"""书上的源码，与作者修改后的有些不一样"""
board_size = 9 * 9
X = X.reshape(samples, board_size)
Y = Y.reshape(samples, board_size)
train_samples = int(0.9 * samples)
X_train, X_test = X[:train_samples], X[train_samples:]
Y_train, Y_test = Y[:train_samples], Y[train_samples:]


"""下面注释的代码是作者的源码"""
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
"""在生成的围棋棋谱数据上运行Keras多层感知机"""
# 下面是书上源码
model = Sequential()
model.add(Dense(1000, activation='sigmoid',input_shape=(board_size,)))
model.add(Dense(500, activation='sigmoid'))
model.add(Dense(board_size, activation='sigmoid'))
model.summary()

model.compile(loss='mean_squared_error',
              optimize='sgd',
              metrics=['accuracy'])

model.fit(X_train, Y_train,
          batch_size=64,
          epochs=15,
          verbose=1,
          validation_data=(X_test,Y_test))

# 评分包括损失值和你的精确值
score = model.evaluate(X_test, Y_test,verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])


"""下面注释的是作者的GitHub源码"""
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
