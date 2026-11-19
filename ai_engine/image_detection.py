import colorsys
import math
import os
from functools import lru_cache
from threading import Lock

from ultralytics import YOLO

_model = None
_model_lock = Lock()
_inference_lock = Lock()
_MIN_SUGGESTION_CONFIDENCE = 0.45

_CATEGORY_BY_LABEL = {
    "backpack": "Bags & accessories",
    "handbag": "Bags & accessories",
    "suitcase": "Bags & accessories",
    "tie": "Clothing",
    "umbrella": "Bags & accessories",
    "book": "Documents & IDs",
    "cell phone": "Electronics",
    "laptop": "Electronics",
    "remote": "Electronics",
    "keyboard": "Electronics",
    "mouse": "Electronics",
    "bottle": "Drinkware",
    "cup": "Drinkware",
    "wine glass": "Drinkware",
    "sports ball": "Sports equipment",
    "baseball bat": "Sports equipment",
    "baseball glove": "Sports equipment",
    "tennis racket": "Sports equipment",
    "skateboard": "Sports equipment",
}


def _color_name(rgb):
    red, green, blue = (channel / 255 for channel in rgb)
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    hue *= 360
    if value < 0.16:
        return "Black"
    if saturation < 0.18:
        if value > 0.9:
            return "White"
        if value < 0.38:
            return "Dark gray"
        if value > 0.72:
            return "Light gray"
        return "Gray"
    if 18 <= hue < 42 and value < 0.62:
        return "Brown"
    if hue < 12 or hue >= 345:
        return "Red"
    if hue < 42:
        return "Orange"
    if hue < 68:
        return "Yellow"
    if hue < 165:
        return "Green"
    if hue < 195:
        return "Cyan"
    if hue < 255:
        return "Blue"
    if hue < 290:
        return "Purple"
    return "Pink"


def _estimate_object_color(image, box):
    x1, y1, x2, y2 = (int(value) for value in box.xyxy[0].tolist())
    image_width, image_height = image.size
    x1, x2 = max(0, x1), min(image_width, x2)
    y1, y2 = max(0, y1), min(image_height, y2)
    if x2 - x1 < 4 or y2 - y1 < 4:
        return ""

    object_crop = image.crop((x1, y1, x2, y2))
    crop_width, crop_height = object_crop.size
    margin_x, margin_y = int(crop_width * 0.12), int(crop_height * 0.12)
    if crop_width - margin_x * 2 >= 4 and crop_height - margin_y * 2 >= 4:
        object_crop = object_crop.crop((
            margin_x,
            margin_y,
            crop_width - margin_x,
            crop_height - margin_y,
        ))

    sample = object_crop.resize((48, 48)).quantize(colors=8).convert("RGB")
    colors = sample.getcolors(48 * 48)
    if not colors:
        return ""
    count, rgb = max(colors, key=lambda color: color[0])
    if count / (48 * 48) < 0.16:
        return ""
    return _color_name(rgb)


def _load_model(model_path):
    global _model
    with _model_lock:
        if _model is None:
            _model = YOLO(model_path)
    return _model


def suggest_details(image, model_path):
    model = _load_model(model_path)
    with _inference_lock:
        result = model.predict(source=image, conf=0.25, device="cpu", verbose=False)[0]
    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0].item())
        label = result.names[class_id]
        detections.append({
            "label": label,
            "confidence": round(float(box.conf[0].item()), 3),
            "category": _CATEGORY_BY_LABEL.get(label, "Other items"),
            "color": _estimate_object_color(image, box),
        })
    detections.sort(key=lambda item: item["confidence"], reverse=True)

    candidate = detections[0] if detections else None
    top = (
        candidate
        if candidate and candidate["confidence"] >= _MIN_SUGGESTION_CONFIDENCE
        else None
    )
    if top:
        notice = "Suggestions are based on the visible object. Check every field; color can be affected by lighting."
    elif candidate:
        color_note = (
            f" A tentative color estimate is {candidate['color']}; please verify it."
            if candidate["color"] else ""
        )
        notice = (
            f"Low confidence ({round(candidate['confidence'] * 100)}%). "
            "Item name, type, and category were left unchanged because the object may be misidentified. "
            f"Enter those details manually.{color_note}"
        )
    else:
        notice = "No supported object was detected. Please enter the item details manually."
    return {
        "item_name": top["label"].replace("_", " ").title() if top else "",
        "category": top["category"] if top else "",
        "item_type": top["label"].replace("_", " ").title() if top else "",
        "color": top["color"] if top else candidate["color"] if candidate else "",
        "detections": detections[:5],
        "notice": notice,
    }


@lru_cache(maxsize=256)
def _cached_image_embedding(image_path, modified_ns, file_size, model_path):
    model = _load_model(model_path)
    with _inference_lock:
        embeddings = model.embed(source=image_path, verbose=False)
    if not embeddings:
        return ()
    values = embeddings[0].detach().cpu().flatten().tolist()
    if not values or not all(math.isfinite(value) for value in values):
        return ()
    return tuple(float(value) for value in values)


def image_embedding(image_path, model_path):
    if not image_path or not model_path or not os.path.isfile(model_path):
        return None
    absolute_path = os.path.abspath(image_path)
    try:
        file_stat = os.stat(absolute_path)
    except OSError:
        return None
    embedding = _cached_image_embedding(
        absolute_path,
        file_stat.st_mtime_ns,
        file_stat.st_size,
        os.path.abspath(model_path),
    )
    return embedding or None
