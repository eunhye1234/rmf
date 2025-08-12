import cv2
import zmq
import time
import base64
import numpy as np
from picamera2 import Picamera2
# from picamera2.controls import AwbModeEnum 
from pinky_lcd import LCD
from PIL import Image


#ZMQ 소켓 설정
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://192.168.0.152:5555")  #서버_IP로

#카메라 및 LCD 초기화
lcd = LCD()
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640,640)}))
picam2.start()
# print(picam2.camera_controls)

try:
    while True:
        frame = picam2.capture_array()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rotate_frame = cv2.rotate(rgb_frame, cv2.ROTATE_180)
        flipped_frame = cv2.flip(rotate_frame, 1)

        #LCD에 표시
        lcd.img_show(Image.fromarray(flipped_frame))

        #BGR 변환
        #이미지 압축(JPEG 인코딩)
        bgr_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', bgr_frame)
        # _, buffer = cv2.imencode('.jpg', flipped_frame)
        jpg_bytes = buffer.tobytes()

        #base64 인코딩 (ZMQ 전송에 적합하게)
        encoded = base64.b64encode(jpg_bytes)

        #전송
        socket.send(encoded)

        #속도 조절
        time.sleep(0.05)

except KeyboardInterrupt:
    print("종료합니다")

finally:
    picam2.close()
    lcd.close()
    socket.close()
    context.term()
