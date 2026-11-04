from Main import muat_kb, forward_chaining

kb = muat_kb("Penipuan.json")
RISIKO = "RISIKO TINGGI: hentikan respons"

KASUS = [
    ("1 impersonation",
     ["pesan_tak_diminta", "mengaku_instansi", "desakan_waktu", "minta_otp_pin_password"],
     {"penipuan mengaku pihak lain (impersonation)", RISIKO}),
    ("2 negatif (hanya ada tautan)",
     ["ada_tautan"],
     set()),
    ("3 hadiah + phishing",
     ["pesan_tak_diminta", "kabar_menang_hadiah", "minta_biaya_tambahan", "ada_tautan", "minta_otp_pin_password"],
     {"penipuan hadiah palsu", "phishing (pencurian data login)", RISIKO}),
    ("4 lowongan kerja",
     ["tawaran_kerja_pesan_pribadi", "minta_bayar_di_muka"],
     {"penipuan lowongan kerja", RISIKO}),
    ("5 belanja online",
     ["harga_tak_wajar", "transfer_rekening_pribadi"],
     {"penipuan belanja online", RISIKO}),
    ("6 investasi ilegal",
     ["untung_tinggi_tanpa_risiko", "izin_tak_terbukti"],
     {"penipuan investasi ilegal", RISIKO}),
]

gagal = 0
for nama, fakta, harapan in KASUS:
    memori, _, _ = forward_chaining(kb, fakta)
    hasil = {k for k in kb["kesimpulan"] if k in memori}
    ok = hasil == harapan
    gagal += not ok
    print(("LULUS" if ok else "GAGAL"), nama, "->", sorted(hasil) or "tidak ada")
print("Semua lulus" if not gagal else f"{gagal} gagal")
raise SystemExit(gagal)