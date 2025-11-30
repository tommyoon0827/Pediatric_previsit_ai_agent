
import json, os
from datetime import datetime

def save_response(payload: dict, base_dir="data/responses"):
    os.makedirs(base_dir, exist_ok=True)
    # Include time in filename to prevent duplicates (e.g., resp_20251119_123000.json)
    fname = f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(base_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        # ensure_ascii=False: Save non-ASCII characters correctly
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
