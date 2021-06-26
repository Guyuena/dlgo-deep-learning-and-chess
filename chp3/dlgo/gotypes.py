# tag::enumimport[]
import enum
# end::enumimport[]
# tag::namedtuple[]
from collections import namedtuple
# end::namedtuple[]
__all__ = [
    'Player',
    'Point',
]


# tag::color[]
class Player(enum.Enum):
    black = 1
    white = 2

    # 既要保护类的封装特性，又要让开发者可以使用“对象.属性”的方式操作操作类属性，除了使用
    # property()函数，Python还提供了 @ property装饰器。通过 @ property
    # 装饰器，可以直接通过方法名来访问方法，不需要在方法名后添加一对“（）”小括号。
    @property
    def other(self):  # 对方棋手 执黑执白
        return Player.black if self == Player.white else Player.white
# end::color[]


# tag::points[]
class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
# end::points[]

    def __deepcopy__(self, memodict={}):
        # These are very immutable.
        return self