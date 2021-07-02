from __future__ import print_function
from __future__ import absolute_import
import os
import glob
import os.path
import tarfile
import gzip
import shutil
import numpy as np
import multiprocessing  # 多处理库
#from os import sys
import sys
from os import system
# from keras.utils import to_categorical
from tensorflow.keras.utils import to_categorical

from dlgo.gosgf import Sgf_game
from dlgo.goboard_fast import Board, GameState, Move
from dlgo.gotypes import Player, Point
from dlgo.data.index_processor import KGSIndex
from dlgo.data.sampling import Sampler
from dlgo.data.generator import DataGenerator
from dlgo.encoders.base import get_encoder_by_name


def worker(jobinfo):
    try:
        clazz, encoder, zip_file, data_file_name, game_list = jobinfo
        clazz(encoder=encoder).process_zip(zip_file, data_file_name, game_list)
    except (KeyboardInterrupt, SystemExit):
        raise Exception('>>> Exiting child process.')


class GoDataProcessor:
    def __init__(self, encoder='simple', data_directory='data'):
        self.encoder_string = encoder
        self.encoder = get_encoder_by_name(encoder, 19)
        self.data_dir = data_directory

    # 您将实现主要的数据处理方法，称为load_go_data。在此方法中，您可以指定要处理的游戏数量以及要加载的数据类型
    # 即训练或测试数据。load_go_data将从KGS中下载在线游戏记录，对指定数量的游戏进行采样，
    # 通过创建功能和标签进行处理，然后将结果持久化到本地作为NumPy数组。

# tag::load_generator[]
    # 加载游戏训练数据
    # data_type，您可以选择train或test,num_samples是指从数据中加载的数目
    def load_go_data(self, data_type='train', num_samples=1000,
                     use_generator=False):
        index = KGSIndex(data_directory=self.data_dir)
        index.download_files()

        sampler = Sampler(data_dir=self.data_dir)
        # 采样指定数据类型和指定数量的对局记录。
        data = sampler.draw_data(data_type, num_samples)

        # 将加载工作送到CPU
        self.map_to_workers(data_type, data)  # <1>  将工作负载映射到多个CPU进程中
        # 根据选择返回生成器和数据集
        if use_generator:
            generator = DataGenerator(self.data_dir, data)
            return generator  # <2>
        else:
            features_and_labels = self.consolidate_games(data_type, data)
            return features_and_labels  # <3>

