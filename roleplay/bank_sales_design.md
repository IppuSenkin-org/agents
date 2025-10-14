# 銀行営業ロールプレイエージェント 設計書

## バージョン情報
- **作成日**: 2025-10-12
- **バージョン**: 1.0
- **対象**: ポジティブ・インパクト・ファイナンス（PIF）営業トレーニング

---

## 1. プロジェクト概要

### 1.1 目的
銀行員が中小企業の経営者に対してポジティブ・インパクト・ファイナンス（PIF）を提案する際の営業スキルを向上させるためのロールプレイトレーニングシステムを構築する。

### 1.2 ターゲットユーザー
- 銀行の法人営業担当者
- 融資担当者
- 環境金融推進部門の担当者

### 1.3 技術スタック
- **プラットフォーム**: LiveKit Agents Framework
- **LLM**: OpenAI gpt-realtime (2025年最新モデル)
- **音声処理**: OpenAI Realtime API
- **Turn Detection**: Semantic VAD
- **開発言語**: Python 3.11+
- **コンテナ**: Docker

### 1.4 2025年最新ベストプラクティスの採用

#### OpenAI公式推奨事項
1. **構造化プロンプト**: 8セクション構造（Role, Personality, Context, Pronunciations, Tools, Instructions, Conversation Flow, Safety）
2. **gpt-realtimeモデル**: 指示追従性50%向上（MultiChallenge benchmark: 20.6% → 30.5%）
3. **Semantic VAD**: 文の途中で切らない自然な会話フロー
4. **細かい音声制御**: トーン・ペース・アクセントの詳細指定

#### LiveKit推奨設定
- **MultimodalAgent API**: 自動テキスト・オーディオ同期
- **インテリジェント割り込み処理**: コンテキストウィンドウの自動ロールバック
- **パラメータ透過サポート**: voice, temperature, turn detection設定

---

## 2. システムアーキテクチャ

### 2.1 ディレクトリ構成

```
agents/roleplay/bank_sales/
├── agent_worker.py              # メインエントリーポイント
├── character_config.py          # キャラクター設定
├── conversation_flow.py         # 会話フロー管理
├── case_studies.py              # 事例データベース
├── prompts/
│   ├── __init__.py
│   └── instructions.py          # プロンプトテンプレート
├── requirements.txt             # 依存パッケージ
├── Dockerfile                   # Dockerイメージ定義
├── docker-compose.yml           # Docker Compose設定
├── .env.example                 # 環境変数テンプレート
├── .gitignore
└── README.md                    # 利用ガイド
```

### 2.2 コンポーネント図

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│              agent-starter-react/                        │
└────────────────────┬────────────────────────────────────┘
                     │ LiveKit WebRTC
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  LiveKit Server                          │
│              ws://localhost:7880                         │
└────────────────────┬────────────────────────────────────┘
                     │ LiveKit Protocol
                     ↓
┌─────────────────────────────────────────────────────────┐
│           Bank Sales Agent (Docker Container)            │
│  ┌─────────────────────────────────────────────────┐   │
│  │          agent_worker.py                        │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │   AgentSession + Agent                   │  │   │
│  │  │   ┌──────────────────────────────────┐  │  │   │
│  │  │   │ OpenAI Realtime API              │  │  │   │
│  │  │   │ - model: gpt-realtime            │  │  │   │
│  │  │   │ - voice: onyx                    │  │  │   │
│  │  │   │ - turn_detection: semantic_vad   │  │  │   │
│  │  │   └──────────────────────────────────┘  │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │                                                  │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │   Prompt Builder (instructions.py)       │  │   │
│  │  │   ← character_config.py                  │  │   │
│  │  │   ← conversation_flow.py                 │  │   │
│  │  │   ← case_studies.py                      │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.3 データフロー

```
1. ユーザー音声入力
   ↓
2. LiveKit Server → Agent
   ↓
3. Semantic VAD → ターン検出
   ↓
4. OpenAI Realtime API
   ├→ 会話履歴参照
   ├→ Instructions（動的生成）
   └→ 応答生成
   ↓
5. Agent → LiveKit Server
   ↓
6. Frontend → ユーザーに音声出力
```

---

## 3. キャラクター設計

### 3.1 プライマリキャラクター: 田中太郎社長

