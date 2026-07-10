class DeviceNotConnectedError(Exception):
    """Raised when no Android device is connected."""
    pass

class ScreenCaptureError(Exception):
    """Raised when screen capturing went wrong"""
    pass