import cv2
import os
from datetime import datetime

os.makedirs('static/snapshots', exist_ok=True)

def test_cameras(max_index=6):
    results = []
    for i in range(max_index):
        print(f"Testing camera index: {i}")
        cap = cv2.VideoCapture(i)
        opened = cap.isOpened()
        print(f"  isOpened: {opened}")
        info = {'index': i, 'opened': opened, 'read': False, 'shape': None, 'error': None, 'saved': None}
        if opened:
            try:
                # give the camera a tiny moment to warm up
                for _ in range(3):
                    ret, frame = cap.read()
                ret, frame = cap.read()
                info['read'] = bool(ret)
                if ret and frame is not None:
                    info['shape'] = frame.shape
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    filename = f"static/snapshots/cam_{i}_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    info['saved'] = filename
                    print(f"  Captured frame shape: {frame.shape}")
                    print(f"  Saved snapshot: {filename}")
                else:
                    print("  Failed to read frame from camera")
            except Exception as e:
                info['error'] = str(e)
                print(f"  Error while reading/saving frame: {e}")
            finally:
                cap.release()
        results.append(info)
    return results


if __name__ == '__main__':
    print("Running camera test (indices 0-5). This may take a few seconds...")
    res = test_cameras(6)
    print("\nSummary:\n")
    for r in res:
        print(r)
