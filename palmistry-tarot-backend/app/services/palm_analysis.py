"""Palm image analysis.

The computer-vision layer detects visual palm features.
The interpretation layer is entertainment/self-reflection content and
does not claim scientific prediction.
"""

from __future__ import annotations

import hashlib
import math

import cv2
import numpy as np

from app.services.palm_line_detector import detect_palm_lines
from app.services.palm_line_detector import is_available as model_is_available


SUPPORTED_LINES = [
    "life",
    "head",
    "heart",
    "fate",
    "sun",
]


def analyze_palm_image(image_bytes: bytes) -> dict:

    np_array = np.frombuffer(
        image_bytes,
        np.uint8,
    )

    image = cv2.imdecode(
        np_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            "Could not read this file as an image."
        )

    if model_is_available():
        result = _analyze_with_model(
            image_bytes,
            image,
        )
    else:
        result = _analyze_with_heuristic(
            image_bytes,
            image,
        )

    return result


# ============================================================
# YOLO MODEL
# ============================================================

def _analyze_with_model(
    image_bytes: bytes,
    image,
) -> dict:

    detection_result = detect_palm_lines(
        image_bytes
    )

    if not detection_result:

        return {
            "confidence": 0.0,
            "detected_lines": [],
            "detections": [],
            "source": "model",
            "annotated_image": None,
            "line_analysis": {},
            "palm_shape": _estimate_palm_shape(image),
            "finger_structure": _estimate_finger_structure(image),
            "insights": {},
        }

    detections = detection_result.get(
        "detections",
        [],
    )

    annotated_image = detection_result.get(
        "annotated_image"
    )

    # Highest-confidence detection for each class
    best_by_line: dict[str, dict] = {}

    for detection in detections:

        line = _normalize_line_name(
            detection["line"]
        )

        detection["line"] = line

        if line not in SUPPORTED_LINES:
            continue

        existing = best_by_line.get(line)

        if (
            existing is None
            or detection["confidence"]
            > existing["confidence"]
        ):
            best_by_line[line] = detection

    confidences = [
        item["confidence"]
        for item in best_by_line.values()
    ]

    overall_confidence = (
        round(
            sum(confidences) / len(confidences),
            2,
        )
        if confidences
        else 0.0
    )

    line_analysis = {}

    for line in SUPPORTED_LINES:

        detection = best_by_line.get(line)

        if detection:

            line_analysis[line] = {
                "detected": True,
                "confidence": detection["confidence"],
                "bbox": detection["bbox"],
                "source": detection.get(
                    "source",
                    "model",
                ),
                "interpretation": _line_interpretation(
                    line,
                    detection,
                ),
            }

        else:

            line_analysis[line] = {
                "detected": False,
                "confidence": 0.0,
                "bbox": None,
                "interpretation": (
                    "This line was not clearly detected "
                    "in the uploaded image."
                ),
            }

    palm_shape = _estimate_palm_shape(
        image
    )

    finger_structure = _estimate_finger_structure(
        image
    )

    insights = {}

    for line in SUPPORTED_LINES:

        key = f"{line}_line"

        insights[key] = line_analysis[line][
            "interpretation"
        ]

    return {
        "confidence": overall_confidence,

        "detected_lines": sorted(
            best_by_line.keys()
        ),

        "detections": detections,

        "source": "model",

        "annotated_image": annotated_image,

        "line_analysis": line_analysis,

        "palm_shape": palm_shape,

        "finger_structure": finger_structure,

        "insights": insights,
    }


# ============================================================
# LINE INTERPRETATION
# ============================================================

def _line_interpretation(
    line: str,
    detection: dict,
) -> str:

    confidence = detection["confidence"]
    source = detection.get(
        "source",
        "model",
    )
    confidence_label = (
        "image-processing confidence"
        if source == "opencv_heuristic"
        else "model confidence"
    )

    messages = {

        "life": (
            "Traditional palmistry associates a clearly visible "
            "Life Line with vitality, resilience and an energetic "
            "approach to change."
        ),

        "head": (
            "Traditional palmistry associates the Head Line with "
            "thinking style, reasoning and decision-making."
        ),

        "heart": (
            "Traditional palmistry associates the Heart Line with "
            "emotional expression, relationships and connection."
        ),

        "fate": (
            "Traditional palmistry associates the Fate Line with "
            "career direction, goals and personal purpose."
        ),

        "sun": (
            "Traditional palmistry associates the Sun Line with "
            "creativity, recognition and self-expression."
        ),
    }

    return (
    f"Detected with {confidence:.1%} "
    f"{confidence_label}. "
    f"{messages.get(line, 'A palm feature was detected.')}"
)


def _normalize_line_name(name: str) -> str:

    name = str(name).lower().strip()

    replacements = {
        "life_line": "life",
        "life line": "life",

        "head_line": "head",
        "head line": "head",

        "heart_line": "heart",
        "heart line": "heart",

        "fate_line": "fate",
        "fate line": "fate",

        "sun_line": "sun",
        "sun line": "sun",
    }

    return replacements.get(
        name,
        name,
    )


