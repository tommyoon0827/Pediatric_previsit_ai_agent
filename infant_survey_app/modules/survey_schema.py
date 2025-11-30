
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# 질문 하나하나의 설계도
class Question(BaseModel):
    id: str
    # '...' 표시는 "이 값은 반드시 있어야 한다"는 뜻입니다. (Missing시 에러 발생)
    age: str = Field(..., description="연령(시기)")
    category: str = Field(..., description="카테고리")
    qtype: str = Field(..., description="응답형식")
    text: str = Field(..., description="질문 내용")

    # Optional[...] = None 표시는 "이 값은 없어도 된다"는 뜻입니다.
    # 원본 데이터에 이 항목들이 비어있어도 에러가 나지 않게 막아주는 역할입니다.
    number: Optional[str] = None
    options: Optional[List[str]] = None
    help: Optional[str] = None
    criteria: Optional[str] = None
    actions: Optional[str] = None
    counseling: Optional[str] = None
    item_guide: Optional[str] = None
    positive_parenting: Optional[str] = None
    caution: Optional[str] = None
    caregiver_note: Optional[str] = None
    pe_item: Optional[str] = None
    pe_caution: Optional[str] = None
    judgment: Optional[str] = None
    edu_topic: Optional[str] = None

    # 앱 내부에서 사용자 답변을 저장할 때 쓸 공간
    answer: Optional[Any] = None
    age_info: Optional[Dict[str, Any]] = None
    age_keys: Optional[List[str]] = None

# 전체 설문 팩(Pack)의 설계도
class SurveyPack(BaseModel):
    meta: Optional[Dict[str, Any]] = None
    questions: List[Question]  # Question들의 리스트
