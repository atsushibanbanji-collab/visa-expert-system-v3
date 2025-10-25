const VisualizationPanel = ({ visualizationData, currentQuestion }) => {
  const getConditionColor = (status, isDerivable) => {
    if (status === 'satisfied') return 'bg-green-100 text-green-800 border-green-300';
    if (status === 'not_satisfied') return 'bg-red-100 text-red-800 border-red-300';
    if (isDerivable) return 'bg-purple-100 text-purple-800 border-purple-300';
    return 'bg-gray-100 text-gray-600 border-gray-300';
  };

  const getConclusionColor = (derived) => {
    return derived
      ? 'bg-blue-100 text-blue-800 border-blue-300'
      : 'bg-gray-100 text-gray-600 border-gray-300';
  };

  if (!visualizationData || !visualizationData.rules) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 h-full">
        <h2 className="text-2xl font-bold text-navy-900 mb-4">
          推論過程の可視化
        </h2>
        <p className="text-gray-600">診断を開始すると、ここに推論過程が表示されます。</p>
      </div>
    );
  }

  const { rules, fired_rules } = visualizationData;

  // 関連するルールのみをフィルタリング
  const relevantRules = rules.filter(rule => {
    // 発火済みのルール
    if (rule.is_fired) return true;

    // 部分的に評価されているルール（少なくとも1つの条件が判明している）
    const hasEvaluatedCondition = rule.conditions.some(
      condition => condition.status !== 'unknown'
    );

    // 今の質問に関係しているルール
    const relatedToCurrentQuestion = currentQuestion && rule.conditions.some(
      condition => condition.fact_name === currentQuestion
    );

    return hasEvaluatedCondition || relatedToCurrentQuestion;
  });

  // ルールの状態を判定
  const getRuleState = (rule) => {
    if (rule.is_fired) return 'fired';

    // 今の質問に関係している
    if (currentQuestion && rule.conditions.some(c => c.fact_name === currentQuestion)) {
      return 'current';
    }

    // 評価中（一部の条件が判明している）
    const hasEvaluatedCondition = rule.conditions.some(
      condition => condition.status !== 'unknown'
    );
    if (hasEvaluatedCondition) return 'evaluating';

    return 'pending';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 flex flex-col h-full max-h-[calc(100vh-200px)]">
      {/* ヘッダー部分（固定） */}
      <div className="flex-shrink-0 mb-4">
        <h2 className="text-2xl font-bold text-navy-900 mb-4">
          推論過程の可視化
        </h2>

        {/* Legend */}
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <h3 className="text-xs font-semibold text-gray-700 mb-2">凡例 - ルールの状態</h3>
          <div className="grid grid-cols-2 gap-2 text-xs mb-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded"></div>
              <span className="text-xs">発火済み</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-400 rounded"></div>
              <span className="text-xs">今の質問に関係</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-300 rounded"></div>
              <span className="text-xs">推論中</span>
            </div>
          </div>
          <h3 className="text-xs font-semibold text-gray-700 mb-2 mt-2">条件の状態</h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded"></div>
              <span className="text-xs">未確認</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-100 border border-green-300 rounded"></div>
              <span className="text-xs">満たす</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-100 border border-red-300 rounded"></div>
              <span className="text-xs">満たさない</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-100 border border-purple-300 rounded"></div>
              <span className="text-xs">導出可能</span>
            </div>
          </div>
        </div>

        {/* Fired Rules Summary */}
        {fired_rules && fired_rules.length > 0 && (
          <div className="bg-blue-50 rounded-lg p-3 mb-4 border-l-4 border-blue-600">
            <h3 className="text-xs font-semibold text-blue-900 mb-1">
              発火したルール: {fired_rules.length}
            </h3>
            <p className="text-xs text-blue-700">
              {fired_rules.join(', ')}
            </p>
          </div>
        )}

        {/* 表示中のルール数 */}
        <div className="text-xs text-gray-600 mb-2">
          表示中のルール: {relevantRules.length} / {rules.length}
        </div>
      </div>

      {/* Rules List（スクロール可能） */}
      <div className="flex-1 overflow-y-auto pr-2">
        <div className="space-y-3">
          {relevantRules.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>質問に回答すると、関連するルールがここに表示されます。</p>
            </div>
          ) : (
            relevantRules.map((rule, index) => {
              const ruleState = getRuleState(rule);
              const stateStyles = {
                fired: 'border-blue-500 bg-blue-50',
                current: 'border-yellow-400 bg-yellow-50',
                evaluating: 'border-orange-300 bg-orange-50',
                pending: 'border-gray-200 bg-white'
              };
              const badgeStyles = {
                fired: 'bg-blue-600 text-white',
                current: 'bg-yellow-500 text-white',
                evaluating: 'bg-orange-400 text-white',
                pending: 'bg-gray-400 text-white'
              };
              const badgeText = {
                fired: '発火済み',
                current: '今の質問に関係',
                evaluating: '推論中',
                pending: '未評価'
              };

              return (
          <div
            key={rule.rule_id}
            className={`border-2 rounded-lg p-4 ${stateStyles[ruleState]}`}
          >
            {/* Rule Header */}
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-navy-900">
                {rule.rule_id}
              </h3>
              <span className={`text-xs px-2 py-1 rounded-full ${badgeStyles[ruleState]}`}>
                {badgeText[ruleState]}
              </span>
            </div>

            {/* Conditions */}
            <div className="mb-3">
              <p className="text-xs font-semibold text-gray-700 mb-2">
                IF (条件 - {rule.operator}):
              </p>
              <div className="space-y-1">
                {rule.conditions.map((condition, condIndex) => (
                  <div key={condIndex}>
                    <div
                      className={`text-xs p-2 rounded border ${getConditionColor(
                        condition.status,
                        condition.is_derivable
                      )}`}
                    >
                      {condition.fact_name}
                      {condition.is_derivable && (
                        <span className="ml-2 text-purple-600 font-semibold">
                          (導出可能)
                        </span>
                      )}
                    </div>
                    {condIndex < rule.conditions.length - 1 && (
                      <div className="text-xs text-gray-500 py-1 px-2">
                        {rule.operator}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Conclusion */}
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-2">
                THEN (結論):
              </p>
              <div
                className={`text-xs p-2 rounded border ${getConclusionColor(
                  rule.conclusion_derived
                )}`}
              >
                {rule.conclusion}
              </div>
            </div>
          </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default VisualizationPanel;
