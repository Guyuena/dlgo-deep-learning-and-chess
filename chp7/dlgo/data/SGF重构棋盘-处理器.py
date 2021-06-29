from __future__ import absolute_import  # 加入绝对引用的特征

# tag::base_imports[]
# 数据文件处理工具包
import os.path
import tarfile
import gzip
import glob
import shutil

import numpy as np
from keras.utils import to_categorical
# end::base_imports[]

# tag::dlgo_imports[]
from dlgo.gosgf import Sgf_game  # 先从新的gosgf模块导入Sgf_game类
from dlgo.goboard_fast import Board, GameState, Move
from dlgo.gotypes import Player, Point
from dlgo.encoders.base import get_encoder_by_name

from dlgo.data.index_processor import KGSIndex
from dlgo.data.sampling import Sampler  # <1> # 从文件中采样训练和测试数据

# <1> Sampler will be used to sample training and test data from files.
# end::dlgo_imports[]

"   围棋数据处理器  "


# tag::processor_init[]
class GoDataProcessor:
    # 初始化，指定编码器和本地数据目录
    def __init__(self, encoder='oneplane', data_directory='data'):
        self.encoder = get_encoder_by_name(encoder, 19) # 构建编码器
        self.data_dir = data_directory  # sgf棋盘压缩包文件路径

    # end::processor_init[]

    """ 加载、处理和存储数据

     实现主要的数据处理方法，称为load_go_data。在此方法中，您可以指定要处理的游戏数量以及要加载的数据类型，即训练或测试数据。
     load_go_data将从KGS中下载在线游戏记录，对指定数量的游戏进行采样，通过创建功能和标签进行处理，然后将结果持久化到本地作为NumPy数组。
     process_zip() unzip_data() consolidate_games() get_handicap()  num_total_examples()
    """

    # tag::load_go_data[]
    "数据处理的主方法"
    # 数据加载
    def load_go_data(self, data_type='train',  # <1>  训练数据集还是测试数据集
                     num_samples=1000):  # <2> 加载的棋局数量
        # 在有提前下载好就这完成下载工作，下载了就不会再下载
        index = KGSIndex(data_directory=self.data_dir)  # 例化下载工具
        index.download_files()  # <3> 从KGS下载所有棋局数据，并保存到本地

        sampler = Sampler(data_dir=self.data_dir)  # 下载后，对下载下来的压缩包数据用采样器进行拆开
        # 将一部分数据划分为训练数据集
        data = sampler.draw_data(data_type, num_samples)  # <4> Sampler实例从数据中抽取指定数量棋局数据，并加载为指定的数据类型

        zip_names = set()  # 压缩文件的文件名集合
        indices_by_zip_name = {}  # 按压缩包名字索引 {}：字典
        for filename, index in data: # 在下载的数据库里面
            zip_names.add(filename)  # <5>收集数据中包含的所有压缩文件名，存放在一个列表中
            if filename not in indices_by_zip_name:  # 不在下载数据集里面
                indices_by_zip_name[filename] = []
            indices_by_zip_name[filename].append(index)  # <6> 按压缩文件名对所有sgf文件索引分组
        for zip_name in zip_names:
            " Python replace() 方法把字符串中的 old（旧字符串） 替换成 new(新字符串)，如果指定第三个参数max，则替换不超过 max 次"
            # .replace(old, new[, max])
            # old - - 将被替换的子字符串。
            # new - - 新字符串，用于替换old子字符串。
            # max - - 可选字符串, 替换不超过 max次
            base_name = zip_name.replace('.tar.gz', '')  # replace方法 去掉.tar.gz的压缩文件后缀
            data_file_name = base_name + data_type   # data_type='train' 训练集
            if not os.path.isfile(self.data_dir + '/' + data_file_name):  # 文件路径下没有这个文件名，就是先判断是否已存在该文件类型
                # 交给后续压缩包处理函数
                self.process_zip(zip_name, data_file_name, indices_by_zip_name[zip_name])  # <7>读出压缩文件，并单独处理每个压缩文件
                # process_zip -->

        features_and_labels = self.consolidate_games(data_type, data)  # <8>  将每个压缩文件得到的特征和标签进行整合并返回
        return features_and_labels

    # <1> As `data_type` you can choose either 'train' or 'test'.
    # <2> `num_samples` refers to the number of games to load data from.
    # <3> We download all games from KGS to our local data directory. If data is available, it won't be downloaded again.
    # <4> The `Sampler` instance selects the specified number of games for a data type.
    # <5> We collect all zip file names contained in the data in a list.
    # <6> Then we group all SGF file indices by zip file name.
    # <7> The zip files are then processed individually.
    # <8> Features and labels from each zip are then aggregated and returned.
    # end::load_go_data[]

    # tag::unzip_data[]
    def unzip_data(self, zip_file_name):
        # 打开gzip压缩包  xxx.gz
        this_gz = gzip.open(self.data_dir + '/' + zip_file_name)  # <1>
        # 去掉 .gz文件后缀    xxx.tar.gz 去掉 .gz后就变为 xxx.tar文件
        tar_file = zip_file_name[0:-3]  # <2> 将 `gz` 文件解压为 `tar` 文件。
        # 内置文件IO函数 open()
        # open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
        this_tar = open(self.data_dir + '/' + tar_file, 'wb')  # 以二进制格式打开一个文件用于读写
        # '/' 文件路径子目录分割符 (self.data_dir + '/' + tar_file) 就是函数的参数的file参数

        "shutil.copyfileobj(fsrc, fdst[, length])：复制文件内容（不包含元数据）从类文件对象src到类文件对dst"
        shutil.copyfileobj(this_gz, this_tar)  # <3>
        this_tar.close()  # 文件关闭
        return tar_file  # 返回 xxx.tar文件

    # <1> Unpack the `gz` file into a `tar` file.
    # <2> Remove ".gz" at the end to get the name of the tar file.
    # <3> Copy the contents of the unpacked file into the `tar` file.
    # end::unzip_data[]

    # tag::read_sgf_files[]
    """
    1、调用unzip_data解压当前文件
    2、初始化一个Encoder实例来编码SGF文件
    3、初始化形状合理的特征和标签Numpy数组
    4、迭代遍历棋局列表，并逐个处理棋局数据
    5、每一局开始前先布置全部让子
    6、读出SGF棋谱中每一个动作
    7、将每一回合的下一步动作编码为label
    8、将每一回合的当前棋局状态编码为feature
    9、将下一步动作执行到棋盘上并继续
    10、在本地文件系统中分块存储特征与标签
    """

    def process_zip(self, zip_file_name, data_file_name, game_list):
        tar_file = self.unzip_data(zip_file_name)  # 先得到一个 xxx.tar压缩文件
        # tarFile类对于就是tar压缩包实例
        " tarfile.open(): 打开tar文件，返回TarFile路径名name的对象"
        zip_file = tarfile.open(self.data_dir + '/' + tar_file)
        # 获得tar文件的文件名，以列表形式返回
        # name_list 文件名列表
        name_list = zip_file.getnames()
        total_examples = self.num_total_examples(zip_file, game_list, name_list)  # <1> 此压缩文件中所有棋局的总动作数量

        shape = self.encoder.shape()  # <2> 根据编码器推断特征与标签的形状  平面数、宽、高
        feature_shape = np.insert(shape, 0, np.asarray([total_examples]))
        features = np.zeros(feature_shape)  # 特征数组
        labels = np.zeros((total_examples,))  # 标签数组

        counter = 0
        for index in game_list:
            name = name_list[index + 1]
            if not name.endswith('.sgf'):
                raise ValueError(name + ' is not a valid sgf')
            # 提取文件内容  先extractfile(name)提取文件，在read()读取文件内容
            sgf_content = zip_file.extractfile(name).read()

            # Sgf_game类，定义在gosgf目录下的sgf.py  Sgf_game类负责对这些字符串解码，并返回成python元组
            # 根据读取的 sgf_content sgf数据来搭建Sgf_game实例
            sgf = Sgf_game.from_string(sgf_content)  # <3>解压文件后，将SGF内容读取为字符串

            game_state, first_move_done = self.get_handicap(sgf)  # <4>布置所有让子，得到开局状态

            for item in sgf.main_sequence_iter():  # <5>遍历SGF文件中的所有动作
                # 这个主序列中的项是(颜色，落子)对，其中"落子"是一对坐标
                color, move_tuple = item.get_move()  # 返回值类型为一个元组
                point = None
                if color is not None:
                    if move_tuple is not None:  # <6>读取落子坐标
                        row, col = move_tuple
                        point = Point(row + 1, col + 1)
                        move = Move.play(point)
                    else:
                        move = Move.pass_turn()  # <7> 没落子，跳过
                    if first_move_done and point is not None:
                        features[counter] = self.encoder.encode(game_state)  # <8> 当前游戏状态编码为特征
                        labels[counter] = self.encoder.encode_point(point)  # <9> 将下一步动作编码为特征的标签label
                        counter += 1
                    game_state = game_state.apply_move(move)  # <10> 将落子动作执行到棋盘上，然后继续下一回合
                    first_move_done = True
        # <1> Determine the total number of moves in all games in this zip file.
        # <2> Infer the shape of features and labels from the encoder we use.
        # <3> Read the SGF content as string, after extracting the zip file.
        # <4> Infer the initial game state by applying all handicap stones.
        # <5> Iterate over all moves in the SGF file.
        # <6> Read the coordinates of the stone to be played...
        # <7> ... or pass, if there is none.
        # <8> We encode the current game state as features...
        # <9> ... and the next move as label for the features.
        # <10> Afterwards the move is applied to the board and we proceed with the next one.
        # end::read_sgf_files[]

        # tag::store_features_and_labels[]
        "将特征与标签分块存储在本地"
        #  设置特征、标签文件名
        feature_file_base = self.data_dir + '/' + data_file_name + '_features_%d'
        label_file_base = self.data_dir + '/' + data_file_name + '_labels_%d'

        chunk = 0  # Due to files with large content, split up after chunksize
        chunksize = 1024
        while features.shape[0] >= chunksize:  # <1> 分块处理特征与标签时，以1024为一个批次
            feature_file = feature_file_base % chunk
            label_file = label_file_base % chunk
            chunk += 1
            current_features, features = features[:chunksize], features[chunksize:]
            current_labels, labels = labels[:chunksize], labels[chunksize:]  # <2>  把当前的分块从feature和label中分割出来
            np.save(feature_file, current_features)
            np.save(label_file, current_labels)  # <3> 存储但单独的文件中

    # <1> We process features and labels in chunks of size 1024.
    # <2> The current chunk is cut off from features and labels...
    # <3> ...  and then stored in a separate file.
    # end::store_features_and_labels[]

    # tag::consolidate_games[]
    "将独立的特征与标签Numpy数组合并到一个集合中"

    def consolidate_games(self, data_type, samples):
        files_needed = set(file_name for file_name, index in samples)
        file_names = []  # 文件名列表
        for zip_file_name in files_needed:
            file_name = zip_file_name.replace('.tar.gz', '') + data_type  # replace() 去掉文件后缀
            file_names.append(file_name)

        feature_list = []  # 特征列表
        label_list = []  # 标签列表
        for file_name in file_names:
            file_prefix = file_name.replace('.tar.gz', '')
            base = self.data_dir + '/' + file_prefix + '_features_*.npy'  # 加上python的 .npy文件后缀
            #  glob.glob(): 返回所有匹配的文件路径列表。它只有一个参数pathname，定义了文件路径匹配规则，这里可以是绝对路径，也可以是相对路径。
            for feature_file in glob.glob(base):  # 把这个路径下的这个文件的文件名以一个列表的形式返回
                label_file = feature_file.replace('features', 'labels')
                x = np.load(feature_file)
                y = np.load(label_file)
                x = x.astype('float32')
                y = to_categorical(y.astype(int), 19 * 19)
                feature_list.append(x)
                label_list.append(y)
        features = np.concatenate(feature_list, axis=0)
        labels = np.concatenate(label_list, axis=0)
        # 保存到本地
        np.save('{}/features_{}.npy'.format(self.data_dir, data_type), features)
        np.save('{}/labels_{}.npy'.format(self.data_dir, data_type), labels)

        return features, labels

    # end::consolidate_games[]

    # tag::get_handicap[]
    @staticmethod
    # 用来获取当前棋局规定的让子的数目，并将他们布置在空白棋盘上
    def get_handicap(sgf):
        go_board = Board(19, 19)
        first_move_done = False
        move = None
        game_state = GameState.new_game(19)
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            for setup in sgf.get_root().get_setup_stones():
                for move in setup:
                    row, col = move
                    go_board.place_stone(Player.black, Point(row + 1, col + 1))
            first_move_done = True
            game_state = GameState(go_board, Player.white, None, move)
        return game_state, first_move_done

    # end::get_handicap[]

    # tag::num_total_examples[]
    # 计算每个压缩文件中可用的动作的总数，从而用来确定特征与标签数组的尺寸
    def num_total_examples(self, zip_file, game_list, name_list):
        total_examples = 0
        for index in game_list:
            name = name_list[index + 1]
            if name.endswith('.sgf'):
                sgf_content = zip_file.extractfile(name).read()
                sgf = Sgf_game.from_string(sgf_content)
                game_state, first_move_done = self.get_handicap(sgf)

                num_moves = 0
                for item in sgf.main_sequence_iter():
                    color, move = item.get_move()
                    if color is not None:
                        if first_move_done:
                            num_moves += 1
                        first_move_done = True
                total_examples = total_examples + num_moves
            else:
                raise ValueError(name + ' is not a valid sgf')
        return total_examples
# end::num_total_examples[]