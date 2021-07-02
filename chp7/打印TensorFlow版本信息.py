
import os
import tensorflow as tf
from tensorflow.python.client import device_lib
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "99"

if __name__ == "__main__":
    print(tf.__version__)

    print(device_lib.list_local_devices())
    print(tf.test.is_gpu_available())



# import torch
# print(torch.__version__)
#
# print(torch.version.cuda)
# print(torch.backends.cudnn.version())





# import os
# import pygame,sys
#
# pygame.init()
# size = width,height = 600,400
# speed = [1,1]
# BLACK = 0,0,0
# screen = pygame.display.set_mode(size)
# pygame.display.set_caption("qiouqiu")
#
#
# ball = pygame.image.load("C:\\Users\\intel\\Desktop\\PYG02-ball.gif")
#
#
# ballrect = ball.get_rect()
#
# while  True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             sys.exit()
#     ballrect = ballrect.move(speed[0],speed[1])
#     if ballrect.left < 0 or ballrect.right > width:
#         speed[0] = -speed[0]
#     if ballrect.top < 0 or ballrect.bottom > height:
#         speed[1] = -speed[1]
#     screen.fill(BLACK)
#     screen.blit(ball,ballrect)
#     pygame.display.update()
#
#
#
#
#
#
#
#
#
#
