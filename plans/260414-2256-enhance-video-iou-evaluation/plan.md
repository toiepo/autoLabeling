# Plan: Enhance Video IoU Evaluation

## Context Links
- [evaluator.py](file:///d:/Tool/toolAutoLabeling/eval/evaluator.py)
- [framing_simulator.py](file:///d:/Tool/toolAutoLabeling/core/framing_simulator.py)

## Overview
- Priority: High
- Status: In Progress
- Description: Refactor the evaluation logic to provide a more comprehensive set of IoU-based metrics for video sequences.

## Key Insights
- Current IoU is a simple average of frame-wise best matches.
- Video IoU (vIoU) should consider the temporal consistency by summing intersections and unions across all frames.
- Framing evaluation often focuses on how well the predicted window matches the ideal bounding box of all targets.

## Requirements
- Support only IoU-based metrics.
- Calculate Average IoU (mIoU).
- Calculate Volume IoU (vIoU).
- Calculate IoU Success Rate (IoU@0.5, IoU@0.75).
- Provide a clean summary report.

## Implementation Steps

### Phase 1: Research & Structure
1. Define the specific IoU metrics to be used:
   - `mean_iou`: Average of best IoU per object per frame.
   - `volume_iou`: (Sum of Intersections) / (Sum of Unions).
   - `success_rate_05`: Percentage of boxes with IoU > 0.5.
   - `success_rate_075`: Percentage of boxes with IoU > 0.75.

### Phase 2: Refactor Evaluator
1. Update `eval/evaluator.py` to calculate these metrics.
2. Ensure it handles frames where detections might be missing.
3. Add a `report()` method to display results nicely.

### Phase 3: Validation
1. Run `simulate` and `evaluate` on a sample video to verify the metrics.

## Todo List
- [ ] Implement `vIoU` calculation logic.
- [ ] Add threshold-based success rates.
- [ ] Create detailed report output.
- [ ] Test with existing data.

## Success Criteria
- The tool outputs multiple IoU metrics.
- The results are consistent with standard video object evaluation.
- No other metrics (like precision/recall) are used as per user request.
