import cv2
import numpy as np


class ScreenCapture:

    def __init__(self, phone):
        self.phone = phone

    def capture(self):

        result = self.phone.run_adb(
            "exec-out",
            "screencap",
            "-p",
            text=False
            )

        png = np.frombuffer(
            result.stdout,
            dtype=np.uint8
            )

        image = cv2.imdecode(
            png,
            cv2.IMREAD_COLOR
            )

        return image