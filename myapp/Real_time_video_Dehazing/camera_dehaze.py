import cv2
import time
import numpy as np
from haze_removal import HazeRemoval  # Import the dehazing class

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

def main():
    cap = cv2.VideoCapture(0)  # Use 0 for default camera

    if not cap.isOpened():
        print("Error: Could not access the camera.")
        return
    # ✅ Set manual exposure to prevent real-time auto-adjustments
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)

    fps_target = 8  # Target FPS
    frame_time = 1.0 / fps_target  
    last_frame_time = time.time()

    hr = HazeRemoval()  # Haze removal instance

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        current_time = time.time()
        if current_time - last_frame_time >= frame_time:
            last_frame_time = current_time  

            # ✅ Convert BGR to RGB for correct color processing
            frame_rgb = correct_color_space(frame)

            # ✅ Normalize the image for dehazing
            frame_normalized = normalize_image(frame_rgb)

            # ✅ Debugging Step 1: Check the Normalized Frame
            cv2.imshow("Step 1: Normalized Frame", frame_normalized)

            # ✅ Run haze removal process
            hr.set_image(frame_normalized)
            hr.get_dark_channel()
            hr.get_air_light()

            # ✅ Reduce color contrast by tweaking `A`
            if hasattr(hr, 'A'):
                hr.A = np.clip(hr.A, 0.85, 1.0)  # Allow more natural brightness

            hr.get_transmission()
            hr.guided_filter_opencv(r=20, eps=0.002)  # Increased `eps` to smooth better
            hr.recover()

            # ✅ Debugging Step 2: Check the Haze-Removed Image Before Rescaling
            print("Before rescaling - Min:", np.min(hr.dst), "Max:", np.max(hr.dst))
            cv2.imshow("Step 2: After Haze Removal", hr.dst)

            # ✅ Normalize only if needed
            if np.max(hr.dst) > 1:  
                dehazed_frame = hr.dst / np.max(hr.dst)  # Scale values between 0 and 1
            else:
                dehazed_frame = np.clip(hr.dst, 0, 1)  # Clip as a safety check

            # ✅ Convert back to uint8 properly
            dehazed_rescaled = rescale_image(dehazed_frame)

            # ✅ Convert RGB back to BGR for OpenCV display
            dehazed_rescaled_bgr = correct_color_space_reverse(dehazed_rescaled)

            # ✅ Debugging Step 3: Check the Rescaled Image
            cv2.imshow('Step 3: Rescaled Image', dehazed_rescaled_bgr)

            # 🛑 Stop here to check if the issue is before/after this step
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
