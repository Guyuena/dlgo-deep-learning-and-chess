import h5py
from dlgo.httpfrontend import get_web_app
from dlgo.agent.predict_diy import DeepLearningAgent, load_prediction_agent


model_file = h5py.File("./deep_robot.h5","r")   # 加载训练的代理人网络模型
robot_from_file = load_prediction_agent(model_file)  # .h5文件解析
web_app = get_web_app({'predict_diy': robot_from_file})  # web部署
web_app.run()