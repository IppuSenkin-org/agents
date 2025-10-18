# 銀行営業ロールプレイエージェント（シンプル版）

## 概要

銀行員が中小企業の経営者に対してポジティブ・インパクト・ファイナンス（PIF）を提案する際の営業スキルを向上させるためのロールプレイトレーニングシステムです。

**キャラクター**: 田中太郎社長（58歳）、田中金属工業株式会社の代表取締役
**技術スタック**: LiveKit Agents + OpenAI Realtime API (gpt-realtime)
**実装方針**: シンプルで柔軟な設計（詳細な背景知識でLLMが自然に反応）

## 特徴

### ✨ シンプルで自然な会話

**従来の問題点**:
- 具体的なセリフを指定していたため「台本通り」の会話になっていた
- フェーズ管理システムが複雑で、柔軟性に欠けていた
- 1,600行以上のコードでメンテナンスが困難

**新しいアプローチ**:
- ✅ **詳細な人物像と背景**を設定（性格、価値観、経験、懸念の理由）
- ✅ **セリフは指定せず**、LLMが文脈に応じて自然に反応
- ✅ **300行未満のシンプルなコード**（81%削減）
- ✅ 同じ営業トークでも毎回違う展開になる柔軟性
- ✅ 会話の方向性は維持しつつ、予測不可能な人間らしさ

### 🎭 田中太郎社長の特徴

田中太郎社長は以下のような人物です:

**性格と価値観**:
- 慎重で実務的な決断スタイル（ROIが明確なら決断できる）
- ビジネスライク、簡潔（相槌「うん」「まぁ」「ふむ」を使う）
- 実利主義（環境は副次的、ビジネスにつながらないと意味がない）
- リスク回避的（保証や確実性を求める）

**知識と経験**:
- 省エネ設備投資の成功経験あり
- PIFや環境認証制度は知らない
- ROI計算は得意だが、書類作業は苦手

**主な懸念**:
- **コスト**: 投資回収の確実性が不明
- **時間**: 50名規模で管理部門が小さく、書類作業は負担
- **効果**: 環境認証が売上につながった経験がない
- **保証**: 失敗のリスクを避けたい

### 🔄 自然な態度の変化

明示的なフェーズ管理はせず、LLMが文脈に応じて自然に態度を変えます:

```
初期: 懐疑的だが話は聞く
  ↓ (具体的な事例を聞く)
関心: コストとROIを確認したい
  ↓ (数字を聞いて計算する)
評価: 悪くないが時間が心配
  ↓ (サポート体制を知る)
検討: 保証はないが検討の価値あり
  ↓ (リスクが低いと判断)
前向き: 資料を見て判断したい
```

## ディレクトリ構成

```
agents/roleplay/
├── agent_worker.py              # メインエントリーポイント（69行）
├── character_config.py          # キャラクター設定（89行）
├── simple_prompt.py             # プロンプト生成（140行）
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md

合計: 約300行（従来の1/5）
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
CHARACTER_TYPE=cautious_ceo  # 現在はこれのみサポート
TEMPERATURE=0.8              # 0.6-1.0（低いほど安定、高いほど多様）
VOICE=onyx                   # onyx, echo, fable, alloy
```

### 2. エージェントの起動

#### Docker実行（推奨）

```bash
docker-compose up --build
```

#### ローカル実行

```bash
pip install -r requirements.txt
python agent_worker.py dev
```

## 使い方

### 基本的な流れ

1. **フロントエンド（ai-roleplay-demo-front）を起動**
2. **エージェントを起動**（上記のコマンド）
3. **ブラウザで接続して営業ロープレを開始**
4. **会話を楽しむ**（毎回違う展開になります）

### 会話例

```
営業: 「社長、今日は前回お話ししていた塗装ラインの更新について、
      少し関連する制度をご紹介できればと思って伺いました。」

社長: 「うん、まぁ聞くだけ聞くけど。新しい制度ってなんだ？」

営業: 「"ポジティブ・インパクト・ファイナンス"というもので、
      簡単に言うと企業の環境や地域への良い取り組みを
      金融面で応援する仕組みです。」

社長: 「ポジティブ…インパクト？初めて聞いたな。
      どうせ証明書出して終わりじゃないの？」

営業: 「群馬の部品メーカーさんでは20〜30万円の投資で、
      トヨタ系の調達評価でランクAを取得し、
      発注量が1.2倍に増えたそうです。」

社長: 「それ、いくらくらいかかったんだ？」
      ↑ 具体的な数字に反応し始める
```

