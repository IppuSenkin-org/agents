import logging
import os

from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, WorkerType, cli
from livekit.plugins import openai, simli

logger = logging.getLogger("gas-sales-roleplay")
logger.setLevel(logging.INFO)

load_dotenv()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room_name": ctx.room.name,
        "roleplay_type": "gas_sales_ultra_realistic_customer",
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


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        worker_type=WorkerType.ROOM,
        agent_name="simli-avatar-agent"
    ))
