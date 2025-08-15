import cv2
import numpy as np
import mediapipe as mp
import random

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Ukuran layar game
WIDTH, HEIGHT = 640, 480

# Bola positif (tambah skor)
balls = []
for _ in range(3):
    balls.append({
        "x": random.randint(50, WIDTH - 50),
        "y": random.randint(-300, -50),
        "radius": 20,
        "speed": random.randint(4, 8),
        "color": (0, 0, 255)  # Merah
    })

# Bola negatif (kurangi skor)
obstacles = []
for _ in range(2):
    obstacles.append({
        "x": random.randint(50, WIDTH - 50),
        "y": random.randint(-300, -50),
        "radius": 25,
        "speed": random.randint(5, 9),
        "color": (0, 0, 0)  # Hitam
    })

# Paddle
paddle_width = 120
paddle_height = 20
paddle_x = WIDTH // 2 - paddle_width // 2
paddle_y = HEIGHT - 50

score = 0

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Deteksi tangan
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Ambil koordinat telapak tangan (landmark 9)
            h, w, _ = frame.shape
            cx = int(hand_landmarks.landmark[9].x * w)
            paddle_x = cx - paddle_width // 2

    # Update bola positif
    for ball in balls:
        ball["y"] += ball["speed"]
        if ball["y"] > HEIGHT:
            ball["x"] = random.randint(50, WIDTH - 50)
            ball["y"] = random.randint(-300, -50)

        # Cek tabrakan
        if (paddle_y < ball["y"] + ball["radius"] < paddle_y + paddle_height and
            paddle_x < ball["x"] < paddle_x + paddle_width):
            score += 1
            ball["x"] = random.randint(50, WIDTH - 50)
            ball["y"] = random.randint(-300, -50)

    # Update bola negatif
    for obs in obstacles:
        obs["y"] += obs["speed"]
        if obs["y"] > HEIGHT:
            obs["x"] = random.randint(50, WIDTH - 50)
            obs["y"] = random.randint(-300, -50)

        # Cek tabrakan
        if (paddle_y < obs["y"] + obs["radius"] < paddle_y + paddle_height and
            paddle_x < obs["x"] < paddle_x + paddle_width):
            score -= 2
            obs["x"] = random.randint(50, WIDTH - 50)
            obs["y"] = random.randint(-300, -50)

    # Gambar bola positif
    for ball in balls:
        cv2.circle(frame, (ball["x"], ball["y"]), ball["radius"], ball["color"], -1)

    # Gambar bola negatif
    for obs in obstacles:
        cv2.circle(frame, (obs["x"], obs["y"]), obs["radius"], obs["color"], -1)

    # Gambar paddle
    cv2.rectangle(frame, (paddle_x, paddle_y),
                  (paddle_x + paddle_width, paddle_y + paddle_height), (255, 0, 0), -1)

    # Tampilkan skor
    cv2.putText(frame, f"Score: {score}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Catch the Ball (Hand Tracking)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC untuk keluar
        break

cap.release()
cv2.destroyAllWindows()
