# Auto-Labeling and Auto-Framing Evaluation Tool

This tool provides a workflow to detect, track, and refine bounding boxes for people in videos, and evaluate auto-framing solutions.

See the [Refinement Guide](docs/refinement-guide.md) for detailed UI instructions.

## Features
- **Auto-Detection**: Uses YOLOv11 for person detection and tracking.
- **Manual Refinement**: Interactive GUI to correct bounding box errors.
- **Evaluation**: Calculates IoU between refined ground truth and framing solutions.

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### 1. Detect and Track
Run YOLO on a video to generate initial detections.
```bash
python main.py --mode track --video inputs/video.mp4 --json data/detections.json
```

### 2. Refine Results
Open the GUI to manually fix bounding boxes to create ground truth.
- `a` / `d`: Previous / Next frame
- `j` / `l`: Seek backward / forward 10 frames
- `s`: Save changes
- `h`: Toggle help overlay
- `q`: Quit
- **Left Click & Drag**: Move or Resize selected box
- **Right Click**: Delete box

```bash
python main.py --mode refine --video inputs/video.mp4 --json data/detections.json
```

### 3. Visualize Results
Watch the video with the tracked or refined bounding boxes.
```bash
python main.py --mode visualize --video inputs/video.mp4 --json data/detections.json
```

### 4. Evaluate Framing
Compare refined ground truth with an auto-framing solution.
```bash
python main.py --mode evaluate --json data/detections.json --eval_json data/framing_results.json
```

## Project Structure
- `core/`: YOLO detector logic.
- `gui/`: Interactive refinement tool.
- `eval/`: Evaluation metrics.
- `inputs/`: Place your input videos here.
- `outputs/`: Processed videos (if any).
- `data/`: JSON tracking data.
