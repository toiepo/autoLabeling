import cv2
import json
import os
import numpy as np

class Refiner:
    def __init__(self, video_path, json_path):
        self.video_path = video_path
        self.json_path = json_path
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
            print(f"Warning: {json_path} not found. Starting with empty labels.")

        self.cap = cv2.VideoCapture(video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = max(int(self.cap.get(cv2.CAP_PROP_FPS)), 1)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Scaling for display (to fit screen)
        self.display_scale = 1.0
        screen_h = 1000
        if self.height > screen_h:
            self.display_scale = screen_h / self.height
            print(f"Frame height {self.height} > {screen_h}. Scaling display by {self.display_scale:.2f}")
        
        self.current_frame_idx = 0
        self.selected_box_idx = -1
        self.drag_mode = None  # 'move', 'resize_tl', 'resize_br'
        self.start_point = None
        self.show_help = True
        self.needs_redraw = True
        self.cached_frame = None
        self.cached_display_frame = None
        self.cached_frame_idx = -1
        
        self.window_name = f"Refinement Tool - {os.path.basename(video_path)}"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # UI Styling
        self.colors = {
            'box': (0, 255, 127),       # Spring Green
            'selected': (0, 165, 255),  # Orange
            'handle': (255, 255, 255),  # White
            'text': (255, 255, 255),
            'bg_overlay': (0, 0, 0)
        }

    def mouse_callback(self, event, x, y, flags, param):
        # Remap coordinates back to original resolution
        x = int(x / self.display_scale)
        y = int(y / self.display_scale)
        
        frame_key = str(self.current_frame_idx)
        if frame_key not in self.data:
            self.data[frame_key] = []

        boxes = self.data[frame_key]
        margin = 15 # pixels for edge detection

        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_box_idx = -1
            self.drag_mode = None
            
            # Check for existing boxes (prioritize handles for resizing)
            for i, det in enumerate(boxes):
                x1, y1, x2, y2 = det['bbox']
                # Corner detection (TL, TR, BL, BR)
                if abs(x - x1) < margin and abs(y - y1) < margin: # TL
                    self.selected_box_idx = i
                    self.drag_mode = 'resize_tl'
                    break
                elif abs(x - x2) < margin and abs(y - y1) < margin: # TR
                    self.selected_box_idx = i
                    self.drag_mode = 'resize_tr'
                    break
                elif abs(x - x1) < margin and abs(y - y2) < margin: # BL
                    self.selected_box_idx = i
                    self.drag_mode = 'resize_bl'
                    break
                elif abs(x - x2) < margin and abs(y - y2) < margin: # BR
                    self.selected_box_idx = i
                    self.drag_mode = 'resize_br'
                    break
                # Move
                elif x1 <= x <= x2 and y1 <= y <= y2:
                    self.selected_box_idx = i
                    self.drag_mode = 'move'
                    self.start_point = (x, y)
                    break
            
            # If nothing clicked, start drawing a NEW box
            if self.selected_box_idx == -1:
                new_id = max([d['id'] for d in boxes] + [0]) + 1
                boxes.append({"id": new_id, "bbox": [x, y, x, y], "confidence": 1.0})
                self.selected_box_idx = len(boxes) - 1
                self.drag_mode = 'resize_br'
            
            self.needs_redraw = True

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selected_box_idx != -1 and self.selected_box_idx < len(boxes):
                bbox = boxes[self.selected_box_idx]['bbox']
                if self.drag_mode == 'move':
                    dx = x - self.start_point[0]
                    dy = y - self.start_point[1]
                    bbox[0] += dx
                    bbox[1] += dy
                    bbox[2] += dx
                    bbox[3] += dy
                    self.start_point = (x, y)
                elif self.drag_mode == 'resize_tl':
                    bbox[0], bbox[1] = x, y
                elif self.drag_mode == 'resize_tr':
                    bbox[2], bbox[1] = x, y
                elif self.drag_mode == 'resize_bl':
                    bbox[0], bbox[3] = x, y
                elif self.drag_mode == 'resize_br':
                    bbox[2], bbox[3] = x, y
                self.needs_redraw = True

        elif event == cv2.EVENT_RBUTTONDOWN:
            # Delete box with a margin (makes dots/small boxes easier to hit)
            hit_margin = 15
            for i, det in enumerate(boxes):
                x1, y1, x2, y2 = det['bbox']
                if x1 - hit_margin <= x <= x2 + hit_margin and y1 - hit_margin <= y <= y2 + hit_margin:
                    boxes.pop(i)
                    self.selected_box_idx = -1
                    self.needs_redraw = True
                    break

        elif event == cv2.EVENT_LBUTTONUP:
            # Finalize box coordinates (ensure x1 < x2, y1 < y2)
            if self.selected_box_idx != -1 and self.selected_box_idx < len(boxes):
                bbox = boxes[self.selected_box_idx]['bbox']
                x1, y1, x2, y2 = bbox
                bbox[0], bbox[2] = min(x1, x2), max(x1, x2)
                bbox[1], bbox[3] = min(y1, y2), max(y1, y2)
                
                # Auto-remove accidental dots (0 area)
                if bbox[0] == bbox[2] or bbox[1] == bbox[3]:
                    boxes.pop(self.selected_box_idx)
                    self.selected_box_idx = -1
                self.needs_redraw = True
                    
            self.drag_mode = None

    def draw_ui(self, frame):
        # Progress Bar
        bar_h = 10
        bar_w = self.width - 40
        cv2.rectangle(frame, (20, self.height - 30), (20 + bar_w, self.height - 30 + bar_h), (50, 50, 50), -1)
        progress = int((self.current_frame_idx / (self.total_frames - 1)) * bar_w) if self.total_frames > 1 else 0
        cv2.rectangle(frame, (20, self.height - 30), (20 + progress, self.height - 30 + bar_h), self.colors['selected'], -1)

        # Frame Info
        info = f"Frame: {self.current_frame_idx}/{self.total_frames - 1} | FPS: {self.fps}"
        cv2.putText(frame, info, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, self.colors['text'], 1, cv2.LINE_8)

        # Help Overlay
        if self.show_help:
            overlay = frame.copy()
            h, w = 220, 300
            cv2.rectangle(overlay, (self.width - w - 20, 20), (self.width - 20, 20 + h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            instructions = [
                "Controls:",
                "[A / D] Previous / Next Frame",
                "[Delete] Delete box",
                "[S] Save | [Q] Quit",
                "---",
                "Mouse:",
                "- Click & Drag: Move/Resize",
                "- Right-Click: Delete"
            ]
            for i, text in enumerate(instructions):
                cv2.putText(frame, text, (self.width - w + 5, 50 + i * 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_8)

    def run(self):
        while True:
            # 1. Update frame cache if needed
            if self.current_frame_idx != self.cached_frame_idx:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
                ret, frame = self.cap.read()
                if not ret: break
                self.cached_frame = frame
                self.cached_frame_idx = self.current_frame_idx
                self.needs_redraw = True

            # 2. Render UI only if something changed
            if self.needs_redraw:
                render_frame = self.cached_frame.copy()
                
                # Update resolution tracking if needed
                fh, fw = render_frame.shape[:2]
                if fh != self.height or fw != self.width:
                    self.height, self.width = fh, fw
                    # Resize window to fit screen if portrait
                    screen_h = 800
                    if self.height > screen_h:
                        scale = screen_h / self.height
                        cv2.resizeWindow(self.window_name, int(self.width * scale), screen_h)

                frame_key = str(self.current_frame_idx)
                boxes = self.data.get(frame_key, [])
                
                for i, det in enumerate(boxes):
                    x1, y1, x2, y2 = map(int, det['bbox'])
                    is_selected = (i == self.selected_box_idx)
                    
                    color = self.colors['selected'] if is_selected else self.colors['box']
                    thickness = 3 if is_selected else 2
                    
                    cv2.rectangle(render_frame, (x1, y1), (x2, y2), color, thickness, cv2.LINE_8)
                    
                    # Draw handles if selected
                    if is_selected:
                        for px in [x1, x2]:
                            for py in [y1, y2]:
                                cv2.circle(render_frame, (px, py), 6, self.colors['handle'], -1, cv2.LINE_8)

                    label = f"ID:{det['id']}"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(render_frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
                    cv2.putText(render_frame, label, (x1 + 5, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_8)

                self.draw_ui(render_frame)
                
                # Show scaled version for display if needed
                display_frame = render_frame
                if self.display_scale != 1.0:
                    display_frame = cv2.resize(render_frame, (int(self.width * self.display_scale), int(self.height * self.display_scale)), 
                                             interpolation=cv2.INTER_LINEAR)
                
                cv2.imshow(self.window_name, display_frame)
                self.needs_redraw = False
            
            # Using 1ms wait during dragging for responsiveness, otherwise 10ms is fine
            wait_time = 1 if self.drag_mode else 10
            key_code = cv2.waitKey(wait_time)
            if key_code == -1: continue
            
            key = key_code & 0xFF
            
            if key == ord('q'): break
            elif key == ord('s'): 
                self.save()
            elif key == ord('h'):
                self.show_help = not self.show_help
                self.needs_redraw = True
            
            # Navigation
            elif key == ord('d') or key == 83 or key_code == 2555904: # Next (D or Right Arrow)
                self.current_frame_idx = min(self.current_frame_idx + 1, self.total_frames - 1)
                self.selected_box_idx = -1
            elif key == ord('a') or key == 81 or key_code == 2424832: # Prev (A or Left Arrow)
                self.current_frame_idx = max(self.current_frame_idx - 1, 0)
                self.selected_box_idx = -1
            
            # ID Modification
            elif self.selected_box_idx != -1:
                frame_key = str(self.current_frame_idx)
                boxes = self.data.get(frame_key, [])
                if self.selected_box_idx < len(boxes):
                    if key == ord(']'): # Increment ID
                        boxes[self.selected_box_idx]['id'] += 1
                        self.needs_redraw = True
                    elif key == ord('[') and boxes[self.selected_box_idx]['id'] > 0: # Decrement ID
                        boxes[self.selected_box_idx]['id'] -= 1
                        self.needs_redraw = True
                    elif ord('0') <= key <= ord('9'): # Set ID 0-9
                        boxes[self.selected_box_idx]['id'] = int(chr(key))
                        self.needs_redraw = True

            elif key == ord('l'): # Skip forward
                self.current_frame_idx = min(self.current_frame_idx + 10, self.total_frames - 1)
                self.selected_box_idx = -1
            elif key == ord('j'): # Skip backward
                self.current_frame_idx = max(self.current_frame_idx - 10, 0)
                self.selected_box_idx = -1
            
            # Delete Box handling
            elif key in [8, 255] or key_code in [3014656]: # Backspace / Delete
                if self.selected_box_idx != -1:
                    frame_key = str(self.current_frame_idx)
                    if frame_key in self.data:
                        self.data[frame_key].pop(self.selected_box_idx)
                        self.selected_box_idx = -1
                        self.needs_redraw = True

        self.cap.release()
        cv2.destroyAllWindows()

    def save(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"Saved changes to {self.json_path}")

if __name__ == "__main__":
    pass
