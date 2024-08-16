import cv2
import json
import matplotlib.pyplot as plt
from datetime import datetime, time  # time fonksiyonunu datetime modülünden içe aktarıyoruz
from collections import defaultdict
import numpy as np
from inference import get_model
import supervision as sv
import os
import time as time_module  # time modülünü time_module olarak yeniden adlandırıyoruz
import warnings


# CUDA ve OpenVINO uyarılarını bastır
warnings.filterwarnings("ignore", message="Specified provider 'CUDAExecutionProvider' is not in available provider names.")
warnings.filterwarnings("ignore", message="Specified provider 'OpenVINOExecutionProvider' is not in available provider names.")

# Modeli yükle
model = get_model(model_id="cctv-curation-dataset-1-hhibk/1")
print("Model yüklendi.")

# İnsan sayısı verilerini saklamak için sözlük
hourly_counts = defaultdict(list)
output_folder = "output"
daily_report_file = os.path.join(output_folder, "daily_human_count_report.json")
current_count_file = os.path.join(output_folder, "current_human_count.json")

# Çıktı klasörünü oluştur
os.makedirs(output_folder, exist_ok=True)

# Görüntü işleme fonksiyonu
def process_image(image):
    print("Görsel işleniyor...")
    results = model.infer(image)[0]
    detections = sv.Detections.from_inference(results)
    human_count = sum([1 for i in detections.class_id if i == 1])
    print(f"İşlenen insan sayısı: {human_count}")
    return human_count, detections

# Güncel insan sayısını güncelleyen fonksiyon
def update_current_human_count(human_count):
    with open(current_count_file, "w") as json_file:
        json.dump(human_count, json_file)  # Sadece güncel insan sayısı kaydedilecek

# Gün sonu raporu kaydeden ve grafiği oluşturan fonksiyon
def save_daily_report():
    hourly_averages = {hour: np.mean(counts) for hour, counts in hourly_counts.items()}
    
    # Günlük ortalama insan sayısını hesapla
    daily_average = np.mean(list(hourly_averages.values()))

    # Günlük rapor dosyasını güncelle
    report_data = []
    if os.path.exists(daily_report_file):
        with open(daily_report_file, "r") as json_file:
            report_data = json.load(json_file)

    report_data.append({
        "date": datetime.now().strftime('%Y-%m-%d'),
        "daily_average": daily_average
    })

    with open(daily_report_file, "w") as json_file:
        json.dump(report_data, json_file)

    # Grafik oluştur ve kaydet
    hours = list(hourly_averages.keys())
    averages = list(hourly_averages.values())

    plt.figure(figsize=(10, 5))
    plt.plot(hours, averages, marker='o')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Hour")
    plt.ylabel("Average Human Count")
    plt.title("Average Human Count Per Hour")
    plt.grid(True)

    plt.savefig(os.path.join(output_folder, f"human_count_graph_{datetime.now().strftime('%Y%m%d')}.png"))
    plt.show()

def is_within_time_range():
    now = datetime.now().time()
    return time(8, 10) <= now <= time(17, 5)

def process_new_images():
    processed_images = set()
    while True:
        print("Yeni görüntüler kontrol ediliyor...")
        for image_file in os.listdir("image_frames"):
            if image_file not in processed_images:
                image_path = os.path.join("image_frames", image_file)
                image = cv2.imread(image_path)

                if image is None:
                    print(f"{image_file} yüklenemedi.")
                    continue

                # İnsan sayısını tespit et
                human_count, detections = process_image(image)
                print(f"{image_file} üzerinde {human_count} kişi bulundu.")

                # Güncel insan sayısını güncelle
                update_current_human_count(human_count)

                # Saatlik verileri sadece belirlenen zaman aralığında topla
                if is_within_time_range():
                    current_hour = datetime.now().strftime('%Y-%m-%d %H:00')
                    hourly_counts[current_hour].append(human_count)

                    # Tahmin edilen sonucu kaydet
                    annotator = sv.BoxAnnotator()
                    label_annotator = sv.LabelAnnotator()
                    annotated_image = annotator.annotate(scene=image, detections=detections)
                    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)
                    cv2.imwrite(os.path.join(output_folder, f"predicted_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"), annotated_image)
                    print(f"{image_file} kaydedildi.")

                processed_images.add(image_file)

        # Saat 17:05'den sonra raporu kaydet ve grafiği oluştur, ancak insan tespiti devam etsin
        if datetime.now().time() > time(17, 5) and hourly_counts:
            print("Gün sonu raporu oluşturuluyor...")
            save_daily_report()
            hourly_counts.clear()  # Günlük veriyi temizle

        # Bir sonraki kontrol için kısa bir süre bekle
        time_module.sleep(5)

print("Görüntü işleme başlıyor...")
process_new_images()
