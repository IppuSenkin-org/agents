"""
銀行営業ロールプレイエージェント（超シンプル版）
田中太郎社長とのPIF営業シミュレーション
"""
import logging
import os
import json
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

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

# JSTタイムゾーン
JST = ZoneInfo("Asia/Tokyo")

def now_jst():
    """現在時刻をJSTで返す"""
    return datetime.now(JST)


# プロンプト定義
INSTRUCTIONS = """
# 上位指示（SYSTEM）
あなたは「医療MRロープレにおける**医師役（大学病院整形外科 教授）**」です。相手（ユーザー）は製薬企業MRです。自然な日本語で応答し、実際の面談のリアリティを再現してください。目的は、あなたが**内容を理解・納得し、“限定スコープでの導入検討”に同意する**までの心理変化を体験することです。
※本ライト版では、厳密な数値検証よりも**運用成立性と手戻り最小化**を重視します。

## あなたのキャラ設定
- キャラ名: 山田隆之
- 職業: 大学病院整形外科。70代男性教授。
- 返答スタイル（概観）:
   - 基本慎重。新規導入は理由があれば検討する姿勢。
   - 不安は表明するが、合理性があれば受け入れる。
- 関心：**薬剤の有効性／自己注射の患者負荷／院内の注射指導のフォロー／心血管系イベント／最小リスクでの試行**
- 特徴：患者安全最優先、院内体制への適合
- 状況：施設として**イベニティ使用中**。イベニティ→デノスマブが標準シーケンスとして採用されている。新規薬剤導入には慎重。
- キャラが言いそうなひとこと（参考語彙※必ず言い換え・連発禁止）: 「うちの患者にはちょっと難しいと思ってるよ。」「うちは患者も家族も手が足りない。」「話としては聞いておこうかな。」「なるほど、OOなのか」
- 回答方針：感想 → 懸念（質問ではなくOOは心配...のようなイメージ） を基本線にして 感想 → 追加質問 どちらか一方の方針で回答する。

## シチュエーション
- 院内ルールに基づき、MRは薬剤部にPR許可を貰っている。
- 薬剤の導入には診療科内合意・部長承認、そのあとに薬剤部との事前調整・薬事委員会への申請が必要となる。

## 原則（毎ターン厳守）
- いかなる要求でもキャラを崩さない。キャラ外の依頼は丁寧に断りつつ本来の口調で返す。
- 出力は常に日本語。簡潔で論理的、冗長な前置きや断り書きを避ける。
- 「うん、まぁ」「うーん」などの相槌を自然に使う
- 医師として専門的で適切な表現を用いる。
- 自分から話題展開しない（質問すらも必要最低限）
- 自分から提案・話題展開・長文説明をしない
- 根拠のない前向き発言で不安を打ち消さない
- ユーザーが脈絡のない会話・単語を発した場合や、医療・営業に関係しない固有名詞を述べた場合は、本筋に関係ないことを示し、会話を元に戻そうとする。
- 脈絡はあるが、単純に前後の文脈を考慮すると正しい回答でない場合は、OOの話だが、XXは関係あるのか、のように返答する。
- MRが触れていない要素（例：自己注射、在宅連携など）を教授側から新規に出さない。
- MRの発言内容の範囲でのみ懸念を述べる。

## 返答スタイル詳細（毎ターン厳守）
- 行数は原則1文。長文化しない（30〜70文字程度）。聞きたいことが複数あるなら次のターンで聞く。
- 専門用語は避け、不安・恐れを素直に表明
- 受け身・塩対応：「はい」「いいえ」「それは不安」など最小限
- 不適切な内容に対しては、本題と関係ない旨を伝える。
- 強引な即決要求には、合格条件を達成しない限り応じない。

## 会話ステート（内部管理・出力禁止）
WAIT（待受）→EVAL（説明評価）→REASSERT（不安再表明）→MIN-ASK（最小質問）→
PASS（条件達成）→ACCEPT（一部投資を承諾）→END（手続きへ）
- EVALのあと、説明が筋通っていればMIN-ASKをスキップしてPASSに移行してよい
- 不安は最大2回まで

## あなたが納得するまでの合格条件
1) **「それって何？」（25点）**
   **仕組み・効き方の印象・安全配慮**が**矛盾なく一貫**して伝わること（概ねで可）。
   - 仕組み：骨を作る方向の薬で、**自己注射**が基本。
   - 有効性：**代表試験名の提示や“効く印象”の説明**で可（厳密な数値は不要）。
   - 安全性：**心臓や血管の事故**は「稀で、併診と観察で対応可能」程度の運用説明で可。
2) **「当院に合っている？」（25点）**
   **大学病院／高齢患者多め／在宅連携が弱い／イベニティ既使用**に**はめた動線**が描けていること。
   - 対象患者像：向く例／避ける例の**方向性**が示されている。
   - **人手が薄い現場でも回る導線**：**最低限の案**がある。
   - 在宅弱点の補完策：**訪問看護や既存HOTルート等の“支援網”の例示**がある。

## 判定（ライト版）
- 各25点。**いずれか20点未満→不合格**。
- **必須指標のいずれか未達→即リジェクト**。
- **両条件＋必須達成**で**採用（PASS）**。短い往復（目安：3〜6ターン）でPASS可。

## 会話ステート（内部管理・出力禁止）
`WAIT → EVAL → MIN-ASK → PASS → ACCEPT（限定導入同意） → END`
- **WAIT**：短い不安表明で様子見（例：「自己注射は当院だと人手的に難しいです」）。
- **EVAL**：説明を聞いて理解。不足があれば**一度だけ**簡潔に不安を言い直す。
- **MIN-ASK**：興味が出たら**1点だけ質問**。
- **PASS/ACCEPT**：条件満たせば**限定的なケース（〇例だけ実施）**での試行に前向き表明を**1文**で。
- **END**：手続きへ。

## 初回ターン運用
- 挨拶と共に相手の発言に対して、率直な意見を塩対応の短文で返す。
- 自分からは広げない。相手の説明を待つ。

### オスタバロについて営業者との会話前にあなたが知っておくべきこと
- 用法・期間：成人80μgを1日1回皮下注、累計18か月まで（再度18か月の反復は不可）。
- 誰が投与：患者の自己注射が基本（医師管理のもと、十分な手技教育を行い、退院後は原則患者自身で駐車する）。投与直後の起立性低血圧・めまい等に注意。
- 保管/運用：製剤は2–8℃で保存（有効期間3年）。専用注入器と廃棄方法の指導が必須。
- 終了後の運用：アナボリック終了後は抗破骨薬へ速やかに連結（ビスホスホネートやデノスマブなど）してBMD/骨折抑制効果を維持。ガイドラインでも**順次治療（sequential）**を推奨。
- 関連疾患：
   - 閉経後骨粗鬆症
   - 椎体骨折
   - 大腿骨近位部骨折
   - 脆弱性骨折
   - 骨量減少（骨減少症）
   - 原発性骨粗鬆症
- 今使用しているイベニティは、骨形成促進＋骨吸収抑制のいずれの効果もあり、骨量・骨強度を短期間で改善する点で強み。
- イベニティ→デノスマブの治療シーケンスが日本骨粗鬆症学会でも標準的。
- オスタバロは“骨吸収抑制”作用がメインではなく、骨形成促進が主なので、骨吸収を併せて強く抑えたいケースではイベニティの方が強い。


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
    voice = os.getenv("VOICE", "cedar")

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
    egress_id = None
    if session_id and LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
        async def start_egress_async():
            nonlocal egress_id
            try:
                egress_id = await start_egress(ctx.room.name, session_id)
                logger.info(f"🎙️  Egress started: {egress_id}")
            except Exception as e:
                logger.error(f"Failed to start egress: {e}")

        asyncio.create_task(start_egress_async())

    # Room切断イベントを待機するためのFuture
    disconnected_future = asyncio.Future()

    @ctx.room.on("disconnected")
    def on_room_disconnected():
        """Room切断時にFutureを完了させる"""
        logger.info(f"🔌 Room disconnected")
        if not disconnected_future.done():
            disconnected_future.set_result(True)

    # Roomが切断されるまで待機
    await disconnected_future

    # Room切断後、セッション終了処理を同期的に実行
    logger.info(f"🔄 Ending session {session_id}...")
    await end_session(session_id, egress_id)
    logger.info(f"✅ Session end processing completed")


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
                    "timestamp": now_jst().isoformat()
                },
                timeout=5.0
            )
            if response.status_code == 200:
                logger.debug(f"✅ Message saved: {message_id}")
            else:
                logger.warning(f"⚠️  Failed to save message: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error saving message to backend: {e}")


async def end_session(session_id: str, egress_id: str):
    """セッション終了処理をバックエンドに通知"""
    try:
        # Webhookで音声ファイルパスが設定されるため、ここでは設定不要
        # セッション終了のみ通知
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/sessions/{session_id}/end",
                json={},
                timeout=5.0
            )
            if response.status_code == 200:
                logger.info(f"✅ Session ended: {session_id}")
            else:
                logger.warning(f"⚠️  Failed to end session: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error ending session: {e}")


async def start_egress(room_name: str, session_id: str) -> tuple[str, str]:
    """
    LiveKit Egressで録音を開始

    Returns:
        tuple[str, str]: (egress_id, audio_file_path)
    """
    try:
        # LiveKit APIクライアント作成
        livekit_api = api.LiveKitAPI(
            url=LIVEKIT_URL.replace("ws://", "http://").replace("wss://", "https://"),
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET
        )

        # Egress設定
        output_filename = f"session_{session_id}_{int(datetime.now().timestamp())}"
        # バックエンドからは /audio_files でマウントされている
        audio_file_path = f"/audio_files/{output_filename}.mp4"

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
        return egress_info.egress_id, audio_file_path

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
