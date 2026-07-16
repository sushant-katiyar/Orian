from collections import defaultdict

def build_label_map(ocr_results: list[dict], template_results: list[dict], screen_height: int) -> dict:
    all_detections = ocr_results + template_results

    groups = defaultdict(list)
    for det in all_detections:
        groups[det["text"]].append(det)

    label_map = {}

    # Define boundaries for thirds
    top_boundary = screen_height / 3
    bottom_boundary = 2 * screen_height / 3

    for label, detections in groups.items():
        if len(detections) == 1:
            label_map[label] = detections[0]
            continue

        # Initialize buckets
        buckets = {
            "top": [],
            "middle": [],
            "bottom": []
        }

        for det in detections:
            cy = det["center_y"]
            if cy < top_boundary:
                buckets["top"].append(det)
            elif cy > bottom_boundary:
                buckets["bottom"].append(det)
            else:
                buckets["middle"].append(det)

        for position, bucket in buckets.items():
            if len(bucket) == 1:
                label_map[f"{label} {position}"] = bucket[0]
            elif len(bucket) > 1:
                # This guarantees "#1" is always the higher/left-most element
                sorted_bucket = sorted(bucket, key=lambda d: (d["center_y"], d.get("center_x", 0)))
                
                for i, det in enumerate(sorted_bucket, start=1):
                    label_map[f"{label} {position} #{i}"] = det

    return label_map