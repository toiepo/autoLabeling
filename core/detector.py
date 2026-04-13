import cv2
import json
import os
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_name='yolo11n.pt'):
        """
        Initializes the YOLO detector. Downloads the model if not present.
        """
        self.model = YOLO(model_name)
        self.classes_to_detect = [0]  # Person

    def process_video(self, video_path, output_json_path):
        if not os.path.exists(video_path):
            print(f"Error: Video not found at {video_path}")
            return

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        print(f"Starting tracking on {video_path}...")
        # stream=True for memory efficiency on long videos
        results = self.model.track(source=video_path, persist=True, classes=self.classes_to_detect, stream=True)
        
        tracking_data = {}
        
        for i, r in enumerate(results):
            frame_id = i
            boxes = r.boxes
            frame_detections = []
            
            if boxes is not None and boxes.id is not None:
                ids = boxes.id.cpu().numpy().astype(int)
                coords = boxes.xyxy.cpu().numpy()
                confs = boxes.conf.cpu().numpy()
                
                for obj_id, box, conf in zip(ids, coords, confs):
                    frame_detections.append({
                        "id": int(obj_id),
                        "bbox": [round(float(x), 2) for x in box],  # [x1, y1, x2, y2]
                        "confidence": round(float(conf), 3)
                    })
            
            tracking_data[frame_id] = frame_detections
            
            if i % 50 == 0:
                print(f"Processed frame {i}")

        with open(output_json_path, 'w') as f:
            json.dump(tracking_data, f, indent=4)
        
        print(f"Successfully saved {len(tracking_data)} frames of tracking data to {output_json_path}")

if __name__ == "__main__":
    pass
