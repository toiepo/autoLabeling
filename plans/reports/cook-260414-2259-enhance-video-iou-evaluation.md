# Cook Report: Enhance Video IoU Evaluation

## Overview
- Task: Refactor IoU evaluation for video sequences.
- Status: COMPLETED
- Date: 2026-04-14

## Changes Implemented

### 1. Evaluator Refactor (`eval/evaluator.py`)
- **Metric Expansion**: Added Volume IoU (vIoU) and Success Rates (IoU@0.5, 0.75, 0.9).
- **vIoU Calculation**: Implemented summation of intersection and union areas over the entire video sequence to provide a temporal-aware metric.
- **Improved Robustness**: Updated the logic to handle missing frames and empty detection sets properly.
- **Detailed Reporting**: Added a formatted print summary for easy analysis.

### 2. Validation
- Performed a simulation run using `main.py --mode simulate`.
- Verified the evaluation report output with real-like data.

## Results
The evaluation now provides a much clearer picture of auto-framing quality than a simple average:
- **mIoU**: Sensitive to small errors.
- **vIoU**: Reflects overall coverage stability.
- **Success Rates**: Quantifies "good enough" framing occurrences.

## Next Steps
- Integrate per-track IoU if person consistency becomes a requirement.
- Consider adding "Containment IoU" specifically for framing windows vs targets.
