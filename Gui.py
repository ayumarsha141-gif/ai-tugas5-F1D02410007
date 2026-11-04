import tkinter as tk
from tkinter import ttk

from Main import muat_kb, fakta_dasar, forward_chaining

KB = muat_kb("Penipuan.json")
RISIKO = "RISIKO TINGGI: hentikan respons"

# Palet
NAVY, BG, PUTIH, INK, ABU, GARIS = "#0F172A", "#EEF2F9", "#FFFFFF", "#1E293B", "#64748B", "#E2E8F0"
BIRU, BIRU_M, BIRU_T = "#2563EB", "#DBEAFE", "#1D4ED8"
MERAH, MERAH_M = "#DC2626", "#FEE2E2"
HIJAU, HIJAU_M = "#16A34A", "#DCFCE7"
ORANYE, ORANYE_M = "#EA580C", "#FFEDD5"
UNGU, UNGU_M = "#7C3AED", "#EDE9FE"
FONT = "Segoe UI"

# Pengelompokan pertanyaan + ikon (hanya tampilan)
GRUP = [
    ("Ciri umum pesan", "💬", BIRU, ["pesan_tak_diminta", "mengaku_instansi", "desakan_waktu",
                                     "ancaman_denda_blokir", "minta_otp_pin_password", "ada_tautan"]),
    ("Hadiah / undian", "🎁", ORANYE, ["kabar_menang_hadiah", "minta_biaya_tambahan"]),
    ("Tawaran kerja", "💼", UNGU, ["tawaran_kerja_pesan_pribadi", "minta_bayar_di_muka"]),
    ("Belanja online", "🛒", HIJAU, ["harga_tak_wajar", "transfer_rekening_pribadi"]),
    ("Investasi", "📈", MERAH, ["untung_tinggi_tanpa_risiko", "izin_tak_terbukti"]),
]

IKON_HASIL = {
    "penipuan mengaku pihak lain (impersonation)": ("🎭", "Mengaku pihak lain", "Pelaku berpura-pura jadi bank/instansi."),
    "penipuan hadiah palsu": ("🎁", "Hadiah palsu", "Hadiah/undian dijadikan umpan biaya atau tautan."),
    "penipuan lowongan kerja": ("💼", "Lowongan kerja palsu", "Kerja fiktif untuk minta uang atau data."),
    "penipuan belanja online": ("🛒", "Belanja online fiktif", "Harga murah, bayar ke rekening pribadi."),
    "penipuan investasi ilegal": ("📈", "Investasi ilegal", "Untung besar tanpa izin resmi."),
    "phishing (pencurian data login)": ("🎣", "Phishing", "Tautan palsu untuk mencuri data login/OTP."),
}

CONTOH = {
    "Contoh 1: Impersonation": ["pesan_tak_diminta", "mengaku_instansi", "desakan_waktu", "minta_otp_pin_password"],
    "Contoh 2: Negatif (tanpa kesimpulan)": ["ada_tautan"],
    "Contoh 3: Hadiah + Phishing": ["pesan_tak_diminta", "kabar_menang_hadiah", "minta_biaya_tambahan",
                                    "ada_tautan", "minta_otp_pin_password"],
}


def rapi(nama):
    return nama.replace("_", " ")


class Scroll(tk.Frame):
    """Frame yang bisa di-scroll."""
    def __init__(self, induk, bg):
        super().__init__(induk, bg=bg)
        self.kanvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.kanvas.yview)
        self.isi = tk.Frame(self.kanvas, bg=bg)
        self.isi.bind("<Configure>", lambda e: self.kanvas.configure(scrollregion=self.kanvas.bbox("all")))
        self.jendela = self.kanvas.create_window((0, 0), window=self.isi, anchor="nw")
        self.kanvas.bind("<Configure>", lambda e: self.kanvas.itemconfigure(self.jendela, width=e.width))
        self.kanvas.configure(yscrollcommand=sb.set)
        self.kanvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        for w in (self.kanvas, self.isi):
            w.bind("<Enter>", self._masuk)
            w.bind("<Leave>", self._keluar)

    def _masuk(self, _):
        self.kanvas.bind_all("<MouseWheel>", lambda e: self.kanvas.yview_scroll(int(-e.delta / 120), "units"))
        self.kanvas.bind_all("<Button-4>", lambda e: self.kanvas.yview_scroll(-1, "units"))
        self.kanvas.bind_all("<Button-5>", lambda e: self.kanvas.yview_scroll(1, "units"))

    def _keluar(self, _):
        self.kanvas.unbind_all("<MouseWheel>")
        self.kanvas.unbind_all("<Button-4>")
        self.kanvas.unbind_all("<Button-5>")

    def kosongkan(self):
        for w in self.isi.winfo_children():
            w.destroy()
        self.kanvas.yview_moveto(0)


