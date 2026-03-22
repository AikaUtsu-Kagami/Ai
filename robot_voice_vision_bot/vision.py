from __future__ import annotations

import threading
import time
from dataclasses import dataclass

try:
    import cv2
except Exception:
    cv2 = None


@dataclass
class VisionSnapshot:
    faces_detected: int
    frame_width: int
    frame_height: int


class VisionEye:
    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self._capture = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest = VisionSnapshot(faces_detected=0, frame_width=0, frame_height=0)
        self._detector = None
        if cv2 is not None:
            self._detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

    def start(self) -> None:
        if cv2 is None:
            return
        self._capture = cv2.VideoCapture(self.camera_index)
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if self._capture:
            self._capture.release()

    def snapshot(self) -> VisionSnapshot:
        with self._lock:
            return self._latest

    def _loop(self) -> None:
        while self._running and self._capture and self._detector:
            ok, frame = self._capture.read()
            if not ok:
                time.sleep(0.05)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self._detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            h, w = gray.shape
            with self._lock:
                self._latest = VisionSnapshot(
                    faces_detected=len(faces),
                    frame_width=w,
                    frame_height=h,
                )
            time.sleep(0.1)
