import cv2
import numpy as np
from myapp.Real_time_video_Dehazing.haze_removal import HazeRemoval

def dehaze_camera():
    cap = cv2.VideoCapture(0)  # Open default camera (change to 1 if using an external camera)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        
        # Apply haze removal
        dehazed_frame = process_frame_with_haze_removal(frame)

        # Display original and processed frames side by side
        combined_frame = np.hstack((frame, dehazed_frame))
        cv2.imshow("Original vs Dehazed", combined_frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def process_frame_with_haze_removal(frame):
    try:
        hr = HazeRemoval()
        
        # Convert frame from BGR (OpenCV default) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hr.src = frame_rgb.astype(np.float64) / 255.0  # Normalize
        hr.rows, hr.cols, _ = hr.src.shape

        # Apply dehazing process
        hr.get_dark_channel()
        hr.get_air_light()
        hr.get_transmission()
        hr.guided_filter_opencv(r=60, eps=0.001)
        hr.recover()
        hr.enhance_visibility(alpha=1.5, beta=30)

        # Convert back to OpenCV BGR format
        result = (hr.dst * 255).astype(np.uint8)
        result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

        return result

    except Exception as e:
        print(f"Error during haze removal: {e}")
        return frame  # Return the original frame if an error occurs

if __name__ == "__main__":
    dehaze_camera()
