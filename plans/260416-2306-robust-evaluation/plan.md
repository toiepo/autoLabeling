# Plan: Robust Geometry-Based Evaluation

Improve `eval/evaluator.py` to handle scenarios where object IDs are inconsistent between models by implementing a one-to-one IoU matching strategy.

## Context
When comparing detections from two different models (e.g., Ground Truth vs. Model B), the IDs assigned to the same person will often differ. Evaluation should rely on the spatial overlap (IoU) rather than the `id` field.

## Proposed Changes
1. **One-to-One Matching**: Update `Evaluator.evaluate()` to ensure that each predicted box matches at most one ground truth box per frame.
2. **Greedy Matching Algorithm**:
   - For each frame, calculate IoU for all possible pairs (GT_i, FN_j).
   - Sort these pairs by IoU in descending order.
   - Match the best pair, then mark both boxes as "used".
   - Repeat until no more pairs have an IoU above a minimum threshold (e.g., 0.1).

## Implementation Steps
1. Modify `Evaluator.evaluate` in `eval/evaluator.py`.
2. Introduce a matching loop that calculates a cost matrix (IoUs) and greedily picks the best matches.
3. Keep the same reporting format for consistency.

## Success Criteria
- Evaluation results are accurate even if IDs are scrambled or missing.
- No "double counting" (one prediction satisfying multiple ground truths).
- Metrics like mIoU remain comparable.
