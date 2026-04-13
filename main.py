import argparse
import sys
import os
from core.detector import YOLODetector
from gui.refiner import Refiner
from eval.evaluator import Evaluator
from gui.visualizer import Visualizer
from core.framing_simulator import FramingSimulator

def main():
    parser = argparse.ArgumentParser(description="Auto-Labeling & Auto-Framing Evaluation Tool")
    parser.add_argument("--mode", choices=['track', 'refine', 'simulate', 'evaluate', 'visualize'], required=True, 
                        help="track: Run YOLO | refine: Manual UI | simulate: Create mock framing | evaluate: Compare | visualize: Play video with boxes")
    parser.add_argument("--video", help="Path to input video")
    parser.add_argument("--json", default="data/detections.json", help="Path to tracking JSON file (Ground Truth)")
    parser.add_argument("--eval_json", default="data/framing_results.json", help="Path to framing results JSON")
    
    args = parser.parse_args()

    # Define default paths if not provided
    if args.video and not args.json:
        video_name = os.path.splitext(os.path.basename(args.video))[0]
        args.json = f"data/{video_name}_gt.json"

    if args.mode == 'track':
        if not args.video:
            print("Error: --video is required for tracking mode.")
            return
        detector = YOLODetector()
        detector.process_video(args.video, args.json)

    elif args.mode == 'refine':
        if not args.video or not os.path.exists(args.video):
            print(f"Error: Video file missing.")
            return
        refiner = Refiner(args.video, args.json)
        refiner.run()

    elif args.mode == 'visualize':
        if not args.video or not os.path.exists(args.video):
            print(f"Error: Video file missing.")
            return
        visualizer = Visualizer(args.video, args.json)
        visualizer.run()

    elif args.mode == 'simulate':
        if not os.path.exists(args.json):
            print(f"Error: Ground truth JSON {args.json} not found. Run 'track' first.")
            return
        sim = FramingSimulator(args.json)
        sim.simulate(args.eval_json)

    elif args.mode == 'evaluate':
        if not os.path.exists(args.json) or not os.path.exists(args.eval_json):
            print("Error: Missing JSON files for evaluation.")
            return
        evaluator = Evaluator(args.json, args.eval_json)
        evaluator.evaluate()

if __name__ == "__main__":
    main()