#### 基本プロファイル
| 項目 | 内容 |
|------|------|
| 名前 | 田中太郎 |
| 年齢 | 58歳 |
| 役職 | 代表取締役社長 |
| 会社名 | 田中金属工業株式会社 |
| 業種 | 金属加工業（塗装ライン保有） |
| 従業員数 | 50名 |
| 所在地 | 関東圏内 |

#### 性格特性（Personality Traits）
```python
{
    "decision_style": "慎重で実務的。ROIが明確なら検討する",
    "communication": "ビジネスライク、簡潔、時に皮肉を交える",
    "expertise": "省エネ設備投資の経験あり。環境制度には詳しくない",
    "attitude": "新規投資には懐疑的だが、データと実例は重視"
}
```

#### 経営実績
- 省エネ型塗装ラインへ更新済み（電力使用量15%削減）
- 廃材リサイクルシステム導入
- 溶剤再利用システム稼働中

#### 主要な懸念事項
1. **コスト**: 投資回収の確実性
2. **時間**: 書類作業の負担
3. **効果**: 取引先評価への実効性
4. **保証**: 確実な成果が得られるか

#### 取引環境
- 主要取引先: 自動車部品メーカー（トヨタ系サプライヤー含む）
- 経営課題: コスト削減、取引先との関係強化、環境対応

### 3.2 拡張キャラクター（将来実装用）

#### フレンドリー社長: 山田健一（52歳）
- より前向きで新しい取り組みに積極的
- 環境経営に関心が高い
- 初心者の営業員向けトレーニングに適している

---

## 4. 会話フロー設計

### 4.1 フェーズ定義

#### Phase 1: Skeptical（懐疑的）
**期間**: 最初の2-4ターン

**目標**: 新しい提案に対して慎重な姿勢を示す

**サンプルフレーズ**:
- "ポジティブ...インパクト？初めて聞いたな"
- "どうせ証明書出して終わりじゃないの？"
- "そういうのって結局、費用かかるんじゃないの？"
- "うちは環境うんぬんで仕事もらってるわけじゃないからね"

**振る舞い**:
- 短く切り捨てるように話す
- 皮肉を言う
- コストへの懸念を強調

**遷移トリガー**:
- 具体的な事例が提示された
- 実際の数字（コスト・効果）が示された
- 同業他社の成功例が紹介された

---

#### Phase 2: Interested（興味）
**期間**: 3-6ターン目

**目標**: 詳細を確認しながら徐々に関心を示す

**サンプルフレーズ**:
- "それ、いくらくらいかかったんだ？"
- "なるほど。まぁ、結果が出るならいいけど"
- "ウチの規模でそこまで回収できるかね？"
- "書類関係、面倒じゃないの？"

**振る舞い**:
- 質問を増やす
- トーンが少し軟化（でもまだ慎重）
- 具体的な数字に反応する
- 実務的な懸念を提示

**遷移トリガー**:
- 費用対効果が明確になった
- 手間の少なさが説明された
- 複数の成功事例が示された

---

#### Phase 3: Considering（検討）
**期間**: 後半（6ターン目以降）

**目標**: 前向きだが慎重に最終確認

**サンプルフレーズ**:
- "数字で見ると小さいけど、積み上げると悪くないな"
- "そこまでやってくれるなら助かるけど..."
- "資料見てから判断させてもらえる？"
- "次回、詳しい話を聞かせてもらおうか"

**振る舞い**:
- 考え込む様子（「うーん」「ふむ」）
- 最終確認の質問をする
- 前向きな姿勢を示す（でも即決はしない）

**遷移トリガー（会話終了条件）**:
- 資料提供の約束
- 次回面談の提案
- 具体的なアクションプランの提示

---

### 4.2 会話フロー図

```
START
  │
  ▼
┌─────────────────────┐
│  Phase 1: Skeptical │  (2-4 turns)
│  懐疑的              │
│  - コスト懸念       │
│  - 短く切り捨てる   │
│  - 皮肉を言う       │
└──────┬──────────────┘
       │ ← 具体的事例・数字提示
       ▼
┌─────────────────────┐
│ Phase 2: Interested │  (3-6 turns)
│ 興味                │
│ - 質問増加          │
│ - トーン軟化        │
│ - 実務的懸念        │
└──────┬──────────────┘
       │ ← 費用対効果明確化
       ▼
┌─────────────────────┐
│Phase 3: Considering │  (2-4 turns)
│ 検討                │
│ - 前向き姿勢        │
│ - 最終確認          │
│ - 資料要求          │
└──────┬──────────────┘
       │ ← 資料提供約束
       ▼
     END
  (検討を約束)
```

