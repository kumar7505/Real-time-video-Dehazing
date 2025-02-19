import PIL.Image as Image
import cv2
import numpy as np
import time
import os
from gf import guided_filter
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
    # Load image
        img = cv2.imread(image_path)
        self.src = img / 255.0  # Normalize image
        self.tran = np.zeros_like(self.src)  # Placeholder for transmission map

        # Downsample image to speed up processing
        self.downsample_image(factor=0.2)

        # Perform haze removal steps...
        self.guided_filter_opencv(r=60, eps=0.001)

        # Additional steps...
        self.show() 


    def enhance_visibility(self, alpha=1.5, beta=30):
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
        print("Starting to compute air light prior...")
        start = time.time()
        flat = self.dark.flatten()
        flat.sort()
        num = int(self.rows * self.cols * 0.001)
        threshold = flat[-num]
        tmp = self.src[self.dark >= threshold]
        tmp.sort(axis=0)
        self.Alight = tmp[-num:, :].mean(axis=0)
        print("Air light computation time:", time.time() - start)

    def get_transmission(self, omega=0.95):
        print("Starting to compute transmission...")
        start = time.time()
        # Vectorized operation
        normalized_src = self.src / self.Alight
        self.tran = 1. - omega * np.min(normalized_src, axis=2)
        print("Transmission computation time:", time.time() - start)

    def guided_filter_opencv(self, r=60, eps=0.001):
        print("Starting to compute guided filter transmission using OpenCV...")
        start = time.time()
        
        # Apply OpenCV's optimized guided filter for better performance
        self.gtran = cv2.ximgproc.guidedFilter(self.src.astype(np.float32), 
                                            self.tran.astype(np.float32), 
                                            r, eps)
        print("Guided filter time:", time.time() - start)


    def recover(self, t0=0.1):
        """ Recover the dehazed image """
        print("Starting recovering...")
        start = time.time()

        # Ensure transmission is not below t0 (avoiding division by zero)
        self.gtran = np.maximum(self.gtran, t0)

        # 🔍 Debugging: Print array shapes
        print("Shape of self.src:", self.src.shape)  # Expected: (height, width, 3)
        print("Shape of self.Alight before reshape:", self.Alight.shape)  # Expected: (3,)

        # Ensure Alight is properly reshaped
        self.Alight = self.Alight.reshape((1, 1, 3))  # Shape: (1,1,3)
        print("Shape of self.Alight after reshape:", self.Alight.shape)  # Expected: (1,1,3)

        # ✅ Ensure transmission t has the correct shape
        t = self.gtran.squeeze()  # Remove unnecessary dimensions
        t = t[:, :, np.newaxis]  # Ensure shape (height, width, 1)
        
        print("Shape of self.gtran after squeeze:", self.gtran.shape)  # Expected: (height, width) or (height, width, 1)
        print("Shape of t after adding new axis:", t.shape)  # ✅ Expected: (height, width, 1)

        # ✅ Apply the dehazing equation
        self.dst = (self.src - self.Alight) / t + self.Alight

        # ✅ Clip values to keep them within [0,1] range
        self.dst = np.clip(self.dst, 0, 1)

        # ✅ Convert to uint8 for proper image saving
        self.dst = (self.dst * 255).astype(np.uint8)

        print("Recovery time:", time.time() - start)


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
