import cv2
import zmq
import base64
import threading
from queue import Queue, Full, Empty
import numpy as np

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

from yolo_tracker import YOLOTracker
from pid_controller import PIDController
from lidar_virtual import LidarVirtualizer
from distance_logger import DistanceLogger
from nav2_goal import Nav2GoalSender


class VisionFollower(Node):
    def __init__(self):
        super().__init__('vision_follower')

        #ROS Publisher
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_pub = self.create_publisher(LaserScan, '/scan_virtual', 10)

        #ROS Subscriber
        # self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)
        #가장 최신 정보만 사용 -> 실시간성 유지
        self.create_subscription(LaserScan, '/scan', self.lidar_callback, 1)

        #각 기능 모듈 초기화
        self.tracker = YOLOTracker(model_path='yoloo11n.pt')
        self.pid = PIDController(kp_ang=0.005, kp_lin=0.002)
        self.virtualizer = LidarVirtualizer()
        self.logger = DistanceLogger('bbox_distance_log.csv')
        self.nav2 = Nav2GoalSender(self)

        #1.스레드 간 통신을 위한 큐 생성(가장 최신 프레임만 저장)
        self.frame_queue = Queue(maxsize=1)
        self.is_running = True

        #2.ZMQ 수신 스레드 생성 및 시작
        self.zmq_thread = threading.Thread(target=self._zmq_receiver_thread)
        self.zmq_thread.start()
        self.get_looter().info("ZMQ Receiver thread started")

        #3. YOLO 처리 스레드 생성 및 시작(기존 메인 루프 역할)
        self.yolo_thread = threading.Thread(target=self._yolo_processor_thread)
        self.yolo_thread.start()
        self.get_looter().info("YOLO Processor thread started")

        #사람 위치 추적
        self.last_person_pose = None

        #OpenCV 창 설정
        cv2.namedWindow("Received Image", cv2.WINDOW_NORMAL)

        #process_frame이 thread 독점하지 않도록 callback과 번갈아서 수행
        self.timer = self.create_timer(0.05, self.process_frame)
    
    def _zmq_receiver_thread(self):
        """생산자: ZMQ로 이미지를 받아 큐에 넣는 역할만 수행"""
        #ZMQ 이미지 수신 설정
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://*:5555")
        self.get_logger().info("✅ Vision 서버 시작: 이미지 수신 대기 중...")

        while self.is_running and rclpy.ok():
            try:
                encoded = socket.recv(flags=zmq.NOBLOCK)
                jpg_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                #큐가 꽉 차 있으면 기존 항목 버리고 새 항목 추가
                if img is not None:
                    try:
                        self.frame_queue.put_nowait(img)

                    except Full:
                        #오래된 프레임 버리고 새 프레임으로 교체
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(img)
            
            except zmq.Again:
                continue #데이터 없으면 다시 시도
            except Exception as e:
                self.get_logger().error(f"ZMQ Thread Error: {e}")
    
    def _yolo_processor_thread(self):
        """소비자: 큐에서 이미지를 꺼내 YOLO 처리 및 ROS 메시지 발행"""
        while self.is_running and rclpy.ok():
            try:
                #큐에서 프레임 가져오기(없으면 잠시 대기)
                img = self.frame_queue.get(timeout=0.1)
            
            except Empty:
                continue

            #YOLO 추적
            boxes, annotated_frame = self.tracker.track(img)

            twist = Twist()
            #이미지에서 사람 존재 여부 확인
            person_found = False

            for box in boxes:
                cls_id = int(box.cls[0])
                if cls_id == 0:    #사람
                    # current_id = int(box.id[0])  
                    if box.id is not None: 
                        cx, cy, w, h = self.tracker.get_bbox_center(box)
                        twist = self.pid.compute(cx, cy, img.shape)
                        self.last_person_pose = (cx, cy)
                        person_found = True
                        break

                    else: None

                else:
                    #사물 -> 거리 계산 -> Lidar 반영 -> 로그 저장
                    cx, cy, w, h = self.tracker.get_bbox_center(box)
                    distance = self.tracker.estimate_distance(w)
                    angle = self.tracker.estimate_angle(cx, img.shape[1])
                    self.virtualizer.insert_obstacle(distance, angle)
                    self.logger.log(w, distance)
            
            #사람 없으면 nav2 goal 전환
            if not person_found:
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                if self.last_person_pose:
                    self.nav2.send_goal(self.last_person_pose)
            
            #속도 명령 전송
            self.cmd_pub.publish(twist)

            #수정된 LiDAr 데이터 publish
            self.scan_pub.publish(self.virtualizer.get_virtual_scan())

            #시각화
            cv2.imshow("Received Image", annotated_frame)

            if cv2.waitKey(1) == ord('q'):
                self.is_running = False
                break
    
    def destroy_node(self):
        """노드 종료 시 스레드 정리"""
        self.get_logger().info("Shutting down threads")
        self.is_running = False
        self.zmq_thread.join()
        self.yolo_thread.join()
        cv2.destroyAllWindows()
        super().destroy_node()
            

    def lidar_callback(self, msg):
        #현재 LiDAR 데이터 저장
        self.virtualizer.update_scan(msg)






    
    # def process_frame(self):
    #     try:
    #         encoded = self.socket.recv(flags=zmq.NOBLOCK)
    #     except zmq.Again:
    #         return       #데이터 없으면 넘어감
        
    #     jpg_bytes = base64.b64decode(encoded)
    #     np_arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
    #     img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    #     if img is None:
    #         return
        
    #     #YOLO 추적
    #     boxes, annotated_frame = self.tracker.track(img)

    #     twist = Twist()
    #     person_found = False

    #     for box in boxes:
    #         cls_id = int(box.cls[0])
    #         if cls_id == 0:    #사람
    #             # current_id = int(box.id[0])  
    #             if box.id is not None: 
    #                 cx, cy, w, h = self.tracker.get_bbox_center(box)
    #                 twist = self.pid.compute(cx, cy, img.shape)
    #                 self.last_person_pose = (cx, cy)
    #                 person_found = True
    #                 break

    #             else: None

    #         else:
    #             #사물 -> 거리 계산 -> Lidar 반영 -> 로그 저장
    #             cx, cy, w, h = self.tracker.get_bbox_center(box)
    #             distance = self.tracker.estimate_distance(w)
    #             angle = self.tracker.estimate_angle(cx, img.shape[1])
    #             self.virtualizer.insert_obstacle(distance, angle)
    #             self.logger.log(w, distance)
        
    #     #사람 없으면 nav2 goal 전환
    #     if not person_found:
    #         twist.linear.x = 0.0
    #         twist.angular.z = 0.0
    #         if self.last_person_pose:
    #             self.nav2.send_goal(self.last_person_pose)
        
    #     #속도 명령 전송
    #     self.cmd_pub.publish(twist)

    #     #수정된 LiDAr 데이터 publish
    #     self.scan_pub.publish(self.virtualizer.get_virtual_scan())

    #     #시각화
    #     cv2.imshow("Received Image", annotated_frame)
    #     cv2.waitKey(1)
