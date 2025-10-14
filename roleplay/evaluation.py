"""
評価・フィードバック機能モジュール
営業パフォーマンスを評価し、フィードバックを生成
"""
from dataclasses import dataclass, field
from typing import List, Dict
from conversation_flow import ConversationState, ConversationPhase


@dataclass
class SalesPerformanceMetrics:
    """営業パフォーマンスメトリクス"""

    # 基本情報
    total_turns: int = 0
    final_phase: ConversationPhase = ConversationPhase.SKEPTICAL
    conversation_completed: bool = False

    # スキル評価（0.0 - 1.0）
    objection_handling_score: float = 0.0      # 懸念への対応スコア
    data_usage_effectiveness: float = 0.0      # 具体的数字の活用度
    case_study_relevance: float = 0.0          # 事例の適切性
    rapport_building: float = 0.0              # 信頼構築スキル
    listening_skills: float = 0.0              # 傾聴力
    phase_progression_speed: float = 0.0       # フェーズ遷移速度

    # 詳細データ
    concerns_addressed: List[str] = field(default_factory=list)
    data_points_provided: List[str] = field(default_factory=list)
    case_studies_used: List[str] = field(default_factory=list)
    missed_opportunities: List[str] = field(default_factory=list)

    def calculate_overall_score(self) -> float:
        """
        総合スコアを計算

        Returns:
            float: 総合スコア（0.0 - 1.0）
        """
        weights = {
            "objection_handling": 0.25,
            "data_usage": 0.25,
            "case_study": 0.15,
            "rapport": 0.15,
            "listening": 0.10,
            "progression": 0.10
        }

        overall = (
            self.objection_handling_score * weights["objection_handling"] +
            self.data_usage_effectiveness * weights["data_usage"] +
            self.case_study_relevance * weights["case_study"] +
            self.rapport_building * weights["rapport"] +
            self.listening_skills * weights["listening"] +
            self.phase_progression_speed * weights["progression"]
        )

        return round(overall, 2)

    def generate_feedback(self) -> str:
        """
        会話終了後のフィードバックを生成

        Returns:
            str: フィードバックメッセージ
        """
        overall_score = self.calculate_overall_score()
        feedback_lines = []

        # ヘッダー
        feedback_lines.append("=" * 60)
        feedback_lines.append("📊 営業ロールプレイ評価レポート")
        feedback_lines.append("=" * 60)
        feedback_lines.append("")

        # 総合評価
        feedback_lines.append(f"🎯 総合スコア: {overall_score * 100:.0f}/100")
        feedback_lines.append(f"   評価: {self._get_grade(overall_score)}")
        feedback_lines.append("")

        # 基本情報
        feedback_lines.append(f"📈 基本情報:")
        feedback_lines.append(f"   - 総ターン数: {self.total_turns}")
        feedback_lines.append(f"   - 最終フェーズ: {self._format_phase(self.final_phase)}")
        feedback_lines.append(f"   - 会話完了: {'✅ はい' if self.conversation_completed else '❌ いいえ'}")
        feedback_lines.append("")

        # 詳細評価
        feedback_lines.append("📋 詳細評価:")
        feedback_lines.append("")

        # 1. 懸念への対応
        feedback_lines.append(f"1️⃣ 懸念への対応: {self._format_score(self.objection_handling_score)}")
        if self.objection_handling_score >= 0.8:
            feedback_lines.append("   ✅ 社長の懸念に対して具体的なデータで効果的に対応しました")
        elif self.objection_handling_score >= 0.5:
            feedback_lines.append("   ⚠️  懸念への対応は良好ですが、さらに具体例があるとより説得力が増します")
        else:
            feedback_lines.append("   ❌ 社長の懸念（コスト、時間、効果）への対応が不十分です")

        if self.concerns_addressed:
            feedback_lines.append(f"   対応した懸念: {', '.join(self.concerns_addressed)}")
        feedback_lines.append("")

        # 2. 具体的数字の活用
        feedback_lines.append(f"2️⃣ 具体的数字の活用: {self._format_score(self.data_usage_effectiveness)}")
        if self.data_usage_effectiveness >= 0.8:
            feedback_lines.append("   ✅ 具体的な数字を効果的に使用し、説得力のある提案ができました")
        elif self.data_usage_effectiveness >= 0.5:
            feedback_lines.append("   ⚠️  数字は使いましたが、もう少しROIや効果を定量的に示すと良いでしょう")
        else:
            feedback_lines.append("   ❌ 具体的な数字が不足しています。費用、効果、ROIを明確に示しましょう")

        if self.data_points_provided:
            feedback_lines.append(f"   提供したデータ: {', '.join(self.data_points_provided)}")
        feedback_lines.append("")

        # 3. 事例の活用
        feedback_lines.append(f"3️⃣ 事例の活用: {self._format_score(self.case_study_relevance)}")
        if self.case_study_relevance >= 0.8:
            feedback_lines.append("   ✅ 適切な事例を効果的に紹介しました")
        elif self.case_study_relevance >= 0.5:
            feedback_lines.append("   ⚠️  事例は紹介しましたが、もう少し詳しく説明すると良いでしょう")
        else:
            feedback_lines.append("   ❌ 具体的な事例が不足しています。同業他社の成功例を紹介しましょう")

        if self.case_studies_used:
            feedback_lines.append(f"   使用した事例: {', '.join(self.case_studies_used)}")
        feedback_lines.append("")

        # 4. 信頼構築
        feedback_lines.append(f"4️⃣ 信頼構築: {self._format_score(self.rapport_building)}")
        if self.rapport_building >= 0.8:
            feedback_lines.append("   ✅ 社長との信頼関係を効果的に構築しました")
        elif self.rapport_building >= 0.5:
            feedback_lines.append("   ⚠️  もう少し社長の立場に寄り添った提案を心がけましょう")
        else:
            feedback_lines.append("   ❌ 信頼構築が不十分です。社長の懸念を理解し、寄り添う姿勢を示しましょう")
        feedback_lines.append("")

        # 改善ポイント
        if self.missed_opportunities:
            feedback_lines.append("💡 見逃した機会:")
            for opportunity in self.missed_opportunities:
                feedback_lines.append(f"   - {opportunity}")
            feedback_lines.append("")

        # 次回への推奨事項
        feedback_lines.append("🎓 次回への推奨事項:")
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            feedback_lines.append(f"   {rec}")
        feedback_lines.append("")

        feedback_lines.append("=" * 60)

        return "\n".join(feedback_lines)

    def _get_grade(self, score: float) -> str:
        """スコアから評価グレードを取得"""
        if score >= 0.9:
            return "S (優秀)"
        elif score >= 0.8:
            return "A (良好)"
        elif score >= 0.7:
            return "B (普通)"
        elif score >= 0.6:
            return "C (要改善)"
        else:
            return "D (不十分)"

    def _format_score(self, score: float) -> str:
        """スコアをフォーマット"""
        percentage = score * 100
        bar_length = int(score * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        return f"{bar} {percentage:.0f}%"

    def _format_phase(self, phase: ConversationPhase) -> str:
        """フェーズを日本語でフォーマット"""
        phase_names = {
            ConversationPhase.SKEPTICAL: "懐疑的",
            ConversationPhase.INTERESTED: "興味",
            ConversationPhase.CONSIDERING: "検討"
        }
        return phase_names.get(phase, "不明")

    def _generate_recommendations(self) -> List[str]:
        """推奨事項を生成"""
        recommendations = []

        if self.objection_handling_score < 0.7:
            recommendations.append(
                "✓ 社長の懸念（コスト、時間、効果、保証）を事前に想定し、"
                "具体的なデータで対応する準備をしましょう"
            )

        if self.data_usage_effectiveness < 0.7:
            recommendations.append(
                "✓ 費用、ROI、効果を具体的な数字で示しましょう"
                "（例: 20〜30万円、1.2倍増加、年間3万円削減）"
            )

        if self.case_study_relevance < 0.7:
            recommendations.append(
                "✓ 同業他社の成功事例を詳しく紹介しましょう"
                "（群馬の部品メーカー、宇都宮の金型メーカーなど）"
            )

        if self.rapport_building < 0.7:
            recommendations.append(
                "✓ 社長の立場に寄り添い、懸念を理解していることを示しましょう"
            )

        if self.phase_progression_speed < 0.5:
            recommendations.append(
                "✓ 会話のテンポが遅すぎます。相手の反応を見ながら情報を提供しましょう"
            )
        elif self.phase_progression_speed > 0.9:
            recommendations.append(
                "✓ 会話のテンポが速すぎます。社長が納得するまで丁寧に説明しましょう"
            )

        if not recommendations:
            recommendations.append("✓ 素晴らしい営業でした！この調子で頑張ってください")

        return recommendations


def evaluate_conversation(state: ConversationState) -> SalesPerformanceMetrics:
    """
    会話状態から営業パフォーマンスを評価

    Args:
        state: 会話状態

    Returns:
        SalesPerformanceMetrics: パフォーマンス評価
    """
    metrics = SalesPerformanceMetrics()

    # 基本情報
    metrics.total_turns = state.turn_count
    metrics.final_phase = state.current_phase
    metrics.conversation_completed = (
        state.current_phase == ConversationPhase.CONSIDERING and
        state.phase_turn_count >= 2
    )

    # 懸念への対応スコア
    total_concerns = 4  # コスト、時間、効果、保証
    addressed_concerns = len(state.concerns_raised)
    metrics.objection_handling_score = min(addressed_concerns / total_concerns, 1.0)
    metrics.concerns_addressed = state.concerns_raised

    # 具体的数字の活用度
    data_types = ["cost", "roi", "case_study", "time_required", "support_offered"]
    provided_count = sum(1 for dt in data_types if state.data_provided.get(dt, False))
    metrics.data_usage_effectiveness = provided_count / len(data_types)
    metrics.data_points_provided = [
        dt for dt in data_types if state.data_provided.get(dt, False)
    ]

    # 事例の活用
    case_study_count = len(state.case_studies_mentioned)
    metrics.case_study_relevance = min(case_study_count / 2, 1.0)  # 2つ以上で満点
    metrics.case_studies_used = state.case_studies_mentioned

    # 信頼構築（データ提供の質とフェーズ進行度から推定）
    phase_score = {
        ConversationPhase.SKEPTICAL: 0.3,
        ConversationPhase.INTERESTED: 0.6,
        ConversationPhase.CONSIDERING: 1.0
    }
    metrics.rapport_building = phase_score.get(state.current_phase, 0.0)

    # 傾聴力（質問への対応状況から推定）
    metrics.listening_skills = min(len(state.questions_asked) / 5, 1.0)

    # フェーズ遷移速度
    ideal_turns = 12  # 理想的な総ターン数（SKEPTICAL 3 + INTERESTED 5 + CONSIDERING 4）
    if state.turn_count == 0:
        metrics.phase_progression_speed = 0.0
    else:
        speed = ideal_turns / state.turn_count
        metrics.phase_progression_speed = min(speed, 1.0) if speed <= 1.5 else 0.5

    # 見逃した機会を検出
    if not state.data_provided.get("cost"):
        metrics.missed_opportunities.append("具体的な費用を提示していません")
    if not state.data_provided.get("roi"):
        metrics.missed_opportunities.append("ROI（投資対効果）を示していません")
    if case_study_count == 0:
        metrics.missed_opportunities.append("具体的な事例を紹介していません")
    if not state.data_provided.get("support_offered"):
        metrics.missed_opportunities.append("サポート体制を説明していません")

    return metrics


if __name__ == "__main__":
    # テスト用
    from conversation_flow import ConversationState, ConversationPhase

    # テストケース1: 優秀な営業
    state1 = ConversationState(
        current_phase=ConversationPhase.CONSIDERING,
        turn_count=12,
        phase_turn_count=3
    )
    state1.mark_data_provided("cost")
    state1.mark_data_provided("roi")
    state1.mark_data_provided("case_study")
    state1.mark_data_provided("time_required")
    state1.mark_data_provided("support_offered")
    state1.concerns_raised = ["cost", "time", "effect", "guarantee"]
    state1.case_studies_mentioned = ["gunma_parts", "utsunomiya_mold"]
    state1.questions_asked = ["cost", "roi", "time", "support", "guarantee"]

    metrics1 = evaluate_conversation(state1)
    print(metrics1.generate_feedback())

    print("\n\n" + "=" * 60 + "\n\n")

    # テストケース2: 改善が必要な営業
    state2 = ConversationState(
        current_phase=ConversationPhase.SKEPTICAL,
        turn_count=3,
        phase_turn_count=3
    )
    state2.mark_data_provided("cost")

    metrics2 = evaluate_conversation(state2)
    print(metrics2.generate_feedback())
