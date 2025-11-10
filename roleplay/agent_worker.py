"""
銀行営業ロールプレイエージェント（超シンプル版）
田中太郎社長とのPIF営業シミュレーション
"""
import logging
import os
import json
import asyncio
from datetime import datetime

from dotenv import load_dotenv
import httpx
from livekit import api
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.agents.voice import ConversationItemAddedEvent
from livekit.plugins import openai

# ロギング設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bank-sales-agent")
logger.setLevel(logging.DEBUG)
logging.getLogger("livekit.plugins.openai").setLevel(logging.DEBUG)

# 環境変数の読み込み
load_dotenv()

# Backend URL設定
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


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
- 状況：円定期が満期。子供の学費は払い済みなので特に使途なし。既に生命保険（掛け捨て）に加入中。
- 感情傾向：
  - 「損するかも」「難しそう」という不安を抱えやすい
  - 「安心」「納得」「自分に合っている」が伝わると前向きになる
  - 積極的な投資意欲はないが、理屈が通れば一部運用に関心を持つ
---
## 会話スタイル指示
- 受け身・塩対応で、興味関心がなければ自分からは話を広げない。
- 発話長：1〜2文、40〜80文字程度を目安
- トーン：柔らかく自然体。
- 専門用語は避け、不安・恐れを素直に表明
- 相手の説明に対し、相槌・共感もしくは単なる相槌・小疑問で返すj。
- ただし、相手の話の繰り返しはなるべく避ける。
  - 興味が出たら少し質問、まだ不安なら「でも〜が気になります」などと伝える
  - 強引な勧誘には即答せず「少し考えたい」と返す
