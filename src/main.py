# just to check all parts of orian for now

from phone import AndroidPhone
from screen import ScreenCapture
from vision import Vision
import cv2


phone = AndroidPhone()
screen = ScreenCapture(phone)
vis = Vision()


img = screen.capture()
test = vis.find_text_on_screen(img,"Word")
print(test)

phone.tap(666,861)