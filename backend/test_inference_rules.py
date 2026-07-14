import unittest

from backend.config import THRESHOLDS
from backend.postprocessing import (
    QUESTION_EVIDENCE_MIN_SCORE,
    apply_questionnaire_evidence,
    get_lexicon_scores,
    normalize_text,
    questionnaire_axis_signal,
)


class InferenceRuleTests(unittest.TestCase):
    def test_mne_does_not_act_as_negation(self):
        score = get_lexicon_scores(
            "Мне нравится общение, я люблю людей и после встреч у меня больше сил."
        )["E"]
        self.assertGreater(score, 0.45)

    def test_negation_does_not_cross_sentence_boundary(self):
        score = get_lexicon_scores(
            "Не люблю шумные места. Люблю людей и общение, они меня заряжают."
        )["E"]
        self.assertGreater(score, 0.25)

    def test_explicit_negation_and_fatigue_support_introversion(self):
        score, hits = questionnaire_axis_signal(
            normalize_text(
                "Не люблю большие компании и быстро устаю от людей."
            ),
            "E",
        )
        self.assertGreater(hits, 0)
        self.assertLess(score, -QUESTION_EVIDENCE_MIN_SCORE)

    def test_liking_people_without_fatigue_supports_extraversion(self):
        score, hits = questionnaire_axis_signal(
            normalize_text(
                "Люблю людей и общение, после встреч больше сил, от них не устаю."
            ),
            "E",
        )
        self.assertGreater(hits, 0)
        self.assertGreater(score, QUESTION_EVIDENCE_MIN_SCORE)

    def test_fatigue_prevents_liking_people_from_becoming_strong_e_rule(self):
        score, _ = questionnaire_axis_signal(
            normalize_text(
                "Люблю людей, но после общения быстро устаю от них и восстанавливаюсь в тишине."
            ),
            "E",
        )
        self.assertLess(abs(score), QUESTION_EVIDENCE_MIN_SCORE)

    def test_direct_question_can_correct_weak_axis_model_result(self):
        model_probs = {"E": 0.25, "N": 0.80, "T": 0.70, "J": 0.80}
        answers = [
            "Люблю людей и общение, они заряжают меня, и я от них не устаю.",
            "Мне нужны факты, конкретные примеры и практика.",
            "В решениях опираюсь на логику и объективные критерии.",
            "Мне нужна свобода и пространство для спонтанности, планы легко меняю.",
            "",
        ]

        adjusted, _, changes = apply_questionnaire_evidence(model_probs, answers)

        self.assertGreaterEqual(adjusted["E"], THRESHOLDS["E"])
        self.assertLess(adjusted["N"], THRESHOLDS["N"])
        self.assertLess(adjusted["J"], THRESHOLDS["J"])
        self.assertEqual(changes["E"], "direct_question_evidence")
        self.assertEqual(changes["N"], "direct_question_evidence")
        self.assertEqual(changes["J"], "direct_question_evidence")


if __name__ == "__main__":
    unittest.main()
