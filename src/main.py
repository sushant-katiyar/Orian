from phone import AndroidPhone

from screen import ScreenCapture

phone = AndroidPhone()

screen = ScreenCapture(phone)

image = screen.capture()

print(image.shape)

print(image.dtype)