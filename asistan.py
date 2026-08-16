import os
import time

# Sistemin dışarıyla iletişim kurmasını tamamen engelle (%100 Offline Mod)
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import foundry_local_sdk

class KurumsalAsistan:
    def __init__(self):
        print("🚀 Kurumsal Asistan Başlatılıyor (Foundry Local Modu)...")
        
        # 1. Saf ChromaDB Bağlantısı
        self.db_yolu = "./chroma_db"
        self.embedding_fonksiyonu = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        self.client = chromadb.PersistentClient(
            path=self.db_yolu,
            settings=Settings(anonymized_telemetry=False)
        )
        self.koleksiyon = self.client.get_collection(
            name="it_destek_koleksiyonu",
            embedding_function=self.embedding_fonksiyonu
        )
        
        # 2. MICROSOFT FOUNDRY LOCAL MOTORU (Dinamik Port)
        print("Yerel AI servisi başlatılıyor...")
        ayar = foundry_local_sdk.Configuration(app_name="IT_Asistan")
        self.yonetici = foundry_local_sdk.FoundryLocalManager(ayar)
        self.yonetici.start_web_service()
        
        # Sunucunun toparlanması için bekleme süresi
        time.sleep(3) 
        
        #  Foundry'nin kendi SDK'sını kullanıyoruz
        self.llm_client = foundry_local_sdk.openai.OpenAI()
        self.model_ismi = "phi-1.5-mini" 

    def soru_sor(self, soru: str) -> str:
        try:
            # Saf ChromaDB üzerinden en yakın 6 belgeyi çek
            sonuclar = self.koleksiyon.query(
                query_texts=[soru],
                n_results=6
            )
            
            gelen_metinler = sonuclar.get("documents", [[]])[0]
            
            if not gelen_metinler or len(gelen_metinler) == 0:
                return "Bu konu hakkında kurumsal bilgi bankasında veri bulunmamaktadır."
                
            birlestirilmis_metin = "\n\n---\n\n".join(gelen_metinler)
            
            # Prompt Hazırlığı
            prompt = f"""Sen kurallara sıkı sıkıya bağlı bir Kurumsal Asistansın. Sadece aşağıdaki <belgeler> etiketleri içindeki bilgileri kullanarak yanıt ver. 

<belgeler>
{birlestirilmis_metin}
</belgeler>

KESİN KURALLAR:
1. Cevabına ASLA "Soru:" veya "Cevap:" gibi kelimelerle başlama. Doğrudan çözümü yaz.
2. Eğer sorunun net yanıtı <belgeler> içinde yoksa SADECE şunu yaz: "Bu konu hakkında kurumsal bilgi bankasında veri bulunmamaktadır."
3. Farklı belgeleri birleştirerek zorlama mantık yürütme.
4. Yalnızca Türkçe konuş.

Soru: {soru}
Cevap:"""
            
            # Foundry LLM'e İstek At
            yanit = self.llm_client.chat.completions.create(
                model=self.model_ismi,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            return yanit.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Asistan şu anda işleminizi gerçekleştiremiyor. Hata: {str(e)}"
            
    def kapat(self):
        # Arka plandaki sunucuyu güvenli bir şekilde kapat
        if hasattr(self, 'yonetici') and self.yonetici:
            self.yonetici.stop_web_service()
            print("Yerel Foundry servisi durduruldu.")