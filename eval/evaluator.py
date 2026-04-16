import json
import numpy as np

class Evaluator:
    def __init__(self, ground_truth_path, framing_results_path):
        """
        Comparing ground truth detections with auto-framing window predictions.
        """
        with open(ground_truth_path, 'r') as f:
            self.gt_data = json.load(f)
        with open(framing_results_path, 'r') as f:
            self.fn_data = json.load(f)

    def calculate_iou(self, box1, box2):
        """Calculates Intersection over Union (IoU) of two boxes [x1, y1, x2, y2]."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        width = max(0, x2 - x1)
        height = max(0, y2 - y1)
        intersection = width * height
        
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection, union

    def evaluate(self):
        total_iou = 0
        total_intersection = 0
        total_union = 0
        count = 0
        
        # Threshold counts
        thresh_05 = 0
        thresh_075 = 0
        thresh_09 = 0

        # Simple evaluation logic: For each frame, compare GT boxes with framing results
        for frame_id, gt_boxes in self.gt_data.items():
            # Support both integer and string keys from JSON
            frame_key = str(frame_id)
            if frame_key not in self.fn_data:
                # If frame missing in framing results, we count it as 0 IoU for all GT boxes
                for gt in gt_boxes:
                    total_union += (gt['bbox'][2] - gt['bbox'][0]) * (gt['bbox'][3] - gt['bbox'][1])
                    count += 1
                continue
            
            fn_boxes = self.fn_data[frame_key]
            
            # One-to-one matching using greedy IoU (ignores IDs)
            candidates = []
            for i, gt in enumerate(gt_boxes):
                for j, fn in enumerate(fn_boxes):
                    inter, union = self.calculate_iou(gt['bbox'], fn['bbox'])
                    iou = inter / union if union > 0 else 0
                    if iou > 0.01: # Small threshold to consider it a candidate match
                        candidates.append((iou, i, j, inter, union))
            
            # Sort candidates by IoU descending
            candidates.sort(key=lambda x: x[0], reverse=True)
            
            matched_gt = set()
            matched_fn = set()
            
            for iou, gt_idx, fn_idx, inter, union in candidates:
                if gt_idx not in matched_gt and fn_idx not in matched_fn:
                    total_iou += iou
                    total_intersection += inter
                    total_union += union
                    count += 1
                    matched_gt.add(gt_idx)
                    matched_fn.add(fn_idx)
                    
                    if iou >= 0.5: thresh_05 += 1
                    if iou >= 0.75: thresh_075 += 1
                    if iou >= 0.9: thresh_09 += 1

            # Penalize unmatched GT boxes (Detections that were missed)
            for i, gt in enumerate(gt_boxes):
                if i not in matched_gt:
                    gt_area = (gt['bbox'][2] - gt['bbox'][0]) * (gt['bbox'][3] - gt['bbox'][1])
                    total_union += gt_area
                    count += 1
            
            # Optional: Penalize unmatched FN boxes (False Positives)
            # In framing, usually FP is less critical than FN, but can be added:
            # for j, fn in enumerate(fn_boxes):
            #     if j not in matched_fn:
            #         fn_area = (fn['bbox'][2] - fn['bbox'][0]) * (fn['bbox'][3] - fn['bbox'][1])
            #         total_union += fn_area
            #         count += 1

        avg_iou = total_iou / count if count > 0 else 0
        volume_iou = total_intersection / total_union if total_union > 0 else 0
        
        sr_05 = thresh_05 / count if count > 0 else 0
        sr_075 = thresh_075 / count if count > 0 else 0
        sr_09 = thresh_09 / count if count > 0 else 0

        print("\n" + "="*30)
        print("VIDEO IoU EVALUATION REPORT")
        print("="*30)
        print(f"Total Instances:  {count}")
        print(f"Mean IoU (mIoU):  {avg_iou:.4f}")
        print(f"Volume IoU (vIoU): {volume_iou:.4f}")
        print("-" * 30)
        print("Success Rates (IoU > Threshold):")
        print(f"  IoU @ 0.50:     {sr_05:.2%}")
        print(f"  IoU @ 0.75:     {sr_075:.2%}")
        print(f"  IoU @ 0.90:     {sr_09:.2%}")
        print("="*30 + "\n")

        return {
            "mIoU": avg_iou,
            "vIoU": volume_iou,
            "sr_05": sr_05,
            "sr_075": sr_075,
            "sr_09": sr_09
        }

if __name__ == "__main__":
    # Example usage:
    # evaluator = Evaluator('data/refined_gt.json', 'data/framing_results.json')
    # evaluator.evaluate()
    pass
