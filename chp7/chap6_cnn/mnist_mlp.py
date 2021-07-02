from __future__ import print_function

# tag::mnist_mlp_imports[]
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense
# end::mnist_mlp_imports[]


# tag::mnist_mlp_preprocessing[]
"""使用Keras加载和预处理mnist数据"""
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

y_train = keras.utils.to_categorical(y_train, 10)
y_test = keras.utils.to_categorical(y_test, 10)
# end::mnist_mlp_preprocessing[]

# tag::mnist_mlp_model[]
"""搭建顺序模型"""
model = Sequential()
model.add(Dense(392, activation='sigmoid', input_shape=(784,)))
model.add(Dense(196, activation='sigmoid'))
model.add(Dense(10, activation='sigmoid'))
model.summary()
# end::mnist_mlp_model[]

# tag::mnist_mlp_model_compile[]
"""编译Keras深度学习模型"""
model.compile(loss='mean_squared_error',
              optimizer='sgd',
              metrics=['accuracy'])
# tag::mnist_mlp_model_compile[]

# tag::mnist_mlp_fit_eval[]
"""训练和评估Keras模型"""
model.fit(x_train, y_train,
          batch_size=128,
          epochs=20)
score = model.evaluate(x_test, y_test)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
# end::mnist_mlp_fit_eval[]
