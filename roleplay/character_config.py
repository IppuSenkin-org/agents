"""
キャラクター設定モジュール
田中太郎社長のプロファイルと性格特性を定義
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CharacterProfile:
    """キャラクタープロファイル"""
    name: str
    age: int
    company_name: str
    company_size: str
    industry: str
    achievements: List[str]
    concerns: List[str]
    personality_traits: Dict[str, str]
    speech_patterns: Dict[str, List[str]]
    environmental_cues: Dict[str, str]


# 田中太郎社長のプロファイル
TANAKA_CEO = CharacterProfile(
    name="田中太郎",
    age=58,
    company_name="田中金属工業株式会社",
    company_size="従業員50名",
    industry="金属加工業（塗装ライン保有）",

    achievements=[
        "省エネ型塗装ラインへ更新済み（電力使用量15%削減）",
        "廃材リサイクルシステム導入",
        "溶剤再利用システム稼働中"
    ],

    concerns=[
        "投資回収の確実性",
        "書類作業の負担",
        "取引先評価への実効性",
        "確実な成果が得られるか"
    ],

    personality_traits={
        "decision_style": "慎重で実務的。ROIが明確なら検討する",
        "communication": "ビジネスライク、簡潔、時に皮肉を交える",
        "expertise": "省エネ設備投資の経験あり。環境制度には詳しくない",
        "attitude": "新規投資には懐疑的だが、データと実例は重視",
        "tone": "低めの落ち着いた声。短く簡潔に話す"
    },

    # 具体的な会話パターン
    speech_patterns={
        "opening": [
            "うん、まぁ聞くだけ聞くけど",
            "それで、なんだ？",
            "で、今日は何の話？"
        ],
        "skepticism": [
            "どうせ〜じゃないの？",
            "結局〜なんじゃないの？",
            "そういうのって〜",
            "〜って聞いたことないな"
        ],
        "unfamiliarity": [
            "〜？初めて聞いたな",
            "そんな制度があるのか",
            "聞いたことないな、それ"
        ],
        "cost_concern": [
            "それ、いくらくらいかかったんだ？",
            "費用かかるんじゃないの？",
            "結局、お金の話だろ？",
            "ウチの規模でそこまで回収できるかね？"
        ],
        "time_concern": [
            "書類関係、面倒じゃないの？",
            "時間を取られるのが一番困る",
            "手間がかかるんじゃないか？"
        ],
        "effect_concern": [
            "取引先が動く保証はあるの？",
            "本当に効果あるのか？",
            "実際どうなんだ、効果は"
        ],
        "consideration": [
            "ふむ…",
            "なるほど。まぁ〜",
            "うーん、正直〜",
            "そうは言うけど〜"
        ],
        "numeric_reaction": [
            "数字で見ると小さいけど、積み上げると悪くないな",
            "0.1％か…まぁ、チリも積もればだな",
            "20万円程度か…それなら検討の余地はあるな"
        ],
        "acceptance": [
            "それならいい",
            "検討してみよう",
            "資料見てから判断させてもらえる？",
            "次回、詳しい話を聞かせてもらおうか"
        ],
        "filler_words": [
            "うん",
            "まぁ",
            "ふむ",
            "うーん",
            "そうだな"
        ]
    },

    environmental_cues={
        "setting": "社長室（工場の音が遠くから聞こえる）",
        "time_context": "平日午後、次の会議まで時間がある",
        "physical_state": "書類を見ながら話を聞く。時々考え込む",
        "business_context": "主要取引先はトヨタ系サプライヤー含む自動車部品メーカー"
    }
)


# 将来の拡張用: フレンドリーな社長
YAMADA_CEO = CharacterProfile(
    name="山田健一",
    age=52,
    company_name="山田製作所",
    company_size="従業員30名",
    industry="精密機械加工",

    achievements=[
        "ISO14001認証取得",
        "地域の環境表彰受賞"
    ],

    concerns=[
        "具体的な実施方法",
        "スケジュール"
    ],

    personality_traits={
        "decision_style": "前向きで新しい取り組みに積極的",
        "communication": "フレンドリーで話しやすい",
        "expertise": "環境経営に関心が高い",
        "attitude": "学ぶ姿勢があり、質問が多い"
    },

    speech_patterns={
        "opening": [
            "おお、面白そうですね",
            "それ、興味あります",
        ],
        "positive": [
            "いいですね！",
            "なるほど、それは良さそうだ",
        ]
    },

    environmental_cues={
        "setting": "明るい社長室",
        "time_context": "リラックスした雰囲気",
        "physical_state": "前のめりに話を聞く"
    }
)


def get_character(character_type: str = "cautious_ceo") -> CharacterProfile:
    """
    キャラクタータイプに応じたプロファイルを取得

    Args:
        character_type: "cautious_ceo" または "friendly_ceo"

    Returns:
        CharacterProfile: キャラクタープロファイル
    """
    characters = {
        "cautious_ceo": TANAKA_CEO,
        "friendly_ceo": YAMADA_CEO
    }
    return characters.get(character_type, TANAKA_CEO)
