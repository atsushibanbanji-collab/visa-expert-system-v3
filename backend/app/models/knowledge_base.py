"""KnowledgeBase クラス - ルールと事実の知識ベースを管理"""
from typing import Dict, List, Set
from .rule import Rule
from .fact import Fact


class KnowledgeBase:
    """知識ベースを管理するクラス"""

    def __init__(self):
        self.rules: List[Rule] = []
        self.facts: Dict[str, bool] = {}
        self.all_fact_names: Set[str] = set()
        self.derivable_facts: Set[str] = set()  # 他のルールから導出可能な事実
        self.basic_facts: Set[str] = set()  # 利用者に質問すべき基本事実

    def add_rule(self, rule: Rule):
        """ルールを追加"""
        self.rules.append(rule)
        # 結論となる事実は導出可能
        self.derivable_facts.add(rule.conclusion)
        # すべての事実名を収集
        for cond in rule.conditions:
            self.all_fact_names.add(cond.fact_name)
        self.all_fact_names.add(rule.conclusion)

    def finalize(self):
        """知識ベースの初期化を完了（基本事実と導出可能な事実を分類）"""
        # 導出可能な事実以外は基本事実
        self.basic_facts = self.all_fact_names - self.derivable_facts

    def get_rule_by_id(self, rule_id: str) -> Rule:
        """IDでルールを取得"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def get_rules_with_conclusion(self, fact_name: str) -> List[Rule]:
        """特定の事実を結論とするルールを取得"""
        return [rule for rule in self.rules if rule.conclusion == fact_name]

    def is_derivable(self, fact_name: str) -> bool:
        """事実が導出可能かを判定"""
        return fact_name in self.derivable_facts

    def is_basic_fact(self, fact_name: str) -> bool:
        """事実が基本事実（質問すべき）かを判定"""
        return fact_name in self.basic_facts

    def get_facts_needed_for_rule(self, rule: Rule) -> Set[str]:
        """ルールが必要とする事実を取得"""
        return {cond.fact_name for cond in rule.conditions}

    def get_unknown_basic_facts_for_rule(self, rule: Rule) -> Set[str]:
        """ルールの条件のうち、まだ不明な基本事実を取得"""
        needed_facts = self.get_facts_needed_for_rule(rule)
        return {
            fact for fact in needed_facts
            if self.is_basic_fact(fact) and self.facts.get(fact) is None
        }
