from dlgo.agent.navie import RandomBot
from dlgo.httpfrontend.server import get_web_app
# from dlgo.agent.predict_diy import DeepLearningAgent
from dlgo.agent.predict import DeepLearningAgent
random_agent = RandomBot()  # 随机代理
web_app = get_web_app({'random':random_agent})  # 加载机器人并开启网络服务
web_app.run()



# 使用 Keras神经网络模型训练模型和编码器来建立 DeeplearningAgent()代理注册到web应用
# model =   # 网络模型
# encoder =  # 编码器类型
# random_agent = DeepLearningAgent(model,encoder)
# web_app = get_web_app({'random':random_agent})
# web_app.run()