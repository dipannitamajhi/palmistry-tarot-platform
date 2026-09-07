"""YOLO-based palm-line detection service."""

from __future__ import annotations

import base64
import os
from functools import lru_cache
from typing import Any

MODEL_PATH = os.getenv("PALM_LINE_MODEL_PATH", "models/best.pt")

CONFIDENCE_THRESHOLD = float(
    os.getenv("PALM_LINE_CONFIDENCE_THRESHOLD", "0.35")
)
FATE_FALLBACK_THRESHOLD = float(
    os.getenv("PALM_LINE_FATE_FALLBACK_THRESHOLD", "0.20")
)

OPENCV_MISSING_LINE_FALLBACK = os.getenv(
    "PALM_LINE_OPENCV_FALLBACK", "true"
).lower() not in {"0", "false", "no", "off"}

# Fallback order.
# Your CURRENT model has:
# fate, head, heart, life
#
# Your FUTURE model should have:
# fate, head, heart, life, sun
#
# Prefer the class names embedded in the YOLO model whenever available.
FALLBACK_CLASS_NAMES = [
    "fate",
    "head",
    "heart",
    "life",
    "sun",
]


class ModelUnavailable(Exception):
    """Raised when no trained YOLO model is available."""


def is_available() -> bool:
    return os.path.exists(MODEL_PATH)


@lru_cache
def _model():
    if not is_available():
        raise ModelUnavailable(
            f"No trained model found at {MODEL_PATH}."
        )

    from ultralytics import YOLO

    return YOLO(MODEL_PATH)


def detect_palm_lines(
    image_bytes: bytes,
) -> dict[str, Any] | None:

    if not is_available():
        return None

    import cv2
    import numpy as np

    np_array = np.frombuffer(image_bytes, np.uint8)

    image = cv2.imdecode(
        np_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        return None

    model = _model()

    results = model.predict(
        image,
        verbose=False,
        conf=CONFIDENCE_THRESHOLD,
    )

    detections: list[dict[str, Any]] = []

    for result in results:

        names = result.names or {}

        for box in result.boxes:

            class_id = int(box.cls[0])

            label = names.get(class_id)

            if not label and class_id < len(FALLBACK_CLASS_NAMES):
                label = FALLBACK_CLASS_NAMES[class_id]

            if not label:
                label = str(class_id)

            label = str(label).lower().strip()

            confidence = round(
                float(box.conf[0]),
                3,
            )

            bbox = [
                round(float(v), 1)
                for v in box.xyxy[0].tolist()
            ]

            detections.append(
              {
                    "line": label,
                    "confidence": confidence,
                    "bbox": bbox,
                    "source": "model",
    }
)
    # Give Fate Line a second chance at a lower threshold.
    # This uses the existing trained Fate class and does NOT require retraining.
    if not any(d["line"] == "fate" for d in detections):

        fate_class_ids = []

        for class_id, class_name in (model.names or {}).items():

            if str(class_name).lower().strip() in {
                "fate",
                "fate_line",
                "fate line",
            }:
                fate_class_ids.append(int(class_id))

        if (
            fate_class_ids
            and FATE_FALLBACK_THRESHOLD < CONFIDENCE_THRESHOLD
        ):

            retry_results = model.predict(
                image,
                verbose=False,
                conf=FATE_FALLBACK_THRESHOLD,
                classes=fate_class_ids,
            )

            for result in retry_results:

                names = result.names or {}

                for box in result.boxes:

                    class_id = int(box.cls[0])

                    label = str(
                        names.get(
                            class_id,
                            "fate",
                        )
                    ).lower().strip()

                    if label not in {
                        "fate",
                        "fate_line",
                        "fate line",
                    }:
                        continue

                    confidence = round(
                        float(box.conf[0]),
                        3,
                    )

                    bbox = [
                        round(float(v), 1)
                        for v in box.xyxy[0].tolist()
                    ]

                    detections.append(
                        {
                            "line": "fate",
                            "confidence": confidence,
                            "bbox": bbox,
                            "source": "model_low_confidence",
                        }
                    )

    # ------------------------------------------------------------
    # OpenCV fallback for Fate/Sun
    # ------------------------------------------------------------
    #
    # Your current YOLO model does not reliably contain the Sun class.
    # Instead of retraining, use image processing to look for palm creases.
    #
    missing_lines = {
        line
        for line in ("fate", "sun")
        if not any(
            d["line"] == line
            for d in detections
        )
    }

    if (
        missing_lines
        and OPENCV_MISSING_LINE_FALLBACK
    ):

        heuristic_detections = (
            _detect_missing_lines_with_opencv(
                image,
                detections,
                missing_lines,
            )
        )

        detections.extend(
            heuristic_detections
        )

    # Draw annotations
    annotated = image.copy()


    for detection in detections:

        x1, y1, x2, y2 = map(
            int,
            detection["bbox"],
        )

        label = detection["line"]
        confidence = detection["confidence"]

        text = f"{label.replace('_', ' ').title()} {confidence:.0%}"

        # Bounding box
        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            3,
        )

        # Label background
        (text_width, text_height), baseline = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            2,
        )

        label_top = max(
            0,
            y1 - text_height - baseline - 10,
        )

        cv2.rectangle(
            annotated,
            (x1, label_top),
            (
                x1 + text_width + 10,
                y1,
            ),
            (0, 255, 0),
            -1,
        )

        # Label text
        cv2.putText(
            annotated,
            text,
            (
                x1 + 5,
                y1 - 5,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )

    # Encode annotated image
    success, encoded_image = cv2.imencode(
        ".jpg",
        annotated,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            90,
        ],
    )

    if not success:
        raise ValueError(
            "Could not create annotated palm image."
        )

    image_base64 = base64.b64encode(
        encoded_image.tobytes()
    ).decode("utf-8")

    return {
        "detections": detections,
        "annotated_image": image_base64,
    }
