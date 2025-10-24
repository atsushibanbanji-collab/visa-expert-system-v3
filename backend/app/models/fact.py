"""Fact クラス - エキスパートシステムの事実を表現"""
from typing import Optional
from pydantic import BaseModel


class Fact(BaseModel):
    """事実を表すクラス"""
    name: str
    value: Optional[bool] = None
    is_derived: bool = False  # 推論で導出された事実かどうか
    derived_from_rule: Optional[str] = None  # どのルールから導出されたか

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Fact):
            return self.name == other.name
        return False
