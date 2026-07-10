import cv2
import numpy as np
from exceptions import ScreenCaptureError

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
        
        if png.size==0:
            raise ScreenCaptureError("No data returned from screencap — check device connection and screen state")
        
        image = cv2.imdecode(
            png,
            cv2.IMREAD_COLOR
            )

        if image is None:
            raise RuntimeError("Failed to capture screen: could not decode image data")
        
        return image
    
