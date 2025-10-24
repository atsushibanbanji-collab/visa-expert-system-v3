# ビザ選定エキスパートシステム

オブジェクト指向設計によるエキスパートシステムを用いたビザ選定支援Webアプリケーション

## システム概要

このシステムは、30個のルールベースの知識を使用して、ビザの選定を支援します。
- **前向き推論エンジン（Forward Chaining）** による自動推論
- **2画面分割UI** で診断と推論過程を同時に可視化
- **オブジェクト指向設計** によるモジュール化されたアーキテクチャ

## 主な機能

### 1. 一問一答形式の診断
- 利用者に質問を順次提示
- はい/いいえで回答
- 推論エンジンが自動的に導出可能な事実を推論

### 2. 推論過程の可視化
- すべてのルールを色分けして表示
  - **グレー**: 未確認の条件
  - **緑**: 条件を満たす（Yes）
  - **赤**: 条件を満たさない（No）
  - **紫**: 他のルールから導出可能な条件
  - **青**: 導出された結論

### 3. ナビゲーション機能
- **前の質問に戻る**: 直前の質問に戻り、回答を変更可能
- **最初から**: 診断を最初からやり直し
- 戻った際に依存する導出事実も自動的にクリア

### 4. プロフェッショナルなデザイン
- ネイビー・グレー・白基調の落ち着いた配色
- レスポンシブデザイン（PC・タブレット対応）
- Tailwind CSS による洗練されたUI

## 技術スタック

### バックエンド
- **Python 3.8+**
- **FastAPI** - 高速なWeb APIフレームワーク
- **Pydantic** - データバリデーション
- **Uvicorn** - ASGIサーバー

### フロントエンド
- **React 18**
- **Vite** - 高速ビルドツール
- **Tailwind CSS** - ユーティリティファーストCSSフレームワーク

### アーキテクチャ
- オブジェクト指向設計
  - `Rule`: ルールクラス
  - `Fact`: 事実クラス
  - `KnowledgeBase`: 知識ベースクラス
  - `InferenceEngine`: 推論エンジンクラス
  - `Consultation`: 診断セッション管理クラス

## セットアップと起動方法

### 前提条件
- Python 3.8以上
- Node.js 16以上
- npm または yarn

### 1. バックエンドのセットアップ

```bash
# backend ディレクトリに移動
cd backend

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 2. バックエンドの起動

```bash
# backend ディレクトリで実行
python main.py
```

バックエンドが http://localhost:8000 で起動します。

### 3. フロントエンドのセットアップ

```bash
# 新しいターミナルを開き、frontend ディレクトリに移動
cd frontend

# 依存パッケージのインストール
npm install
```

### 4. フロントエンドの起動

```bash
# frontend ディレクトリで実行
npm run dev
```

フロントエンドが http://localhost:5173 で起動します。

### 5. アプリケーションにアクセス

ブラウザで http://localhost:5173 を開きます。

## ディレクトリ構造

```
visa-expert-system/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── rule.py           # ルールクラス
│   │   │   ├── fact.py           # 事実クラス
│   │   │   └── knowledge_base.py # 知識ベースクラス
│   │   ├── services/
│   │   │   ├── inference_engine.py # 推論エンジン
│   │   │   └── consultation.py     # 診断セッション管理
│   │   ├── api/
│   │   │   └── routes.py         # APIルート
│   │   └── data/
│   │       └── rules.json        # 30個のルール定義
│   ├── main.py                   # FastAPIアプリケーション
│   └── requirements.txt          # Python依存パッケージ
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DiagnosisPanel.jsx      # 診断パネル
│   │   │   └── VisualizationPanel.jsx  # 可視化パネル
│   │   ├── App.jsx               # メインアプリケーション
│   │   └── index.css             # スタイル
│   ├── package.json              # npm依存パッケージ
│   └── vite.config.js            # Vite設定
└── README.md
```

## API エンドポイント

### 診断関連
- `POST /api/consultation/start` - 診断セッションを開始
- `POST /api/consultation/answer` - 質問に回答
- `POST /api/consultation/back` - 前の質問に戻る
- `POST /api/consultation/restart` - 診断を最初からやり直し
- `GET /api/consultation/visualization` - 推論過程の可視化データを取得
- `GET /api/consultation/conclusions` - 診断結果を取得

### ルール・事実関連
- `GET /api/rules` - すべてのルールを取得
- `GET /api/facts` - すべての事実を取得

### ヘルスチェック
- `GET /health` - ヘルスチェック

## 知識ベース

システムには30個のルールが定義されています：

- **Eビザ** 関連ルール
- **Lビザ（Blanket/Individual）** 関連ルール
- **H-1Bビザ** 関連ルール
- **Bビザ** 関連ルール
- **J-1ビザ** 関連ルール
- その他のビザカテゴリー

各ルールは以下の形式で定義されています：
```json
{
  "id": "rule_1",
  "conditions": [
    {"fact_name": "条件1", "required_value": true},
    {"fact_name": "条件2", "required_value": true}
  ],
  "operator": "AND",
  "conclusion": "結論",
  "conclusion_value": true,
  "priority": 100
}
```

## 使用方法

1. アプリケーションを起動
2. システムが最初の質問を表示
3. 「はい」または「いいえ」で回答
4. 推論エンジンが自動的に導出可能な事実を推論
5. 次の質問が表示される
6. 診断が完了すると、適用可能なビザが表示される

### ナビゲーション
- **前の質問に戻る**: 直前の質問に戻って回答を変更
- **最初から**: 診断を最初からやり直し

## 推論過程の可視化

右側のパネルでは、すべてのルールの状態をリアルタイムで確認できます：
- 各ルールの条件部（IF部分）
- 条件間の論理演算子（AND/OR）
- 結論部（THEN部分）
- 条件の状態（未確認/満たす/満たさない/導出可能）
- 発火したルールのハイライト

## ライセンス

このプロジェクトは教育・研究目的で作成されました。

## 作成者

Expert System Development Team
