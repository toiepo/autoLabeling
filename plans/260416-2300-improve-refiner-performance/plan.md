# Plan: Improve Refiner Performance

Optimize the `gui/refiner.py` interactive tool to eliminate lag during bounding box drawing and manipulation.

## Context
The current implementation of `Refiner.run()` decodes the video frame from disk on every iteration of its main loop, regardless of whether the frame has changed. This causes significant lag, especially with high-resolution videos or during interactive mouse operations.

## Proposed Changes

### 1. Frame Caching
- Introduce `self.cached_frame` to store the decoded image of the current frame index.
- Only call `cap.read()` when `self.current_frame_idx` changes or is uninitialized.
- This will drastically reduce CPU/IO usage during interactive drawing.

### 2. Redraw Strategy
- Use an `update_screen()` method that encapsulates the drawing logic.
- Only redraw when necessary (frame changes, mouse movement, key presses).
- Draw on a copy of the cached frame to keep the original frame clean.

### 3. Display Scaling Optimization
- Pre-scale the cached frame if `display_scale != 1.0` to avoid repeated `cv2.resize` calls if nothing changes.
- Or simply resize only the final output.

## Implementation Steps

1.  **Modify `Refiner.__init__`**:
    - Add `self.cached_frame = None` and `self.cached_frame_idx = -1`.
2.  **Update `Refiner.run()`**:
    - Implement the caching logic for `cap.read()`.
    - Move box/UI drawing logic into a separate method `get_display_frame()`.
    - Optimize the main loop to only redraw when `update_needed` is true or with a minimal timeout.
3.  **Refine `mouse_callback`**:
    - Ensure it triggers a redraw on movement.

## Success Criteria
- Bounding box drawing and dragging feel smooth (high FPS UI).
- CPU usage is significantly lower when idle (not changing frames).
- No functional regressions in navigation or saving.
