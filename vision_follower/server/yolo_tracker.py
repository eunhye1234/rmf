from ultralytics import YOLO
import math

class YOLOTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def track(self, img):
        results = self.model.track(source=img, show=False, persist=True)
        return results[0].boxes, results[0].plot()
    
    def get_bbox_center(self, box):
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cx = int((x1+x2)/2)
        cy = int((y1+y2)/2)
        w = int(x2-x1)
        h = int(y2-y1)
        return cx, cy, w, h
    
    def estimate_distance(self, bbox_width, focal_length=800, real_width=0.5):
        #물체와 카메라의 실제 거리 추정값
        return (real_width * focal_length) / bbox_width
    
    def estimate_angle(self, cx, img_width, fov=60):
        #카메라 기준 실제 공간에서의 물체가 있는 방향 추정값(각도) 
        offset = cx - (img_width/2)
        return (offset / (img_width/2)) * (fov/2) * math.pi/180