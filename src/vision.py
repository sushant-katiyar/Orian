import cv2

class Vision:

    def __init__(self):
        pass

    def find_on_screen(self, screenshot, template_path, threshold=0.8, raise_if_missing=True):
        template = cv2.imread(template_path)

        if template is None:
            raise FileNotFoundError(f"Could not load template: {template_path}")

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Unpack the top-left corner from max_loc
        x_start, y_start = max_loc

        # Get height and width from template.shape
        # Remember: OpenCV shapes are (height, width, channels)
        template_height, template_width = template.shape[:2]

        # Calculate the center coordinates
        tap_x = x_start + (template_width // 2)
        tap_y = y_start + (template_height // 2)

        # calculating the tap target
        tap_target = (tap_x, tap_y)

        # checking against threshold
        if max_val<threshold:
            if raise_if_missing:
                raise RuntimeError(f"Template not found on screen (best match: {max_val:.2f}, threshold: {threshold})")
            else:
                return None
        # returning the tap_target
        return tap_target
             