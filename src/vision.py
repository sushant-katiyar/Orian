import cv2
import pytesseract
import os

class Vision:

    def __init__(self):
        pass


    def _match_template(self, screenshot, template_path):
        """Core matching math shared by find_on_screen and scan_all_templates."""
        template = cv2.imread(template_path)

        if template is None:
            raise FileNotFoundError(f"Could not load template: {template_path}")

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        x_start, y_start = max_loc
        template_height, template_width = template.shape[:2]

        return {
            "max_val": max_val,
            "left": x_start,
            "top": y_start,
            "width": template_width,
            "height": template_height,
        }

    def find_on_screen(self, screenshot, template_path, threshold=0.8, raise_if_missing=True):
        match = self._match_template(screenshot, template_path)

        tap_x = match["left"] + (match["width"] // 2)
        tap_y = match["top"] + (match["height"] // 2)
        tap_target = (tap_x, tap_y)

        if match["max_val"] < threshold:
            if raise_if_missing:
                raise RuntimeError(f"Template not found on screen (best match: {match['max_val']:.2f}, threshold: {threshold})")
            else:
                return None

        return tap_target

    def scan_all_templates(self, screenshot, template_dir, threshold=0.8):
        results = []

        for filename in os.listdir(template_dir):
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            name = os.path.splitext(filename)[0]
            template_path = os.path.join(template_dir, filename)

            try:
                match = self._match_template(screenshot, template_path)
            except FileNotFoundError:
                continue

            if match["max_val"] < threshold:
                continue

            row = {
                "text": name,
                "confidence": match["max_val"],
                "left": match["left"],
                "top": match["top"],
                "width": match["width"],
                "height": match["height"],
                "center_x": match["left"] + (match["width"] // 2),
                "center_y": match["top"] + (match["height"] // 2),
            }
            results.append(row)
        return results

    def preprocess_for_ocr(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized_down_gray = cv2.resize(gray, (500,900), interpolation=cv2.INTER_AREA)
        
        thresh_standard = cv2.adaptiveThreshold(gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2)

        
        yield thresh_standard      

        thresh_inverted = cv2.adaptiveThreshold(gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 
            11, 
            2)

        
        yield thresh_inverted

    def filtering_data(self, data, min_confidence):
        processed = []
        for text, conf, left, top, width, height in zip(
    data['text'], data['conf'], data['left'], data['top'], data['width'], data['height']):
            conf=int(conf)
            if text.strip() and conf>=min_confidence:
                row={"text":text,"confidence":conf,"left":left,"top":top,"width":width,"height":height,"center_x":left+(width//2),"center_y":top+(height//2)}
                processed.append(row)
        return processed  
    
    def get_best_ocr_result(self, img, min_confidence):
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        filtered_data = self.filtering_data(data, min_confidence)
        if filtered_data:
            return filtered_data
        
        standard = self.preprocess_for_ocr(img)
        data = pytesseract.image_to_data(next(standard), output_type=pytesseract.Output.DICT)
        filtered_data = self.filtering_data(data, min_confidence)
        if filtered_data:
            return filtered_data
        
        data = pytesseract.image_to_data(next(standard), output_type=pytesseract.Output.DICT)
        filtered_data = self.filtering_data(data, min_confidence)
        if filtered_data:
            return filtered_data
        
        return []
    
    def find_text_on_screen(self,img, target_text,min_confidence=60):
        data = self.get_best_ocr_result(img,min_confidence)
        matching_dicts = [d for d in data if target_text.lower() in d["text"].lower()]

        if not matching_dicts:
            return []
    
        highest_conf = max(d["confidence"] for d in matching_dicts)
        best_matches = [d for d in matching_dicts if d["confidence"] == highest_conf]
    
        return best_matches

            
       