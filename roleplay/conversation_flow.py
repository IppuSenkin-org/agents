"""
会話フロー管理モジュール
フェーズ遷移とトリガー条件を定義
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ConversationPhase(Enum):
    """会話フェーズ"""
    SKEPTICAL = "skeptical"      # 懐疑的
    INTERESTED = "interested"    # 興味
    CONSIDERING = "considering"  # 検討


@dataclass
class TransitionTrigger:
    """フェーズ遷移のトリガー条件"""
    type: str  # "keyword" | "turn_count" | "data_provided" | "combined"
    value: Any
    description: str


@dataclass
class PhaseConfig:
    """フェーズ設定"""
    phase: ConversationPhase
    goal: str
    sample_phrases: List[str]
    behaviors: List[str]
    transition_triggers: List[TransitionTrigger]
    min_turns: int
    max_turns: int


@dataclass
class ConversationState:
    """会話状態"""
    current_phase: ConversationPhase = ConversationPhase.SKEPTICAL
    turn_count: int = 0
    phase_turn_count: int = 0
    concerns_raised: List[str] = field(default_factory=list)
    case_studies_mentioned: List[str] = field(default_factory=list)
    questions_asked: List[str] = field(default_factory=list)
    data_provided: Dict[str, bool] = field(default_factory=lambda: {
        "cost": False,
        "roi": False,
        "case_study": False,
        "time_required": False,
        "support_offered": False
    })
    keywords_detected: List[str] = field(default_factory=list)

    def should_transition(self, config: PhaseConfig) -> bool:
        """
        フェーズ遷移すべきか判定

        Args:
            config: 現在のフェーズ設定

        Returns:
            bool: 遷移すべきならTrue
        """
        # 最小ターン数に達していない場合は遷移しない
        if self.phase_turn_count < config.min_turns:
            return False

        # 最大ターン数を超えた場合は強制遷移
        if self.phase_turn_count >= config.max_turns:
            return True

        # トリガー条件をチェック
        for trigger in config.transition_triggers:
            if self._check_trigger(trigger):
                return True

        return False

    def _check_trigger(self, trigger: TransitionTrigger) -> bool:
        """
        個別のトリガー条件をチェック

        Args:
            trigger: トリガー条件

        Returns:
            bool: 条件を満たす場合True
        """
        if trigger.type == "turn_count":
            return self.phase_turn_count >= trigger.value

        elif trigger.type == "data_provided":
            # 指定されたデータがすべて提供されているかチェック
            required_data = trigger.value
            if isinstance(required_data, dict):
                return all(
                    self.data_provided.get(key, False) == value
                    for key, value in required_data.items()
                )
            return False

        elif trigger.type == "keyword":
            # キーワードのいずれかが検出されたかチェック
            keywords = trigger.value
            if isinstance(keywords, list):
                return any(kw in self.keywords_detected for kw in keywords)
            return False

        elif trigger.type == "combined":
            # 複数条件の組み合わせ
            conditions = trigger.value
            if isinstance(conditions, dict):
                # すべての条件を満たす必要がある
                data_ok = conditions.get("data_provided", {})
                keywords_ok = conditions.get("keywords", [])

                data_satisfied = all(
                    self.data_provided.get(key, False)
                    for key in data_ok
                )
                keyword_satisfied = any(
                    kw in self.keywords_detected
                    for kw in keywords_ok
                ) if keywords_ok else True

                return data_satisfied and keyword_satisfied

        return False

    def add_turn(self):
        """ターン数を増加"""
        self.turn_count += 1
        self.phase_turn_count += 1

    def transition_to(self, new_phase: ConversationPhase):
        """
        新しいフェーズに遷移

        Args:
            new_phase: 遷移先のフェーズ
        """
        self.current_phase = new_phase
        self.phase_turn_count = 0

    def mark_data_provided(self, data_type: str):
        """
        データ提供済みとしてマーク

        Args:
            data_type: データタイプ（cost, roi, case_study, etc.）
        """
        if data_type in self.data_provided:
            self.data_provided[data_type] = True

    def add_keyword(self, keyword: str):
        """
        検出されたキーワードを追加

        Args:
            keyword: キーワード
        """
        if keyword not in self.keywords_detected:
            self.keywords_detected.append(keyword)


# フェーズ設定の定義
PHASE_CONFIGS = {
    ConversationPhase.SKEPTICAL: PhaseConfig(
        phase=ConversationPhase.SKEPTICAL,
        goal="新しい提案に対して慎重な姿勢を示す",
        sample_phrases=[
            "ポジティブ…インパクト？初めて聞いたな",
            "どうせ証明書出して終わりじゃないの？",
            "そういうのって結局、費用かかるんじゃないの？",
            "うちは環境うんぬんで仕事もらってるわけじゃないからね"
        ],
        behaviors=[
            "短く切り捨てるように話す",
            "皮肉を言う",
            "コストへの懸念を強調",
            "新しい用語に戸惑いを示す"
        ],
        transition_triggers=[
            TransitionTrigger(
                type="combined",
                value={
                    "data_provided": ["cost", "case_study"],
                    "keywords": ["具体的", "実際", "数字", "万円", "実例"]
                },
                description="具体的な費用と事例が提示された"
            ),
            TransitionTrigger(
                type="turn_count",
                value=4,
                description="最小ターン数（4ターン）経過"
            )
        ],
        min_turns=2,
        max_turns=5
    ),

    ConversationPhase.INTERESTED: PhaseConfig(
        phase=ConversationPhase.INTERESTED,
        goal="詳細を確認しながら徐々に関心を示す",
        sample_phrases=[
            "それ、いくらくらいかかったんだ？",
            "なるほど。まぁ、結果が出るならいいけど",
            "ウチの規模でそこまで回収できるかね？",
            "書類関係、面倒じゃないの？"
        ],
        behaviors=[
            "質問を増やす",
            "トーンが少し軟化（でもまだ慎重）",
            "具体的な数字に反応する",
            "実務的な懸念を提示"
        ],
        transition_triggers=[
            TransitionTrigger(
                type="combined",
                value={
                    "data_provided": ["cost", "roi", "time_required", "support_offered"],
                    "keywords": []
                },
                description="費用対効果と手間の説明が完了"
            ),
            TransitionTrigger(
                type="turn_count",
                value=5,
                description="最小ターン数（5ターン）経過"
            )
        ],
        min_turns=3,
        max_turns=7
    ),

    ConversationPhase.CONSIDERING: PhaseConfig(
        phase=ConversationPhase.CONSIDERING,
        goal="前向きだが慎重に最終確認",
        sample_phrases=[
            "数字で見ると小さいけど、積み上げると悪くないな",
            "そこまでやってくれるなら助かるけど...",
            "資料見てから判断させてもらえる？",
            "次回、詳しい話を聞かせてもらおうか"
        ],
        behaviors=[
            "考え込む様子（「うーん」「ふむ」）",
            "最終確認の質問をする",
            "前向きな姿勢を示す（でも即決はしない）"
        ],
        transition_triggers=[
            TransitionTrigger(
                type="keyword",
                value=["資料", "次回", "検討", "持ってくる", "詳しい"],
                description="資料提供・次回面談の提案"
            )
        ],
        min_turns=2,
        max_turns=5
    )
}


def get_next_phase(current_phase: ConversationPhase) -> Optional[ConversationPhase]:
    """
    次のフェーズを取得

    Args:
        current_phase: 現在のフェーズ

    Returns:
        Optional[ConversationPhase]: 次のフェーズ。最終フェーズの場合はNone
    """
    phase_order = [
        ConversationPhase.SKEPTICAL,
        ConversationPhase.INTERESTED,
        ConversationPhase.CONSIDERING
    ]

    try:
        current_index = phase_order.index(current_phase)
        if current_index < len(phase_order) - 1:
            return phase_order[current_index + 1]
    except ValueError:
        pass

    return None


def analyze_user_message(message: str, state: ConversationState) -> ConversationState:
    """
    ユーザーメッセージを分析して会話状態を更新

    Args:
        message: ユーザーメッセージ
        state: 現在の会話状態

    Returns:
        ConversationState: 更新された会話状態
    """
    message_lower = message.lower()

    # コストに関するキーワード検出
    cost_keywords = ["万円", "円", "費用", "コスト", "料金"]
    if any(kw in message_lower for kw in cost_keywords):
        state.mark_data_provided("cost")
        state.add_keyword("費用")

    # ROI/効果に関するキーワード検出
    roi_keywords = ["増加", "削減", "効果", "利益", "倍", "%", "パーセント"]
    if any(kw in message_lower for kw in roi_keywords):
        state.mark_data_provided("roi")
        state.add_keyword("効果")

    # 事例に関するキーワード検出
    case_keywords = ["メーカー", "企業", "会社", "事例", "実績", "群馬", "宇都宮"]
    if any(kw in message_lower for kw in case_keywords):
        state.mark_data_provided("case_study")
        state.add_keyword("事例")

    # 時間/手間に関するキーワード検出
    time_keywords = ["期間", "時間", "ヶ月", "週間", "スケジュール"]
    if any(kw in message_lower for kw in time_keywords):
        state.mark_data_provided("time_required")

    # サポートに関するキーワード検出
    support_keywords = ["対応", "代行", "サポート", "手伝", "お手伝い", "こちらで"]
    if any(kw in message_lower for kw in support_keywords):
        state.mark_data_provided("support_offered")
        state.add_keyword("サポート")

    # 資料・次回に関するキーワード検出
    next_keywords = ["資料", "次回", "お持ちします", "詳しい", "また"]
    if any(kw in message_lower for kw in next_keywords):
        state.add_keyword("次回提案")

    return state