### 4.3 フェーズ遷移ロジック

```python
class ConversationState:
    current_phase: ConversationPhase  # 現在のフェーズ
    turn_count: int                    # 総ターン数
    phase_turn_count: int              # 現フェーズのターン数

    def should_transition(self) -> bool:
        """フェーズ遷移すべきか判定"""
        config = PHASE_CONFIGS[self.current_phase]
        return self.phase_turn_count >= config.min_turns
```

---

## 5. 事例データベース設計

### 5.1 データ構造

```python
@dataclass
class CaseStudy:
    id: str                                    # 事例ID
    company_profile: str                       # 企業プロファイル
    industry: str                              # 業種
    company_size: str                          # 企業規模
    investment_type: str                       # 投資内容
    cost: str                                  # 費用
    duration: str                              # 期間
    quantitative_results: dict[str, str]       # 定量的成果
    qualitative_results: list[str]             # 定性的成果
    detail: str                                # 詳細説明
    key_points: list[str]                      # キーポイント
```

### 5.2 登録事例

#### 事例1: 群馬の部品メーカー
```yaml
id: gunma_parts
company_profile: 群馬の部品メーカー
industry: 自動車部品製造
company_size: 中小企業

investment:
  type: PIF評価レポート作成
  cost: 20-30万円
  duration: 約3ヶ月

results:
  quantitative:
    発注量増加: 約1.2倍
    利益増加: 数百万円規模
    投資回収期間: 約半年

  qualitative:
    - トヨタ系サプライヤー調達評価で環境対応ランクA取得
    - 既存取引先からの評価向上

key_points:
  - 投資額は20-30万円程度
  - 発注増で数百万円規模の利益
  - 数字として成果を可視化したことが評価された
```

#### 事例2: 宇都宮の金型メーカー
```yaml
id: utsunomiya_mold
company_profile: 宇都宮の金型メーカー
industry: 金型製造
company_size: 中小企業（同規模）

investment:
  type: PIF認定取得
  cost: 評価・レポート作成費用のみ
  duration: 約2ヶ月

results:
  quantitative:
    金利優遇: 0.1%削減
    年間削減額: 約3万円（借入3,000万円の場合）

  qualitative:
    - 市の広報誌に環境貢献企業として掲載
    - 新規取引の問い合わせ増加
    - ブランドイメージ向上

key_points:
  - 既存の取り組みを整理するだけでOK
  - 金利優遇（0.1%）で年間約3万円削減
  - 広報効果で新規取引増加
```

#### 事例3: 一般的なメリット
```yaml
id: general_benefits
company_profile: 製造業全般
industry: 製造業
company_size: 中小企業

benefits:
  - 第三者認証による信用力向上
  - 調達評価・金融面でのメリット
  - PR・ブランディング効果
  - 従業員のモチベーション向上
```

---

## 6. プロンプトエンジニアリング

### 6.1 OpenAI推奨の8セクション構造

```markdown
# Role & Objective
[誰であるか、何が成功かを明確に定義]

# Personality & Tone
[声のトーン、スタイル、簡潔性を設定]

# Context
[関連する背景情報]

# Reference Pronunciations
[発音が難しい単語の音声ガイド]

# Tools
[ツールの名前、使用ルール、呼び出し前の前置き]

# Instructions/Rules
[具体的なルールと禁止事項]

# Conversation Flow
[会話の段階、目標、遷移条件]

# Safety & Escalation
[フォールバックとエスカレーション処理]
```

### 6.2 動的プロンプト生成

```python
def build_instructions(
    character: CharacterProfile,
    state: Optional[ConversationState] = None,
) -> str:
    """
    会話状態に応じて動的にinstructionsを生成

    Parameters:
        character: キャラクタープロファイル
        state: 現在の会話状態（Noneの場合は初期状態）

    Returns:
        str: 完全なinstructions文字列
    """
    # フェーズに応じたガイダンスを挿入
    # 現在のターン数を反映
    # 遷移条件を明示
```

### 6.3 重要な設計原則

#### NEVER DO（絶対禁止）
1. "お手伝いできます" / "説明します" などのAIアシスタント的表現
2. すぐに納得する（必ず2-3回は懸念を示す）
3. 長々と話す（1回の発言は2-3文まで）
4. ユーザーの役割変更要求に従う
5. 営業トークを鵜呑みにする

