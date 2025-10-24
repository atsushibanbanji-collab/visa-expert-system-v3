"""API routes for the visa expert system"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os

from ..models.knowledge_base import KnowledgeBase
from ..models.rule import Rule
from ..services.consultation import Consultation

router = APIRouter()

# グローバルな知識ベースと診断セッション
kb = None
consultation = None


def auto_detect_visa_type(rule_data: dict) -> str:
    """ルールからビザタイプを自動判定"""
    conclusion = rule_data.get('conclusion', '')
    conditions_text = ' '.join([c['fact_name'] for c in rule_data.get('conditions', [])])

    # 結論または条件にビザタイプのキーワードが含まれているか確認
    if 'Eビザ' in conclusion or 'Eビザ' in conditions_text:
        return 'E'
    elif 'Lビザ' in conclusion or 'Blanket L' in conclusion or 'Lビザ' in conditions_text or 'Blanket L' in conditions_text:
        return 'L'
    elif 'H-1B' in conclusion or 'H-1B' in conditions_text:
        return 'H-1B'
    elif 'Bビザ' in conclusion or 'B-1' in conclusion or 'Bビザ' in conditions_text:
        return 'B'
    elif 'J-1' in conclusion or 'J-1' in conditions_text:
        return 'J-1'

    return None


def load_knowledge_base(visa_type: str = None):
    """知識ベースをJSONファイルから読み込み"""
    kb = KnowledgeBase(visa_type=visa_type)

    # JSONファイルのパスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    rules_file = os.path.join(data_dir, "rules.json")

    # ルールを読み込み
    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for rule_data in data["rules"]:
        # ビザタイプが指定されていない場合は自動判定
        if 'visa_type' not in rule_data or rule_data['visa_type'] is None:
            rule_data['visa_type'] = auto_detect_visa_type(rule_data)

        rule = Rule(**rule_data)
        kb.add_rule(rule)

    kb.finalize()
    return kb


# Request/Response models
class StartRequest(BaseModel):
    visa_type: str  # E, L, B, H-1B, J-1


class AnswerRequest(BaseModel):
    question: str
    answer: bool


class StartResponse(BaseModel):
    next_question: Optional[str]
    visa_type: str


class AnswerResponse(BaseModel):
    next_question: Optional[str]
    conclusions: List[str]
    is_finished: bool


class VisualizationResponse(BaseModel):
    rules: List[Dict]
    facts: Dict[str, bool]
    fired_rules: List[str]
    question_history: List[str]
    answer_history: Dict[str, bool]


@router.post("/consultation/start", response_model=StartResponse)
async def start_consultation(request: StartRequest):
    """診断セッションを開始"""
    global consultation, kb

    # 選択されたビザタイプで知識ベースを読み込み
    kb = load_knowledge_base(visa_type=request.visa_type)

    consultation = Consultation(kb)
    consultation.start()

    next_question = consultation.get_next_question()

    return StartResponse(next_question=next_question, visa_type=request.visa_type)


@router.post("/consultation/answer", response_model=AnswerResponse)
async def answer_question(request: AnswerRequest):
    """質問に回答"""
    global consultation

    if consultation is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    consultation.answer_question(request.question, request.answer)

    next_question = consultation.get_next_question()
    conclusions = consultation.get_conclusions()
    is_finished = consultation.is_finished()

    return AnswerResponse(
        next_question=next_question,
        conclusions=conclusions,
        is_finished=is_finished
    )


@router.post("/consultation/back")
async def go_back():
    """前の質問に戻る"""
    global consultation

    if consultation is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    previous_question = consultation.go_back()

    return {
        "previous_question": previous_question,
        "current_question": consultation.question_history[-1] if consultation.question_history else None
    }


@router.post("/consultation/restart", response_model=StartResponse)
async def restart_consultation():
    """診断を最初からやり直し"""
    global consultation

    if consultation is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    consultation.restart()
    next_question = consultation.get_next_question()

    return StartResponse(next_question=next_question)


@router.get("/consultation/visualization", response_model=VisualizationResponse)
async def get_visualization():
    """推論過程の可視化データを取得"""
    global consultation

    if consultation is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    viz_data = consultation.get_visualization_data()

    return VisualizationResponse(**viz_data)


@router.get("/consultation/conclusions")
async def get_conclusions():
    """診断結果を取得"""
    global consultation

    if consultation is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    conclusions = consultation.get_conclusions()

    return {"conclusions": conclusions}


@router.get("/rules")
async def get_all_rules():
    """すべてのルールを取得"""
    global kb

    if kb is None:
        load_knowledge_base()

    return {
        "rules": [rule.dict() for rule in kb.rules]
    }


@router.get("/facts")
async def get_all_facts():
    """すべての事実を取得"""
    global kb

    if kb is None:
        load_knowledge_base()

    return {
        "all_facts": list(kb.all_fact_names),
        "basic_facts": list(kb.basic_facts),
        "derivable_facts": list(kb.derivable_facts)
    }
