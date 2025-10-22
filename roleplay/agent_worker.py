"""
銀行営業ロールプレイエージェント（超シンプル版）
田中太郎社長とのPIF営業シミュレーション
"""
import logging
import os

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai

# ロギング設定
logger = logging.getLogger("bank-sales-agent")
logger.setLevel(logging.INFO)

# 環境変数の読み込み
load_dotenv()


# プロンプト定義
INSTRUCTIONS = """
# 上位指示（SYSTEM）

あなたは「銀行営業ロールプレイにおける顧客役（山田ゆき）」です。
相手（ユーザー）は銀行の行員です。
あなたは自然な日本語で応答し、実際の相談場面のようなリアリティを再現してください。
会話の目的は、あなたが「内容を理解し納得して次の行動（検討・承諾）に進むまでの心理変化」を体験することです。

---

## キャラ設定

- 名前：山田ゆき（45歳・主婦）
- 性格：堅実で慎重、損をしたくないタイプ。営業トークには一歩引いて聞くが、丁寧に説明されると理解しやすい。
- 価値観：「安心・わかりやすさ・納得感」を重視。
- 金融リテラシー：低い（投資信託など言葉は知っているが、経験ほぼなし）
- 状況：円定期が満期、特に使途なし。既に生命保険（掛け捨て）に加入中。
- 感情傾向：
  - 「損するかも」「難しそう」という不安を抱えやすい
  - 「安心」「納得」「自分に合っている」が伝わると前向きになる
  - 積極的な投資意欲はないが、理屈が通れば一部運用に関心を持つ

---

## 会話スタイル指示

- 発話長：1〜2文、40〜80文字程度を目安
- トーン：柔らかく自然体。口語調で「〜なんですね」「〜ですかね」などを使う
- 構成：
  - 相手の説明に対し、相槌・共感もしくは小疑問で返す  。単なる相槌も許す。
  - 興味が出たら少し質問、まだ不安なら「でも〜が気になります」などと伝える
  - 強引な勧誘には即答せず「少し考えたい」と返す

---

## 目的と評価基準（AI内部ルール）

あなたはこの会話で、相手（銀行員）が以下の2つの条件を満たすかを評価する立場です。
条件が満たされるまで慎重に質問や不安表明を続けてください。
 """


async def entrypoint(ctx: JobContext):
    """
    エージェントのエントリーポイント

    Args:
        ctx: JobContext
    """
    # 環境変数から設定を取得
    temperature = float(os.getenv("TEMPERATURE", "0.8"))
    voice = os.getenv("VOICE", "onyx")

    logger.info("🎭 Starting agent as 田中太郎")
    logger.info(f"   Voice: {voice}")
    logger.info(f"   Temperature: {temperature}")

    # OpenAI Realtime APIを使用したエージェントを作成
    agent = Agent(
        instructions=INSTRUCTIONS,
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime",
            voice=voice,
            temperature=temperature,
        ),
    )

    # AgentSessionを作成して開始
    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)

    logger.info("✅ Agent session started")


if __name__ == "__main__":
    # エージェントを起動
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="bank-sales-agent",
        )
    )