# ============================================================
# PALM SHAPE
# ============================================================

def _estimate_palm_shape(image) -> dict:

    height, width = image.shape[:2]

    ratio = width / max(
        height,
        1,
    )

    # This is an approximate visual classification.
    # It is not medical or scientific.
    if ratio < 0.70:
        shape = "Long Palm"

    elif ratio > 1.05:
        shape = "Broad Palm"

    else:
        shape = "Balanced Palm"

    return {
        "shape": shape,
        "width": width,
        "height": height,
        "aspect_ratio": round(
            ratio,
            3,
        ),
        "method": "image_geometry",
        "interpretation": (
            f"The image geometry is approximately "
            f"{shape.lower()}. Traditional palmistry "
            f"may associate this shape with different "
            f"temperament styles."
        ),
    }


# ============================================================
# FINGER STRUCTURE
# ============================================================

def _estimate_finger_structure(image) -> dict:

    height, width = image.shape[:2]

    # Basic image-based placeholder until hand landmarks
    # are added. We explicitly identify this as an estimate.
    aspect_ratio = height / max(
        width,
        1,
    )

    if aspect_ratio > 1.25:
        structure = "Elongated hand appearance"

    elif aspect_ratio < 0.90:
        structure = "Broad hand appearance"

    else:
        structure = "Balanced hand appearance"

    return {
        "structure": structure,
        "method": "image_geometry_estimate",
        "landmarks_available": False,
        "interpretation": (
            "Finger-level structure is currently an "
            "image-based estimate. A hand-landmark model "
            "will provide more accurate measurements of "
            "the thumb and five fingers."
        ),
    }


# ============================================================
# HEURISTIC FALLBACK
# ============================================================

def _analyze_with_heuristic(
    image_bytes: bytes,
    image,
) -> dict:

    resized = cv2.resize(
        image,
        (600, 600),
    )

    gray = cv2.cvtColor(
        resized,
        cv2.COLOR_BGR2GRAY,
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0,
    )

    edges = cv2.Canny(
        blurred,
        40,
        120,
    )

    edge_density = (
        float(np.count_nonzero(edges))
        / edges.size
    )

    contrast = float(
        np.std(gray)
    )

    lighting_quality = min(
        1.0,
        contrast / 60,
    )

    confidence = round(
        (
            0.6
            * min(
                1.0,
                edge_density * 8,
            )
        )
        + (
            0.4
            * lighting_quality
        ),
        2,
    )

    seed = int(
        hashlib.sha256(
            image_bytes
        ).hexdigest(),
        16,
    )

    insights = {
        "life_line": _pick(
            seed,
            0,
            LIFE_LINE_OPTIONS,
        ),

        "head_line": _pick(
            seed,
            1,
            HEAD_LINE_OPTIONS,
        ),

        "heart_line": _pick(
            seed,
            2,
            HEART_LINE_OPTIONS,
        ),

        "fate_line": _pick(
            seed,
            3,
            FATE_LINE_OPTIONS,
        ),

        "sun_line": _pick(
            seed,
            4,
            SUN_LINE_OPTIONS,
        ),
    }

    return {
        "confidence": confidence,
        "edge_density": round(
            edge_density,
            4,
        ),
        "source": "heuristic",
        "annotated_image": None,
        "detected_lines": [],
        "detections": [],
        "line_analysis": {},
        "palm_shape": _estimate_palm_shape(
            image
        ),
        "finger_structure": _estimate_finger_structure(
            image
        ),
        "insights": insights,
    }


def _pick(
    seed: int,
    offset: int,
    options: list[str],
) -> str:

    return options[
        (seed + offset)
        % len(options)
    ]


LIFE_LINE_OPTIONS = [
    "Traditional palmistry associates this line with vitality and resilience.",
    "Traditional palmistry associates this line with energy and adaptation.",
    "Traditional palmistry associates this line with steadiness and change."
]

HEAD_LINE_OPTIONS = [
    "Traditional palmistry associates this line with analytical thinking.",
    "Traditional palmistry associates this line with creativity and intuition.",
    "Traditional palmistry associates this line with reasoning and decision-making."
]

HEART_LINE_OPTIONS = [
    "Traditional palmistry associates this line with emotional expression.",
    "Traditional palmistry associates this line with affection and relationships.",
    "Traditional palmistry associates this line with connection and feelings."
]

FATE_LINE_OPTIONS = [
    "Traditional palmistry associates this line with goals and direction.",
    "Traditional palmistry associates this line with career and purpose.",
    "Traditional palmistry associates this line with adaptability and ambition."
]

SUN_LINE_OPTIONS = [
    "Traditional palmistry associates this line with creativity.",
    "Traditional palmistry associates this line with recognition and expression.",
    "Traditional palmistry associates this line with achievement and visibility."
]