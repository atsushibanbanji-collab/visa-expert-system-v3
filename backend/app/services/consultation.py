"""Consultation クラス - 診断セッションの管理"""
from typing import Dict, List, Optional
from ..models.knowledge_base import KnowledgeBase
from .inference_engine import InferenceEngine


class Consultation:
    """診断セッションを管理するクラス"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.engine = InferenceEngine(knowledge_base)
        self.question_history: List[str] = []  # 質問履歴
        self.answer_history: Dict[str, bool] = {}  # 回答履歴

    def start(self):
        """診断セッションを開始"""
        self.kb.facts = {}
        self.question_history = []
        self.answer_history = {}
        self.engine.fired_rules = []

    def get_next_question(self) -> Optional[str]:
        """次の質問を取得"""
        next_fact = self.engine.get_next_question()
        if next_fact and next_fact not in self.question_history:
            self.question_history.append(next_fact)
        return next_fact

    def answer_question(self, fact_name: str, answer: bool):
        """質問に回答"""
        self.kb.facts[fact_name] = answer
        self.answer_history[fact_name] = answer
        # 推論を実行して導出可能な事実を導出
        self.engine.forward_chain()

    def go_back(self) -> Optional[str]:
        """前の質問に戻る"""
        if len(self.question_history) < 2:
            # 最初の質問の場合は戻れない
            return None

        # 最後の質問を削除
        last_question = self.question_history.pop()

        # 最後の回答をクリア
        if last_question in self.answer_history:
            del self.answer_history[last_question]

        # 推論エンジンで該当する事実とその依存事実をリセット
        self.engine.reset_from_fact(last_question)

        # 前の質問を返す
        return self.question_history[-1] if self.question_history else None

    def restart(self):
        """診断を最初からやり直し"""
        self.start()

    def get_conclusions(self) -> List[str]:
        """診断結果（結論）を取得"""
        return self.engine.get_conclusions()

    def get_visualization_data(self) -> Dict:
        """推論過程の可視化データを取得"""
        return {
            "rules": self.engine.get_rule_statuses(),
            "facts": self.kb.facts,
            "fired_rules": self.engine.fired_rules,
            "question_history": self.question_history,
            "answer_history": self.answer_history
        }

    def is_finished(self) -> bool:
        """診断が完了したか判定"""
        # 次の質問がない、または結論が導出された場合
        next_question = self.engine.get_next_question()
        conclusions = self.get_conclusions()
        return next_question is None or len(conclusions) > 0
