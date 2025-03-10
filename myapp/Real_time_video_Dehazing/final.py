import cv2
import os
import numpy as np
from haze_removal import HazeRemoval  # Import the dehazing class
import tkinter as tk
from tkinter import filedialog


def correct_color_space(image):
    """ Convert BGR to RGB for correct color processing """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def correct_color_space_reverse(image):
    """ Convert RGB back to BGR for OpenCV display """
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def normalize_image(image):
    """ Ensure correct normalization without over-scaling """
    return np.clip(image.astype(np.float32) / 255.0, 0, 1)


def rescale_image(image):
    """ Convert normalized image back to uint8 format """
    return np.clip(image * 255, 0, 255).astype(np.uint8)


def process_frame_with_haze_removal(frame):
    # Convert the frame to RGB for correct color processing
    frame_rgb = correct_color_space(frame)

    # Normalize the image for haze removal
    frame_normalized = normalize_image(frame_rgb)

    # Initialize HazeRemoval class and apply steps
    hr = HazeRemoval()
    hr.set_image(frame_normalized)
    hr.get_dark_channel()
    hr.get_air_light()
    hr.get_transmission()
    hr.guided_filter_opencv(r=60, eps=0.001)  # Apply guided filter
    hr.recover()

    # Scale the processed frame back to the correct range
    if np.max(hr.dst) > 1:
        dehazed_frame = hr.dst / np.max(hr.dst)  # Normalize if necessary
    else:
        dehazed_frame = np.clip(hr.dst, 0, 1)

    # Rescale the dehazed frame back to uint8 for OpenCV display
    dehazed_rescaled = rescale_image(dehazed_frame)

    # Convert the dehazed frame back to BGR for saving/displaying
    dehazed_rescaled_bgr = correct_color_space_reverse(dehazed_rescaled)

    return dehazed_rescaled_bgr  # Return the final dehazed frame


def extract_frames(video_path):
    if not video_path:
        print("No video selected.")
        return
    
    folder_path = os.path.join(os.path.dirname(video_path), 'frames')
    os.makedirs(folder_path, exist_ok=True)
    
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    
    while success:
        frame_path = os.path.join(folder_path, f"frame{count}.jpg")
        cv2.imwrite(frame_path, image)
        success, image = vidcap.read()
        print(f'Saved {frame_path}')
        count += 1
    
    vidcap.release()
    print(f"Frames saved in: {folder_path}")


def frames_to_video(frames_folder, output_video_path, fps=30):
    frame_files = [f for f in os.listdir(frames_folder) if f.endswith('.jpg') or f.endswith('.png')]
    frame_files.sort()  # Sort files numerically if they have numerical names
    
    # Create a VideoWriter object
    first_frame_path = os.path.join(frames_folder, frame_files[0])
    first_frame = cv2.imread(first_frame_path)
    height, width, _ = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Define codec for video output
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    for frame_file in frame_files:
        frame_path = os.path.join(frames_folder, frame_file)
        frame = cv2.imread(frame_path)

        # Apply haze removal to the frame
        dehazed_frame = process_frame_with_haze_removal(frame)
        
        # Write the dehazed frame to the video
        out.write(dehazed_frame)
    
    out.release()  # Release VideoWriter object
    print("Video created successfully!")


def start_extraction():
    video_path = entry_path.get()
    extract_frames(video_path)  # Extract frames from video
    frames_folder = os.path.join(os.path.dirname(video_path), 'frames')
    output_video_path = os.path.join(os.path.dirname(video_path), 'output.mp4')
    print('frames_folder', frames_folder)
    print('output_video_path', output_video_path)
    frames_to_video(frames_folder, output_video_path, fps=5)  # Recompile the processed frames back into a video


def browse_video():
    # Open a file dialog to select a video file
    video_path = filedialog.askopenfilename(
        title="Select a video file",
        filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")]
    )
    
    # Set the selected file path in the entry field
    entry_path.delete(0, tk.END)  # Clear any existing text in the entry field
    entry_path.insert(0, video_path)  # Insert the selected file path


# Create Tkinter GUI
root = tk.Tk()
root.title("Video Frame Extractor & Dehazer")

label = tk.Label(root, text="Enter video path or browse:")
label.pack(pady=5)

entry_path = tk.Entry(root, width=50)
entry_path.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=browse_video)
browse_button.pack(pady=5)

extract_button = tk.Button(root, text="Submit", command=start_extraction)
extract_button.pack(pady=5)

root.mainloop()
