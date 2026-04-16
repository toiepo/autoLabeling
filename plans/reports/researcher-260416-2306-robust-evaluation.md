# Researcher Report: ID-Independent Evaluation Strategy

## Problem Statement
The user needs to evaluate a model's output against ground truth when the object IDs do not match (e.g., Model A IDs persons as 1, 2 while Model B IDs them as 5, 6).

## Solution: Spatial Matching (IoU)
Instead of looking at IDs, we use the bounding box coordinates to find the most likely match. 

### Comparison: Match-by-ID vs. Match-by-IoU

| Feature | Match-by-ID | Match-by-IoU (Current/Proposed) |
| :--- | :--- | :--- |
| **Requirement** | Stable tracking IDs across models | Bounding box coordinates |
| **Robustness** | Fails if re-ID occurs | Handles re-ID and ID swaps |
| **Multi-Object** | Simple mapping | Requires matching algorithm (Greedy/Hungarian) |

## implementation Details
The project already uses IoU for matching, which means **it already works without matching IDs**. However, to prevent "double-counting" errors, I will implement a one-to-one matching algorithm that pairs the best boxes first and removes them from the candidate pool for that frame.

See implementation details in [plan.md](../../plans/260416-2306-robust-evaluation/plan.md).
