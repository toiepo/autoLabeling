# Phase 3: Interactive Refinement GUI

## Overview
- Priority: High
- Status: Todo
- Effort: Medium/Hard

## Requirements
- Load processed video frames
- Overlay YOLO detections
- Allow user to:
    - Drag bounding boxes to fix them
    - Add new boxes
    - Delete incorrect boxes
    - Update tracking ID if broken

## Implementation Steps
1. Create `gui/refiner.py` using OpenCV mouse events or a small Tkinter wrapper
2. Implement "Pause/Play" and "Edit Mode"
3. Keyboard shortcuts for efficiency (n: next frame, p: prev, s: save)

## Todo List
- [ ] Basic OpenCV viewer with bbox overlay
- [ ] Mouse event handler for box modification
- [ ] Saving refined labels back to file
