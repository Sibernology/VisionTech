import locale
locale.setlocale(locale.LC_ALL, 'C')
import cv2  # type: ignore
import mediapipe as mp  # type: ignore 
import numpy as np  # type: ignore
import subprocess
import time
import math
import os
from typing import TypedDict, List, Any, Tuple

class HandData(TypedDict):
    status: List[bool]
    size: float
    wrist: Tuple[int, int]
    lms: Any
    y: float

class ProGestureControl:
    def __init__(self):
        self.SCREENSHOT_HOLD_TIME = 1.0
        self.VOL_SENSITIVITY = 2
        self.CAMERA_INDEX = 1  # Default camera index is usually 0
        self.MENU_TIMEOUT = 10.0
        self.SMOOTHENING = 7 

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8 
        )
        self.mp_face = mp.solutions.face_detection
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.6)
        self.mp_draw = mp.solutions.drawing_utils
        
        self.cap = cv2.VideoCapture(self.CAMERA_INDEX)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        try:
            output = subprocess.check_output("xdotool getdisplaygeometry", shell=True, text=True)
            self.screen_w, self.screen_h = map(int, output.strip().split())
        except Exception:
            self.screen_w, self.screen_h = 1920, 1080  # Default fallback

        self.last_action_time = 0.0
        self.action_cooldown = 1.5
        self.help_open = False
        self.help_timer = 0.0
        self.fist_start_time = 0.0
        self.is_fist_held = False
        self.prev_hand_size = 0.0
        self.volume_level = 50
        
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        
        self.mouse_active = False
        self.vol_bar_display = 400

    def run_cmd(self, cmd):
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def get_hand_size(self, landmarks, w, h):
        x1, y1 = landmarks.landmark[0].x * w, landmarks.landmark[0].y * h
        x2, y2 = landmarks.landmark[9].x * w, landmarks.landmark[9].y * h
        return math.hypot(x2 - x1, y2 - y1)

    def is_tight_fist(self, lms, w, h):
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        folded = all(lms.landmark[tip].y > lms.landmark[pip].y for tip, pip in zip(tips, pips))
        if not folded:
            return False
        wrist_x, wrist_y = lms.landmark[0].x * w, lms.landmark[0].y * h
        ref_len = self.get_hand_size(lms, w, h)
        avg_tip_dist = sum(math.hypot(lms.landmark[t].x * w - wrist_x, lms.landmark[t].y * h - wrist_y) for t in tips) / 4
        return avg_tip_dist < (ref_len * 0.9)

    def get_finger_status(self, hand_lms):
        tips = [8, 12, 16, 20]
        status = [hand_lms.landmark[tip].y < hand_lms.landmark[tip - 2].y for tip in tips]
        is_right = hand_lms.landmark[17].x > hand_lms.landmark[5].x
        thumb = hand_lms.landmark[4].x < hand_lms.landmark[3].x if is_right else hand_lms.landmark[4].x > hand_lms.landmark[3].x
        status.insert(0, thumb)
        return status

    def move_mouse_xdotool(self, x, y):
        try:
            subprocess.run(f"xdotool mousemove {int(x)} {int(y)}", shell=True, check=True)
            return True
        except Exception:
            return False

    def process(self):
        while True:
            success, img = self.cap.read()
            if not success:
                break
            img = cv2.flip(img, 1)
            h, w, _ = img.shape
            h, w = int(h), int(w)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            now = time.time()

            if self.help_open and (now - self.help_timer > self.MENU_TIMEOUT):
                self.help_open = False

            face_results = self.face_detection.process(img_rgb)
            if face_results.detections:
                for det in face_results.detections:
                    bbox = det.location_data.relative_bounding_box
                    fx, fy = int(bbox.xmin * w), int(bbox.ymin * h)
                    fw, fh = int(bbox.width * w), int(bbox.height * h)
                    
                    x1, y1 = max(0, fx), max(0, fy)
                    x2, y2 = min(w, fx + fw), min(h, fy + fh)
                    
                    if (x2 - x1) > 0 and (y2 - y1) > 0:
                        img[y1:y2, x1:x2] = cv2.GaussianBlur(img[y1:y2, x1:x2], (99, 99), 30)

            hand_results = self.hands.process(img_rgb)
            mouse_mode_active = False
            
            if hand_results.multi_hand_landmarks:
                hands_data: List[HandData] = []
                for hand_lms in hand_results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                    status = self.get_finger_status(hand_lms)
                    
                    if status[1] and status[2] and not status[3] and not status[4]:
                        x1, y1 = hand_lms.landmark[8].x * w, hand_lms.landmark[8].y * h
                        x2, y2 = hand_lms.landmark[12].x * w, hand_lms.landmark[12].y * h
                        dist = math.hypot(x2 - x1, y2 - y1)
                        
                        if dist < 45:
                            mouse_mode_active = True
                            mx = np.interp(x1, [250, int(w) - 250], [0, self.screen_w])
                            my = np.interp(y1, [100, int(h) - 100], [0, self.screen_h])
                            
                            if self.plocX == 0 and self.plocY == 0:
                                self.plocX, self.plocY = mx, my
                            
                            self.clocX = self.plocX + (mx - self.plocX) / self.SMOOTHENING
                            self.clocY = self.plocY + (my - self.plocY) / self.SMOOTHENING
                            
                            self.move_mouse_xdotool(self.clocX, self.clocY)
                            
                            cv2.circle(img, (int(x1), int(y1)), 20, (0, 255, 255), cv2.FILLED)
                            cv2.circle(img, (int(x2), int(y2)), 20, (0, 255, 255), cv2.FILLED)
                            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 3)
                            
                            self.plocX, self.plocY = self.clocX, self.clocY
                            
                            if not status[0] and (now - self.last_action_time > 0.3):
                                subprocess.Popen("xdotool click 1", shell=True)
                                cv2.putText(img, "TIKLAMA", (int(x1)-50, int(y1)-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                                self.last_action_time = now

                    hands_data.append({
                        'status': status,
                        'size': self.get_hand_size(hand_lms, w, h),
                        'wrist': (int(hand_lms.landmark[0].x * w), int(hand_lms.landmark[0].y * h)),
                        'lms': hand_lms,
                        'y': hand_lms.landmark[9].y
                    })

                if mouse_mode_active:
                    cv2.putText(img, "FARE MODU AKTIF", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.putText(img, f"Pozisyon: {int(self.clocX)},{int(self.clocY)}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                if len(hands_data) == 1 and not mouse_mode_active:
                    h_data = hands_data[0]
                    s = h_data['status']
                    
                    if self.is_tight_fist(h_data['lms'], w, h):
                        if not self.is_fist_held:
                            self.fist_start_time = now
                            self.is_fist_held = True
                        elapsed = now - self.fist_start_time
                        progress = min(elapsed / self.SCREENSHOT_HOLD_TIME, 1.0)
                        cx, cy = h_data['wrist']
                        cv2.ellipse(img, (cx, cy), (65, 65), 0, 0, 360 * progress, (0, 0, 255), 6)
                        if elapsed >= self.SCREENSHOT_HOLD_TIME and (now - self.last_action_time > self.action_cooldown):
                            screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")
                            os.makedirs(screenshot_dir, exist_ok=True)
                            path = os.path.join(screenshot_dir, f"ss_{int(now)}.png")
                            self.run_cmd(f"scrot {path}")
                            self.last_action_time = now
                    else: 
                        self.is_fist_held = False

                    if all(s):
                        diff = h_data['size'] - self.prev_hand_size
                        if self.prev_hand_size != 0 and abs(diff) > 3.0:
                            cmd = f"+{self.VOL_SENSITIVITY}%" if diff > 0 else f"-{self.VOL_SENSITIVITY}%"
                            self.run_cmd(f"pactl set-sink-volume @DEFAULT_SINK@ {cmd}")
                            self.volume_level = np.clip(self.volume_level + (self.VOL_SENSITIVITY if diff > 0 else -self.VOL_SENSITIVITY), 0, 100)
                        self.prev_hand_size = h_data['size']
                    else: 
                        self.prev_hand_size = 0.0

                    if now - self.last_action_time > self.action_cooldown:
                        if s == [False, True, False, False, False]:
                            self.run_cmd("playerctl play-pause")
                            self.last_action_time = now
                        elif s == [False, True, True, False, False]:
                            self.run_cmd("playerctl next")
                            self.last_action_time = now
                        elif s == [False, True, True, True, False]:
                            self.run_cmd("playerctl previous")
                            self.last_action_time = now

                elif len(hands_data) == 2:
                    if all(hands_data[0]['status']) and all(hands_data[1]['status']):
                        if hands_data[0]['y'] < 0.4 and hands_data[1]['y'] < 0.4:
                            if now - self.last_action_time > self.action_cooldown:
                                self.help_open = not self.help_open
                                self.help_timer = now 
                                self.last_action_time = now
            else:
                self.plocX, self.plocY = 0, 0

            self.vol_bar_display = np.interp(self.volume_level, [0, 100], [400, 150])
            cv2.rectangle(img, (w - 50, 150), (w - 20, 400), (50, 50, 50), -1)
            cv2.rectangle(img, (w - 50, int(self.vol_bar_display)), (w - 20, 400), (0, 255, 0), -1)

            if self.help_open:
                overlay = img.copy()
                cv2.rectangle(overlay, (150, 150), (w - 150, h - 150), (0, 0, 0), -1)
                img = cv2.addWeighted(overlay, 0.7, img, 0.3, 0)
                menu = ["KONTROLLER", "1. Yumruk: Screenshot", "2. Fare: Isaret+Orta", "3. Tikla: Bas Parmak", "4. Isaret: Play", "5. Zafer: Next", "6. Avuc: Ses"]
                for i, text in enumerate(menu):
                    cv2.putText(img, text, (200, 200 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Gesture Control Ultimate", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # xdotool yüklü mü kontrol et
    try:
        subprocess.run("which xdotool", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("xdotool bulundu, fare kontrolü hazır")
    except Exception:
        print("xdotool bulunamadı, yüklemek için: sudo apt install xdotool")
    
    ProGestureControl().process()