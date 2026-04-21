import cv2
import json
import os
import numpy as np
import tkinter as tk
from tkinter import colorchooser

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
        self.cached_frame_idx = -1
        self.show_settings_for_box = None
        self.is_playing = False
        self.history = []
        self.last_known_state = json.dumps(self.data, sort_keys=True)
        self.show_crosshair = False
        self.show_labels = True
        self.mouse_pos = (0, 0)
        
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

        bar_h = 10
        bar_w = self.width - 40
        bar_x1, bar_y1 = 20, self.height - 30
        bar_x2, bar_y2 = 20 + bar_w, self.height - 30 + bar_h
        
        self.mouse_pos = (x, y)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.is_playing = False
            
            # Allow clicking on the seek bar with a wider Y margin
            if bar_y1 - 15 <= y <= bar_y2 + 15 and bar_x1 <= x <= bar_x2:
                self.is_seeking = True
                progress = max(0.0, min(1.0, (x - bar_x1) / bar_w))
                self.current_frame_idx = int(progress * (self.total_frames - 1))
                self.selected_box_idx = -1
                self.drag_mode = None
                self.needs_redraw = True
                return

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
            if getattr(self, 'show_crosshair', False):
                self.needs_redraw = True

            if getattr(self, 'is_seeking', False):
                progress = max(0.0, min(1.0, (x - bar_x1) / bar_w))
                self.current_frame_idx = int(progress * (self.total_frames - 1))
                self.needs_redraw = True
                return

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

        elif event == cv2.EVENT_LBUTTONDBLCLK:
            for i, det in enumerate(boxes):
                x1, y1, x2, y2 = det['bbox']
                # Check for existing boxes
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.show_settings_for_box = det
                    break

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
            if getattr(self, 'is_seeking', False):
                self.is_seeking = False
                return
                
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
            h, w = 320, 320
            cv2.rectangle(overlay, (self.width - w - 20, 20), (self.width - 20, 20 + h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            instructions = [
                "Controls:",
                "[SPACE] Play / Pause",
                "[A / D] Previous / Next Frame",
                "[CTRL+Z] Undo",
                "[C] Copy prev frame boxes",
                "[X] Clear frame boxes",
                "[V] Toggle text labels",
                "[G] Toggle crosshair",
                "[S] Save | [Q] Quit",
                "---",
                "Mouse:",
                "- Click & Drag: Move/Resize",
                "- Right-Click: Delete box",
                "- Double-Click: Settings"
            ]
            for i, text in enumerate(instructions):
                cv2.putText(frame, text, (self.width - w + 5, 50 + i * 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_8)

    def run(self):
        while True:
            # 1. Update frame cache if needed
            if self.current_frame_idx != self.cached_frame_idx:
                # OPTIMIZATION: Only use cap.set if we are NOT stepping sequentially to avoid massive decoding lag
                if self.current_frame_idx != self.cached_frame_idx + 1:
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
                    
                    if is_selected and 'color' in det:
                        color = det['color']
                    elif is_selected:
                        color = self.colors['selected']
                    else:
                        color = det.get('color', self.colors['box'])
                        
                    thickness = 3 if is_selected else 2
                    
                    cv2.rectangle(render_frame, (x1, y1), (x2, y2), color, thickness, cv2.LINE_8)
                    
                    # Draw handles if selected
                    if is_selected:
                        for px in [x1, x2]:
                            for py in [y1, y2]:
                                cv2.circle(render_frame, (px, py), 6, self.colors['handle'], -1, cv2.LINE_8)

                    if getattr(self, 'show_labels', True):
                        label = f"ID:{det['id']}"
                        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        cv2.rectangle(render_frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
                        cv2.putText(render_frame, label, (x1 + 5, y1 - 5), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_8)

                self.draw_ui(render_frame)
                
                if getattr(self, 'show_crosshair', False):
                    cx, cy = self.mouse_pos
                    cv2.line(render_frame, (cx, 0), (cx, self.height), (200, 200, 200), 1, cv2.LINE_AA)
                    cv2.line(render_frame, (0, cy), (self.width, cy), (200, 200, 200), 1, cv2.LINE_AA)
                
                # Show scaled version for display if needed
                display_frame = render_frame
                if self.display_scale != 1.0:
                    display_frame = cv2.resize(render_frame, (int(self.width * self.display_scale), int(self.height * self.display_scale)), 
                                             interpolation=cv2.INTER_LINEAR)
                
                cv2.imshow(self.window_name, display_frame)
                self.needs_redraw = False
            
            if getattr(self, 'show_settings_for_box', None):
                self.open_settings_box(self.show_settings_for_box)
                self.show_settings_for_box = None
                self.needs_redraw = True

            # Automatic History tracking for Undo
            current_state_str = json.dumps(self.data, sort_keys=True)
            if current_state_str != self.last_known_state:
                if not getattr(self, 'drag_mode', None):
                    self.history.append(self.last_known_state)
                    if len(self.history) > 100:
                        self.history.pop(0)
                    self.last_known_state = current_state_str

            if self.is_playing:
                wait_time = max(1, int(1000 / self.fps) - 5)
            else:
                wait_time = 1 if getattr(self, 'drag_mode', None) or getattr(self, 'is_seeking', False) else 10
            key_code = cv2.waitKey(wait_time)
            
            if key_code == -1:
                if self.is_playing:
                    self.current_frame_idx = min(self.current_frame_idx + 1, self.total_frames - 1)
                    if self.current_frame_idx == self.total_frames - 1:
                        self.is_playing = False
                    self.selected_box_idx = -1
                continue
            
            key = key_code & 0xFF
            
            if key == ord('q'): break
            elif key == ord('s'): 
                self.save()
            elif key == ord('c'): # Copy from prev
                if self.current_frame_idx > 0:
                    prev_key = str(self.current_frame_idx - 1)
                    if prev_key in self.data and self.data[prev_key]:
                        self.data[str(self.current_frame_idx)] = json.loads(json.dumps(self.data[prev_key]))
                        self.needs_redraw = True
            elif key == ord('x'): # Clear frame
                frame_key = str(self.current_frame_idx)
                if frame_key in self.data:
                    self.data[frame_key] = []
                    self.selected_box_idx = -1
                    self.needs_redraw = True
            elif key == ord('v'): # Toggle labels
                self.show_labels = not getattr(self, 'show_labels', True)
                self.needs_redraw = True
            elif key == ord('g'): # Toggle crosshair
                self.show_crosshair = not getattr(self, 'show_crosshair', False)
                self.needs_redraw = True
            elif key == 32: # SPACE
                if self.current_frame_idx >= self.total_frames - 1 and not self.is_playing:
                    self.current_frame_idx = 0
                self.is_playing = not self.is_playing
            elif key == 26: # CTRL + Z
                if self.history:
                    self.data = json.loads(self.history.pop())
                    self.last_known_state = json.dumps(self.data, sort_keys=True)
                    self.drag_mode = None
                    self.selected_box_idx = -1
                    self.needs_redraw = True
                    self.is_playing = False
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

    def open_settings_box(self, box):
        root = tk.Tk()
        root.title(f"Settings (Box ID: {box.get('id', 0)})")
        root.attributes('-topmost', True)
        root.geometry("+300+300")
        root.resizable(False, False)

        tk.Label(root, text="ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        id_var = tk.IntVar(value=box.get('id', 0))
        tk.Entry(root, textvariable=id_var).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Coordinate X1:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        x1_var = tk.DoubleVar(value=box['bbox'][0])
        tk.Entry(root, textvariable=x1_var).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Coordinate Y1:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        y1_var = tk.DoubleVar(value=box['bbox'][1])
        tk.Entry(root, textvariable=y1_var).grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Coordinate X2:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        x2_var = tk.DoubleVar(value=box['bbox'][2])
        tk.Entry(root, textvariable=x2_var).grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(root, text="Coordinate Y2:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        y2_var = tk.DoubleVar(value=box['bbox'][3])
        tk.Entry(root, textvariable=y2_var).grid(row=4, column=1, padx=10, pady=5)

        tk.Label(root, text="Confidence:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        conf_var = tk.DoubleVar(value=box.get('confidence', 1.0))
        tk.Entry(root, textvariable=conf_var).grid(row=5, column=1, padx=10, pady=5)

        color = box.get('color', None)
        
        def choose_color():
            nonlocal color
            bg_color = "#00ff7f" if color is None else f"#{int(color[2]):02x}{int(color[1]):02x}{int(color[0]):02x}"
            c = colorchooser.askcolor(initialcolor=bg_color, parent=root)
            if c[0]:
                r, g, b = map(int, c[0])
                color = (b, g, r) # OpenCV BGR
                color_btn.config(bg=c[1])

        tk.Label(root, text="Box Color:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        color_btn = tk.Button(root, text="Choose Color", command=choose_color, width=15)
        if color:
            color_btn.config(bg=f"#{int(color[2]):02x}{int(color[1]):02x}{int(color[0]):02x}")
        color_btn.grid(row=6, column=1, padx=10, pady=5)
        
        def apply_changes():
            try:
                box['id'] = id_var.get()
                box['bbox'] = [float(x1_var.get()), float(y1_var.get()), float(x2_var.get()), float(y2_var.get())]
                box['confidence'] = float(conf_var.get())
                if color is not None:
                    box['color'] = color
                root.destroy()
            except Exception as e:
                print(f"Invalid input: {e}")

        tk.Button(root, text="Apply Changes", command=apply_changes, width=20, bg="#4CAF50", fg="white").grid(row=7, column=0, columnspan=2, pady=15)
        
        root.mainloop()

if __name__ == "__main__":
    pass
