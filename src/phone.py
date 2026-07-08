# Stream       Purpose
# stdout       Normal, expected output/data
# stderr       Errors, warnings, diagnostics
# returncode 0 = success, 
# anything else = failure (the specific number can mean different things per-tool)

import subprocess
from exceptions import DeviceNotConnectedError

class AndroidPhone:
    def __init__(self):
        self.device_id = None
    _NO_CONNECTION_NEEDED = {"devices", "version"}

    def run_adb(self, *args):
        if args and args[0] not in self._NO_CONNECTION_NEEDED:
            self._ensure_connected()

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
        self.run_adb("shell", "input", "keyevent", "3")
    
    def back(self):
        self.run_adb("shell", "input", "keyevent", "4")
    
    def tap(self,x,y):
        self.run_adb("shell","input","tap",str(x),str(y))
    
    def swipe(self, x1, y1, x2, y2):
        self.run_adb("shell","input","swipe",str(x1),str(y1),str(x2),str(y2))
    
    def power(self):
        self.run_adb("shell","input","keyevent","26")
    
    def volume_up(self):
        self.run_adb("shell","input","keyevent","24")

    def volume_down(self):
        self.run_adb("shell","input","keyevent","25")

    def get_serial(self):
        serial = self.run_adb("get-serialno")
        return serial.stdout.strip()
    
    def is_connected(self):
        result = self.run_adb("devices")
        lines = result.stdout.strip().splitlines()
        return any(line.split()[-1]=="device" for line in lines[1:])
        