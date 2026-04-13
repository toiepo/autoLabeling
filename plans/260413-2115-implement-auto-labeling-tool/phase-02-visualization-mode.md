# Phase 2: Visualization Mode

## Context Links
- [main.py](file:///d:/Tool/toolAutoLabeling/main.py)
- [gui/refiner.py](file:///d:/Tool/toolAutoLabeling/gui/refiner.py)

## Overview
Priority: High
Status: Todo
Description: Add a visualization mode to play the video with tracked / refined bounding boxes.

## Requirements
- A new command line option `--mode visualize`.
- Automatic playback of the video with boxes overlaid.
- Ability to pause/play and adjust speed.

## Implementation Steps
1. Create a `Visualizer` class in `gui/visualizer.py` (or reuse/extend `Refiner`).
2. Implement logic to read JSON and draw boxes on each frame in a loop.
3. Update `main.py` to support the `visualize` mode.

## Todo List
- [ ] Create `gui/visualizer.py`.
- [ ] Add `--mode visualize` to `main.py`.
- [ ] Implement playback controls (Pause: Space, Exit: Q).
