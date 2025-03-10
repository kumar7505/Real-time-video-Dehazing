import cv2
import os

def frames_to_video(frames_folder, output_video_path, fps=30):
    frame_files = [f for f in os.listdir(frames_folder) if f.endswith('.jpg') or f.endswith('.png')]
    frame_files.sort()  # Sort files numerically if they have numerical names
    
    frame = cv2.imread(os.path.join(frames_folder, frame_files[0]))
    height, width, _ = frame.shape
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Define the codec for the video output
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))  # Initialize VideoWriter object
    
    for frame_file in frame_files:
        frame_path = os.path.join(frames_folder, frame_file)
        frame = cv2.imread(frame_path)
        out.write(frame)  # Write frame to video    
    
    out.release()  # Release VideoWriter object
    print("Video created successfully!")

# Example usage:
frames_folder = r'C:\Users\Prasanth\sta\Django\Dehazer\myapp\Real_time_video_Dehazing\dehazed'
output_video_path = r'C:\Users\Prasanth\sta\Django\Dehazer\myapp\Real_time_video_Dehazing\output.mp4'
frames_to_video(frames_folder, output_video_path,fps=5)