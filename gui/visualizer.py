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
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Scaling logic (consistent with Refiner)
        display_scale = 1.0
        screen_h = 1000
        if self.height > screen_h:
            display_scale = screen_h / self.height
            print(f"High-res detected. Scaling view by {display_scale:.2f}")

        frame_idx = 0
        paused = False
        
        while frame_idx < self.total_frames:
            if not paused:
                # Sequential read is much faster than cap.set()
                ret, frame = self.cap.read()
                if not ret: break

                frame_key = str(frame_idx)
                if frame_key in self.data:
                    for det in self.data[frame_key]:
                        x1, y1, x2, y2 = map(int, det['bbox'])
                        # Use LINE_8 for speed
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2, cv2.LINE_8)
                        label = f"ID:{det['id']}"
                        cv2.putText(frame, label, (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_8)

                # Info Overlay
                cv2.putText(frame, f"Frame: {frame_idx}/{self.total_frames-1}", (20, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_8)
                
                # Show scaled version for display
                display_frame = frame
                if display_scale != 1.0:
                    display_frame = cv2.resize(frame, (int(self.width * display_scale), int(self.height * display_scale)),
                                             interpolation=cv2.INTER_LINEAR)
                
                cv2.imshow(self.window_name, display_frame)
                frame_idx += 1

            # Adjust wait time to match video FPS
            wait_time = max(1, int(1000 / self.fps))
            key = cv2.waitKey(wait_time if not paused else 0) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
                if not paused:
                    # When unpausing, we need to sync the capture back to the current frame_idx
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

        self.cap.release()
        cv2.destroyAllWindows()
