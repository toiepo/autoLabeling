# Debugger Report: Refiner Performance Issue

## Issue Analysis
The `Refiner` class in `gui/refiner.py` suffers from significant lag during bounding box operations (drawing, moving, resizing).

### Root Cause
The main loop in `run()` performs a `cap.set()` and `cap.read()` on every iteration. 
```python
while True:
    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame_idx)
    ret, frame = self.cap.read()
```
Even with a 30ms wait, the overhead of seeking and decoding a video frame from disk is too high for interactive UI responsiveness, especially on high-resolution videos. This happens even if the frame index hasn't changed.

## Solution
1. **Frame Caching**: Cache the decoded frame. Only update the cache when `current_frame_idx` changes.
2. **Selective Rendering**: Decouple frame decoding from UI rendering.
3. **Event-Driven UI**: Trigger redraws only when state changes (mouse move, key press).

## Plan
See [plan.md](../../plans/260416-2300-improve-refiner-performance/plan.md) for details.
