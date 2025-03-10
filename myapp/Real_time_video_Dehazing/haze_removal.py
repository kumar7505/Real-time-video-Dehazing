import PIL.Image as Image
import cv2
import numpy as np
import time
import os
from myapp.Real_time_video_Dehazing.gf import guided_filter  # Assuming your haze removal script is in this file
# from gf import guided_filter
from numba import jit, prange
import matplotlib.pyplot as plt
import sys

class HazeRemoval(object):
    def __init__(self, omega=0.95, t0=0.1, radius=7, r=20, eps=0.001):
        self.src = None
        self.dst = None
        self.rows = 0
        self.cols = 0
        self.omega = omega
        self.t0 = t0
        self.radius = radius
        self.r = r
        self.eps = eps

    def set_image(self, image):
        """Sets the image for processing and initializes the image dimensions."""
        self.src = image
        self.rows, self.cols, _ = self.src.shape  # Set the rows and cols based on the image size
        self.dst = np.zeros_like(self.src)  # Initialize destination image

    def get_air_light(self):
        # Now self.rows and self.cols are initialized, so this method should work fine
        num = int(self.rows * self.cols * 0.001)
        # Continue with the rest of the method as usual
    def downsample_image(self, factor=0.2):
        """ Downsample the image and transmission map to speed up processing. """
        height, width = self.src.shape[:2]
        new_size = (int(width * factor), int(height * factor))
        self.src_downsampled = cv2.resize(self.src, new_size)
        self.tran_downsampled = cv2.resize(self.tran, new_size, interpolation=cv2.INTER_LINEAR)

    def process(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Error loading image. Ensure the file exists and is a valid image.")

        self.src = img / 255.0  # Normalize image
        self.tran = np.zeros_like(self.src)  # Placeholder for transmission map

        # Downsample image safely
        self.downsample_image(factor=0.2)

        # Proceed with haze removal steps...
        self.guided_filter_opencv(r=60, eps=0.001)
        self.show()

    def enhance_visibility(self, alpha=1.3, beta=10):
        """Enhances the contrast and brightness of the dehazed image."""
        self.dst = cv2.convertScaleAbs(self.dst, alpha=alpha, beta=beta)


    def open_image(self, img_path):
        print(f"Opening image: {img_path}")
        self.img_path = img_path  # ✅ Store file path
        img = Image.open(img_path)
        
        # Convert image to RGB if it's grayscale
        self.src = np.array(img).astype(np.float64) / 255.
        
        # Check if the image is grayscale or color
        if len(self.src.shape) == 2:  # Grayscale
            self.src = np.repeat(self.src[:, :, np.newaxis], 3, axis=2)  # Convert to 3 channels
            print("Converted grayscale to RGB.")
        
        self.rows, self.cols, _ = self.src.shape
        self.dark = np.zeros((self.rows, self.cols), dtype=np.float64)
        self.Alight = np.zeros(3, dtype=np.float64)
        self.tran = np.zeros((self.rows, self.cols), dtype=np.float64)
        self.dst = np.zeros_like(self.src, dtype=np.float64)



    def get_dark_channel(self, radius=7):
        print("Starting to compute dark channel prior...")
        start = time.time()
        tmp = self.src.min(axis=2)
        kernel = np.ones((radius*2 + 1, radius*2 + 1))
        self.dark = cv2.erode(tmp, kernel)
        print("Dark channel computation time:", time.time() - start)

    def get_air_light(self):
        print("Starting air light estimation...")
        start = time.time()

        num = max(10, int(self.rows * self.cols * 0.001))  # Ensure at least 10 pixels
        flat = np.sort(self.dark.flatten())[-num:]  # Get brightest dark pixels

        selected_pixels = self.src[self.dark >= flat.min()]
        
        if selected_pixels.size == 0:
            raise ValueError("No valid pixels found for air light estimation.")

        self.Alight = np.mean(selected_pixels[:num], axis=0)  # Improved stability
        print("Air light computed:", self.Alight)
        print("Computation time:", time.time() - start)



    def get_transmission(self, omega=0.95):
        print("Starting to compute transmission...")
        start = time.time()

        normalized_src = self.src / (self.Alight + 1e-6)  # Avoid division by zero
        self.tran = 1. - omega * np.min(normalized_src, axis=2)

        # Reduce lower bound to allow darker areas to remain
        self.tran = np.clip(self.tran, 0.1, 1)  # Lowered from 0.2 to 0.1
        print("Transmission computed with improved minimum threshold")
        print("Transmission computation time:", time.time() - start)



    def guided_filter_opencv(self, r=60, eps=0.001):
        print("Starting to compute guided filter transmission using OpenCV...")
        start = time.time()
        
        # Apply OpenCV's optimized guided filter for better performance
        self.gtran = cv2.ximgproc.guidedFilter(self.src.astype(np.float32), 
                                            self.tran.astype(np.float32), 
                                            r, eps)
        print("Guided filter time:", time.time() - start)

    def recover(self, t0=0.1, gamma=1.2, saturation_scale=1.2):
        print("Starting recovery process...")
        start = time.time()

        self.gtran = np.maximum(self.gtran, t0)

        # Reduce air light impact to prevent excessive brightness
        adjusted_A = self.Alight * 0.85  # Adjust air light contribution
        t = self.gtran[:, :, np.newaxis]
        self.dst = (self.src - adjusted_A) / t + adjusted_A
        self.dst = np.clip(self.dst, 0, 1)

        # Dynamic gamma adjustment based on image brightness
        avg_brightness = np.mean(self.dst)
        gamma = 1.5 if avg_brightness < 0.3 else 1.2

        # Optimized gamma correction using LUT
        look_up_table = np.array([(i / 255.0) ** (1 / gamma) * 255 for i in range(256)], dtype=np.uint8)
        self.dst = cv2.LUT((self.dst * 255).astype(np.uint8), look_up_table)

        # Adjust saturation
        hsv = cv2.cvtColor(self.dst, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] *= saturation_scale
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        self.dst = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        print("Recovery completed in", time.time() - start, "seconds")




    def show(self):
        dehazed_dir = os.path.join(os.path.dirname(__file__), "dehazed")
        if not os.path.exists(dehazed_dir):
            os.makedirs(dehazed_dir)

        # Save the final image (in RGB order: BGR to RGB)
        cv2.imwrite(os.path.join(dehazed_dir, "dst.jpg"), self.dst[:, :, (2, 1, 0)])

        # Save intermediary images for inspection (optional)
        cv2.imwrite("img/src.jpg", (self.src * 255).astype(np.uint8)[:, :, (2, 1, 0)])
        cv2.imwrite("img/dark.jpg", (self.dark * 255).astype(np.uint8))
        cv2.imwrite("img/tran.jpg", (self.tran * 255).astype(np.uint8))
        cv2.imwrite("img/gtran.jpg", (self.gtran * 255).astype(np.uint8))
        cv2.imwrite("img/dst.jpg", self.dst[:, :, (2, 1, 0)])

        # Use self.img_path for saving the image with its original name
        im_path = self.img_path
        im_name_ext = os.path.basename(im_path)
        im_name, im_ext = os.path.splitext(im_name_ext)

        cv2.imwrite(f"./dehazed-new/{im_name}_dehazed{im_ext}", self.dst)

if __name__ == '__main__':
    print('Starting haze removal...')
    
    # Record the start time
    start_time = time.time()
    
    hr = HazeRemoval()
    hr.open_image(sys.argv[1])
    hr.get_dark_channel()
    hr.get_air_light()
    hr.get_transmission()
    hr.guided_filter_opencv(r=60, eps=0.001)  # Use the correct method
    hr.recover()
    hr.enhance_visibility(alpha=1.5, beta=30)
    hr.show()
    
    # Record the end time
    end_time = time.time()
    
    # Calculate the total time taken
    total_time = end_time - start_time
    print(f"Haze removal completed. Total time taken: {total_time:.4f} seconds.")
