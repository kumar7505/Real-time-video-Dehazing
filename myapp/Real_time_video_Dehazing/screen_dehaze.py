import cv2
import time
import numpy as np
import mss  # Screen capture library
import pyautogui  # To get screen size
from haze_removal import HazeRemoval  # Import the dehazing class

def correct_color_space(image):
    """ Convert BGR to RGB for correct color processing """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def correct_color_space_reverse(image):
    """ Convert RGB back to BGR for OpenCV display """
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def normalize_image(image):
    """ Normalize image to [0,1] range """
    return np.clip(image.astype(np.float32) / 255.0, 0, 1)

def rescale_image(image):
    """ Convert normalized image back to uint8 format """
    return np.clip(image * 255, 0, 255).astype(np.uint8)

def adjust_contrast_saturation(image, contrast=0.5, gamma=1.1, saturation=1.2):
    """ Reduce contrast, adjust gamma, and control saturation """
    
    # ✅ Blend dehazed image with original to reduce harsh contrast
    image = cv2.addWeighted(image, contrast, image, 1 - contrast, 0)

    # ✅ Apply gamma correction to soften brightness
    gamma_table = np.array([(i / 255.0) ** (1 / gamma) * 255 for i in range(256)]).astype(np.uint8)
    image = cv2.LUT(image, gamma_table)

    # ✅ Convert to HSV to adjust saturation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= saturation  # Scale saturation
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    image = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return image

def capture_screen():
    """ Capture the screen using mss """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Capture primary screen
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)[:, :, :3]  # Convert BGRA -> BGR
        return img

def main():
    fps_target = 8  # Target FPS
    frame_time = 1.0 / fps_target  
    last_frame_time = time.time()

    hr = HazeRemoval()  # Haze removal instance

    while True:
        frame = capture_screen()  # Get screen capture

        current_time = time.time()
        if current_time - last_frame_time >= frame_time:
            last_frame_time = current_time  

            # ✅ Convert BGR to RGB for correct processing
            frame_rgb = correct_color_space(frame)

            # ✅ Normalize the image for dehazing
            frame_normalized = normalize_image(frame_rgb)

            # ✅ Run haze removal process
            hr.set_image(frame_normalized)
            hr.get_dark_channel()
            hr.get_air_light()
            hr.get_transmission()
            hr.guided_filter_opencv(r=20, eps=0.002)
            hr.recover()

            # ✅ Convert back to uint8 properly
            dehazed_frame = rescale_image(hr.dst)

            # ✅ Convert RGB back to BGR for OpenCV display
            dehazed_bgr = correct_color_space_reverse(dehazed_frame)

            # ✅ Adjust contrast and saturation for better look
            final_output = adjust_contrast_saturation(dehazed_bgr, contrast=0.5, gamma=1.1, saturation=1.2)

            # ✅ Display the result
            cv2.imshow('Dehazed Screen', final_output)

            # 🛑 Stop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
