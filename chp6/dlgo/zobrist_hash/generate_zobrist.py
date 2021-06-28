# tag::generate_zobrist[]
import random

from dlgo.gotypes import Player, Point

"""
    哈希函数指将哈希表中元素的关键键值映射为元素存储位置的函数

    哈希表中元素是由哈希函数确定的。将数据元素的关键字K作为自变量，通过一定的函数关系（称为哈希函数），计算出的值，即为该元素的存储地址。表示为：
    Addr = H（key）
"""


def to_python(player_state):
    if player_state is None:
        return 'None'
    if player_state == Player.black:
        return Player.black
    return Player.white


# 生成哈希值
MAX63 = 0x7fffffffffffffff  # 64位数

table = {}
empty_board = 0
for row in range(1, 20):
    for col in range(1, 20):
        for state in (Player.black, Player.white):
            code = random.randint(0, MAX63)
            table[Point(row, col), state] = code

print('from .gotypes import Player, Point')
print('')
print("__all__ = ['HASH_CODE', 'EMPTY_BOARD']")
print('')
print('HASH_CODE = {')
for (pt, state), hash_code in table.items():
    print('    (%r, %s): %r,' % (pt, to_python(state), hash_code))
print('}')
print('')
print('EMPTY_BOARD = %d' % (empty_board,))
# end::generate_zobrist[]
