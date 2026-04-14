# Plan: Update JSON Naming Convention

## Context Links
- [main.py](file:///d:/Tool/toolAutoLabeling/main.py)
- [detector.py](file:///d:/Tool/toolAutoLabeling/core/detector.py)

## Overview
- Priority: Medium
- Status: In Progress
- Description: Automatically generate JSON filenames using the video source name and a suffix ("_detection").

## Key Insights
- The current default `--json data/detections.json` prevents the automatic naming logic from running.
- User wants output files to be named based on the video (e.g., `myvideo_detection.json`).

## Requirements
- When `--video` is provided, automatically derive the JSON path if it's not explicitly set.
- Use `[videoname]_detection.json` suffix for `track` mode or general output.

## Implementation Steps

### Phase 1: Modify main.py Argument Parsing
1. Change the default of `--json` to `None` so we can detect when the user hasn't provided one.
2. Update the logic to construct `data/[video_name]_detection.json`.

### Phase 2: Update Mode Logic
1. Ensure all modes (`track`, `refine`, etc.) use the derived path if needed.

## Todo List
- [ ] Remove default value from `--json` argument.
- [ ] Update naming logic to use `_detection.json` suffix.
- [ ] Verify functionality with `track` mode.

## Success Criteria
- Running `python main.py --mode track --video inputs/test.mp4` creates `data/test_detection.json`.
