"""InferenceEngine クラス - 推論エンジンの実装"""
from typing import Dict, List, Set, Tuple
from ..models.knowledge_base import KnowledgeBase
from ..models.rule import Rule


class InferenceEngine:
    """前向き推論（Forward Chaining）エンジン"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.fired_rules: List[str] = []  # 発火したルールの履歴

    def forward_chain(self) -> Dict[str, bool]:
        """前向き推論を実行し、導出可能なすべての事実を推論"""
        changed = True
        iteration = 0
        max_iterations = 100  # 無限ループ防止

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            for rule in self.kb.rules:
                # すでに結論が導出済みの場合はスキップ
                if self.kb.facts.get(rule.conclusion) is not None:
                    continue

                # ルールが発火可能かチェック
                if rule.can_fire(self.kb.facts):
                    # 結論を導出
                    self.kb.facts[rule.conclusion] = rule.conclusion_value
                    self.fired_rules.append(rule.id)
                    changed = True

        return self.kb.facts

    def get_next_question(self) -> str:
        """次に質問すべき基本事実を取得"""
        # まず推論を実行して、導出可能な事実を全て導出
        self.forward_chain()

        # すでに判明している基本事実を除外
        unknown_basic_facts = {
            fact for fact in self.kb.basic_facts
            if self.kb.facts.get(fact) is None
        }

        if not unknown_basic_facts:
            return None

        # 優先順位を考慮して次の質問を選択
        # 1. 最も優先度の高いルールの条件に含まれる基本事実
        # 2. より多くのルールに影響する基本事実
        best_fact = self._select_best_fact(unknown_basic_facts)
        return best_fact

    def _select_best_fact(self, candidates: Set[str]) -> str:
        """最適な質問対象の事実を選択"""
        if not candidates:
            return None

        # 各候補事実について、それを条件とするルールをカウント
        fact_scores = {}
        for fact in candidates:
            score = 0
            for rule in self.kb.rules:
                # このルールがまだ評価中で、この事実を必要としているか
                if self.kb.facts.get(rule.conclusion) is None:
                    needed_facts = self.kb.get_unknown_basic_facts_for_rule(rule)
                    if fact in needed_facts:
                        # ルールの優先度を考慮
                        score += rule.priority + 1

            fact_scores[fact] = score

        # スコアが最も高い事実を選択
        best_fact = max(fact_scores.items(), key=lambda x: x[1])[0]
        return best_fact

    def get_conclusions(self) -> List[str]:
        """導出されたすべての結論を取得"""
        # まず推論を実行
        self.forward_chain()

        # ビザ申請の結論（末端の結論）を取得
        conclusions = []
        for fact_name, value in self.kb.facts.items():
            if value and "申請ができます" in fact_name:
                conclusions.append(fact_name)

        return conclusions

    def get_rule_statuses(self) -> List[Dict]:
        """すべてのルールの状態を取得（可視化用）"""
        statuses = []
        for rule in self.kb.rules:
            condition_status = rule.get_condition_status(self.kb.facts)
            conclusion_derived = self.kb.facts.get(rule.conclusion) is not None

            statuses.append({
                "rule_id": rule.id,
                "conditions": [
                    {
                        "fact_name": cond.fact_name,
                        "required_value": cond.required_value,
                        "status": condition_status.get(cond.fact_name, "unknown"),
                        "is_derivable": self.kb.is_derivable(cond.fact_name)
                    }
                    for cond in rule.conditions
                ],
                "operator": rule.operator,
                "conclusion": rule.conclusion,
                "conclusion_value": rule.conclusion_value,
                "conclusion_derived": conclusion_derived,
                "can_fire": rule.can_fire(self.kb.facts),
                "is_fired": rule.id in self.fired_rules
            })

        return statuses

    def reset_from_fact(self, fact_name: str):
        """特定の事実とそれに依存する導出事実をリセット"""
        # 該当する事実をクリア
        if fact_name in self.kb.facts:
            del self.kb.facts[fact_name]

        # この事実に依存する導出事実を再帰的にクリア
        self._clear_dependent_facts(fact_name)

        # 発火したルールの履歴をリセット
        self.fired_rules = []

        # 推論を再実行
        self.forward_chain()

    def _clear_dependent_facts(self, fact_name: str):
        """依存する導出事実を再帰的にクリア"""
        for rule in self.kb.rules:
            # このルールが該当する事実を条件として使用しているか
            if any(cond.fact_name == fact_name for cond in rule.conditions):
                # このルールの結論をクリア
                conclusion = rule.conclusion
                if conclusion in self.kb.facts:
                    del self.kb.facts[conclusion]
                    # さらにこの結論に依存する事実もクリア
                    self._clear_dependent_facts(conclusion)