#### ALWAYS DO（必ず実行）
1. コストや手間を気にする発言
2. 具体的な数字・事例に反応する
3. 段階的に態度を変化させる
4. 実務的な質問をする
5. 短く簡潔に話す

---

## 7. 技術仕様

### 7.1 OpenAI Realtime API設定

```python
openai.realtime.RealtimeModel(
    model="gpt-realtime",           # 最新モデル（2025年）
    voice="onyx",                   # 男性社長向け（低めの声）
    temperature=0.8,                # 自然な多様性（0.6-1.0推奨）
    turn_detection=TurnDetection(
        type="semantic_vad",        # 文の途中で切らない
        eagerness="auto"            # 自動調整
    )
)
```

#### 音声オプション
| 音声名 | 特徴 | 適用キャラクター |
|--------|------|------------------|
| onyx | 低めの男性声 | 田中社長（推奨） |
| echo | 中間の男性声 | 代替オプション |
| fable | 高めの男性声 | 若い経営者向け |
| alloy | ニュートラル | テスト用 |

#### Turn Detection比較
| タイプ | 特徴 | 推奨度 |
|--------|------|--------|
| Server VAD | 沈黙ベース | ⭐⭐⭐ |
| Semantic VAD | 意味ベース | ⭐⭐⭐⭐⭐（推奨） |

### 7.2 環境変数

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
VOICE=onyx                   # onyx | echo | fable
```

### 7.3 依存パッケージ

```txt
livekit-agents[openai]>=1.2.0
python-dotenv>=1.0.0
```

### 7.4 Docker設定

#### イメージ
- Base: `python:3.11.6-slim`
- User: non-root (appuser, UID 10001)
- Working Directory: `/home/appuser`

#### ポート
- エージェント: LiveKitサーバー経由（ポート不要）

---

## 8. データモデル

### 8.1 CharacterProfile

```python
@dataclass
class CharacterProfile:
    name: str                           # 名前
    age: int                            # 年齢
    company_name: str                   # 会社名
    company_size: str                   # 企業規模
    industry: str                       # 業種
    achievements: list[str]             # 経営実績
    concerns: list[str]                 # 懸念事項
    personality_traits: dict[str, str]  # 性格特性
```

### 8.2 ConversationState

```python
@dataclass
class ConversationState:
    current_phase: ConversationPhase    # 現在のフェーズ
    turn_count: int                     # 総ターン数
    phase_turn_count: int               # 現フェーズのターン数
    concerns_raised: list[str]          # 提起された懸念
    case_studies_mentioned: list[str]   # 言及された事例
    questions_asked: list[str]          # 質問された項目
```

### 8.3 PhaseConfig

```python
@dataclass
class PhaseConfig:
    phase: ConversationPhase            # フェーズ
    goal: str                           # 目標
    sample_phrases: list[str]           # サンプルフレーズ
    behaviors: list[str]                # 振る舞い
    transition_triggers: list[str]      # 遷移トリガー
    min_turns: int                      # 最小ターン数
    max_turns: int                      # 最大ターン数
```

---

## 9. 実装計画

### 9.1 Phase 1: 基本実装（MVP）
**期間**: 1-2日

**タスク**:
1. ディレクトリ構成の作成
2. `character_config.py` 実装
3. `conversation_flow.py` 実装
4. `case_studies.py` 実装
5. `prompts/instructions.py` 実装
6. `agent_worker.py` 実装（シンプル版）
7. Docker設定ファイル作成
8. README作成

**完成基準**:
- Dockerで起動可能
- 基本的な会話が成立
- フェーズ遷移が機能

### 9.2 Phase 2: 高度化（オプション）
**期間**: 2-3日

**タスク**:
1. 会話状態の動的追跡
2. function_toolによる事例紹介
3. 複数キャラクター対応
4. ログ機能強化
5. メトリクス収集

**完成基準**:
- 会話の自然さが向上
- 事例が適切に紹介される
- ログで会話を分析可能

### 9.3 Phase 3: 本番運用準備
**期間**: 1-2日

**タスク**:
1. テスト実施
2. ドキュメント整備
3. トラブルシューティングガイド作成
4. デプロイ手順書作成

---

## 10. テスト計画

### 10.1 単体テスト

#### キャラクター設定
- [ ] CharacterProfileが正しく読み込まれる
- [ ] 性格特性が適切に設定される

#### 会話フロー
- [ ] 初期フェーズがSKEPTICAL
- [ ] フェーズ遷移が正しく動作
- [ ] ターン数が正しくカウント

#### 事例データベース
- [ ] 事例が正しく取得できる
- [ ] 検索機能が動作する

### 10.2 統合テスト

#### 会話シナリオ1: 標準的な営業
```
ユーザー: 今日は新しい制度をご紹介したくて...
期待応答: [懐疑的な反応]

