# Refinement Mode Guide

The Refinement Mode is a powerful interactive tool designed to transform raw YOLO detections into high-quality **Ground Truth** data. 

## 🎮 Basic Controls

| Action | Shortcut |
| :--- | :--- |
| **Previous / Next Frame** | `Left Arrow` / `Right Arrow` (or `A` / `D`) |
| **Seek +/- 10 Frames** | `J` / `L` |
| **Save Changes** | `S` |
| **Toggle Help Overlay** | `H` |
| **Quit** | `Q` |

---

## 📦 Interacting with Bounding Boxes

### 1. Creating a New Box
- **Action**: Click on an empty area of the frame.
- **Workflow**: A "dot" will appear where you click. **Immediately drag** your mouse to size the box correctly. 
- *Note: If you accidentally click without dragging, the "dot" box will be automatically removed when you release the mouse.*

### 2. Selecting a Box
- **Action**: Click inside any existing bounding box.
- **Visual**: The selected box will turn **Orange** and show **White Handles** at its four corners.

### 3. Modifying a Box
Once a box is selected:
- **Move**: Click and drag the **center** of the box.
- **Resize**: Click and drag any of the **four corner handles**.
- **Normalize**: Don't worry about drawing "backwards"—coordinates are automatically normalized (min/max) when you release the mouse.

### 4. Managing IDs
Unifying IDs across frames is critical for correct tracking evaluation.
- **Increment ID**: Press `]`
- **Decrement ID**: Press `[`
- **Quick Set (0-9)**: Press any number key `0` through `9` to instantly assign that ID.

### 5. Deleting a Box
- **Option A**: Select the box and press the `Delete` or `Backspace` key.
- **Option B**: **Right-click** inside (or very near) the box you want to remove. 

---

## 💡 Pro-Tips for Ground Truth
1. **Consistency is Key**: Ensure the same person has the same **ID** across every frame they appear in.
2. **Tight Fit**: Bounding boxes should tightly enclose the person for accurate IoU calculation.
3. **Save Frequently**: Press `S` every few minutes or after significant corrections to ensure your progress is captured.
4. **Dots**: If you see a tiny "dot" box you can't click easily, use the **Right-Click** nearby; it has a built-in safety margin for easy deletion.
