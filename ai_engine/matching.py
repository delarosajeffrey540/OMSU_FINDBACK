import os
from math import sqrt


def cosine_similarity(first_embedding, second_embedding):
    if not first_embedding or not second_embedding or len(first_embedding) != len(second_embedding):
        return None
    dot_product = sum(first * second for first, second in zip(first_embedding, second_embedding))
    first_norm = sqrt(sum(value * value for value in first_embedding))
    second_norm = sqrt(sum(value * value for value in second_embedding))
    if not first_norm or not second_norm:
        return None
    return round(max(0.0, min(1.0, dot_product / (first_norm * second_norm))) * 100)


def similarity_score(lost_report, found_report, visual_similarity=None):
    score = 0
    if lost_report.category.lower() == found_report.category.lower():
        score += 35
    if lost_report.color and found_report.color and lost_report.color.lower() == found_report.color.lower():
        score += 25
    lost_name = lost_report.item_name.strip().lower()
    found_name = found_report.item_name.strip().lower()
    if lost_name == found_name:
        score += 30
    elif lost_name in found_name or found_name in lost_name:
        score += 20
    if visual_similarity is not None:
        score = round(score * 0.6 + visual_similarity * 0.4)
    return min(score, 95)


def match_reports(lost_reports, found_reports, upload_folder, model_path, logger=None):
    pairs = []
    embedding_cache = {}

    def report_embedding(report):
        if not report.photo_filename:
            return None
        if report.id not in embedding_cache:
            from ai_engine.image_detection import image_embedding

            image_path = os.path.join(upload_folder, report.photo_filename)
            try:
                embedding_cache[report.id] = image_embedding(image_path, model_path)
            except Exception:
                if logger:
                    logger.exception("Could not embed report image %s.", report.id)
                embedding_cache[report.id] = None
        return embedding_cache[report.id]

    for lost_report in lost_reports:
        lost_embedding = report_embedding(lost_report)
        for found_report in found_reports:
            if lost_report.user_id == found_report.user_id:
                continue
            visual_similarity = None
            if lost_embedding and found_report.photo_filename:
                found_embedding = report_embedding(found_report)
                visual_similarity = cosine_similarity(lost_embedding, found_embedding)
            score = similarity_score(lost_report, found_report, visual_similarity)
            if score >= 35 or (visual_similarity is not None and visual_similarity >= 65):
                pairs.append((lost_report, found_report, score, visual_similarity))

    return sorted(pairs, key=lambda pair: pair[2], reverse=True)
