import cv2
import os
import sys
# Load face detector (simple + reliable)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

name = sys.argv[1].strip().replace(" ", "_")

dataset_path = "dataset"
person_path = os.path.join(dataset_path, name)
os.makedirs(person_path, exist_ok=True)

cap = cv2.VideoCapture(1)

count = 0
max_images = 30

print("Press 'c' to capture | 'q' to quit")

def augment(img):
    imgs = []

    imgs.append(img)
    imgs.append(cv2.flip(img, 1))
    imgs.append(cv2.convertScaleAbs(img, alpha=1.2, beta=20))
    imgs.append(cv2.convertScaleAbs(img, alpha=0.8, beta=-20))

    return imgs

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Improve lighting
    frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=20)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    cv2.putText(frame, f"{name} {count}/{max_images}",
                (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Register", frame)

    key = cv2.waitKey(1)

    if key == ord('c') and len(faces) > 0:
        x, y, w, h = faces[0]

        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        images = augment(face)

        for img in images:
            count += 1
            cv2.imwrite(os.path.join(person_path, f"{count}.jpg"), img)

        print(f"Saved {len(images)} images")

    elif key == ord('q'):
        break

    if count >= max_images:
        break

cap.release()
cv2.destroyAllWindows()

print("✅ Registration Done")