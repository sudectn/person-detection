import os
import time
import cv2
import threading
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Görsellerin kaydedileceği klasör
output_folder = "image_frames"

# Çıktı klasörünü oluştur
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# RTSP URL bilgilerini .env dosyasından al
camera_username = os.getenv("CAMERA_USERNAME")
camera_password = os.getenv("CAMERA_PASSWORD")
camera_ip = os.getenv("CAMERA_IP")
camera_port = os.getenv("CAMERA_PORT", "554")  # Portu varsayılan olarak 554 alıyoruz
camera_path = os.getenv("CAMERA_PATH", "")     # Kamera yolu

rtsp_url = f'rtsp://{camera_username}:{camera_password}@{camera_ip}:{camera_port}/{camera_path}'

capture_interval = 20  # Varsayılan kare alma aralığı
interval_lock = threading.Lock()

def is_corrupted_or_gray(image):
    """Resmin bozuk veya gri tonlamalı olup olmadığını kontrol et"""
    if image.mode not in ("L", "RGB"):
        return False

    if image.mode == "RGB":
        gray_image = image.convert('L')
        histogram = gray_image.histogram()
        total_pixels = sum(histogram)
        if total_pixels == 0:
            return True
        gray_level_distribution = [float(count) / total_pixels for count in histogram]
        max_gray_level = max(gray_level_distribution)
        if max_gray_level > 0.9:
            return True
    return False

def capture_image_from_stream():
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("Kamera bağlantısı kurulamadı.")
        return

    ret, frame = cap.read()
    if ret:
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if is_corrupted_or_gray(image):
            print("Bozuk veya gri tonlamalı görüntü atlandı.")
            return

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        img_name = f"image_{timestamp}.jpg"
        img_path = os.path.join(output_folder, img_name)
        image.save(img_path)
        os.chmod(img_path, 0o777)  # Dosyaya tam izin ver
        print(f"{img_name} kaydedildi.")
    else:
        print("Görüntü alınamadı.")
    cap.release()

def capture_images_periodically():
    global capture_interval
    while True:
        with interval_lock:
            interval = capture_interval
        capture_image_from_stream()
        time.sleep(interval)

if __name__ == '__main__':
    # Kare çıkarma iş parçacığını başlat
    thread = threading.Thread(target=capture_images_periodically)
    thread.start()

