import json
import os

# ルールファイルのパス
script_dir = os.path.dirname(os.path.abspath(__file__))
rules_file = os.path.join(script_dir, 'app', 'data', 'rules.json')

# ルールを読み込み
with open(rules_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 各ルールにvisa_typeを追加
for rule in data['rules']:
    rule_id = rule['id']
    conclusion = rule['conclusion']
    conditions_text = ' '.join([c['fact_name'] for c in rule['conditions']])

    # ルールIDと結論からビザタイプを判定
    if 'Eビザ' in conclusion or 'Eビザ' in conditions_text:
        rule['visa_type'] = 'E'
    elif 'Lビザ' in conclusion or 'Blanket L' in conclusion or 'Lビザ' in conditions_text or 'Blanket L' in conditions_text:
        rule['visa_type'] = 'L'
    elif 'H-1B' in conclusion:
        rule['visa_type'] = 'H-1B'
    elif 'Bビザ' in conclusion or 'B-1' in conclusion:
        rule['visa_type'] = 'B'
    elif 'J-1' in conclusion:
        rule['visa_type'] = 'J-1'
    else:
        # 中間結論の場合、Noneのまま（後で依存関係から推定される）
        rule['visa_type'] = None

# 保存
with open(rules_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Updated rules.json with visa_type information')
print(f'Total rules: {len(data["rules"])}')
