#!/usr/bin/env python3
"""
단일 노드 버전: F 고정 + 이미지 중심 사용
- YOLO 이미지 수신(ZMQ)
- 사람 감지 → PID FOLLOW
- 사람 미검출, 사물 존재 → Nav2로 마지막 사람 위치 goal + 사물 LaserScan 가상 장애물
- /cmd_vel mutex 처리
- TF2로 카메라 좌표 → map 좌표 변환
"""

import base64
import math
import threading
from typing import List, Optional, Tuple

import cv2
import numpy as np
import rclpy
import zmq

from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.action import ActionClient

from geometry_msgs.msg import Twist, PointStamped, PoseStamped
from sensor_msgs.msg import LaserScan
from nav2_msgs.action import NavigateToPose

import tf2_ros
from tf2_geometry_msgs import do_transform_point

import camera_info_manager as cim
from ament_index_python.packages import get_package_share_directory
import os
import rclpy.duration

try:
    from ultralytics import YOLO
except Exception as e:
    YOLO = None

# =====================
# Parameters
# =====================
ZMQ_BIND = "tcp://*:5555"
CAMERA_FRAME = "camera_link"
BASE_FRAME = "base_link"
MAP_FRAME = "map"
LASER_FRAME = "base_link"
# F = 763.5  # 미리 계산한 유사 초점 거리(px)
REAL_WIDTHS = {0: 0.45, "generic_object": 0.112}
Kp_ang = 0.005
Kp_lin = 0.002
MAX_LIN_SPEED = 0.30
MAX_ANG_SPEED = 0.50
WINDOW_NAME = "Vision Debug"
CHAIR_CLASS_ID = 56
HUMAN_CLASS_ID = 0
BENCH_CLASS_ID = 13
COUCH_CLASS_ID = 58