# <1> Map workload to CPUs
# <2> Either return a Go data generator...
# <3> ... or return consolidated data as before.
# end::load_generator[]
    # 解压数据
    def unzip_data(self, zip_file_name):
        this_gz = gzip.open(self.data_dir + '/' + zip_file_name)
        # 去掉后缀gz
        tar_file = zip_file_name[0:-3]
        this_tar = open(self.data_dir + '/' + tar_file, 'wb')
        # 将解压文件的内容复制到"tar"文件中
        shutil.copyfileobj(this_gz, this_tar)
        this_tar.close()
        return tar_file

    # 将压缩文件进行处理，得到特征和标签，game_list里存该zip文件夹下所有sgf文件下标
    def process_zip(self, zip_file_name, data_file_name, game_list):
        tar_file = self.unzip_data(zip_file_name)
        zip_file = tarfile.open(self.data_dir + '/' + tar_file)
        # 获得该zip下的所有文件名
        name_list = zip_file.getnames()
        # 确定此压缩文件中落子总数，也就对应数据总数
        total_examples = self.num_total_examples(zip_file, game_list, name_list)
        # 从您使用的编码器中推断特征和标签的形状，即(1,19,19)
        shape = self.encoder.shape()
        # 把数据总数插入到shape数组的第一个，这样的思维数组有几个三维数组，即代表有几局盘面，而每个三维数组都是经过编码后的单平面形状
        feature_shape = np.insert(shape, 0, np.asarray([total_examples]))
        features = np.zeros(feature_shape)
        # 一个局面对应一个标签，所以有几局就有几个标签
        labels = np.zeros((total_examples,))

        # 用于特征和标签的下标
        counter = 0
        for index in game_list:        # 遍历每个文件
            name = name_list[index + 1]
            if not name.endswith('.sgf'):
                raise ValueError(name + ' is not a valid sgf')
            """读取该文件内容 sgf_content  """
            sgf_content = zip_file.extractfile(name).read()    # 读取该文件内容
            # 使用from_string方法，根据文件内容创建一个Sgf_game
            # 可以复盘棋局
            sgf = Sgf_game.from_string(sgf_content)
            # 得到初始游戏状态
            game_state, first_move_done = self.get_handicap(sgf)
            # 遍历文件中的主要落子序列
            for item in sgf.main_sequence_iter():
                color, move_tuple = item.get_move()
                point = None
                if color is not None:
                    # 有落子
                    if move_tuple is not None:
                        row, col = move_tuple
                        point = Point(row + 1, col + 1)
                        move = Move.play(point)
                    # 玩家pass了
                    else:
                        move = Move.pass_turn()
                    #如果第一步下了的话，就把之前的局面和下的一步编码后加入到特征和标签数组里
                    if first_move_done and point is not None:
                        features[counter] = self.encoder.encode(game_state)
                        labels[counter] = self.encoder.encode_point(point)
                        counter += 1
                    game_state = game_state.apply_move(move)
                    first_move_done = True
        # 将特征矩阵和标签矩阵存入到文件中
        feature_file_base = self.data_dir + '/' + data_file_name + '_features_%d'
        label_file_base = self.data_dir + '/' + data_file_name + '_labels_%d'
        # 由于文件包含大量内容，因此在chunksize之后拆分
        chunk = 0  # Due to files with large content, split up after chunksize
        chunksize = 1024
        # 将数据总数按1024进行分割，每个分块都存到单独地的文件中
        while features.shape[0] >= chunksize:
            feature_file = feature_file_base % chunk
            label_file = label_file_base % chunk
            chunk += 1
            # 当前的块与功能和标签被切断...
            current_features, features = features[:chunksize], features[chunksize:]
            current_labels, labels = labels[:chunksize], labels[chunksize:]
            # 然后存储在一个单独的文件中，每个文件中存储1024个的数据
            np.save(feature_file, current_features)
            np.save(label_file, current_labels)

    # 合并所有数组成一个
    def consolidate_games(self, name, samples):
        files_needed = set(file_name for file_name, index in samples)
        file_names = []
        for zip_file_name in files_needed:
            file_name = zip_file_name.replace('.tar.gz', '') + name
            file_names.append(file_name)

        feature_list = []
        label_list = []
        for file_name in file_names:
            file_prefix = file_name.replace('.tar.gz', '')
            base = self.data_dir + '/' + file_prefix + '_features_*.npy'
            for feature_file in glob.glob(base):
                label_file = feature_file.replace('features', 'labels')
                x = np.load(feature_file)
                y = np.load(label_file)
                x = x.astype('float32')
                y = to_categorical(y.astype(int), 19 * 19)
                feature_list.append(x)
                label_list.append(y)

        features = np.concatenate(feature_list, axis=0)
        labels = np.concatenate(label_list, axis=0)

        feature_file = self.data_dir + '/' + name
        label_file = self.data_dir + '/' + name

        np.save(feature_file, features)
        np.save(label_file, labels)

        return features, labels

    # 获取让子（可能没让子）的初始棋盘状态,让子后表示黑棋已经让出先行权，因此first_move_done为true
    @staticmethod
    def get_handicap(sgf):  # Get handicap stones
        go_board = Board(19, 19)
        first_move_done = False
        move = None
        game_state = GameState.new_game(19)
        # 有让子就加上让的棋子
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            for setup in sgf.get_root().get_setup_stones():
                for move in setup:
                    row, col = move
                    go_board.place_stone(Player.black, Point(row + 1, col + 1))  # black gets handicap
            first_move_done = True
            game_state = GameState(go_board, Player.white, None, move)
        return game_state, first_move_done

    def map_to_workers(self, data_type, samples):
        zip_names = set()
        indices_by_zip_name = {}
        for filename, index in samples:
            zip_names.add(filename)
            if filename not in indices_by_zip_name:
                indices_by_zip_name[filename] = []
            indices_by_zip_name[filename].append(index)

        zips_to_process = []
        for zip_name in zip_names:
            base_name = zip_name.replace('.tar.gz', '')
            data_file_name = base_name + data_type
            if not os.path.isfile(self.data_dir + '/' + data_file_name):
                zips_to_process.append((self.__class__, self.encoder_string, zip_name,
                                        data_file_name, indices_by_zip_name[zip_name]))
        "----------------多线程----------------"
        "----------------多线程----------------"
        "----------------多线程----------------"
        "----------------多线程----------------"
        cores = multiprocessing.cpu_count()  # Determine number of CPU cores and split work load among them
        # pool = multiprocessing.Pool(processes=cores)
        pool = multiprocessing.Pool(processes=4)
        p = pool.map_async(worker, zips_to_process)
        try:
            _ = p.get()
        except KeyboardInterrupt:  # Caught keyboard interrupt, terminating workers
            pool.terminate()
            pool.join()
            sys.exit(-1)  # 初始
            # system.exit(-1) # 修改后

    def num_total_examples(self, zip_file, game_list, name_list):
        total_examples = 0
        for index in game_list:
            name = name_list[index + 1]
            # 后缀名是.sgf
            if name.endswith('.sgf'):
                # 读取sgf文件里的内容
                sgf_content = zip_file.extractfile(name).read()
                # 根据内容创建Sgf_game
                sgf = Sgf_game.from_string(sgf_content)
                game_state, first_move_done = self.get_handicap(sgf)
                # 只计算真正落子的数目
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