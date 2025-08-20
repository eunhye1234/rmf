'''
Sample Usage:-
python calibration.py --dir calibration_checkerboard/ --square_size 0.024
'''

import numpy as np
import cv2
import os
import argparse


def calibrate(dirpath, square_size, width, height, visualize=False):
    """ Apply camera calibration operation for images in the given directory path. """

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
    objp = np.zeros((height*width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    objp = objp * square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    
    # --- ADDED: Variable to store the image shape ---
    img_shape = None

    images = os.listdir(dirpath)
    print(f"Found {len(images)} images in '{dirpath}'")

    for fname in images:
        img = cv2.imread(os.path.join(dirpath, fname))
        
        if img is None:
            print(f"[X] Failed to load image: {fname}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # --- ADDED: Store the shape from the first valid image ---
        if img_shape is None:
            img_shape = gray.shape[::-1]

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (width, height), None)

        # If found, add object points, image points (after refining them)
        if ret:
            print(f"[O] Checkerboard found: {fname}")
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            if visualize:
                drawn_img = cv2.drawChessboardCorners(img.copy(), (width, height), corners2, ret)
                cv2.imshow('img', drawn_img)
                cv2.waitKey(500) # Show for 0.5 seconds
        else:
            print(f"[X] Checkerboard not found: {fname}")

    if visualize:
        cv2.destroyAllWindows()
    
    # --- ADDED: Check if any points were found before calibrating ---
    if not objpoints or not imgpoints:
        print("\n[ERROR] Calibration failed. No checkerboard corners were detected in any of the images.")
        print("Please check the image directory and the --width/--height arguments.")
        return [False, None, None, None, None]

    print(f"\nCalibrating using {len(objpoints)} valid images...")
    # --- CHANGED: Use the stored img_shape instead of gray.shape ---
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_shape, None, None)

    return [ret, mtx, dist, rvecs, tvecs]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dir", required=True, help="Path to folder containing checkerboard images for calibration")
    ap.add_argument("-w", "--width", type=int, help="Width of checkerboard (default=9)",  default=9)
    ap.add_argument("-t", "--height", type=int, help="Height of checkerboard (default=6)", default=6)
    ap.add_argument("-s", "--square_size", type=float, default=1, help="Length of one edge (in metres)")
    ap.add_argument("-v", "--visualize", type=str, default="False", help="To visualize each checkerboard image")
    args = vars(ap.parse_args())
    
    dirpath = args['dir']
    # 2.4 cm == 0.024 m
    # square_size = 0.024
    square_size = args['square_size']

    width = args['width']
    height = args['height']

    if args["visualize"].lower() == "true":
        visualize = True
    else:
        visualize = False

    ret, mtx, dist, rvecs, tvecs = calibrate(dirpath, square_size, visualize=visualize, width=width, height=height)

    print(mtx)
    print(dist)

    np.save("calibration_matrix", mtx)
    np.save("distortion_coefficients", dist)
