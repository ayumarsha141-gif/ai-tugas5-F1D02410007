import argparse
import json
import sys

def muat_kb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def syarat_terpenuhi(aturan, memori):
    ada = [s in memori for s in aturan["jika"]]
    return all(ada) if aturan["mode"] == "dan" else any(ada)


def fakta_dasar(kb):
    """Fakta yang tidak pernah menjadi hasil aturan -> ditanyakan ke user."""
    hasil = {r["maka"] for r in kb["aturan"]}
    return [f for f in kb["fakta"] if f not in hasil]


def tanya_user(kb):
    print(kb["judul"])
    print("Jawab y/t.")
    jawaban = []
    for i, f in enumerate(fakta_dasar(kb), 1):
        j = ""
        while j not in ("y", "t"):
            j = input(f"{i}. {kb['fakta'][f]} (y/t) > ").strip().lower()
        if j == "y":
            jawaban.append(f)
    return jawaban


def forward_chaining(kb, fakta_awal):
    memori = list(fakta_awal)          # list agar urutan tetap
    asal = {}                          # hasil -> aturan penghasilnya
    log = []
    siklus = 0
    while True:
        cocok = [r for r in kb["aturan"]
                 if r["maka"] not in memori and syarat_terpenuhi(r, memori)]
        if not cocok:
            siklus += 1
            log.append(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break
        r = cocok[0]
        siklus += 1
        memori.append(r["maka"])
        asal[r["maka"]] = r
        log.append(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
    return memori, asal, log


def alasan(fakta, asal, memori, kb, tingkat=0):
    """Telusuri mundur: fakta ini berasal dari aturan mana."""
    r = asal.get(fakta)
    if r is None:
        return []
    pakai = [s for s in r["jika"] if s in memori]
    nama = [kb["fakta"].get(s, s) if s in kb["fakta"] else s for s in pakai]
    baris = ["  " * tingkat + f"{fakta}  <- {r['id']} ({'; '.join(pakai)}) [sumber: {', '.join(r['sumber'])}]"]
    for s in pakai:
        baris += alasan(s, asal, memori, kb, tingkat + 1)
    return baris


def jalankan(kb, fakta_awal):
    memori, asal, log = forward_chaining(kb, fakta_awal)
    print()
    print("Fakta awal:", ", ".join(fakta_awal) if fakta_awal else "(tidak ada)")
    print()
    print("\n".join(log))
    print()
    hasil = [k for k in kb["kesimpulan"] if k in memori]
    if not hasil:
        print("Kesimpulan: tidak ada kesimpulan dari aturan yang tersedia")
        print("Catatan: ini bukan jaminan pesan aman. Tetap verifikasi ke pihak resmi.")
    else:
        print("Kesimpulan:")
        for k in hasil:
            print(f"  - {k}")
        print("Alasan:")
        for k in hasil:
            print("\n".join("  " + b for b in alasan(k, asal, memori, kb)))
        for k in hasil:
            if k in kb.get("tindakan", {}):
                print("Saran tindakan:")
                for t in kb["tindakan"][k]:
                    print(f"  * {t}")
    print()
    print("Catatan:", kb["batas"])
    return hasil


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", default="Penipuan.json")
    ap.add_argument("--ya", help="fakta 'ya' dipisah koma (tanpa tanya jawab, untuk uji otomatis)")
    a = ap.parse_args()
    kb = muat_kb(a.kb)
    if a.ya is not None:
        awal = [x.strip() for x in a.ya.split(",") if x.strip()]
        valid = set(fakta_dasar(kb))
        salah = [x for x in awal if x not in valid]
        if salah:
            sys.exit(f"Fakta tidak dikenal: {salah}")
    else:
        awal = tanya_user(kb)
    jalankan(kb, awal)


if __name__ == "__main__":
    main()