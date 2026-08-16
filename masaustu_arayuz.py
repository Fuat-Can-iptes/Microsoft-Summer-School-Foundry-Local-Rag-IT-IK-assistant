import customtkinter as ctk
from asistan import KurumsalAsistan
import threading

# Temel Görünüm Ayarları - Daha modern bir karanlık tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AsistanArayuzu(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Pencere Ayarları
        self.title("Kurumsal Destek Asistanı")
        self.geometry("1050x700")
        self.minsize(850, 600)
        
        # Arka Planda RAG Motorunu Başlat
        self.asistan = KurumsalAsistan()

        # Ekranı iki sütuna böl (0: Sidebar, 1: Ana Ekran)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. SOL PANEL (SIDEBAR) TASARIMI
        # ==========================================
        # Sidebar arka planını biraz daha koyu yaparak kontrast yarattık
        self.sidebar_cerceve = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#1a1a1c")
        self.sidebar_cerceve.grid(row=0, column=0, sticky="nsew")
        self.sidebar_cerceve.grid_rowconfigure(9, weight=1) 

        # Başlık - Logosuz, Göze Çarpan Tipografi
        self.baslik_label = ctk.CTkLabel(
            self.sidebar_cerceve, 
            text="Kurumsal Destek\nAsistanı", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#3ea6ff", # Dikkat çekici bir kurumsal mavi tonu
            justify="left"
        )
        self.baslik_label.grid(row=1, column=0, padx=20, pady=(40, 30), sticky="w")

        # Sık Sorulan Sorular Başlığı
        self.sss_baslik = ctk.CTkLabel(
            self.sidebar_cerceve, 
            text="SIK SORULAN SORULAR", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            text_color="#7a7a7a"
        )
        self.sss_baslik.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # SSS Soruları Listesi
        self.sorular = [
            "Bilgi Güvenliği, Şifreleme ve Antivirüs Prosedürleri nelerdir?",
            "İsteğe Bağlı ve Departman Bazlı Yazılımların Kurulumunu nasıl yapabilirim?",
            "Şirket içi davranış kuralları nelerdir?",
            "VPN Bağlı Ancak Şirket Uygulamalarına Erişilemiyor, ne yapmalıyım?",
            "3 yıldır bu şirkette çalışıyorum. Yıllık izin hakkım kaç gündür?",
            "Yazıcı Ağda Görünmüyor ve Çevrimdışı (Offline) ne yapmam gerek ?"
        ]

        # SSS Butonlarını Döngüyle Oluştur
        for i, soru in enumerate(self.sorular):
            gorunen_metin = soru[:36] + "..." if len(soru) > 36 else soru
            
            btn = ctk.CTkButton(
                self.sidebar_cerceve, 
                text=f"• {gorunen_metin}", 
                anchor="w", 
                fg_color="transparent", 
                hover_color="#2d2d30", # Üzerine gelince hoş bir gri
                text_color="#d1d1d1",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                command=lambda s=soru: self.mesaj_gonder(hazir_soru=s)
            )
            btn.grid(row=3+i, column=0, padx=15, pady=2, sticky="ew")

        # ==========================================
        # 2. SAĞ PANEL (SOHBET EKRANI) TASARIMI
        # ==========================================
        self.ana_cerceve = ctk.CTkFrame(self, fg_color="transparent")
        self.ana_cerceve.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Sohbet Ekranı (Daha geniş font, satır aralıkları düzenli)
        self.sohbet_gecmisi = ctk.CTkTextbox(self.ana_cerceve, font=ctk.CTkFont(family="Segoe UI", size=15), wrap="word", fg_color="#232326")
        self.sohbet_gecmisi.pack(pady=(0, 10), padx=0, fill="both", expand=True)
        
        # Renk Etiketleri (Kullanıcı ve Asistanı Ayırmak İçin Kritik Kısım)
        self.sohbet_gecmisi.tag_config("kullanici_isim", foreground="#3ea6ff")
        self.sohbet_gecmisi.tag_config("asistan_isim", foreground="#2ebd59")
        self.sohbet_gecmisi.tag_config("sistem", foreground="#888888")
        
        self.sohbet_gecmisi.insert("0.0", "👋 Merhaba, ben Kurumsal Destek Asistanı. Soldaki sık sorulan sorulardan birini seçebilir veya sorunuzu aşağıya yazabilirsiniz.\n\n", "sistem")
        self.sohbet_gecmisi.configure(state="disabled")
        
        # Durum Bilgisi (Asistan yanıt yazıyor...)
        self.durum_label = ctk.CTkLabel(self.ana_cerceve, text="", font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"), text_color="#aaaaaa")
        self.durum_label.pack(anchor="w", padx=5)

        # Alt Giriş Alanı Çerçevesi
        self.alt_cerceve = ctk.CTkFrame(self.ana_cerceve, fg_color="transparent")
        self.alt_cerceve.pack(fill="x", pady=(5, 0))

        self.mesaj_girisi = ctk.CTkEntry(self.alt_cerceve, placeholder_text="Sorunuzu buraya yazın...", height=50, font=ctk.CTkFont(family="Segoe UI", size=15))
        self.mesaj_girisi.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.mesaj_girisi.bind("<Return>", lambda event: self.mesaj_gonder())
        
        self.gonder_butonu = ctk.CTkButton(self.alt_cerceve, text="Gönder", width=110, height=50, font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), command=self.mesaj_gonder)
        self.gonder_butonu.pack(side="right")

    # ==========================================
    # 3. İŞLEM FONKSİYONLARI
    # ==========================================
    def mesaj_gonder(self, hazir_soru=None):
        kullanici_sorusu = hazir_soru if hazir_soru else self.mesaj_girisi.get()
        
        if not kullanici_sorusu.strip():
            return
            
        # Kullanıcı mesajını ekrana bas (Mavi renkli başlık ile)
        self.sohbet_ekle("kullanici", kullanici_sorusu)
        self.mesaj_girisi.delete(0, "end")
        
        # Arayüzü dondurmamak için arama işlemini Thread ile başlat
        self.durum_label.configure(text="Asistan belgeleri tarıyor ve yanıt üretiyor...")
        self.mesaj_girisi.configure(state="disabled") # Çift gönderimi engelle
        self.gonder_butonu.configure(state="disabled")
        
        threading.Thread(target=self.yanit_al, args=(kullanici_sorusu,)).start()

    def yanit_al(self, soru):
        # RAG Motorundan cevabı al
        cevap = self.asistan.soru_sor(soru)
        
        # Asistan mesajını ekrana bas (Yeşil renkli başlık ile)
        self.sohbet_ekle("asistan", cevap)
        
        # Durum çubuğunu temizle ve giriş alanlarını tekrar aç
        self.durum_label.configure(text="")
        self.mesaj_girisi.configure(state="normal")
        self.gonder_butonu.configure(state="normal")

    def sohbet_ekle(self, gonderen, metin):
        self.sohbet_gecmisi.configure(state="normal")
        
        if gonderen == "kullanici":
            self.sohbet_gecmisi.insert("end", "👤 Siz:\n", "kullanici_isim")
            self.sohbet_gecmisi.insert("end", metin + "\n\n")
        elif gonderen == "asistan":
            self.sohbet_gecmisi.insert("end", "🤖 Asistan:\n", "asistan_isim")
            self.sohbet_gecmisi.insert("end", metin + "\n\n")
            
        self.sohbet_gecmisi.see("end")
        self.sohbet_gecmisi.configure(state="disabled")

if __name__ == "__main__":
    uygulama = AsistanArayuzu()
    uygulama.mainloop()