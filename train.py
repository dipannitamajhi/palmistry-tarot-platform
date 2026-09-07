"""
Train the YOLO palm-line detector.

Run this from inside the `dataset` folder's PARENT directory, i.e. your
project root should look like:

    your_project/
        train.py          <- this file
        yolo26n.pt         <- base pretrained model
        dataset/
            data.yaml
            train/
            valid/
            test/

Then just run:
    python train.py
"""

from pathlib import Path
from ultralytics import YOLO

# Path(__file__).parent means "the folder this script lives in" — this is
# what makes the script portable. It will work no matter whose computer
# runs it, unlike a hardcoded "D:\..." path which only works on one PC.
PROJECT_ROOT = Path(__file__).parent
DATA_YAML = PROJECT_ROOT / "dataset" / "data.yaml"
BASE_MODEL = PROJECT_ROOT / "yolo26n.pt"


def main():
    if not DATA_YAML.exists():
        raise FileNotFoundError(
            f"Could not find {DATA_YAML}. Make sure the 'dataset' folder "
            f"sits next to this script."
        )

    model = YOLO(str(BASE_MODEL))

    model.train(
        data=str(DATA_YAML),
        epochs=50,          # let it run all 50 — don't stop it early this time
        imgsz=640,
        batch=8,
        name="palmistry_model",
    )

    print("Training completed! Check runs/detect/palmistry_model/results.csv "
          "for the final metrics, and copy runs/detect/palmistry_model/weights/best.pt "
          "into your backend's models/ folder when you're happy with it.")


if __name__ == "__main__":
    main()