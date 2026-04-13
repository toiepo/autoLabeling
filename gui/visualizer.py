import cv2
import json
import os

class Visualizer:
    def __init__(self, video_path, json_path):
        self.video_path = video_path
        self.json_path = json_path
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
            print(f"Error: {json_path} not found.")

        self.cap = cv2.VideoCapture(video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.window_name = f"Visualization - {os.path.basename(video_path)}"
        cv2.namedWindow(self.window_name)

    def run(self):
        print("Starting visualization playback...")
        print("Controls: [Space] Pause/Play | [Q] Quit")
        
        frame_idx = 0
        paused = False
        
        while frame_idx < self.total_frames:
            if not paused:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()
                if not ret: break

                frame_key = str(frame_idx)
                if frame_key in self.data:
                    for det in self.data[frame_key]:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2, cv2.LINE_AA)
                        label = f"ID:{det['id']}"
                        cv2.putText(frame, label, (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

                # Info Overlay
                cv2.putText(frame, f"Frame: {frame_idx}/{self.total_frames-1}", (20, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
                
                cv2.imshow(self.window_name, frame)
                frame_idx += 1

            key = cv2.waitKey(int(1000 / self.fps) if not paused else 0) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
            
            if paused:
                # Still show current frame and handle Q
                continue

        self.cap.release()
        cv2.destroyAllWindows()
