import cv2 
import zmq
import base64
import numpy as np
from ultralytics import YOLO

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

#PID 제어 상수
Kp_ang = 0.005
Kp_lin = 0.002
MAX_LIN_SPEED = 0.3
MAX_ANG_SPEED = 0.5

class VisionFollower(Node):
    def __init__(self):
        super().__init__('vision_follower')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.target_track_id = None        #처음에 None으로 초기화

        # YOLO 사전 학습 모델 로드
        self.model = YOLO('yolo11n.pt')

        #ZMQ 소켓 설정
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.bind("tcp://*:5555")  # 모든 IP에서 연결 허용
        self.get_logger().info("✅ Vision 서버 시작: 이미지 수신 대기 중...")

        # print("이미지 수신 대기 중...")

        #OpenCV 창 설정
        cv2.namedWindow("Recived Image", cv2.WINDOW_NORMAL)

        #루프 실행
        self.process_frames()
    
    def process_frames(self):
        while rclpy.ok():
            try:
                # base64로 인코딩된 이미지 수신
                encoded = self.socket.recv()
                jpg_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                # 화면에 표시
                if img is None:
                    continue
                
                #객체 탐지 결과 처리
                # results = self.model.predict(source=img, show=False)
                results = self.model.track(source=img, show=False, persist=True)
                boxes = results[0].boxes
                target_center = None

                for box in boxes:
                    cls_id = int(box.cls[0])
                    if cls_id == 0:     #0번 클래스=='person'
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        center_x = int((x1+x2)/2)
                        center_y = int((y1+y2)/2)
                        

                        if box.id is not None:
                            current_id = int(box.id[0])

                            #아직 타켓이 없으면 이 사람을 타겟으로 설정
                            if self.target_track_id is None:
                                self.target_track_id = current_id
                                print(f"Set target track_id: {self.target_track_id}")
                            
                            #타켓 아이디가 같으면 따라가기
                            if current_id == self.target_track_id:
                                target_center = (center_x, center_y)
                                print(f"Following person with track_id: {current_id}")
                                break

                            track_id = int(box.id[0])
                            print(f"Detected person with track_id: {track_id}")
                        break   #첫 번째 사람만 추적
                
                twist = Twist()
                
                #PID 제어 계산(탐지된 경우만)
                if target_center:
                    frame_center_x = img.shape[1] // 2
                    frame_center_y = img.shape[0] // 2

                    err_x = target_center[0] - frame_center_x
                    err_y = frame_center_y - target_center[1]  

                    # angular_z = -Kp_ang * err_x 
                    angular_z = Kp_ang * err_x   #양수: L
                    linear_x = Kp_lin * err_y      

                    twist.linear.x = np.clip(linear_x, 0.0, MAX_LIN_SPEED)
                    twist.angular.z = np.clip(angular_z, -MAX_ANG_SPEED, MAX_ANG_SPEED)

                    self.get_logger().info(f"추적 중: linear_x={twist.linear.x:.2f}, angular_z={twist.angular.z:.2f}")
                
                else:
                    #탐지 실패 시 정지
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0
                    self.get_logger().info("사람 탐지 실패. 정지합니다.")
                
                self.cmd_pub.publish(twist)


                #탐지 결과 시각화
                annotated_frame = results[0].plot()    #numpy 배열 BGR이미지
                cv2.imshow("Received Image", annotated_frame)

                #RGB 변환
                # frame_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                # cv2.imshow("Camera", frame_bgr)
                # cv2.imshow("Received Image", img)

                if cv2.waitKey(1) == 27:  # ESC 키 누르면 종료
                    break

            except KeyboardInterrupt:
                break
        
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    node = VisionFollower()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
