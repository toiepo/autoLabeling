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

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0

    def evaluate(self):
        total_iou = 0
        count = 0
        
        # Simple evaluation logic: For each frame, compare GT boxes with framing results
        for frame_id, gt_boxes in self.gt_data.items():
            if frame_id not in self.fn_data:
                continue
            
            fn_boxes = self.fn_data[frame_id]
            
            for gt in gt_boxes:
                # Find best matching framing box
                best_iou = 0
                for fn in fn_boxes:
                    iou = self.calculate_iou(gt['bbox'], fn['bbox'])
                    best_iou = max(best_iou, iou)
                
                total_iou += best_iou
                count += 1

        avg_iou = total_iou / count if count > 0 else 0
        print(f"Average IoU: {avg_iou:.4f}")
        return avg_iou

if __name__ == "__main__":
    # evaluator = Evaluator('data/refined_gt.json', 'data/framingv1.json')
    # evaluator.evaluate()
    pass