def _detect_missing_lines_with_opencv(
    image,
    existing_detections: list[dict[str, Any]],
    missing_lines: set[str],
) -> list[dict[str, Any]]:
    """
    Estimate missing Fate/Sun lines from palm creases.

    This is a fallback for the current YOLO model.
    It does not replace a properly trained five-class model.
    """

    import cv2
    import numpy as np

    height, width = image.shape[:2]

    if height < 200 or width < 200:
        return []

    # ------------------------------------------------------------
    # Determine palm region
    # ------------------------------------------------------------

    boxes = [
        d.get("bbox")
        for d in existing_detections
        if d.get("bbox")
    ]

    if boxes:

        x1 = min(b[0] for b in boxes)
        y1 = min(b[1] for b in boxes)
        x2 = max(b[2] for b in boxes)
        y2 = max(b[3] for b in boxes)

        pad_x = max(
            80,
            int((x2 - x1) * 0.55),
        )

        pad_y = max(
            100,
            int((y2 - y1) * 0.45),
        )

        x1 = max(
            0,
            int(x1 - pad_x),
        )

        y1 = max(
            0,
            int(y1 - pad_y),
        )

        x2 = min(
            width,
            int(x2 + pad_x),
        )

        y2 = min(
            height,
            int(y2 + pad_y),
        )

    else:

        # Generic palm region
        x1 = int(width * 0.18)
        x2 = int(width * 0.82)

        y1 = int(height * 0.28)
        y2 = int(height * 0.92)

    if (
        x2 - x1 < 160
        or y2 - y1 < 220
    ):
        return []

    roi = image[
        y1:y2,
        x1:x2,
    ]

    rh, rw = roi.shape[:2]

    # ------------------------------------------------------------
    # Enhance palm creases
    # ------------------------------------------------------------

    gray = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY,
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    gray = clahe.apply(gray)

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

    blackhat_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (9, 9),
    )

    blackhat = cv2.morphologyEx(
        gray,
        cv2.MORPH_BLACKHAT,
        blackhat_kernel,
    )

    blackhat = cv2.normalize(
        blackhat,
        None,
        0,
        255,
        cv2.NORM_MINMAX,
    )

    _, crease_mask = cv2.threshold(
        blackhat,
        22,
        255,
        cv2.THRESH_BINARY,
    )

    crease_mask = cv2.morphologyEx(
        crease_mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 7),
        ),
        iterations=1,
    )

    edges = cv2.Canny(
        gray,
        35,
        105,
    )

    edges = cv2.bitwise_or(
        edges,
        crease_mask,
    )

    # ------------------------------------------------------------
    # Detect long crease segments
    # ------------------------------------------------------------

    min_len = max(
        45,
        int(rh * 0.16),
    )

    max_gap = max(
        18,
        int(rh * 0.035),
    )

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(
            24,
            int(rh * 0.035),
        ),
        minLineLength=min_len,
        maxLineGap=max_gap,
    )

    if lines is None:
        return []

    candidates = {
        "fate": [],
        "sun": [],
    }

    for raw in np.asarray(lines).reshape(-1, 4):

        lx1, ly1, lx2, ly2 = map(
            int,
            raw,
        )

        dx = lx2 - lx1
        dy = ly2 - ly1

        length = float(
            np.hypot(
                dx,
                dy,
            )
        )

        if length < min_len:
            continue

        verticality = (
            abs(dy)
            / max(length, 1.0)
        )

        if verticality < 0.78:
            continue

        cx = (
            ((lx1 + lx2) / 2)
            / rw
        )

        cy = (
            ((ly1 + ly2) / 2)
            / rh
        )

        length_ratio = min(
            1.0,
            length / max(
                rh * 0.45,
                1.0,
            ),
        )

        # Avoid finger edges and wrist area
        if cy < 0.18 or cy > 0.94:
            continue

        # --------------------------------------------------------
        # Fate Line
        # Central part of palm
        # --------------------------------------------------------

        if (
            "fate" in missing_lines
            and 0.30 <= cx <= 0.64
        ):

            score = (
                0.50 * verticality
                + 0.30 * length_ratio
                + 0.20 * (
                    1.0
                    - abs(cx - 0.48)
                    / 0.30
                )
            )

            candidates["fate"].append(
                (
                    score,
                    (
                        lx1 + x1,
                        ly1 + y1,
                        lx2 + x1,
                        ly2 + y1,
                    ),
                )
            )

        # --------------------------------------------------------
        # Sun Line
        # Ring-finger side of palm
        # --------------------------------------------------------

        if (
            "sun" in missing_lines
            and 0.48 <= cx <= 0.80
        ):

            score = (
                0.50 * verticality
                + 0.30 * length_ratio
                + 0.20 * (
                    1.0
                    - abs(cx - 0.62)
                    / 0.32
                )
            )

            candidates["sun"].append(
                (
                    score,
                    (
                        lx1 + x1,
                        ly1 + y1,
                        lx2 + x1,
                        ly2 + y1,
                    ),
                )
            )

    # ------------------------------------------------------------
    # Convert best candidates to detections
    # ------------------------------------------------------------

    results = []

    for line in missing_lines:

        ranked = sorted(
            candidates.get(
                line,
                [],
            ),
            key=lambda item: item[0],
            reverse=True,
        )

        if not ranked:
            continue

        score, segment = ranked[0]

        if score < 0.55:
            continue

        # This is deliberately lower than normal YOLO confidence.
        confidence = round(
            min(
                0.82,
                0.35 + 0.45 * score,
            ),
            3,
        )

        sx1, sy1, sx2, sy2 = segment

        bbox = [
            float(min(sx1, sx2)),
            float(min(sy1, sy2)),
            float(max(sx1, sx2)),
            float(max(sy1, sy2)),
        ]

        results.append(
            {
                "line": line,
                "confidence": confidence,
                "bbox": bbox,
                "source": "opencv_heuristic",
            }
        )

    return results