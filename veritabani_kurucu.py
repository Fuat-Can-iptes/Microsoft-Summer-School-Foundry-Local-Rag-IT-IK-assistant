import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ITBilgiBankasi:
    def __init__(self):
        # 1. AYARLAR VE VERİTABANI BAĞLANTISI
        self.kok_klasor = "dokumanlar" 
        self.db_yolu = "./chroma_db"
        
        print("🔄 ChromaDB başlatılıyor ve Çok Dilli Model yükleniyor...")
        self.embedding_fonksiyonu = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        self.client = chromadb.PersistentClient(path=self.db_yolu)
        
        try:
            self.client.delete_collection(name="it_destek_koleksiyonu")
        except:
            pass
            
        self.koleksiyon = self.client.create_collection(
            name="it_destek_koleksiyonu",
            embedding_function=self.embedding_fonksiyonu
        )

        # 2. METİN PARÇALAYICI (GENİŞLETİLMİŞ CHUNK SİSTEMİ)
        # Buralar başlık ve içerik kopmasın diye büyütüldü!
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", " "]
        )

    def belgeleri_isleye_ve_kaydet(self):
        print("🔄 IT ve İK Dokümanları taranıyor...\n")
        islenen_dosya_sayisi = 0
        toplam_parca_sayisi = 0

        hedef_yol = os.path.abspath(self.kok_klasor)
        print(f"Hedef Klasör: {hedef_yol}")

        for mevcut_klasor, _, dosyalar in os.walk(hedef_yol):
            for dosya in dosyalar:
                if not dosya.endswith(".txt"):
                    continue

                dosya_yolu = os.path.join(mevcut_klasor, dosya)
                
                # Yol parçalarını güvenli bir şekilde ayıkla
                goreli_yol = os.path.relpath(dosya_yolu, hedef_yol)
                yol_parcalari = goreli_yol.replace("\\", "/").split("/")
                
                departman = yol_parcalari[0] if len(yol_parcalari) > 1 else "genel"
                kategori = yol_parcalari[1] if len(yol_parcalari) > 2 else "genel"

                with open(dosya_yolu, "r", encoding="utf-8") as f:
                    metin = f.read().strip()

                if not metin:
                    print(f"⚠️ DİKKAT: {dosya} dosyası BOŞ!")
                    continue

                # Metni parçalara böl
                parcalar = self.text_splitter.split_text(metin)
                
                for index, parca in enumerate(parcalar):
                    # Benzersiz ve detaylı ID yapısı
                    dokuman_id = f"{departman}_{kategori}_{dosya}_part_{index}"
                    
                    self.koleksiyon.add(
                        documents=[parca],
                        metadatas=[{"departman": departman, "kategori": kategori, "dosya_adi": dosya}],
                        ids=[dokuman_id]
                    )
                    toplam_parca_sayisi += 1
                
                print(f"✅ İşlendi: {dosya} ({len(parcalar)} parça) | Departman: {departman} | Kategori: {kategori}")
                islenen_dosya_sayisi += 1

        print(f"\n🎉 İşlem Tamam! {islenen_dosya_sayisi} belge, toplam {toplam_parca_sayisi} vektör parçasına ayrılarak veritabanına işlendi.")

# --- ANA ÇALIŞTIRMA BLOĞU ---
if __name__ == "__main__":
    bilgi_bankasi = ITBilgiBankasi()
    bilgi_bankasi.belgeleri_isleye_ve_kaydet()