"""KnowledgeBase クラス - ルールと事実の知識ベースを管理"""
from typing import Dict, List, Set, Optional
from .rule import Rule
from .fact import Fact


class KnowledgeBase:
    """知識ベースを管理するクラス"""

    def __init__(self, visa_type: Optional[str] = None):
        self.all_rules: List[Rule] = []  # すべてのルール
        self.rules: List[Rule] = []  # フィルタリングされたルール
        self.facts: Dict[str, bool] = {}
        self.all_fact_names: Set[str] = set()
        self.derivable_facts: Set[str] = set()  # 他のルールから導出可能な事実
        self.basic_facts: Set[str] = set()  # 利用者に質問すべき基本事実
        self.visa_type: Optional[str] = visa_type  # フィルタリング対象のビザタイプ

    def add_rule(self, rule: Rule):
        """ルールを追加"""
        self.all_rules.append(rule)

    def finalize(self):
        """知識ベースの初期化を完了（基本事実と導出可能な事実を分類）"""
        # ビザタイプでフィルタリング
        if self.visa_type:
            self.rules = self._filter_rules_by_visa_type(self.visa_type)
        else:
            self.rules = self.all_rules

        # フィルタリングされたルールから事実を収集
        for rule in self.rules:
            # 結論となる事実は導出可能
            self.derivable_facts.add(rule.conclusion)
            # すべての事実名を収集
            for cond in rule.conditions:
                self.all_fact_names.add(cond.fact_name)
            self.all_fact_names.add(rule.conclusion)

        # 導出可能な事実以外は基本事実
        self.basic_facts = self.all_fact_names - self.derivable_facts

    def _filter_rules_by_visa_type(self, visa_type: str) -> List[Rule]:
        """ビザタイプに関連するルールを再帰的に取得"""
        # まず、ビザタイプに直接マッチするルールを取得
        target_rules = [r for r in self.all_rules if r.visa_type == visa_type]

        # 依存するルールを再帰的に追加
        needed_conclusions = set()
        for rule in target_rules:
            for cond in rule.conditions:
                needed_conclusions.add(cond.fact_name)

        # 必要な結論を出すルールを追加
        changed = True
        while changed:
            changed = False
            for rule in self.all_rules:
                if rule not in target_rules and rule.conclusion in needed_conclusions:
                    target_rules.append(rule)
                    # このルールの条件も必要
                    for cond in rule.conditions:
                        if cond.fact_name not in needed_conclusions:
                            needed_conclusions.add(cond.fact_name)
                            changed = True

        return target_rules

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
