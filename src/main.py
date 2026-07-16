# just to check all parts of orian for now

from phone import AndroidPhone
from screen import ScreenCapture
from vision import Vision
import nerve as nv
from PIL import Image

phone = AndroidPhone()
screen = ScreenCapture(phone)
vis = Vision()


img = screen.capture()
height,width,channel = img.shape

test = vis.get_best_ocr_result(img)
test2=vis.scan_all_templates(img,"Orian/templates")
nerve = nv.build_label_map(test,test2,height)
print(nerve)

