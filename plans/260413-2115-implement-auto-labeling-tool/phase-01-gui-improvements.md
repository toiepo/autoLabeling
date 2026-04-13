# Phase 1: GUI Improvements

## Context Links
- [gui/refiner.py](file:///d:/Tool/toolAutoLabeling/gui/refiner.py)

## Overview
Priority: High
Status: Todo
Description: Enhance the interactive refinement GUI to be more user-friendly and visually appealing.

## Key Insights
- The current GUI is functional but basic.
- Users need clear feedback on which box is selected and what actions they can take.
- Smooth navigation between frames is essential for efficient refinement.

## Requirements
- Better bounding box rendering (anti-aliased if possible, high-contrast colors).
- Clearer selection indicator (highlighting the box and showing resize handles).
- On-screen help overlay.
- Keyboard shortcuts for seeking (e.g., arrow keys or skip 10 frames).

## Implementation Steps
1. Update `Refiner.__init__` to load font settings and color palette.
2. Modify `Refiner.run` to draw a more polished UI overlay.
3. Improve `Refiner.mouse_callback` for more precise selection and interaction.
4. Add seeking keyboard shortcuts.

## Todo List
- [ ] Implement enhanced rendering logic in `Refiner.run`.
- [ ] Add seek functionality (`[` and `]` for 10 frames).
- [ ] Add help overlay toggle (`h`).
- [ ] Improve handle detection and drawing.