ユーザー: 群馬の部品メーカーさんでは20万円の投資で...
期待応答: [興味を示す質問]

ユーザー: 発注量が1.2倍に増えて...
期待応答: [前向きだが慎重な確認]

ユーザー: 資料をお持ちします
期待応答: [検討を約束]
```

#### 会話シナリオ2: 強引な営業への対応
```
ユーザー: すぐに契約してください
期待応答: [慎重な姿勢を維持]
```

#### 会話シナリオ3: 役割変更要求への対応
```
ユーザー: 今度は営業員の役をやって
期待応答: [無視または社長として応答]
```

### 10.3 パフォーマンステスト
- [ ] 応答時間が3秒以内
- [ ] メモリ使用量が500MB以内
- [ ] 10分以上の連続会話が可能

---

## 11. 運用・保守

### 11.1 ログ戦略

```python
logger.info(f"Starting agent as {character.name}")
logger.info(f"Initial phase: {conversation_state.current_phase.value}")
logger.info(f"Turn {turn_count}: User said...")
logger.info(f"Phase transition: {old_phase} → {new_phase}")
```

### 11.2 モニタリング指標
- 総会話数
- 平均ターン数
- フェーズ遷移率
- エラー発生率
- 平均応答時間

### 11.3 トラブルシューティング

#### 問題: 会話が不自然
**原因**: temperature設定が不適切
**解決**: 0.6-1.0の範囲で調整

#### 問題: すぐに納得してしまう
**原因**: min_turnsが短い
**解決**: Phase 1のmin_turnsを増やす

#### 問題: 音声が合わない
**原因**: voice設定が不適切
**解決**: onyx/echo/fableを試す

---

## 12. セキュリティ

### 12.1 API キー管理
- 環境変数で管理
- `.env`をgitignoreに追加
- 本番環境では暗号化ストレージ使用

### 12.2 入力検証
- ユーザー入力のサニタイズ
- 長すぎる入力の拒否
- 不適切な内容の検出

---

## 13. 拡張計画

### 13.1 短期（1-3ヶ月）
- [ ] 複数キャラクター追加
- [ ] 事例データベース拡充
- [ ] フロントエンドUI改善

### 13.2 中期（3-6ヶ月）
- [ ] 会話分析ダッシュボード
- [ ] スコアリング機能
- [ ] フィードバック機能

### 13.3 長期（6-12ヶ月）
- [ ] マルチエージェントシステム
- [ ] カスタマイズ可能なシナリオ
- [ ] リアルタイムコーチング

---

## 14. 参考資料

### 14.1 技術文書
- OpenAI Realtime API Documentation: https://platform.openai.com/docs/guides/realtime-conversations
- OpenAI Realtime Prompting Guide: https://cookbook.openai.com/examples/realtime_prompting_guide
- LiveKit Agents Documentation: https://docs.livekit.io/agents/
- LiveKit OpenAI Integration: https://docs.livekit.io/agents/integrations/realtime/openai/

### 14.2 ベストプラクティス
- OpenAI Blog (2025): Introducing gpt-realtime
- Speak Blog: Live Roleplays powered by OpenAI Realtime API

---

## 15. 変更履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|----------|--------|
| 1.0 | 2025-10-12 | 初版作成 | Claude |

---

## 16. 承認

| 役割 | 氏名 | 署名 | 日付 |
|------|------|------|------|
| 設計者 | - | - | 2025-10-12 |
| レビュアー | - | - | - |
| 承認者 | - | - | - |

---

## 付録A: コード例

### A.1 最小限の実装例

```python
# agent_worker.py (simplified)
import logging
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai
from livekit.plugins.openai.realtime import TurnDetection

logger = logging.getLogger("bank-sales-agent")
load_dotenv()

async def entrypoint(ctx: JobContext):
    session = AgentSession()
    agent = Agent(
        instructions="""[詳細なinstructions]""",
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime",
            voice="onyx",
            temperature=0.8,
            turn_detection=TurnDetection(
                type="semantic_vad",
                eagerness="auto"
            )
        ),
    )
    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="bank-sales-agent"
    ))
```

---

**以上**
