import subprocess
import os

def run_pipeline(video_path):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    gt_json = f"data/{video_name}_gt.json"
    sim_json = f"data/{video_name}_framing.json"

    print(f"\n{'='*20}")
    print(f"Processing {video_name}")
    print(f"{'='*20}")

    # 1. Track
    print("\n[1/3] Detecting & Tracking...")
    subprocess.run(["python", "main.py", "--mode", "track", "--video", video_path, "--json", gt_json])

    # 2. Simulate
    print("\n[2/3] Simulating Auto-Framing...")
    subprocess.run(["python", "main.py", "--mode", "simulate", "--json", gt_json, "--eval_json", sim_json])

    # 3. Evaluate
    print("\n[3/3] Evaluating Initial Solution...")
    subprocess.run(["python", "main.py", "--mode", "evaluate", "--json", gt_json, "--eval_json", sim_json])

    print(f"\nDone! You can now refine the labels manually with:")
    print(f"python main.py --mode refine --video {video_path} --json {gt_json}")

if __name__ == "__main__":
    videos = ["inputs/video_01.mp4", "inputs/video_02.mp4"]
    for v in videos:
        if os.path.exists(v):
            run_pipeline(v)
        else:
            print(f"Sample video {v} not found.")
