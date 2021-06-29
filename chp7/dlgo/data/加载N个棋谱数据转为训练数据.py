
from dlgo.data.processor import GoDataProcessor



if __name__ == '__main__':
    processor = GoDataProcessor()
    features, labels = processor.load_go_data('train', 100)   # 在data文件夹里面得到名字为features_train.npy和 label_train.npy的特征与标签数据