class VisionNavNode(Node):
    def __init__(self):
        super().__init__("vision_nav_node")

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.scan_sub = self.create_subscription(LaserScan, "/scan", self.scan_cb, 10)
        self.scan_pub = self.create_publisher(LaserScan, "/new_scan", 10)
        self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=5.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self, spin_thread=True)
        if YOLO is None:
            self.get_logger().error("Ultralytics YOLO missing")
            raise RuntimeError("YOLO missing")
        self.model = YOLO('yolo11n.pt')

        # ZMQ
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.bind(ZMQ_BIND)
        self.get_logger().info("✅ Waiting for images over ZMQ...")

        # State
        self.mode = "FOLLOW"
        self.nav_goal_active = False
        self._goal_handle = None
        self.last_person_goal: Optional[PoseStamped] = None
        self.latest_scan: Optional[LaserScan] = None

        pkg_share_dir = get_package_share_directory('vision_following')
        camera_info_url = 'file://' + os.path.join(pkg_share_dir, 'config', 'camera_calibration.yaml')
        self.cam_info_manager = cim.CameraInfoManager(self, 'my_camera', camera_info_url)
        self.cam_info_manager.loadCameraInfo()
        
        # NEW: 카메라 정보에서 파라미터 직접 로드
        cam_info = self.cam_info_manager.getCameraInfo()
        self.camera_matrix = np.array(cam_info.k).reshape((3, 3))
        self.dist_coeffs = np.array(cam_info.d)
        
        self.fx = self.camera_matrix[0, 0]
        self.fy = self.camera_matrix[1, 1]
        self.cx = self.camera_matrix[0, 2]
        self.cy = self.camera_matrix[1, 2]

        # Camera intrinsics (fixed)
        # self.fx: float = F
        # self.fy: float = F
        # self.cx: Optional[float] = None
        # self.cy: Optional[float] = None

        # Mutex
        self.vel_lock = threading.Lock()

        self.obstacle_cache = []        # (u_c, v_c, w_px, cls_id, timestamp)를 저장할 리스트
        self.persistence_duration = rclpy.duration.Duration(seconds=3.0)    #장애물 유지 시간 3초
        self.obstacle_ids  = (CHAIR_CLASS_ID, COUCH_CLASS_ID, BENCH_CLASS_ID)
 
        try:
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        except Exception:
            pass

        self.create_timer(0.0, self.loop_once)

    def scan_cb(self, msg: LaserScan):
        self.latest_scan = msg

    def loop_once(self):
        raw_img = self._recv_image()
        if raw_img is None:
            self._check_nav_result_nonblocking()
            return
        
        # 모든 계산은 왜곡이 보정된 이미지를 기준으로 수행합니다.
        img = cv2.undistort(raw_img, self.camera_matrix, self.dist_coeffs)

        now = self.get_clock().now()

        results = self.model.predict(source=img, verbose=False, imgsz=img.shape[:2][::-1])
        det = results[0]
        boxes = det.boxes

        person = None

        for b in boxes:
            cls_id = int(b.cls[0])
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            u_c = (x1 + x2)/2.0
            v_c = (y1 + y2)/2.0
            w_px = x2 - x1
            if cls_id == HUMAN_CLASS_ID:
                # self.get_logger().info("-----------------PERSON")
                person = (u_c, v_c, w_px)
            else:
                self.obstacle_cache.append((u_c, v_c, w_px, cls_id, now))

        scan_to_publish = self.latest_scan

        #사람 감지
        if person is not None:
            if self.mode == "NAV2":
                self._cancel_nav_goal_if_active()
            self.mode = "FOLLOW"
            u_c, v_c, w_px = person
            # real_w = REAL_WIDTHS.get(0, 0.112)
            real_w = REAL_WIDTHS.get(0, 0.097)
            Z = self._depth_from_width(w_px, real_w)
            cam_xyz = self._pixel_to_cam(u_c, v_c, Z)
            # self._publish_pid_cmd(u_c, v_c)
            # self._update_last_person_goal(cam_xyz)
        #사람 없음
        else:
            chairs = [obj for obj in self.obstacle_cache if obj[3] in self.obstacle_ids]
            # self._stop_cmd()
            # if objects and self.last_person_goal is not None:
            # if objects:
            if chairs:
            # if cls_id == CHAIR_CLASS_ID:
                self.get_logger().info("-----------------CHAIR")
                scan_to_publish = self._inject_virtual_obstacles(chairs)
                if self.mode != "NAV2":
                    # self._send_nav_goal(self.last_person_goal)
                    self.mode = "NAV2"
            
            else:
                self._stop_cmd()

        if scan_to_publish:
            self.scan_pub.publish(scan_to_publish)

        # 2.캐시에서 오래된 장애물 제거(Pruning)
        #리스트를 뒤에서부터 순회하며 삭제해야 인덱스 문제가 없음
        for i in range(len(self.obstacle_cache) -1, -1, -1):
            *_, timestamp = self.obstacle_cache[i]
            if (now - timestamp) > self.persistence_duration:
                self.obstacle_cache.pop(i)

        # self._check_nav_result_nonblocking()
        try:
            annotated = det.plot()
            cv2.imshow(WINDOW_NAME, annotated)
            if cv2.waitKey(1) & 0xFF == 27:
                rclpy.shutdown()
        except Exception:
            pass

    def _recv_image(self) -> Optional[np.ndarray]:
        try:
            encoded = self.socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again:
            return None
        jpg_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img

    def _depth_from_width(self, width_px: float, real_width_m: float) -> float:
        #픽셀너비 + 실제 너비 -> 3D거리 추정
        if width_px <= 1e-6:
            return float('inf')
        return (real_width_m * self.fx) / width_px

    def _pixel_to_cam(self, u: float, v: float, Z: float) -> Tuple[float, float, float]:
        #이미지 좌표, 추정 3D거리 -> 카메라 3D 좌표
        X = (u - self.cx) * Z / self.fx
        Y = (v - self.cy) * Z / self.fy
        return float(X), float(Y), float(Z)

    def _update_last_person_goal(self, cam_xyz: Tuple[float, float, float]):
        #카메라 좌표 -> map 좌표
        try:
            stamp = self.get_clock().now().to_msg()
            pt = PointStamped()
            pt.header.stamp = stamp
            pt.header.frame_id = CAMERA_FRAME
            pt.point.x, pt.point.y, pt.point.z = cam_xyz
            tf = self.tf_buffer.lookup_transform(MAP_FRAME, CAMERA_FRAME, stamp, timeout=Duration(seconds=0.2))
            map_pt = do_transform_point(pt, tf).point
            ps = PoseStamped()
            ps.header.frame_id = MAP_FRAME
            ps.header.stamp = stamp
            ps.pose.position.x = map_pt.x
            ps.pose.position.y = map_pt.y
            ps.pose.position.z = map_pt.z
            ps.pose.orientation.w = 1.0
            self.last_person_goal = ps
        except Exception as e:
            self.get_logger().warn(f"TF(cam→{MAP_FRAME}) failed for person: {e}")

    def _publish_pid_cmd(self, u_c: float, v_c: float):
        err_x = u_c - self.cx
        err_y = self.cy - v_c
        angular_z = Kp_ang * err_x
        linear_x = Kp_lin * err_y
        twist = Twist()
        twist.linear.x = float(np.clip(linear_x, 0.0, MAX_LIN_SPEED))
        twist.angular.z = float(np.clip(angular_z, -MAX_ANG_SPEED, MAX_ANG_SPEED))
        with self.vel_lock:
            self.cmd_pub.publish(twist)

    def _stop_cmd(self):
        with self.vel_lock:
            self.cmd_pub.publish(Twist())

    # --- Nav2 & Virtual Obstacle Methods ---
    def _send_nav_goal(self, goal: PoseStamped):
        if not isinstance(goal, PoseStamped):
            self.get_logger().error(f"Invalid goal type: {type(goal)}")
            return

        self.nav_client.wait_for_server(timeout_sec=2.0)
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self._goal_response_cb)

    def _goal_response_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Nav2 goal rejected')
            self.nav_goal_active = False
            return
        self._goal_handle = goal_handle
        self.nav_goal_active = True
        goal_handle.get_result_async().add_done_callback(self._nav_result_cb)

    def _nav_result_cb(self, future):
        self.nav_goal_active = False
        self.mode = "FOLLOW"

    def _cancel_nav_goal_if_active(self):
        if self.nav_goal_active and self._goal_handle is not None:
            self._goal_handle.cancel_goal_async()
            self.nav_goal_active = False

    def _check_nav_result_nonblocking(self):
        pass  # callback handles status

    def _inject_virtual_obstacles(self, cached_object: List[Tuple[float, float, float, int, rclpy.time.Time]]):
        if self.latest_scan is None:
            return
        
        # self.get_logger().info("run1")
        scan = LaserScan()
        scan.header = self.latest_scan.header
        scan.angle_min = self.latest_scan.angle_min
        scan.angle_max = self.latest_scan.angle_max
        scan.angle_increment = self.latest_scan.angle_increment
        scan.time_increment = self.latest_scan.time_increment
        scan.scan_time = self.latest_scan.scan_time
        scan.range_min = self.latest_scan.range_min
        scan.range_max = self.latest_scan.range_max
        scan.ranges = list(self.latest_scan.ranges)
        scan.intensities = list(self.latest_scan.intensities)

        # self.get_logger().info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        # self.get_logger().info(f'angle_min {scan.angle_min}')
        # self.get_logger().info(f'angle_max {scan.angle_max}')
        # self.get_logger().info(f'angle_increment {scan.angle_increment}')
        # self.get_logger().info(f'range_min {scan.range_min}')
        # self.get_logger().info(f'range_max {scan.range_max}')
        # # self.get_logger().info(f'angle_min {scan.ranges})
        # # self.get_logger().info(f'angle_min ')
        # self.get_logger().info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2222")

        for u_c, v_c, w_px, cls_id, _ in cached_object:
            # real_w = REAL_WIDTHS.get(cls_id, 0.112)
            real_w = REAL_WIDTHS.get(cls_id, 0.097)
            Z = self._depth_from_width(w_px, real_w)
            # angle 계산
            angle = math.atan2(u_c - self.cx, self.fx)
            # angle = math.atan2(self.cx - u_c, self.fx)

            corrected_angle = angle + math.pi

            if corrected_angle > scan.angle_max:
                corrected_angle -= 2*math.pi

            index = int((corrected_angle - scan.angle_min) / scan.angle_increment)    
            # index = int((angle - scan.angle_min) / scan.angle_increment)
            # if 0 <= index < len(scan.ranges):
            #     scan.ranges[index] = min(scan.ranges[index], Z)
            n=25
            # print("run2")
            for i in range(index-n, index+n+1):
                if 0<=i<len(scan.ranges):
                    # scan.ranges[i] = min(scan.ranges[i], Z)
                    scan.ranges[i] = Z
        # print("run3")
        # print("Original: ", self.latest_scan.ranges[index-n:index+n])
        # print("Modified: ", scan.ranges[index-n:index+n])
        # self.scan_pub.publish(scan)
        return scan


def main(args=None):
    rclpy.init(args=args)
    node = VisionNavNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
