"""Rule クラス - エキスパートシステムのルールを表現"""
from typing import List, Literal, Optional
from pydantic import BaseModel


class Condition(BaseModel):
    """条件を表すクラス"""
    fact_name: str
    required_value: bool = True


class Rule(BaseModel):
    """ルールを表すクラス"""
    id: str
    conditions: List[Condition]
    operator: Literal["AND", "OR"] = "AND"  # 条件間の論理演算子
    conclusion: str  # 結論となる事実の名前
    conclusion_value: bool = True  # 結論の真偽値
    priority: int = 0  # 優先順位（質問の順序制御に使用）
    visa_type: Optional[str] = None  # ビザタイプ（E, L, B, H-1B, J-1など）

    def can_fire(self, facts: dict) -> bool:
        """ルールが発火可能かを判定"""
        if self.operator == "AND":
            return all(
                facts.get(cond.fact_name) == cond.required_value
                for cond in self.conditions
                if facts.get(cond.fact_name) is not None
            ) and all(
                facts.get(cond.fact_name) is not None
                for cond in self.conditions
            )
        else:  # OR
            return any(
                facts.get(cond.fact_name) == cond.required_value
                for cond in self.conditions
                if facts.get(cond.fact_name) is not None
            )

    def is_partially_evaluated(self, facts: dict) -> bool:
        """ルールが部分的に評価されているか（一部の条件が判明している）"""
        return any(
            facts.get(cond.fact_name) is not None
            for cond in self.conditions
        )

    def get_condition_status(self, facts: dict) -> dict:
        """各条件の状態を取得"""
        status = {}
        for cond in self.conditions:
            fact_value = facts.get(cond.fact_name)
            if fact_value is None:
                status[cond.fact_name] = "unknown"
            elif fact_value == cond.required_value:
                status[cond.fact_name] = "satisfied"
            else:
                status[cond.fact_name] = "not_satisfied"
        return status
