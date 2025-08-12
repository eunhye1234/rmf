import csv
import os
import threading


class DistanceLogger:
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.lock()

        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["bbox_width", "distance"])
    
    def log(self, bbox_width, distance):
        with self.lock:
            try:
                with open(self.filename, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([bbox_width, distance])
            
            except Exception as e:
                print(f"Error writing to log file: {e}")
                pass
                    










# class DistanceLogger:
#     def __init__(self, filename):
#         self.filename = filename

#         if not os.path.exists(filename):
#             with open(filename, 'w', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["bbox_width", "distance"])
    
#     def log(self, bbox_width, distance):
#         with open(self.filename, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow([bbox_width, distance])
