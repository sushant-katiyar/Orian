import cv2
import pytesseract

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

            
       