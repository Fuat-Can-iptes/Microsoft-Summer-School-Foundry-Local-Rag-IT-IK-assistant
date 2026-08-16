# 🏢 Microsoft Summer School - Foundry Local RAG IT/İK Asistanı

Bu proje, **Microsoft Foundry Yaz Okulu** programı kapsamında geliştirilmiştir. Kurum içi IT (Bilgi İşlem) ve İK (İnsan Kaynakları) departmanlarına ait dokümanları okuyarak çalışanların sorularına yanıt veren, **%100 çevrimdışı (offline)** çalışan ve veri gizliliğini temel alan bir **RAG (Retrieval-Augmented Generation)** masaüstü uygulamasıdır.

---

## ✨ Temel Özellikler

* **🔒 %100 Çevrimdışı (Air-Gapped) Güvenlik:** Kurumsal verilerin dışarı sızmasını engellemek amacıyla uygulamanın internet erişimi `os.environ` değişkenleri ile tamamen kapatılmıştır. Sistem uçtan uca yerelde çalışır.
* **🧠 Microsoft Foundry Local Entegrasyonu:** LLM motoru olarak Microsoft Foundry Local (dinamik port mimarisiyle) kullanılmıştır.
* **📚 RAG (Retrieval-Augmented Generation):** Kurum belgeleri parçalanıp vektörel olarak **ChromaDB**'ye kaydedilir. Sorulara sadece bu veritabanından çekilen bağlam (context) ile yanıt verilir.
* **🛡️ Halüsinasyon Kontrolü:** Modelin uydurma (hallucination) yapmasını engellemek için üç katmanlı bir yapı kurulmuştur:

  1. ChromaDB alakalı belge bulamazsa işlem erken kesilir (**Early Stopping**).
  2. Kısıtlayıcı **Prompt Mühendisliği** uygulanmıştır.
  3. LLM `temperature` değeri `0.1` olarak ayarlanarak deterministik sonuçlar elde edilmiştir.
* **⚡ Asenkron Masaüstü Arayüzü:** **CustomTkinter** ile tasarlanan arayüz, LLM API istekleri sırasında kilitlenmeleri önlemek için **Threading (İş Parçacıkları)** kullanılarak asenkron hale getirilmiştir.

---

## 🏗️ Proje Mimarisi ve Dosya Yapısı

* 📄 **`veritabani_kurucu.py`**: `Dokumanlar` klasöründeki `.txt` dosyalarını okur, chunk'lara (parçalara) ayırır ve `paraphrase-multilingual-MiniLM-L12-v2` modeli ile ChromaDB vektör veritabanını oluşturur.
* 📄 **`asistan.py`**: RAG mimarisinin kalbidir. Vektör aramasını (Retrieval) yapar, Foundry sunucusunu ayağa kaldırır ve Prompt'u hazırlayarak LLM'den yanıt alır.
* 📄 **`masaustu_arayuz.py`**: Kullanıcı deneyimini (UI) yönetir. CustomTkinter ile tasarlanmıştır ve Threading mimarisini barındırır.
* 📁 **`Dokumanlar/`**: Kurum içi bilgi bankasını oluşturan ham metin (`.txt`) dosyalarının bulunduğu dizindir.
* 📄 **`.gitignore`**: Büyük boyutlu vektör veritabanını (`chroma_db`) ve önbellek dosyalarını GitHub reposundan uzak tutar.

> **Not:** Veri gizliliği ve mimari standartlar gereği `chroma_db` (Vektör Veritabanı) klasörü bilerek GitHub'a yüklenmemiştir. Projeyi inceleyen kişinin veritabanını kendi bilgisayarında aşağıda belirtilen şekilde oluşturması gerekmektedir.

---

## 🚀 Adım Adım Kurulum ve Çalıştırma Rehberi (Yeni Başlayanlar İçin)

Projeyi kendi bilgisayarınızda (Localhost) hatasız bir şekilde çalıştırmak için lütfen hiçbir adımı atlamadan sırasıyla uygulayınız.

### Ön Koşullar (Bilgisayarınızda Olması Gerekenler)

1. **Python Kurulumu:** Bilgisayarınızda Python (3.8 veya üzeri) kurulu olmalıdır. Kurulu değilse [python.org](https://www.python.org/downloads/) adresinden indirebilirsiniz.

   > Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretlemeyi unutmayın!

2. **Microsoft Foundry Local:** Sisteminizde Microsoft Foundry Local yazılımının kurulu ve çalışmaya hazır olduğundan emin olun.

---

### Adım 1: Projeyi İndirin ve VS Code'da Açın

Bu projeyi yeşil renkli **Code** butonuna basarak ZIP olarak indirebilir veya terminal üzerinden klonlayabilirsiniz:

```bash
git clone https://github.com/kullanici-adiniz/repository-isminiz.git
```

İndirdiğiniz klasörü **Visual Studio Code (VS Code)** ile açın.

VS Code üst menüsünden:

**Terminal → New Terminal**

yolunu izleyerek alt kısımdaki komut satırını açın.

Alternatif olarak:

```text
Ctrl + `
```

kısayolunu da kullanabilirsiniz.

---

### Adım 2: Sanal Ortam (Virtual Environment) Oluşturun

Proje kütüphanelerinin bilgisayarınızdaki diğer projelerle çakışmaması için izole bir ortam kurmalıyız.

#### Windows için

```bash
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux için

```bash
python3 -m venv venv
source venv/bin/activate
```

Başarılı olursa terminal satırının başında:

```text
(venv)
```

yazısını göreceksiniz.

---

### Adım 3: Gerekli Kütüphaneleri Yükleyin

Sanal ortamınız aktifken (başında `venv` yazıyorken), projenin ihtiyaç duyduğu tüm paketleri tek seferde kurmak için şu komutu çalıştırın:

```bash
pip install chromadb customtkinter langchain-text-splitters sentence-transformers openai
```

Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir. Paketlerin yüklenmesinin tamamlanmasını bekleyin.

---

### Adım 4: Veritabanını İnşa Edin (Kritik Adım)

Güvenlik ve dosya boyutu nedeniyle vektör veritabanı (`chroma_db`) projeye dahil edilmemiştir.

Kendi bilgisayarınızda bu veritabanını sıfırdan oluşturmak için aşağıdaki komutu çalıştırın:

```bash
python veritabani_kurucu.py
```

Ekranda **"İşlem Tamam!"** mesajını görene kadar bekleyin.

Bu işlem:

* `Dokumanlar` klasöründeki metinleri okur.
* Metinleri chunk'lara ayırır.
* Embedding işlemini gerçekleştirir.
* ChromaDB vektör veritabanını oluşturur.

İşlem tamamlandığında proje klasörünün içerisinde `chroma_db` klasörü oluşacaktır.

---

### Adım 5: Uygulamayı Başlatın

Bu adımla beraber  tüm altyapı hazır.

Arka planda Foundry Local sunucusunu tetikleyecek ve görsel arayüzü açacak olan şu komutu çalıştırın:

```bash
python masaustu_arayuz.py
```

Açılan pencereden asistanla **çevrimdışı ve güvenli bir şekilde** sohbet etmeye başlayabilirsiniz.

---

## 📌 Proje Notu

Bu proje **Microsoft Foundry Yaz Okulu** çalışmaları kapsamında geliştirilmiştir.

Amacı, kurumsal IT ve İK dokümanlarına dayalı olarak çalışanların sorularını **yerel LLM + RAG mimarisi** kullanarak güvenli şekilde yanıtlayabilen bir masaüstü asistanı geliştirmektir.
