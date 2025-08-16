import cv2
import numpy as np
import mediapipe as mp
import random
import pygame
import time

# 🎵 Inisialisasi mixer untuk sound
pygame.mixer.init()

# Load musik & efek
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.play(-1)  # Loop tanpa henti

sound_up = pygame.mixer.Sound("score_up.wav")
sound_down = pygame.mixer.Sound("score_down.wav")
sound_bonus = pygame.mixer.Sound("bonus.wav")
sound_levelup = pygame.mixer.Sound("level_up.wav")

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Ukuran layar game
WIDTH, HEIGHT = 1280, 720

# Paddle
paddle_width = 150
paddle_height = 25
paddle_x = WIDTH // 2 - paddle_width // 2
paddle_y = HEIGHT - 60

# Bola
balls = []
for _ in range(5):
    balls.append({
        "x": random.randint(50, WIDTH - 50),
        "y": random.randint(-500, -50),
        "radius": 20,
        "speed": random.randint(4, 8),
        "color": (0, 0, 255),  # Merah positif
        "type": "normal"
    })

obstacles = []
for _ in range(3):
    obstacles.append({
        "x": random.randint(50, WIDTH - 50),
        "y": random.randint(-500, -50),
        "radius": 25,
        "speed": random.randint(5, 10),
        "color": (0, 0, 0),  # Hitam negatif
        "type": "normal"
    })

bonus_balls = []

score = 0
combo = 0
level = 1
start_time = time.time()
powerup_end = 0
score_multiplier = 1

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


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
            h, w, _ = frame.shape
            cx = int(hand_landmarks.landmark[9].x * w)
            paddle_x = max(0, min(WIDTH - paddle_width, cx - paddle_width // 2))  # Batas layar

    # Update bola positif
    for ball in balls:
        ball["y"] += ball["speed"]
        if ball["y"] > HEIGHT:
            ball["x"] = random.randint(50, WIDTH - 50)
            ball["y"] = random.randint(-500, -50)

        # Cek tabrakan
        if (paddle_y < ball["y"] + ball["radius"] < paddle_y + paddle_height and
            paddle_x < ball["x"] < paddle_x + paddle_width):
            score += 1 * score_multiplier
            combo += 1
            sound_up.play()
            ball["x"] = random.randint(50, WIDTH - 50)
            ball["y"] = random.randint(-500, -50)

    # Update bola negatif
    for obs in obstacles:
        obs["y"] += obs["speed"]
        if obs["y"] > HEIGHT:
            obs["x"] = random.randint(50, WIDTH - 50)
            obs["y"] = random.randint(-500, -50)

        # Cek tabrakan
        if (paddle_y < obs["y"] + obs["radius"] < paddle_y + paddle_height and
            paddle_x < obs["x"] < paddle_x + paddle_width):
            score -= 2
            combo = 0
            sound_down.play()
            obs["x"] = random.randint(50, WIDTH - 50)
            obs["y"] = random.randint(-500, -50)

    # Spawn bonus secara acak
    if random.randint(1, 500) == 1:  # peluang kecil
        bonus_balls.append({
            "x": random.randint(50, WIDTH - 50),
            "y": -50,
            "radius": 30,
            "speed": 6,
            "color": (0, 255, 255),  # Kuning emas
            "type": random.choice(["double_score", "wide_paddle"])
        })

    # Update bonus balls
    for bonus in bonus_balls[:]:
        bonus["y"] += bonus["speed"]
        if bonus["y"] > HEIGHT:
            bonus_balls.remove(bonus)

        if (paddle_y < bonus["y"] + bonus["radius"] < paddle_y + paddle_height and
            paddle_x < bonus["x"] < paddle_x + paddle_width):
            sound_bonus.play()
            if bonus["type"] == "double_score":
                score_multiplier = 2
                powerup_end = time.time() + 5
            elif bonus["type"] == "wide_paddle":
                paddle_width = 250
                powerup_end = time.time() + 5
            bonus_balls.remove(bonus)

    # Reset powerup
    if time.time() > powerup_end:
        paddle_width = 150
        score_multiplier = 1

    # Naikkan level setiap 20 poin
    if score // 20 + 1 > level:
        level += 1
        sound_levelup.play()
        for ball in balls:
            ball["speed"] += 1
        for obs in obstacles:
            obs["speed"] += 1

    # Gambar bola positif
    for ball in balls:
        cv2.circle(frame, (ball["x"], ball["y"]), ball["radius"], ball["color"], -1)

    # Gambar bola negatif
    for obs in obstacles:
        cv2.circle(frame, (obs["x"], obs["y"]), obs["radius"], obs["color"], -1)

    # Gambar bonus
    for bonus in bonus_balls:
        cv2.circle(frame, (bonus["x"], bonus["y"]), bonus["radius"], bonus["color"], -1)

    # Gambar paddle
    cv2.rectangle(frame, (paddle_x, paddle_y),
                  (paddle_x + paddle_width, paddle_y + paddle_height), (255, 0, 0), -1)

    # Tampilkan skor & level
    cv2.putText(frame, f"Score: {score}  Combo: {combo}  Level: {level}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Catch the Ball (Hand Tracking)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC untuk keluar
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.music.stop()
