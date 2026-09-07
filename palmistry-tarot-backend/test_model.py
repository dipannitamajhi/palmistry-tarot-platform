from ultralytics import YOLO

model = YOLO("models/best.pt")

results = model.predict(
    source="test_images/test_image.jpg",
    save=True,
    conf=0.25
)

for result in results:
    print(result)