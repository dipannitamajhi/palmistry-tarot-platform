from ultralytics import YOLO

model = YOLO('models/best.pt')
results = model.predict('test_image.jpg', conf=0.1, save=False)

for r in results:
    print(f"Found {len(r.boxes)} detections")
    for box in r.boxes:
        print(model.names[int(box.cls[0])], float(box.conf[0]))