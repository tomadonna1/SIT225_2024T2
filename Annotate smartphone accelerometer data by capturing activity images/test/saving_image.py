import cv2
import os
import numpy as np

# Create a simple white image
test_image = 255 * np.ones((720, 1280, 3), dtype=np.uint8) 

# Specify a simple save path with a file name and extension
save_path = r"C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.3D\test\test_image.jpg"

# Try to save the image
if cv2.imwrite(save_path, test_image):
    print(f"Image saved successfully to {save_path}")
else:
    print(f"Failed to save image to {save_path}")