def pil(induk, teks, fg, bg, tebal=True, ukuran=9):
    return tk.Label(induk, text=teks, fg=fg, bg=bg, padx=8, pady=1,
                    font=(FONT, ukuran, "bold" if tebal else "normal"))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Pakar Deteksi Penipuan Digital")
        self.geometry("1280x800")
        self.minsize(1040, 640)
        self.configure(bg=BG)
        self.dasar = fakta_dasar(KB)
        self.pilih = {f: False for f in self.dasar}
        self.kartu = {}
        self._gaya()
        self._header()
        badan = tk.Frame(self, bg=BG)
        badan.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        badan.columnconfigure(0, weight=5, uniform="k")
        badan.columnconfigure(1, weight=6, uniform="k")
        badan.rowconfigure(0, weight=1)
        self._kiri(badan)
        self._kanan(badan)
        self._awal()

    # ---------- gaya ----------
    def _gaya(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Aksi.TButton", font=(FONT, 11, "bold"), foreground="white",
                    background=BIRU, padding=(22, 10), borderwidth=0)
        s.map("Aksi.TButton", background=[("active", BIRU_T)])
        s.configure("Sek.TButton", font=(FONT, 10), foreground=INK, background=GARIS,
                    padding=(14, 9), borderwidth=0)
        s.map("Sek.TButton", background=[("active", "#CBD5E1")])
        s.configure("TCombobox", padding=6)

    def _header(self):
        h = tk.Frame(self, bg=NAVY)
        h.pack(fill="x", pady=(0, 16))
        kiri = tk.Frame(h, bg=NAVY)
        kiri.pack(side="left", padx=22, pady=16)
        tk.Label(kiri, text="🛡  Anti-Scam Expert System", bg=NAVY, fg="white",
                 font=(FONT, 20, "bold")).pack(anchor="w")
        tk.Label(kiri, text="Deteksi pesan penipuan digital dengan Forward Chaining  •  sumber aturan: OJK dan FTC",
                 bg=NAVY, fg="#94A3B8", font=(FONT, 10)).pack(anchor="w", pady=(3, 0))
        self.chip = tk.Label(h, text="0 gejala dipilih", bg="#1E293B", fg="#E2E8F0",
                             font=(FONT, 10, "bold"), padx=14, pady=6)
        self.chip.pack(side="right", padx=22)

    # ---------- panel kiri ----------
    def _kiri(self, induk):
        k = tk.Frame(induk, bg=PUTIH, highlightbackground=GARIS, highlightthickness=1)
        k.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(k, text="1  Apa yang Anda temui?", bg=PUTIH, fg=INK, font=(FONT, 14, "bold")
                 ).pack(anchor="w", padx=18, pady=(16, 0))
        tk.Label(k, text="Klik kartu untuk memilih. Hijau/biru = YA, abu-abu = TIDAK.", bg=PUTIH, fg=ABU,
                 font=(FONT, 9)).pack(anchor="w", padx=18, pady=(0, 8))
        sc = Scroll(k, PUTIH)
        sc.pack(fill="both", expand=True, padx=(10, 0))
        for judul, ikon, warna, daftar in GRUP:
            tk.Label(sc.isi, text=f"{ikon}  {judul.upper()}", bg=PUTIH, fg=warna,
                     font=(FONT, 9, "bold")).pack(anchor="w", padx=10, pady=(12, 4))
            for f in daftar:
                if f in self.pilih:
                    self._buat_kartu(sc.isi, f, warna)

        bawah = tk.Frame(k, bg=PUTIH)
        bawah.pack(fill="x", padx=18, pady=(8, 16))
        baris = tk.Frame(bawah, bg=PUTIH)
        baris.pack(fill="x")
        ttk.Button(baris, text="🔍  Analisis", style="Aksi.TButton", command=self.analisis).pack(side="left")
        ttk.Button(baris, text="Reset", style="Sek.TButton", command=self.reset).pack(side="left", padx=8)
        tk.Label(bawah, text="Contoh cepat (isi jawaban otomatis)", bg=PUTIH, fg=ABU,
                 font=(FONT, 9)).pack(anchor="w", pady=(12, 3))
        self.contoh = ttk.Combobox(bawah, values=list(CONTOH), state="readonly", font=(FONT, 10))
        self.contoh.pack(fill="x")
        self.contoh.bind("<<ComboboxSelected>>", self.isi_contoh)

    def _buat_kartu(self, induk, f, warna):
        luar = tk.Frame(induk, bg=GARIS, padx=1, pady=1)
        luar.pack(fill="x", padx=8, pady=3)
        isi = tk.Frame(luar, bg=PUTIH)
        isi.pack(fill="x")
        garis = tk.Frame(isi, bg=GARIS, width=5)
        garis.pack(side="left", fill="y")
        teks = tk.Label(isi, text=KB["fakta"][f], bg=PUTIH, fg=INK, font=(FONT, 10),
                        wraplength=370, justify="left", anchor="w")
        teks.pack(side="left", fill="x", expand=True, padx=12, pady=9)
        badge = tk.Label(isi, text="TIDAK", bg="#F1F5F9", fg=ABU, font=(FONT, 8, "bold"), width=6, pady=3)
        badge.pack(side="right", padx=10)
        self.kartu[f] = (luar, isi, garis, teks, badge, warna)
        for w in (luar, isi, garis, teks, badge):
            w.bind("<Button-1>", lambda e, x=f: self.toggle(x))
            w.configure(cursor="hand2")

    def _warnai(self, f):
        luar, isi, garis, teks, badge, warna = self.kartu[f]
        ya = self.pilih[f]
        bg = {BIRU: BIRU_M, ORANYE: ORANYE_M, UNGU: UNGU_M, HIJAU: HIJAU_M, MERAH: MERAH_M}[warna] if ya else PUTIH
        luar.configure(bg=warna if ya else GARIS)
        for w in (isi, teks):
            w.configure(bg=bg)
        garis.configure(bg=warna if ya else GARIS)
        badge.configure(text="YA" if ya else "TIDAK", bg=warna if ya else "#F1F5F9",
                        fg="white" if ya else ABU)
        self.chip.configure(text=f"{sum(self.pilih.values())} gejala dipilih")

    def toggle(self, f):
        self.pilih[f] = not self.pilih[f]
        self._warnai(f)

    # ---------- panel kanan ----------
    def _kanan(self, induk):
        k = tk.Frame(induk, bg=PUTIH, highlightbackground=GARIS, highlightthickness=1)
        k.grid(row=0, column=1, sticky="nsew")
        tk.Label(k, text="2  Hasil analisis", bg=PUTIH, fg=INK, font=(FONT, 14, "bold")
                 ).pack(anchor="w", padx=18, pady=(16, 8))
        self.sc = Scroll(k, PUTIH)
        self.sc.pack(fill="both", expand=True, padx=(10, 0), pady=(0, 10))

    def _awal(self):
        self.sc.kosongkan()
        tk.Label(self.sc.isi, text="🔎", bg=PUTIH, font=(FONT, 40)).pack(pady=(110, 0))
        tk.Label(self.sc.isi, text="Belum ada analisis", bg=PUTIH, fg=INK, font=(FONT, 14, "bold")).pack()
        tk.Label(self.sc.isi, text="Pilih gejala di kiri lalu tekan Analisis,\natau coba Contoh cepat.",
                 bg=PUTIH, fg=ABU, font=(FONT, 10), justify="center").pack(pady=6)

    # ---------- aksi ----------
    def reset(self):
        for f in self.pilih:
            self.pilih[f] = False
            self._warnai(f)
        self.contoh.set("")
        self._awal()

    def isi_contoh(self, _=None):
        pilihan = CONTOH[self.contoh.get()]
        for f in self.pilih:
            self.pilih[f] = f in pilihan
            self._warnai(f)
        self.analisis()

    # ---------- komponen hasil ----------
    def _kotak(self, warna_garis=GARIS, bg=PUTIH):
        luar = tk.Frame(self.sc.isi, bg=warna_garis, padx=1, pady=1)
        luar.pack(fill="x", padx=12, pady=(0, 10))
        dalam = tk.Frame(luar, bg=bg)
        dalam.pack(fill="x")
        return dalam

    def _judul(self, teks):
        tk.Label(self.sc.isi, text=teks, bg=PUTIH, fg=INK, font=(FONT, 11, "bold")
                 ).pack(anchor="w", padx=14, pady=(8, 6))

    def _pohon(self, induk, fakta, asal, memori, tingkat=0):
        r = asal.get(fakta)
        baris = tk.Frame(induk, bg=PUTIH)
        baris.pack(fill="x", padx=(10 + tingkat * 22, 8), pady=2, anchor="w")
        if r is None:
            tk.Label(baris, text=f"•  {rapi(fakta)}", bg=PUTIH, fg=ABU, font=(FONT, 9)).pack(side="left")
            return
        pil(baris, r["id"], "white", BIRU).pack(side="left")
        tk.Label(baris, text=fakta, bg=PUTIH, fg=INK, font=(FONT, 10, "bold"),
                 wraplength=420, justify="left").pack(side="left", padx=8)
        for s in r["sumber"]:
            pil(baris, s, UNGU, UNGU_M, ukuran=8).pack(side="left", padx=1)
        for premis in [p for p in r["jika"] if p in memori]:
            self._pohon(induk, premis, asal, memori, tingkat + 1)

    def _hampir(self, memori):
        """Aturan 'dan' yang baru sebagian terpenuhi (untuk menjelaskan kasus tanpa kesimpulan)."""
        hasil = []
        for r in KB["aturan"]:
            if r["maka"] in memori or r["mode"] != "dan" or len(r["jika"]) < 2:
                continue
            ada = [p for p in r["jika"] if p in memori]
            kurang = [p for p in r["jika"] if p not in memori]
            if ada and kurang:
                hasil.append((r, ada, kurang))
        return hasil

    # ---------- analisis ----------
    def analisis(self):
        awal = [f for f in self.dasar if self.pilih[f]]
        memori, asal, log = forward_chaining(KB, awal)
        hasil = [k for k in KB["kesimpulan"] if k in memori]
        jenis = [k for k in hasil if k != RISIKO]
        self.sc.kosongkan()

        # Banner
        if RISIKO in hasil:
            b = self._kotak(MERAH, MERAH_M)
            tk.Label(b, text="⚠", bg=MERAH_M, fg=MERAH, font=(FONT, 30)).pack(side="left", padx=(16, 8), pady=12)
            t = tk.Frame(b, bg=MERAH_M)
            t.pack(side="left", pady=12)
            tk.Label(t, text="RISIKO TINGGI", bg=MERAH_M, fg=MERAH, font=(FONT, 17, "bold")).pack(anchor="w")
            tk.Label(t, text="Hentikan respons: jangan klik, jangan transfer, jangan bagikan OTP.",
                     bg=MERAH_M, fg="#7F1D1D", font=(FONT, 10), wraplength=430, justify="left").pack(anchor="w")
        else:
            b = self._kotak(BIRU, BIRU_M)
            tk.Label(b, text="ℹ", bg=BIRU_M, fg=BIRU, font=(FONT, 30)).pack(side="left", padx=(16, 8), pady=12)
            t = tk.Frame(b, bg=BIRU_M)
            t.pack(side="left", pady=12)
            tk.Label(t, text="Tidak ada kesimpulan", bg=BIRU_M, fg=BIRU, font=(FONT, 17, "bold")).pack(anchor="w")
            tk.Label(t, text="Belum ada pola penipuan yang terpenuhi. Ini BUKAN jaminan pesan aman.",
                     bg=BIRU_M, fg="#1E3A8A", font=(FONT, 10), wraplength=430, justify="left").pack(anchor="w")

        # Jenis penipuan
        if jenis:
            self._judul("Jenis penipuan terdeteksi")
            for k in jenis:
                ikon, nama, ket = IKON_HASIL[k]
                c = self._kotak(ORANYE, ORANYE_M)
                tk.Label(c, text=ikon, bg=ORANYE_M, font=(FONT, 20)).pack(side="left", padx=(14, 8), pady=8)
                t = tk.Frame(c, bg=ORANYE_M)
                t.pack(side="left", pady=8)
                tk.Label(t, text=nama, bg=ORANYE_M, fg="#9A3412", font=(FONT, 12, "bold")).pack(anchor="w")
                tk.Label(t, text=ket, bg=ORANYE_M, fg="#7C2D12", font=(FONT, 9)).pack(anchor="w")

        # Penjelasan kasus tanpa kesimpulan
        if not hasil:
            self._judul("Kenapa tidak ada kesimpulan?")
            c = self._kotak()
            if not awal:
                tk.Label(c, text="Belum ada gejala yang dipilih.", bg=PUTIH, fg=ABU, font=(FONT, 10)
                         ).pack(anchor="w", padx=14, pady=10)
            else:
                tk.Label(c, text="Gejala yang Anda pilih belum memenuhi syarat satu pun aturan. "
                                 "Beberapa aturan baru sebagian terpenuhi:",
                         bg=PUTIH, fg=INK, font=(FONT, 10), wraplength=520, justify="left"
                         ).pack(anchor="w", padx=14, pady=(10, 4))
                for r, ada, kurang in self._hampir(memori):
                    row = tk.Frame(c, bg=PUTIH)
                    row.pack(fill="x", padx=14, pady=3, anchor="w")
                    pil(row, r["id"], "white", BIRU).pack(side="left")
                    tk.Label(row, text=f"sudah ada: {', '.join(rapi(a) for a in ada)}   |   masih kurang: "
                                       f"{', '.join(rapi(x) for x in kurang)}",
                             bg=PUTIH, fg=INK, font=(FONT, 9), wraplength=470, justify="left").pack(side="left", padx=8)
                tk.Frame(c, bg=PUTIH, height=8).pack()

        # Alasan
        if jenis:
            self._judul("Alasan: aturan mana yang dipakai")
            c = self._kotak()
            for k in jenis:
                self._pohon(c, k, asal, memori)
                tk.Frame(c, bg=GARIS, height=1).pack(fill="x", padx=10, pady=6)
            if RISIKO in hasil:
                r = asal[RISIKO]
                row = tk.Frame(c, bg=PUTIH)
                row.pack(fill="x", padx=10, pady=(0, 8), anchor="w")
                pil(row, r["id"], "white", MERAH).pack(side="left")
                tk.Label(row, text="RISIKO TINGGI  ←  " + ", ".join(
                    IKON_HASIL[p][1] for p in r["jika"] if p in memori),
                    bg=PUTIH, fg=INK, font=(FONT, 10, "bold"), wraplength=440, justify="left"
                ).pack(side="left", padx=8)

        # Saran
        if RISIKO in hasil:
            self._judul("Saran tindakan")
            c = self._kotak(HIJAU, HIJAU_M)
            for s in KB["tindakan"][RISIKO]:
                tk.Label(c, text="✔  " + s, bg=HIJAU_M, fg="#14532D", font=(FONT, 10),
                         wraplength=520, justify="left").pack(anchor="w", padx=14, pady=4)

        # Proses FC
        self._judul("Proses Forward Chaining")
        c = self._kotak()
        tk.Label(c, text="Fakta awal:  " + (", ".join(rapi(a) for a in awal) if awal else "(tidak ada)"),
                 bg=PUTIH, fg=ABU, font=(FONT, 9), wraplength=520, justify="left"
                 ).pack(anchor="w", padx=14, pady=(10, 6))
        for i, baris in enumerate(log, 1):
            row = tk.Frame(c, bg=PUTIH)
            row.pack(fill="x", padx=14, pady=3, anchor="w")
            akhir = "berhenti" in baris
            tk.Label(row, text=str(i), bg=ABU if akhir else BIRU, fg="white", width=3,
                     font=(FONT, 9, "bold")).pack(side="left")
            if akhir:
                tk.Label(row, text="Tidak ada aturan baru, berhenti", bg=PUTIH, fg=ABU,
                         font=(FONT, 10, "italic")).pack(side="left", padx=10)
            else:
                rid, hasil_r = baris.split(": ", 1)[1].split(" -> ")
                pil(row, rid, "white", BIRU).pack(side="left", padx=(10, 0))
                tk.Label(row, text="→  " + hasil_r, bg=PUTIH, fg=INK, font=(FONT, 10),
                         wraplength=430, justify="left").pack(side="left", padx=8)
        tk.Frame(c, bg=PUTIH, height=8).pack()

        # Batas
        self._judul("Batas keberlakuan")
        c = self._kotak(GARIS, "#F8FAFC")
        tk.Label(c, text=KB["batas"], bg="#F8FAFC", fg=ABU, font=(FONT, 9, "italic"),
                 wraplength=530, justify="left").pack(anchor="w", padx=14, pady=10)


if __name__ == "__main__":
    App().mainloop()