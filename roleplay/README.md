# 銀行営業ロールプレイエージェント

## 概要

銀行員が中小企業の経営者に対してポジティブ・インパクト・ファイナンス（PIF）を提案する際の営業スキルを向上させるためのロールプレイトレーニングシステムです。

**キャラクター**: 田中太郎社長（58歳）、田中金属工業株式会社の代表取締役
**技術スタック**: LiveKit Agents + OpenAI Realtime API (gpt-realtime)
**設計バージョン**: 2025年最新ベストプラクティス準拠

## 特徴

### ✨ 2025年ベストプラクティス対応

- **詳細な口調・反応パターン**: 実際の会話例を再現できる具体的な speech_patterns
- **動的プロンプト生成**: 会話状態に応じて instructions を動的に生成
- **トリガーベースのフェーズ遷移**: ターン数だけでなく、キーワードや提供データに基づく自然な遷移
- **リアルタイムフィードバック**: 営業パフォーマンスの自動評価とスコアリング
- **Semantic VAD**: 文の途中で切らない自然な会話フロー

### 🎭 キャラクター特性

田中太郎社長は以下のような特徴を持っています:

- 慎重で実務的な決断スタイル
- 短く簡潔に話す（「うん、まぁ」「ふむ」などの相槌）
- 新しい用語には戸惑う（「ポジティブ…インパクト？初めて聞いたな」）
- 具体的な数字に強く反応する
- 段階的に態度を変化させる（懐疑的 → 興味 → 検討）

### 📊 3つの会話フェーズ

1. **SKEPTICAL（懐疑的）**: 2-5ターン
   - コストへの懸念
   - 新制度への不信感

2. **INTERESTED（興味）**: 3-7ターン
   - 質問が増える
   - 具体的な数字に反応

3. **CONSIDERING（検討）**: 2-5ターン
   - 前向きだが即決しない
   - 資料要求

## ディレクトリ構成

```
agents/roleplay/
├── agent_worker.py              # メインエントリーポイント
├── character_config.py          # キャラクター設定
├── conversation_flow.py         # 会話フロー管理
├── case_studies.py              # 事例データベース
├── evaluation.py                # フィードバック機能
├── prompts/
│   ├── __init__.py
│   └── instructions.py          # 動的プロンプト生成
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── bank_sales_design.md         # 設計書
└── README.md
```

## セットアップ

### 1. 環境変数の設定

`.env`ファイルを作成:

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```bash
# LiveKit設定
LIVEKIT_URL=ws://172.17.0.1:7880
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# OpenAI設定
OPENAI_API_KEY=sk-...

# エージェント設定（オプション）
CHARACTER_TYPE=cautious_ceo  # cautious_ceo | friendly_ceo
TEMPERATURE=0.8              # 0.6-1.0
VOICE=onyx                   # onyx | echo | fable | alloy
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. エージェントの起動

#### ローカル実行

```bash
python agent_worker.py dev
```

#### Docker実行（推奨）

```bash
docker-compose up --build
```

## 使い方

### 基本的な流れ

1. **フロントエンド（agent-starter-react）を起動**
2. **エージェントを起動**（上記のコマンド）
3. **ブラウザで接続して営業ロープレを開始**
4. **会話終了後、ログでフェーズ遷移を確認**

### 会話例

```
営業: 「社長、今日は前回お話ししていた塗装ラインの更新について、
      少し関連する制度をご紹介できればと思って伺いました。」

社長: 「うん、まぁ聞くだけ聞くけど。新しい制度ってなんだ？」

営業: 「"ポジティブ・インパクト・ファイナンス"というもので...」

社長: 「ポジティブ…インパクト？初めて聞いたな」

営業: 「群馬の部品メーカーさんでは20万円の投資で...」

社長: 「それ、いくらくらいかかったんだ？」
      ↑ この時点でフェーズがSKEPTICAL → INTERESTEDに遷移
```

## フロントエンドとの接続

このエージェントは `bank-sales-agent` という名前で登録されています。

フロントエンド (`agent-starter-react/app-config.ts`) で以下のように指定:
```typescript
agentName: 'bank-sales-agent',
```

## 主要機能の詳細

### 1. キャラクター設定（character_config.py）

田中太郎社長の詳細な speech_patterns を定義:

```python
speech_patterns = {
    "opening": ["うん、まぁ聞くだけ聞くけど", ...],
    "skepticism": ["どうせ〜じゃないの?", ...],
    "cost_concern": ["それ、いくらくらいかかったんだ？", ...],
}
```

### 2. 会話フロー管理（conversation_flow.py）

トリガーベースのフェーズ遷移とユーザーメッセージの自動分析

### 3. 動的プロンプト生成（prompts/instructions.py）

会話状態に応じて instructions を動的に生成

### 4. 評価・フィードバック（evaluation.py）

営業パフォーマンスを自動評価（総合スコア、懸念への対応、数字の活用度など）

## カスタマイズ

### キャラクターの変更

`.env`で設定:
```bash
CHARACTER_TYPE=friendly_ceo  # より前向きな社長
```

### 温度とボイスの調整

```bash
TEMPERATURE=0.7  # 0.6-1.0（低いほど安定）
VOICE=echo       # onyx, echo, fable, alloy
```

## トラブルシューティング

- **会話が不自然**: `TEMPERATURE`を調整（0.7〜0.9）
- **すぐに納得してしまう**: `conversation_flow.py`のmin_turnsを増やす
- **音声が合わない**: `.env`で`VOICE`を変更

## ログの見方

```
🎭 Starting agent as 田中太郎
📊 Initial phase: skeptical
📝 Turn 3: User said: 群馬の部品メーカーさんでは...
🔄 Phase transition: skeptical → interested
```

## 参考資料

- [設計書（bank_sales_design.md）](./bank_sales_design.md)
- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime-conversations)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
