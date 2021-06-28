import os

from flask import Flask  # Flask是一个使用 Python 编写的轻量级 Web 应用框架
from flask import jsonify
from flask import request

import dlgo
from dlgo import agent
from dlgo import goboard_fast as goboard
from dlgo.utils import point_from_coords
from dlgo.utils import point_from_coords

__all__ = [
    'get_web_app',
]


def get_web_app(bot_map):  # 创建一个用于服务机器人的网络应用程序。
    """Create a flask application for serving bot moves.
    The bot_map maps from URL path fragments to Agent instances.
    The /static path will return some static content (including the
    jgoboard JS).
    Clients can get the post move by POSTing json to
    /select-move/<bot name>
    客户可以通过将 JSON POST 到 select-move<bot name> 来获取帖子移动
    Example:
    # >>> myagent = dlgo.agent.navie.RandomBot() # 例化代理类型
    # >>> web_app = get_web_app({'random': myagent})
    # >>> web_app.run()
    Returns: Flask application instance
    """
    here = os.path.dirname(__file__)  # 返回当前.py脚本的路径
    static_path = os.path.join(here, 'static') # 连接两个或更多的路径名组件   测试实验见语法测试
    # static_path ='\httpfrontend\static'
    app = Flask(__name__, static_folder=static_path, static_url_path='/static')
    # Flask是一个使用 Python 编写的轻量级 Web 应用框架

    # Flask–路由
    # ' ' :访问地址
    # .methods = [ ]: 当前url地址,允许访问的请求方式 类型为可迭代对象,允许八种http请求方式

    @app.route('/select-move/<bot_name>', methods=['POST'])
    def select_move(bot_name):
        content = request.json
        board_size = content['board_size']
        game_state = goboard.GameState.new_game(board_size)
        # Replay the game up to this point.
        for move in content['moves']:
            if move == 'pass':
                next_move = goboard.Move.pass_turn()
            elif move == 'resign':
                next_move = goboard.Move.resign()
            else:
                next_move = goboard.Move.play(point_from_coords(move))
            game_state = game_state.apply_move(next_move)
        bot_agent = bot_map[bot_name]
        bot_move = bot_agent.select_move(game_state)
        if bot_move.is_pass:
            bot_move_str = 'pass'
        elif bot_move.is_resign:
            bot_move_str = 'resign'
        else:
            bot_move_str = point_from_coords(bot_move.point)
        return jsonify({
            'bot_move': bot_move_str,
            'diagnostics': bot_agent.diagnostics()
        })

    return app

# 访问地址 : http://127.0.0.1:5000/info/1


