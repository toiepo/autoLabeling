# Cook Report: Update JSON Naming Convention

## Overview
- Task: Automate JSON filename generation based on video input.
- Status: COMPLETED
- Date: 2026-04-14

## Changes Implemented

### 1. Main Entry Point (`main.py`)
- **Dynamic Naming**: Removed the hardcoded default `"data/detections.json"` for the `--json` argument.
- **Video-Based Suffix**: Implemented logic to automatically set the tracking JSON path to `data/[video_name]_detection.json` if no path is provided and a video is specified.
- **Framing Naming**: Added similar logic for evaluation results, defaulting to `data/[video_name]_framing.json`.
- **Fallbacks**: Maintained generic fallbacks (`data/detections.json` and `data/framing_results.json`) for cases where no video is provided (e.g., direct evaluation of existing JSONs).

## Verification
- Running `python main.py --mode track --video inputs/video_02.mp4` now correctly targets `data/video_02_detection.json`.
- Running `python main.py --mode evaluate --video inputs/video_01.mp4` targets `data/video_01_detection.json` and `data/video_01_framing.json`.

## Results
Users no longer need to manually specify output paths for every video; the tool now follows a project-standard naming convention automatically.
