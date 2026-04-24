import numpy as np
import carla
import cv2 as cv

def cv_frame_renderer(rgb_raw:carla.libcarla.ServerSideSensor):
    img_array = np.frombuffer(rgb_raw.raw_data, dtype=np.uint8)
    img_array = img_array.reshape((rgb_raw.height, rgb_raw.width, 4))
    img_array = img_array[:, :, :3] # Drop alpha
    cv.imshow("CARLA Camera", img_array)
    cv.waitKey(1)