import enum
from collections import namedtuple
"""
    因为元组的局限性：不能为元组内部的数据进行命名，所以往往我们并不知道一个元组所要表达的意义，
    所以在这里引入了 collections.namedtuple 这个工厂函数，来构造一个带字段名的元组
"""

"""
  2021-06-17
  player类  落子回合
"""


# 执白执黑

class Player(enum.Enum):  # 黑白棋手
    black = 1
    white = 2
    '''
     返回对方棋子颜色，如果本方是白棋，那就返回Player.black
    '''
    @property
    def other(self):
        return Player.black if self == Player.white else Player.white


# 棋盘坐标
# nametuple命名元组，就可以在访问交叉点的具体坐标，用Point.row和Point.col替代point[0]和point[1]
# 行rows：Y (height) 列cols：X (width)
# 新建元组类的一个子类名Point， Point这个子类有两个属性值 row，col， 就可以在后面使用中例化Point对象，并读取器属性值
class Point(namedtuple('Point', 'row col')):   # 定义一个namedtuple类型：Point  Point元组的属性：row和col ，也就是坐标位置
    def neighbors(self):  # 定义一个查询交叉点Point的所有相邻点的方法
        """
        返回当前点的相邻点，也就是相对于当前点的上下左右四个点
        """
        return [
            Point(self.row - 1, self.col),  # point点的下面的邻点
            Point(self.row + 1, self.col),  # point点的上面的邻点
            Point(self.row, self.col - 1),  # point点的左面的邻点
            Point(self.row, self.col + 1)   # point点的右面的邻点
        ]

    # 第三章书上没有添加
    def __deepcopy__(self, memodict={}):  # 深度拷贝
        # These are very immutable.
        return self