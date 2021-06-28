# tag::data_generator[]
import glob
import numpy as np
from keras.utils import to_categorical

"""围棋数据生成器"""

class DataGenerator:
    def __init__(self, data_directory, samples):
        self.data_directory = data_directory
        self.samples = samples
        self.files = set(file_name for file_name, index in samples)  # <1>  生成器可以访问我们之前采样的一组文件
        self.num_samples = None

    def get_num_samples(self, batch_size=128, num_classes=19 * 19):  # <2> 根据应用程序，我们可能需要知道我们有多少样本。
        if self.num_samples is not None:
            return self.num_samples
        else:
            self.num_samples = 0
            for X, y in self._generate(batch_size=batch_size, num_classes=num_classes):
                self.num_samples += X.shape[0]
            return self.num_samples
# <1> Our generator has access to a set of files that we sampled earlier.
# <2> Depending on the application, we may need to know how many examples we have.
# end::data_generator[]

# tag::private_generate[]
    "私有化_generate方法"
    # 负责创建并返回批量数据
    def __generate(self, batch_size, num_classes):
        for zip_file_name in self.files:
            file_name = zip_file_name.replace('.tar.gz', '') + 'train'
            base = self.data_directory + '/' + file_name + '_features_*.npy'
            for feature_file in glob.glob(base):
                label_file = feature_file.replace('features', 'labels')
                x = np.load(feature_file)
                y = np.load(label_file)
                x = x.astype('float32')
                y = to_categorical(y.astype(int), num_classes)
                while x.shape[0] >= batch_size:
                    x_batch, x = x[:batch_size], x[batch_size:]
                    y_batch, y = y[:batch_size], y[batch_size:]
                    yield x_batch, y_batch  # <1>

# <1> We return or "yield" batches of data as we go.
# end::private_generate[]

# tag::generate[]
    """返回生成器的方法"""
    """yield构造的生成器"""
    # 外部通过调用generate()来构建生成器，而真正搭建生成器的是_generate()被私有化了，不能直接调用
    def generate(self, batch_size=128, num_classes=19 * 19):
        while True:
            for item in self.__generate(batch_size, num_classes):
                yield item
                # yield : 产出、产生、提供
                # 带有 yield 的函数在 Python 中被称之为 generator（生成器），何谓 generator ？
                # yield 的作用就是把一个函数变成一个generator，带有yield 的函数不再是一个普通函数，Python
                # 解释器会将其视为一个generator
# end::generate[]