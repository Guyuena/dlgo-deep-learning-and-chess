# 从SGF文件中重放游戏记录。原来的SGF文件编码游戏移动与字符串，
# 如B[ee]。Sgf_game类解码这些字符串并将它们作为Python元组返回。
# 你就可以将这些落子应用到GameState对象以重建游戏


from __future__ import print_function
from __future__ import absolute_import
import os
import glob
import os.path
import tarfile
import gzip
import shutil
import time

import numpy as np
import multiprocessing  # 多处理库
#from os import sys
import sys
from os import system
# from keras.utils import to_categorical

import dlgo
from dlgo.gosgf.sgf import Sgf_game
from dlgo.goboard_fast import GameState, Move
from dlgo.gotypes import Point
from dlgo.utils import print_board

# 从SGF文件中重放游戏记录。原来的SGF文件编码游戏移动与字符串，如B[ee]。Sgf_game类解码这些字符串并将它们作为Python元组返回。
# 你就可以将这些落子应用到GameState对象以重建游戏

# 解压数据
def unzip_data(data_dir,zip_file_name):
    this_gz = gzip.open(data_dir + '/' + zip_file_name)
    # 去掉后缀gz
    tar_file = zip_file_name[0:-3]
    this_tar = open(data_dir + '/' + tar_file, 'wb')
    # 将解压文件的内容复制到"tar"文件中
    shutil.copyfileobj(this_gz, this_tar)
    this_tar.close()
    return tar_file

def process_zip_print_board( data_dir,zip_file_name):


    tar_file = unzip_data(data_dir,zip_file_name)
    zip_file = tarfile.open(data_dir + '/' + tar_file)
    # 获得该zip下的所有文件名
    name_list = zip_file.getnames()  # 压缩包里面的所有文件
    print(name_list)
    name = name_list[1]  # 只复盘了第一个sgf棋盘


    if name.endswith('.sgf'):
        # 读取sgf文件里的内容

        sgf_content1 = zip_file.extractfile(name).read()
    sgf_content = sgf_content1
    sgf_game = Sgf_game.from_string(sgf_content)
    game_state = GameState.new_game(19)

    # 重复游戏的主要顺序，你忽略了棋局变化和评论
    for item in sgf_game.main_sequence_iter():
        # 这个主序列中的项是(颜色，落子)对，其中"落子"是一对坐标。

        color, move_tuple = item.get_move()
        if color is not None and move_tuple is not None:
           row, col = move_tuple
           point = Point(row + 1, col + 1)
           print(point)
           move = Move.play(point)
           # 将读出的落子应用到棋盘上
           game_state = game_state.apply_move(move)
           time.sleep(0)  # 延时
           print_board(game_state.board)

if __name__ == '__main__':
    dir = 'data'  # 路径
    filename = 'KGS-2001-19-2298-.tar.gz'  # 哪个压缩包
    process_zip_print_board(dir, filename)