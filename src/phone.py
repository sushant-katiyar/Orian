# Stream       Purpose
# stdout       Normal, expected output/data
# stderr       Errors, warnings, diagnostics
# returncode 0 = success, 
# anything else = failure (the specific number can mean different things per-tool)

import subprocess
from exceptions import DeviceNotConnectedError
import os

class AndroidPhone:
    def __init__(self):
        self.device_id = None

    def run_shell(self,*args):

        self._ensure_connected()
        return self.run_adb("shell", *args)

    def run_adb(self, *args):

        command = ["adb"] + list(args)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )


        return result

    def _ensure_connected(self):
        if not self.is_connected():
            raise DeviceNotConnectedError("No Android device connected.")
    
    def devices(self):
        return self.run_adb("devices")
    
    def home(self):
        return self.run_shell("input", "keyevent", "3")
    
    def back(self):
        return self.run_shell("input", "keyevent", "4")
    
    def tap(self,x,y):
        return self.run_shell("input","tap",str(x),str(y))
    
    def swipe(self, x1, y1, x2, y2):
        return self.run_shell("input","swipe",str(x1),str(y1),str(x2),str(y2))
    
    def power(self):
        return self.run_shell("input","keyevent","26")
    
    def volume_up(self):
        return self.run_shell("input","keyevent","24")

    def volume_down(self):
        return self.run_shell("input","keyevent","25")

    def get_serial(self):
        serial = self.run_adb("get-serialno")
        return serial.stdout.strip()
    
    def screenshot(self, local_path = "HiddenObjectAi/screenshots/screen.png"):
        os.makedirs(os.path.dirname(local_path),exist_ok=True)
        device_path = "/sdcard/screen.png"
        self.run_shell("screencap","-p",device_path)
        self.run_adb("pull",device_path,local_path)
        return local_path
    
    def is_connected(self):
        result = self.run_adb("devices")
        lines = result.stdout.strip().splitlines()
        return any(
            parts and parts[-1] == "device" 
            for line in lines[1:] for parts in [line.split()])
        