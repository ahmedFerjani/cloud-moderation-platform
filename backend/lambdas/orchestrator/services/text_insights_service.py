from decimal import Decimal

import boto3

MAX_COMPREHEND_TEXT_LENGTH = 5000
SUPPORTED_PII_LANGUAGE_CODES = {"en", "es"}
TOXICITY_LABEL_THRESHOLD = Decimal("0.70")

comprehend = boto3.client("comprehend")


def _extract_pii_summary(analysis_text: str, language_code: str) -> tuple[int, list[str]]:
    if language_code not in SUPPORTED_PII_LANGUAGE_CODES:
        return 0, []

    pii_response = comprehend.detect_pii_entities(
        Text=analysis_text,
        LanguageCode=language_code,
    )
    pii_entities = pii_response.get("Entities", [])
    pii_entities_count = len(pii_entities)
    pii_entity_types = sorted({entity.get("Type") for entity in pii_entities if entity.get("Type")})
    return pii_entities_count, pii_entity_types


def _extract_toxicity_summary(analysis_text: str, language_code: str) -> tuple[Decimal, list[dict]]:
    if language_code != "en":
        return Decimal("0"), []

    toxic_response = comprehend.detect_toxic_content(
        TextSegments=[{"Text": analysis_text}],
        LanguageCode=language_code,
    )

    toxic_label_scores: dict[str, Decimal] = {}
    max_toxicity_score = Decimal("0")

    for result in toxic_response.get("ResultList", []):
        for label in result.get("Labels", []):
            label_name = label.get("Name")
            label_score = label.get("Score")
            if not label_name or label_score is None:
                continue

            decimal_score = Decimal(str(label_score))
            toxic_label_scores[label_name] = decimal_score
            if decimal_score > max_toxicity_score:
                max_toxicity_score = decimal_score

    toxicity_labels = [
        {"name": label_name, "score": toxic_label_scores[label_name]}
        for label_name in sorted(toxic_label_scores.keys())
    ]
    return max_toxicity_score, toxicity_labels


def analyze_extracted_text(extracted_text: str) -> dict:
    analysis_text = extracted_text.strip()[:MAX_COMPREHEND_TEXT_LENGTH]

    dominant_language_response = comprehend.detect_dominant_language(Text=analysis_text)
    languages = dominant_language_response.get("Languages", [])
    language_code = (languages[0].get("LanguageCode") if languages else "en") or "en"

    sentiment_response = comprehend.detect_sentiment(
        Text=analysis_text,
        LanguageCode=language_code,
    )

    sentiment_scores = {
        score_name: Decimal(str(score_value))
        for score_name, score_value in sentiment_response.get("SentimentScore", {}).items()
    }

    pii_entities_count, pii_entity_types = _extract_pii_summary(analysis_text, language_code)
    max_toxicity_score, toxicity_labels = _extract_toxicity_summary(analysis_text, language_code)

    return {
        "language_code": language_code,
        "sentiment": sentiment_response.get("Sentiment", "UNKNOWN"),
        "sentiment_scores": sentiment_scores,
        "toxicity_detected": max_toxicity_score >= TOXICITY_LABEL_THRESHOLD,
        "max_toxicity_score": max_toxicity_score,
        "toxicity_labels": toxicity_labels,
        "pii_entities_count": pii_entities_count,
        "pii_entity_types": pii_entity_types,
        "analyzed_text_length": len(analysis_text),
    }
