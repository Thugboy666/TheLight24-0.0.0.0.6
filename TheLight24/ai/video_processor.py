import os, time
import cv2
import numpy as np
from ai.utils import load_env, ensure_dirs

def main():
    ensure_dirs()
    env = load_env()
    cam_index = int(env.get("CAM_INDEX","0"))

    cap = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(cam_index)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    face_cascade_path = "data/models/haarcascades/haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(face_cascade_path) if os.path.exists(face_cascade_path) else None

    prev_gray = None
    win = "TheLight24 – Webcam (locale)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Face detection
        if face_cascade is not None:
            faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60,60))
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

        # Motion via optical flow
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None,
                                                0.5, 3, 15, 3, 5, 1.2, 0)
            mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
            motion = np.uint8(np.clip(mag*10, 0, 255))
            motion_color = cv2.applyColorMap(motion, cv2.COLORMAP_TURBO)
            mh, mw = motion_color.shape[:2]
            frame[0:mh//3, 0:mw//3] = cv2.resize(motion_color, (mw//3, mh//3))

        prev_gray = gray

        cv2.imshow(win, frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
