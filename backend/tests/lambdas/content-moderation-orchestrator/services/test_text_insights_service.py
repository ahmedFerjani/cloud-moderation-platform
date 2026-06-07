from decimal import Decimal
from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_services


# Verifies Comprehend analysis returns moderation-oriented text insights.
def test_analyze_extracted_text_returns_insights() -> None:
    with patch.object(orchestrator_services.comprehend, "detect_dominant_language") as mock_lang:
        mock_lang.return_value = {"Languages": [{"LanguageCode": "en", "Score": 0.99}]}

        with patch.object(orchestrator_services.comprehend, "detect_sentiment") as mock_sentiment:
            mock_sentiment.return_value = {
                "Sentiment": "NEGATIVE",
                "SentimentScore": {
                    "Positive": 0.01,
                    "Negative": 0.91,
                    "Neutral": 0.05,
                    "Mixed": 0.03,
                },
            }

            with patch.object(orchestrator_services.comprehend, "detect_pii_entities") as mock_pii:
                mock_pii.return_value = {
                    "Entities": [
                        {"Type": "NAME", "Score": 0.99},
                        {"Type": "ADDRESS", "Score": 0.88},
                    ]
                }

                with patch.object(
                    orchestrator_services.comprehend, "detect_toxic_content"
                ) as mock_toxic:
                    mock_toxic.return_value = {
                        "ResultList": [
                            {
                                "Labels": [
                                    {"Name": "INSULT", "Score": 0.82},
                                    {"Name": "HATE_SPEECH", "Score": 0.11},
                                ]
                            }
                        ]
                    }

                    insights = orchestrator_services.analyze_extracted_text(
                        "some extracted text from image"
                    )

    assert insights["language_code"] == "en"
    assert insights["sentiment"] == "NEGATIVE"
    assert insights["sentiment_scores"]["Negative"] == Decimal("0.91")
    assert insights["toxicity_detected"]
    assert insights["max_toxicity_score"] == Decimal("0.82")
    assert insights["toxicity_labels"][0]["name"] == "HATE_SPEECH"
    assert insights["toxicity_labels"][1]["name"] == "INSULT"
    assert insights["pii_entities_count"] == 2
    assert insights["pii_entity_types"] == ["ADDRESS", "NAME"]


# Verifies PII detection is skipped when language is unsupported by Comprehend PII API.
def test_analyze_extracted_text_skips_pii_for_unsupported_language() -> None:
    with patch.object(orchestrator_services.comprehend, "detect_dominant_language") as mock_lang:
        mock_lang.return_value = {"Languages": [{"LanguageCode": "fr", "Score": 0.99}]}

        with patch.object(orchestrator_services.comprehend, "detect_sentiment") as mock_sentiment:
            mock_sentiment.return_value = {
                "Sentiment": "NEUTRAL",
                "SentimentScore": {
                    "Positive": 0.1,
                    "Negative": 0.1,
                    "Neutral": 0.75,
                    "Mixed": 0.05,
                },
            }

            with patch.object(orchestrator_services.comprehend, "detect_pii_entities") as mock_pii:
                with patch.object(
                    orchestrator_services.comprehend, "detect_toxic_content"
                ) as mock_toxic:
                    insights = orchestrator_services.analyze_extracted_text("bonjour le monde")

                    mock_toxic.assert_not_called()

    assert insights["language_code"] == "fr"
    assert insights["pii_entities_count"] == 0
    assert insights["pii_entity_types"] == []
    assert not insights["toxicity_detected"]
    assert insights["max_toxicity_score"] == Decimal("0")
    assert insights["toxicity_labels"] == []
    mock_pii.assert_not_called()
