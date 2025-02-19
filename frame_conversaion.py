import cv2
import os

# Create a folder to store frames if it doesn't exist
#folder_path = 'frames'
#if not os.path.exists(folder_path):
    #os.makedirs(folder_path)

# Open the video file
vidcap = cv2.VideoCapture(r'C:\Users\ACER\Downloads\miniproframes\miniprojectimg\image-dehaze-main\video.mp4')

success, image = vidcap.read()
count = 0
while success:
    # Save frame as JPEG file in the folder
    cv2.imwrite(os.path.join(r"C:\Users\ACER\Downloads\miniproframes\miniprojectimg\image-dehaze-main\frames", "frame%d.jpg" % count), image)
    success, image = vidcap.read()
    print('Read a new frame: ', success)
    count += 1

vidcap.release()  # Release the video capture object