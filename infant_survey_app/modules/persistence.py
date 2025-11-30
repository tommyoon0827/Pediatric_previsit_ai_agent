
import json, os
from datetime import datetime

def save_response(payload: dict, base_dir="data/responses"):
    os.makedirs(base_dir, exist_ok=True)
    # 파일명에 시간을 넣어서 중복을 방지합니다 (예: resp_20251119_123000.json)
    fname = f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(base_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        # ensure_ascii=False: 한글이 깨지지 않게 저장
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
