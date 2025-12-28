# 🏥 Enhanced Medical Imaging Viewer

PyQt5 + Matplotlib tabanlı, **DICOM / NIfTI** destekli bir medikal görüntü görüntüleyici.
Uygulama; **windowing (WC/WW)**, **brightness/contrast**, **3D slice navigation**, **preset yönetimi**, **hasta raporu oluşturma** ve **Gemini tabanlı AI rapor / AI chat** gibi özellikleri tek arayüzde birleştirir.

---

## ✨ Özellikler

### 📁 Dosya Desteği

* ✅ **DICOM** yükleme (`.dcm`, `.dicom`) — `pydicom` ile
* ✅ **NIfTI** yükleme (`.nii`, `.nii.gz`) — `nibabel` ile
* 🧪 Dosya yoksa demo amaçlı **sample CT verisi** üretme

### 🎚️ Görüntü İşleme

* ✅ **DICOM windowing (VOI LUT formülü)** ile WC/WW uygulama
* ✅ **Brightness / Contrast** ayarı
* ✅ Matplotlib canvas üzerinde **grayscale render**

### 🧊 3D / Volume Navigation

* ✅ 3D veri tespitinde **slice slider** otomatik açılır
* ✅ Slice label: `Slice: current / total`

### 🔧 Preset Sistemi

* ✅ Modality’ye göre (CT/MRI/US/MG) **preset listesi** güncellenir
* ✅ Preset seçilince WC/WW otomatik set edilir

### 🧑‍⚕️ Hasta Bilgisi ve Rapor

* ✅ DICOM metadata’dan hasta bilgilerini çekme (PatientName, PatientID, StudyDate, Modality)
* ✅ **Patient Report** penceresi:

  * Patient Information
  * Image Information
  * Serbest rapor yazımı
  * 🤖 AI Suggestion üretme (demo/simülasyon)

### 🤖 AI (Gemini) Entegrasyonu

* ✅ Gemini API Key yönetimi (Preferences & Set API Key)
* ✅ **AIThread (QThread)** ile UI’yi bloklamadan API çağrısı
* ✅ **Generate AI Report**: profesyonel rapor ürettirme
* ✅ **AI Chat**: case context + chat history ile konuşma
* ✅ Chat penceresi geometry kaydı (QSettings)

### 🌙 Tema / Kullanılabilirlik

* ✅ Light / Dark theme (QSS)
* ✅ Matplotlib figure background tema ile uyumlu
* ✅ Fullscreen (F11)
* ✅ Chat input: **Ctrl+Enter** ile gönderme

---

## 🧩 Mimari Bileşenler

### 1) `MedicalImageViewer (QMainWindow)`

Ana uygulama penceresi:

* UI oluşturma (splitter, kontrol paneli, menü, status bar)
* DICOM/NIfTI yükleme ve metadata parse
* Windowing + brightness/contrast pipeline
* Preset ve modality yönetimi
* AI rapor üretimi ve AI chat penceresini açma

### 2) `AIThread (QThread)`

Gemini API çağrısını arka planda çalıştırır:

* `result_ready(str)` sinyali ile sonucu UI’ye iletir
* `error_occurred(str)` sinyali ile hataları UI’ye iletir

### 3) `PatientReportDialog (QDialog)`

Hasta raporu oluşturma:

* Hasta ve görüntü bilgilerini form alanlarında gösterir
* Serbest metin rapor editörü
* 🤖 AI suggestion (demo: `QTimer.singleShot` ile simülasyon)

### 4) `AIChatDialog (QDialog)`

AI chat ekranı:

* İlk mesaj olarak case context basar
* Chat geçmişi + current mesaj ile “full prompt” oluşturur
* Ctrl+Enter ile gönderme
* Pencere boyutu/konumu QSettings ile saklanır

---

## 🪟 UI Akışı

1. **Uygulama açılır** → sample CT datası üretilir → görüntü render edilir
2. Kullanıcı **DICOM/NIfTI yükler** → pixel array + metadata parse edilir
3. Kullanıcı:

   * modality seçer 🩺
   * preset seçer 🔧
   * WC/WW ayarlar 🎚️
   * brightness/contrast ayarlar 🌟
   * 3D ise slice gezer 🧊
4. İsterse:

   * 📝 **Patient Report** oluşturur
   * 📝 **AI Report** üretir
   * 💬 **AI Chat** ile case hakkında konuşur

---

## 🔧 Kurulum

### 1) Sanal ortam (önerilir)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 2) Bağımlılıklar

```bash
pip install pyqt5 numpy matplotlib requests
pip install pydicom nibabel
```

> Not: `pydicom` ve `nibabel` import’u try/except ile kontrol edildiği için opsiyoneldir.
> Ancak DICOM/NIfTI açmak için ilgili paketlerin kurulu olması gerekir.

---

## ▶️ Çalıştırma

```bash
python main.py
```

Uygulama başladığında terminalde:

* `🏥 Starting Enhanced Medical Imaging Viewer...`

---

## 🔑 Gemini API Key

API key’i iki farklı yerden set edebilirsin:

* `AI → Set API Key`
* `File → Preferences → Gemini API Key`

Key **QSettings** ile saklanır:

* `MedicalViewer / EnhancedViewer`

---

## 🧠 Windowing (VOI LUT) Mantığı

Kodda `apply_dicom_windowing()` fonksiyonu:

* `RescaleSlope` ve `RescaleIntercept` ile HU/gerçek değer dönüşümü uygular
* Sonra DICOM standardındaki VOI LUT windowing formülü ile 0–255’e map eder
* Çıktı: `uint8` grayscale

Ardından `apply_brightness_contrast()`:

* kontrastı 128 etrafında uygular
* brightness offset ekler

---

## 🧪 Bilinen Varsayımlar / Notlar

* NIfTI yüklenince modality varsayılan olarak **MRI** atanır.
* 4D NIfTI’da ilk volume alınır.
* AI rapor prompt’u şimdilik **görüntünün kendisini** değil, modality/preset gibi context’i kullanır.

  * (Gerçek analiz için pixel data’yı bir VLM/medikal model pipeline’ına bağlamak gerekir.)

---

## 🗂️ Proje Yapısı Önerisi

```text
project/
  main.py
  README.md
  requirements.txt
```

`requirements.txt` örneği:

```text
PyQt5
numpy
matplotlib
requests
pydicom
nibabel
```

---

## 🛣️ Roadmap (Geliştirme Fikirleri)

* 🧠 Gerçek “image-to-report” akışı (VLM veya medikal model)
* 🧩 Multi-frame DICOM series loading (folder / series picker)
* 📊 Histogram / HU measurement tools
* 🖱️ ROI çizimi + ölçüm (distance/area)
* 🧾 Report export (PDF / DOCX)
* 🔒 PHI/PII redaction + logging

---

## 📜 Lisans

MIT