※ 同じ営業トークでも、社長の返答は毎回微妙に変わります

## フロントエンドとの接続

このエージェントは `bank-sales-agent` という名前で登録されています。

フロントエンド (`ai-roleplay-demo-front/app-config.ts`) で以下のように指定:
```typescript
agentName: 'bank-sales-agent',
```

## 主要ファイルの説明

### 1. character_config.py

田中太郎社長の詳細なプロファイルを定義:

```python
TANAKA_CEO = CharacterProfile(
    name="田中太郎",
    age=58,
    company_name="田中金属工業株式会社",

    # 性格・価値観（なぜそう考えるか）
    personality={
        "decision_style": "慎重で実務的。ROIが明確なら決断できる...",
        "values": "実利主義。環境は副次的...",
        ...
    },

    # 懸念とその理由
    concerns={
        "cost": "投資回収の確実性。中小企業で投資余力が限られている...",
        "time": "50名規模で管理部門が小さい。書類作業は本業を奪う...",
        ...
    }
)
```

### 2. simple_prompt.py

キャラクターの背景知識を含むプロンプトを生成:

- 人物像の詳細説明
- 会社の具体的背景
- 知識と経験のレベル
- 懸念の理由
- 参考事例（背景知識として）
- 基本ルール（AIっぽい話し方禁止等）

### 3. agent_worker.py

シンプルなエントリーポイント:

```python
# キャラクターを取得
character = get_character(character_type)

# プロンプトを生成
instructions = build_prompt(character)

# エージェントを作成
agent = Agent(
    instructions=instructions,
    llm=openai.realtime.RealtimeModel(
        model="gpt-realtime",
        voice=voice,
        temperature=temperature,
    ),
)
```

## カスタマイズ

### 温度とボイスの調整

`.env`ファイルで設定:

```bash
# より安定した会話（予測しやすい）
TEMPERATURE=0.7

# より多様な会話（予測しにくい）
TEMPERATURE=0.9

# 音声の変更
VOICE=echo       # onyx, echo, fable, alloy
```

### 社長の性格を変更

`character_config.py`の`TANAKA_CEO`を編集:

```python
personality={
    "decision_style": "より積極的に新しい投資を検討する...",
    "values": "環境対策を重視する...",
    ...
}
```

### プロンプトの調整

`simple_prompt.py`の`build_prompt()`関数を編集:

```python
def build_prompt(character: CharacterProfile = TANAKA_CEO) -> str:
    prompt = f"""
    # あなたの役割

    あなたは{character.name}...

    # （ここに追加の指示を記述）
    """
    return prompt
```

## トラブルシューティング

### 会話が不自然

**原因**: TEMPERATURE設定が不適切
**解決**: `.env`で調整（0.7〜0.9の範囲）

```bash
TEMPERATURE=0.8  # バランスの取れた設定
```

### 社長がすぐに納得してしまう

**原因**: プロンプトの指示が弱い
**解決**: `simple_prompt.py`で「段階的に態度を変える」の指示を強化

### 音声が合わない

**原因**: VOICE設定が不適切
**解決**: `.env`で変更

```bash
VOICE=onyx   # 低めの男性声（推奨）
VOICE=echo   # 中間の男性声
VOICE=fable  # 高めの男性声
```

### 会話が台本通りになる

これは起こらないはずです！もし起こった場合:
1. `simple_prompt.py`に具体的なセリフが含まれていないか確認
2. TEMPERATUREを上げて多様性を増やす（0.9など）

## ログの見方

```bash
🎭 Starting agent as 田中太郎
   Voice: onyx
   Temperature: 0.8
✅ Agent session started
```

シンプルなログのみ表示されます。フェーズ遷移のログは廃止されました。

## 参考資料

- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime-conversations)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)

## 変更履歴

### v2.0 (シンプル版) - 2025-10-18
- ✨ フェーズ管理システムを削除してシンプル化
- ✨ 具体的なセリフ指定を削除し、背景知識ベースに変更
- ✨ コード量を81%削減（1,609行 → 298行）
- ✨ より自然で柔軟な会話を実現

### v1.0 (初版) - 2025-10-12
- 🎉 初版リリース
- フェーズ管理システム実装
- 詳細な会話パターン定義