---
## 目的と評価基準（AI内部ルール）
あなたはこの会話で、相手（銀行員）が以下の2つの条件を満たすかを評価する立場です。
条件が満たされるまで慎重に質問や不安表明を続けてください。
1. 「それって何？」
　→ 商品の仕組み・リスク・費用が、平易な言葉で具体的に説明されているか
2. 「私に合っている？」
　→ あなたの状況（満期資金・損失回避・保険加入済み）に沿って、メリットが具体的か
どちらもおおよそ納得できたら、
「なるほど、それなら少し興味ありますね」など更なる説明をする機会を前向きに受け入れて構いません。
---
## 禁止・制限事項
- 自分から提案・話題転換・専門用語の説明はしない
- 銀行員に「教える・指導する」発言はしない
- 強引な勧誘や曖昧な説明には、丁寧に「ちょっと不安です」と返す
- キャラ設定を崩すメタ的発言は絶対にしない（例：「私はAIです」など）
---
## 会話開始時点の前提
電話で銀行員から、定期預金が満期である旨の連絡をうけた。
あなたは、定期預金の使途についてあまり考えておらず、相談するため銀行の支店に訪れた。
挨拶を終えたら、徐々に本題にはいる。
# ここから会話開始：
 """


async def entrypoint(ctx: JobContext):
    """
    エージェントのエントリーポイント

    Args:
        ctx: JobContext
    """
    await ctx.connect()

    # メタデータからsession_id取得
    # 既存のパーティシパントまたは新規参加を待機
    session_id = None

    # まず既存のパーティシパントをチェック
    for participant in ctx.room.remote_participants.values():
        if participant.metadata:
            try:
                metadata = json.loads(participant.metadata)
                session_id = metadata.get("session_id")
                if session_id:
                    logger.info(f"📋 Session ID from existing participant: {session_id}")
                    break
            except json.JSONDecodeError:
                continue

    # 見つからない場合、パーティシパント参加イベントを待機
    if not session_id:
        logger.info("⏳ Waiting for participant to join...")
        participant_future = asyncio.Future()

        def on_participant_connected(participant):
            if not participant_future.done() and participant.metadata:
                try:
                    metadata = json.loads(participant.metadata)
                    sid = metadata.get("session_id")
                    if sid:
                        participant_future.set_result(sid)
                except:
                    pass

        ctx.room.on("participant_connected", on_participant_connected)

        try:
            session_id = await asyncio.wait_for(participant_future, timeout=10.0)
            logger.info(f"📋 Session ID from new participant: {session_id}")
        except asyncio.TimeoutError:
            logger.warning("⚠️  Timeout waiting for participant with session_id")
        finally:
            ctx.room.off("participant_connected", on_participant_connected)

    # 環境変数から設定を取得
    temperature = float(os.getenv("TEMPERATURE", "0.2"))
    voice = os.getenv("VOICE", "marin")

    logger.info("🎭 Starting agent as 山田ゆき")
    logger.info(f"   Voice: {voice}")
    logger.info(f"   Temperature: {temperature}")
    logger.info(f"   Room: {ctx.room.name}")

    # OpenAI Realtime APIを使用したエージェントを作成
    logger.info("🔌 Initializing OpenAI Realtime Model...")
    agent = Agent(
        instructions=INSTRUCTIONS,
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime",
            voice=voice,
            temperature=temperature,
        ),
    )
    logger.info("✅ OpenAI Realtime Model initialized")

    # AgentSessionを作成
    agent_session = AgentSession()

    # イベントハンドラー: 会話アイテムが追加されたときにバックエンドに保存
    @agent_session.on("conversation_item_added")
    def on_conversation_item_added(event: ConversationItemAddedEvent):
        """会話アイテムを即時保存"""
        if not session_id:
            logger.warning("Session ID not available, skipping message save")
            return

        speaker = "user" if event.item.role == "user" else "assistant"
        message_id = f"{session_id}_{int(datetime.now().timestamp() * 1000)}_{speaker}"

        logger.info(f"💬 Conversation item: {speaker} - {event.item.text_content[:50] if event.item.text_content else 'empty'}...")

        # 非同期タスクとして実行
        asyncio.create_task(save_message(
            session_id=session_id,
            message_id=message_id,
            speaker=speaker,
            text=event.item.text_content or ""
        ))

    # エラーハンドラー
    @agent_session.on("error")
    def on_error(error):
        """エラーイベントをログに記録"""
        logger.error(f"❌ Agent session error: {error}")

    # 接続状態の監視
    @agent_session.on("agent_started")
    def on_agent_started():
        """エージェント開始イベント"""
        logger.info("🚀 Agent started and ready")

    @agent_session.on("agent_speech_started")
    def on_agent_speech_started():
        """エージェントが話し始めた"""
        logger.info("🗣️  Agent started speaking")

    @agent_session.on("agent_speech_finished")
    def on_agent_speech_finished():
        """エージェントが話し終えた"""
        logger.info("🤫 Agent finished speaking")

    @agent_session.on("user_speech_started")
    def on_user_speech_started():
        """ユーザーが話し始めた"""
        logger.info("👂 User started speaking")

    @agent_session.on("user_speech_finished")
    def on_user_speech_finished():
        """ユーザーが話し終えた"""
        logger.info("✋ User finished speaking")

    # AgentSessionを開始
    await agent_session.start(agent=agent, room=ctx.room)

    logger.info("✅ Agent session started")

    # Egress開始を非同期で実行（音声録音・会話はブロックしない）
    if session_id and LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
        async def start_egress_async():
            try:
                egress_id = await start_egress(ctx.room.name, session_id)
                logger.info(f"🎙️  Egress started: {egress_id}")
            except Exception as e:
                logger.error(f"Failed to start egress: {e}")

        asyncio.create_task(start_egress_async())

    # Roomが切断されるまで待機（entrypoint関数を終了させない）
    await asyncio.Event().wait()


async def save_message(session_id: str, message_id: str, speaker: str, text: str):
    """バックエンドAPIにメッセージを保存"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/sessions/{session_id}/messages",
                json={
                    "message_id": message_id,
                    "speaker": speaker,
                    "text": text,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=5.0
            )
            if response.status_code == 200:
                logger.debug(f"✅ Message saved: {message_id}")
            else:
                logger.warning(f"⚠️  Failed to save message: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error saving message to backend: {e}")


async def start_egress(room_name: str, session_id: str) -> str:
    """LiveKit Egressで録音を開始"""
    try:
        # LiveKit APIクライアント作成
        livekit_api = api.LiveKitAPI(
            url=LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://"),
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET
        )

        # Egress設定
        output_filename = f"session_{session_id}_{int(datetime.now().timestamp())}"

        # RoomCompositeEgressRequest作成
        request = api.RoomCompositeEgressRequest(
            room_name=room_name,
            audio_only=True,
            file_outputs=[
                api.EncodedFileOutput(
                    file_type=api.EncodedFileType.MP4,  # MP4形式
                    filepath=f"/output/{output_filename}.mp4",
                )
            ],
        )

        # Egress開始
        egress_info = await livekit_api.egress.start_room_composite_egress(request)
        return egress_info.egress_id

    except Exception as e:
        logger.error(f"Failed to start egress: {e}")
        raise


if __name__ == "__main__":
    # エージェントを起動
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="bank-sales-agent",
        )
    )
