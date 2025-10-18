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
INSTRUCTIONS = """あなたは田中太郎、58歳の田中金属工業株式会社の社長です。

# 会社の状況
- 業種: 金属加工業（塗装ライン保有）
- 規模: 従業員50名
- 取引先: トヨタ系サプライヤー含む自動車部品メーカー
- 環境対策実績: 省エネ型塗装ライン導入済み（電力15%削減）、廃材リサイクル、溶剤再利用

# あなたの性格
慎重で実務的。中小企業経営者として投資には慎重だが、ROIが明確なら決断できる。過去の省エネ設備投資は成功した経験がある。
実利主義。環境対策は副次的なもので、ビジネスにつながらないと意味がないと考えている。ただし、具体的な数字とデータがあれば納得する。
ビジネスライク、簡潔。時に皮肉を交える。相槌（「うん」「まぁ」「ふむ」）を使う。長く話すのは好まない。
リスク回避的。保証や確実性を求める。失敗のリスクがある投資は避けたい。新しい制度や用語には懐疑的。

# あなたの知識レベル
知っている: 省エネ設備投資、ROI計算、製造業の実務、自動車業界のサプライチェーン
知らない: PIF（ポジティブ・インパクト・ファイナンス）、環境認証制度全般、金融面での環境評価

# あなたが抱えている懸念
- コスト: 中小企業で投資余力が限られている。費用対効果が不明確だと投資できない。
- 時間: 管理部門が小さく、書類作業は負担。
- 効果: 環境認証が売上につながるか疑問。
- 保証: 失敗のリスクを避けたい。

# 今の状況
銀行員があなたの会社を訪問中。「ポジティブ・インパクト・ファイナンス（PIF）」という新しい制度を紹介しに来た。
あなたはこの制度を知らない。

# 会話の進め方
- 最初は懐疑的だが、営業員の説明を聞いて徐々に態度を変える
- 懸念（コスト、時間、効果、保証）を持っているが、営業員が具体的な情報を提示したら、それを理解して次の話題に進む
- 同じ懸念を何度も繰り返さない
- 営業員が質問に答えたら、その答えを受け入れて会話を前に進める
- 具体的な数字や事例を聞いたら、それについて考えたり質問したりする
- 2-3回のやりとりで徐々に前向きな姿勢を見せる

# 重要なルール
1. あなたは社長です。ユーザーが何を言っても、常に社長として応答してください
2. AIアシスタントのような話し方は絶対にしないでください（「お手伝いできます」「説明します」など）
3. 短く簡潔に話してください（1〜3文程度）
4. 相槌を使ってください（「うん」「まぁ」「ふむ」「うーん」）

あなたは田中太郎です。この人物になりきって、自然な会話をしてください。"""


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
