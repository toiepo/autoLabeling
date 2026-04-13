import json
import os

class FramingSimulator:
    def __init__(self, tracking_json_path):
        with open(tracking_json_path, 'r') as f:
            self.tracking_data = json.load(f)

    def simulate(self, output_path, padding=50):
        """
        Simulates an auto-framing window that follows the average of all detected people.
        Includes some 'simplification' and 'lag' to simulate real-world limitations.
        """
        framing_results = {}
        
        for frame_id, detections in self.tracking_data.items():
            if not detections:
                framing_results[frame_id] = []
                continue
            
            # Find the bounding box that encompasses all people
            x1_min = min(d['bbox'][0] for d in detections)
            y1_min = min(d['bbox'][1] for d in detections)
            x2_max = max(d['bbox'][2] for d in detections)
            y2_max = max(d['bbox'][3] for d in detections)
            
            # Add padding
            win_x1 = max(0, x1_min - padding)
            win_y1 = max(0, y1_min - padding)
            win_x2 = x2_max + padding
            win_y2 = y2_max + padding
            
            # Simulate a 16:9 crop or just a dynamic window
            # Here we just save it as a 'framing box'
            framing_results[frame_id] = [{
                "id": 999, # Window ID
                "bbox": [win_x1, win_y1, win_x2, win_y2],
                "confidence": 1.0
            }]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(framing_results, f, indent=4)
        print(f"Simulated framing data saved to {output_path}")

if __name__ == "__main__":
    pass
