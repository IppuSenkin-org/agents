import logging
import os
import json
import asyncio
from datetime import datetime

from dotenv import load_dotenv
import httpx

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, WorkerType, cli
from livekit.agents.voice import ConversationItemAddedEvent
from livekit.plugins import openai, simli

logger = logging.getLogger("gas-sales-roleplay")
logger.setLevel(logging.INFO)

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

async def entrypoint(ctx: JobContext):
    # メタデータからsession_id取得
    metadata = {}
    session_id = None
    try:
        if ctx.room.metadata:
            metadata = json.loads(ctx.room.metadata)
            session_id = metadata.get("session_id")
            logger.info(f"Session ID from metadata: {session_id}")
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse room metadata: {e}")

    ctx.log_context_fields = {
        "room_name": ctx.room.name,
        "roleplay_type": "gas_sales_ultra_realistic_customer",
        "session_id": session_id,
    }

    openai_api_key = os.getenv("OPENAI_API_KEY")
    logger.info(f"OpenAI API Key exists: {bool(openai_api_key)}")
    logger.info(f"OpenAI API Key prefix: {openai_api_key[:20] if openai_api_key else 'None'}...")

    try:
        session = AgentSession(
            llm=openai.realtime.RealtimeModel(voice="sage"),
            resume_false_interruption=False,
        )
        logger.info("AgentSession created successfully")
    except Exception as e:
        logger.error(f"Failed to create AgentSession: {e}", exc_info=True)
        raise

    # イベントハンドラー: 会話アイテムが追加されたときにバックエンドに保存
    @session.on("conversation_item_added")
    def on_conversation_item_added(event: ConversationItemAddedEvent):
        """メイン経路: 会話アイテムを即時保存"""
        if not session_id:
            logger.warning("Session ID not available, skipping message save")
            return

        speaker = "user" if event.item.role == "user" else "assistant"
        message_id = f"{session_id}_{int(datetime.now().timestamp() * 1000)}_{speaker}"

        logger.info(f"Conversation item added: {speaker} - {event.item.text_content[:50] if event.item.text_content else 'empty'}...")

        # 非同期タスクとして実行
        asyncio.create_task(save_message(
            session_id=session_id,
            message_id=message_id,
            speaker=speaker,
            text=event.item.text_content or ""
        ))

    simliAPIKey = os.getenv("SIMLI_API_KEY")
    simliFaceID = os.getenv("SIMLI_FACE_ID")
    simliLivekitURL = os.getenv("SIMLI_LIVEKIT_URL")  # Simli用のパブリックURL

    logger.info(f"Simli configuration - API Key exists: {bool(simliAPIKey)}, Face ID: {simliFaceID}, LiveKit URL: {simliLivekitURL}")

    try:
        simli_avatar = simli.AvatarSession(
            simli_config=simli.SimliConfig(
                api_key=simliAPIKey,
                face_id=simliFaceID,
            ),
        )
        logger.info("Simli AvatarSession created successfully")
        await simli_avatar.start(
            session,
            room=ctx.room,
            livekit_url=simliLivekitURL,  # Simliクラウドサービス用のパブリックURL
        )
        logger.info("Simli AvatarSession started successfully")
    except Exception as e:
        logger.error(f"Failed to start Simli AvatarSession: {e}", exc_info=True)
        raise

    # start the agent, it will join the room and wait for the avatar to join
    try:
        logger.info("Starting AgentSession...")
        await session.start(
            agent=Agent(instructions= """あなたは山田美咲（35歳女性）です。
                                        ガス会社の既存顧客として普通に会話してください。
                                        営業トークには慎重で、お得なら興味を示します。"""
                                    ),
            room=ctx.room,
        )
        logger.info("AgentSession started successfully")
    except Exception as e:
        logger.error(f"Failed to start AgentSession: {e}", exc_info=True)
        raise


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
                logger.debug(f"Message saved: {message_id}")
            else:
                logger.warning(f"Failed to save message: {response.status_code}")
    except Exception as e:
        logger.error(f"Error saving message to backend: {e}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        worker_type=WorkerType.ROOM,
        agent_name="simli-avatar-agent"
    ))
