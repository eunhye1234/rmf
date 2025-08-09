import numpy as np
from geometry_msgs.msg import Twist

class PIDController:
    def __init__(self, kp_ang, kp_lin, max_lin=0.3, max_ang=0.5):
        self.kp_ang = kp_ang
        self.kp_lin = kp_lin
        self.max_lin = max_lin
        self.max_ang = max_ang
    
    def compute(self, cx, cy, frame_shape):
        #frame_shape의 크기(높이, 너비, 채널)
        frame_cx = frame_shape[1] // 2
        frame_cy = frame_shape[0] // 2

        err_x = cx - frame_cx
        err_y = frame_shape[1] - frame_cy

        twist = Twist()
        twist.linear.x = np.clip(self.kp_lin * err_y, 0.0, self.max_lin)
        twist.angular.z = np.clip(self.kp_ang * err_x, -self.max_ang, self.max_ang)
        return twist
    