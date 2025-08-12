import math
import copy
import threading
from sensor_msgs.msg import LaserScan


class LidarVirtualizer:
    def __init__(self):
        self.lastest_scan = None
        self.lock = threading.Lock()
    
    def update_scan(self, scan_msg):
        #lastest_scan에 접근하는 모든 곳에 lock 적용
        with self.lock:
            self.lastest_scan = scan_msg
    
    def insert_obstacle(self, distance, angle, width_deg=10):
        #width_deg를 가변적이도록 후에 코드 수정
        with self.lock:
            if self.lastest_scan is None:
                return
            
            scan = copy.deepcopy(self.lastest_scan)
            angle_min = scan.angle_min
            angle_increment = scan.angle_increment

            #라이다 배열에서의 물체의 중심의 index
            index = int((angle - angle_min) / angle_increment)
            #라이다 배열에서의 탐지된 물체의 너비?
            half_width = int((math.radians(width_deg) / 2) / angle_increment)

            for i in range(index - half_width, index + half_width + 1):
                if 0 <= i < len(scan.ranges):
                    #실제 측정값과 물체 추정값 중 더 작은 값 선택
                    scan.ranges[i] = min(scan.ranges[i], distance)
            self.lastest_scan = scan
    
    def get_virtual_scan(self):
        with self.lock:
            if self.lastest_scan is None:
                return LaserScan()   
            return copy.deepcopy(self.lastest_scan)
    







# class LidarVirtualizer:
#     def __init__(self):
#         self.lastest_scan = None
    
#     def update_scan(self, scan_msg):
#         self.lastest_scan = scan_msg
    
#     def insert_obstacle(self, distance, angle, width_deg=10):
#         if self.lastest_scan is None:
#             return
        
#         scan = copy.deepcopy(self.lastest_scan)
#         angle_min = scan.angle_min
#         angle_increment = scan.angle_increment

#         index = int((angle - angle_min) / angle_increment)
#         half_width = int((math.radians(width_deg) / 2) / angle_increment)

#         for i in range(index - half_width, index + half_width + 1):
#             if 0 <= i < len(scan.ranges):
#                 scan.ranges[i] = min(scan.ranges[i], distance)
#         self.lastest_scan = scan
    
#     def get_virtual_scan(self):
#         return self.lastest_scan if self.lastest_scan else LaserScan()
