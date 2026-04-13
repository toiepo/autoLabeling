# Phase 2: YOLO Detection and Tracking

## Overview
- Priority: High
- Status: Todo
- Effort: Medium

## Requirements
- Load YOLO model (ultralytics)
- Run inference on video
- Persist detections per frame (ID, bbox, confidence)

## Implementation Steps
1. Create `core/detector.py` to wrap YOLO logic
2. Implement tracking using `model.track()`
3. Save results to a temporary JSON/CSV format for refinement

## Todo List
- [ ] Implement `YOLODetector` class
- [ ] Script to process video and save raw detections
