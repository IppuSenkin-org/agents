"""
事例データベースモジュール
PIF導入事例を管理
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CaseStudy:
    """事例データ"""
    id: str
    company_profile: str
    industry: str
    company_size: str
    investment_type: str
    cost: str
    duration: str
    quantitative_results: Dict[str, str]
    qualitative_results: List[str]
    detail: str
    key_points: List[str]


# 事例データベース
CASE_STUDIES = {
    "gunma_parts": CaseStudy(
        id="gunma_parts",
        company_profile="群馬の部品メーカー",
        industry="自動車部品製造",
        company_size="中小企業",
        investment_type="PIF評価レポート作成",
        cost="20〜30万円程度",
        duration="約3ヶ月",
        quantitative_results={
            "発注量増加": "約1.2倍",
            "利益増加": "数百万円規模",
            "投資回収期間": "約半年"
        },
        qualitative_results=[
            "トヨタ系サプライヤー調達評価で環境対応ランクA取得",
            "既存取引先からの評価向上",
            "企業ブランド価値の向上"
        ],
        detail=(
            "群馬の部品メーカーさんではPIFを活用して評価レポートを作成し、"
            "トヨタ系のサプライヤー調達評価で\"環境対応ランクA\"を取得しました。"
            "その結果、次年度の発注量が約1.2倍に増えています。"
            "これは、数字として\"省エネの成果\"が可視化できたからこそ評価された例です。"
        ),
        key_points=[
            "投資額は20〜30万円程度",
            "発注増で数百万円規模の利益",
            "数字として成果を可視化したことが評価された"
        ]
    ),

    "utsunomiya_mold": CaseStudy(
        id="utsunomiya_mold",
        company_profile="宇都宮の金型メーカー",
        industry="金型製造",
        company_size="中小企業（同規模）",
        investment_type="PIF認定取得",
        cost="評価・レポート作成費用のみ",
        duration="約2ヶ月",
        quantitative_results={
            "金利優遇": "0.1%削減",
            "年間削減額": "約3万円（借入3,000万円の場合）"
        },
        qualitative_results=[
            "市の広報誌に環境貢献企業として掲載",
            "新規取引の問い合わせ増加",
            "ブランドイメージ向上",
            "従業員の意識向上"
        ],
        detail=(
            "宇都宮の金型メーカーさんでは同規模で取り組みを整理しただけで、"
            "PIF認定を受けて金利が0.1％優遇されました。"
            "借入が3,000万円規模でしたので、単純計算で年間約3万円の削減です。"
            "さらに\"環境貢献企業\"として市の広報誌にも掲載されて、"
            "新規取引の問い合わせが来たそうです。"
        ),
        key_points=[
            "既存の取り組みを整理するだけでOK",
            "金利優遇（0.1%）で年間約3万円削減",
            "広報効果で新規取引増加"
        ]
    ),

    "general_benefits": CaseStudy(
        id="general_benefits",
        company_profile="製造業全般",
        industry="製造業",
        company_size="中小企業",
        investment_type="PIF全般",
        cost="ケースバイケース",
        duration="2〜3ヶ月",
        quantitative_results={},
        qualitative_results=[
            "第三者認証による信用力向上",
            "調達評価・金融面でのメリット",
            "PR・ブランディング効果",
            "従業員のモチベーション向上"
        ],
        detail=(
            "PIF（ポジティブ・インパクト・ファイナンス）は、"
            "企業の環境や地域への良い取り組みを金融面で応援する仕組みです。"
            "省エネ設備を導入されている企業に特に適しています。"
        ),
        key_points=[
            "環境への取り組みが第三者に認められる",
            "取引先からの評価が向上",
            "金融面でのメリット（金利優遇等）"
        ]
    )
}


def get_case_study(case_id: str) -> Optional[CaseStudy]:
    """
    事例IDから事例を取得

    Args:
        case_id: 事例ID

    Returns:
        Optional[CaseStudy]: 事例データ。存在しない場合はNone
    """
    return CASE_STUDIES.get(case_id)


def search_case_studies(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
) -> List[CaseStudy]:
    """
    条件に合う事例を検索

    Args:
        industry: 業種
        company_size: 企業規模

    Returns:
        List[CaseStudy]: マッチする事例のリスト
    """
    results = []

    for case in CASE_STUDIES.values():
        match = True

        if industry and industry not in case.industry:
            match = False

        if company_size and company_size not in case.company_size:
            match = False

        if match:
            results.append(case)

    return results


def get_all_case_studies() -> List[CaseStudy]:
    """
    全事例を取得

    Returns:
        List[CaseStudy]: 全事例のリスト
    """
    return list(CASE_STUDIES.values())


def format_case_study_summary(case: CaseStudy) -> str:
    """
    事例の要約を生成

    Args:
        case: 事例データ

    Returns:
        str: 要約文
    """
    summary = f"{case.company_profile}の事例:\n"
    summary += f"投資: {case.cost}\n"

    if case.quantitative_results:
        summary += "成果: "
        summary += ", ".join(
            f"{k}={v}" for k, v in case.quantitative_results.items()
        )
        summary += "\n"

    summary += f"ポイント: {', '.join(case.key_points)}"

    return summary
