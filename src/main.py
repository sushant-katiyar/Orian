# just to check all parts of orian for now

from phone import AndroidPhone
from screen import ScreenCapture
from vision import Vision

phone = AndroidPhone()

screen = ScreenCapture(phone)

image = screen.capture()

vis = Vision()
test=vis.find_on_screen(image,"Orian\\screenshots\\screenshot2.png",raise_if_missing=False)
print(test)

phone.tap(162, 1318)