"""
銀行営業ロールプレイエージェント - メインエントリーポイント
田中太郎社長とのPIF営業シミュレーション
"""
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai

# 自作モジュールのインポート
from character_config import get_character, CharacterProfile
from conversation_flow import (
    ConversationState,
    ConversationPhase,
    PHASE_CONFIGS,
    get_next_phase,
    analyze_user_message,
)
from prompts.instructions import build_instructions
from evaluation import evaluate_conversation

# ロギング設定
logger = logging.getLogger("bank-sales-agent")
logger.setLevel(logging.INFO)

# 環境変数の読み込み
load_dotenv()


class BankSalesAgent:
    """銀行営業ロールプレイエージェント"""

    def __init__(
        self,
        character_type: str = "cautious_ceo",
        temperature: float = 0.8,
        voice: str = "onyx",
    ):
        """
        初期化

        Args:
            character_type: キャラクタータイプ（cautious_ceo または friendly_ceo）
            temperature: LLMの温度パラメータ（0.6-1.0推奨）
            voice: 音声タイプ（onyx, echo, fable, alloy）
        """
        self.character: CharacterProfile = get_character(character_type)
        self.state: ConversationState = ConversationState()
        self.temperature: float = temperature
        self.voice: str = voice

        logger.info(f"🎭 Starting agent as {self.character.name}")
        logger.info(f"📊 Initial phase: {self.state.current_phase.value}")

    def get_current_instructions(self) -> str:
        """
        現在の会話状態に基づいたinstructionsを取得

        Returns:
            str: instructions文字列
        """
        return build_instructions(character=self.character, state=self.state)

    def update_state(self, user_message: str):
        """
        ユーザーメッセージに基づいて会話状態を更新

        Args:
            user_message: ユーザーのメッセージ
        """
        # ターン数を増加
        self.state.add_turn()

        # メッセージを分析して状態を更新
        self.state = analyze_user_message(user_message, self.state)

        logger.info(f"📝 Turn {self.state.turn_count}: User said: {user_message[:50]}...")

        # フェーズ遷移をチェック
        current_phase = self.state.current_phase
        phase_config = PHASE_CONFIGS[current_phase]

        if self.state.should_transition(phase_config):
            next_phase = get_next_phase(current_phase)
            if next_phase:
                old_phase = current_phase.value
                self.state.transition_to(next_phase)
                logger.info(f"🔄 Phase transition: {old_phase} → {next_phase.value}")
            else:
                logger.info("✅ Conversation reached final phase")

    def get_evaluation(self) -> str:
        """
        現在の会話のパフォーマンス評価を取得

        Returns:
            str: 評価レポート
        """
        metrics = evaluate_conversation(self.state)
        return metrics.generate_feedback()


# グローバルなエージェントインスタンス（会話状態を保持）
_agent_instance: Optional[BankSalesAgent] = None


async def entrypoint(ctx: JobContext):
    """
    エージェントのエントリーポイント

    Args:
        ctx: JobContext
    """
    global _agent_instance

    # 環境変数から設定を取得
    character_type = os.getenv("CHARACTER_TYPE", "cautious_ceo")
    temperature = float(os.getenv("TEMPERATURE", "0.8"))
    voice = os.getenv("VOICE", "onyx")

    # エージェントインスタンスを作成
    _agent_instance = BankSalesAgent(
        character_type=character_type,
        temperature=temperature,
        voice=voice,
    )

    # 初期instructionsを取得
    initial_instructions = _agent_instance.get_current_instructions()

    # LiveKit Agent Sessionを開始
    session = AgentSession()

    # OpenAI Realtime APIを使用したエージェントを作成
    agent = Agent(
        instructions=initial_instructions,
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime",
            voice=voice,
            temperature=temperature,
        ),
    )

    logger.info("🚀 Bank Sales Agent started")
    logger.info(f"   Character: {_agent_instance.character.name}")
    logger.info(f"   Voice: {voice}")
    logger.info(f"   Temperature: {temperature}")

    # セッション開始
    await session.start(agent=agent, room=ctx.room)

    # 会話終了後の評価（実際にはフロントエンドからトリガーする必要があります）
    # ここでは例として記載
    """
    # 会話終了時:
    evaluation = _agent_instance.get_evaluation()
    logger.info("=" * 60)
    logger.info("📊 EVALUATION REPORT")
    logger.info("=" * 60)
    logger.info(evaluation)
    """


def get_agent_instance() -> Optional[BankSalesAgent]:
    """
    現在のエージェントインスタンスを取得（テスト用）

    Returns:
        Optional[BankSalesAgent]: エージェントインスタンス
    """
    return _agent_instance


if __name__ == "__main__":
    # エージェントを起動
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="bank-sales-agent",
        )
    )
