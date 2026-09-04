# CLP-1 Kalkulus Diferensial — Bahasa Indonesia

Edisi lengkap Bahasa Indonesia (`id-ID`) yang dipelihara secara independen
dari *CLP-1 Differential Calculus* karya Joel Feldman, Andrew Rechnitzer, dan
Elyse Yeager.

## Baca dan unduh

1. **[Baca buku teks Bahasa Indonesia dalam pembaca layar penuh](https://zenodo.org/records/21938930/preview/00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf)**
   — 442 halaman. [Unduh PDF rilis beku](https://zenodo.org/records/21938930/files/00_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_BUKU_TEKS.pdf?download=1)
   atau [lihat salinan repositori](output/CLP1_Kalkulus_Diferensial_Bahasa_Indonesia_Buku_Teks.pdf).
2. **[Baca buku soal, petunjuk, jawaban, dan penyelesaian dalam pembaca layar penuh](https://zenodo.org/records/21938930/preview/01_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_SOAL_DAN_PENYELESAIAN.pdf)**
   — 646 halaman dengan 695 soal, 620 petunjuk, 695 jawaban, dan 695
   penyelesaian. [Unduh PDF rilis beku](https://zenodo.org/records/21938930/files/01_CLP1_KALKULUS_DIFERENSIAL_BAHASA_INDONESIA_2026.08.14.1_SOAL_DAN_PENYELESAIAN.pdf?download=1)
   atau [lihat salinan repositori](output/CLP1_Kalkulus_Diferensial_Bahasa_Indonesia_Soal_dan_Penyelesaian.pdf).
3. **Kutip edisi:** DOI versi
   [`10.5281/zenodo.21938930`](https://doi.org/10.5281/zenodo.21938930); DOI
   konsep yang selalu menunjuk ke versi Bahasa Indonesia terbaru:
   [`10.5281/zenodo.21938929`](https://doi.org/10.5281/zenodo.21938929).
4. **Audit edisi:** lihat [QA](QA.id-ID.md),
   [keputusan terjemahan](TRANSLATION_DECISIONS.id-ID.md),
   [koreksi sumber](UPSTREAM_SOURCE_CORRECTIONS.id-ID.md), dan
   [manifest byte](provenance/FILE_MANIFEST.id-ID.csv).

## Cakupan dan status

Rilis `2026.08.14.1` mencakup seluruh buku teks dan seluruh buku soal CLP-1.
Sumber LaTeX dapat disunting dan dibangun ulang. Formula, struktur environment,
label, referensi, dan urutan aset dipertahankan kecuali koreksi sumber yang
dicatat. Gambar berteks Inggris yang aktif dilokalkan sebagai aset vektor
terpisah agar aset pembanding upstream tetap utuh.

Kedua pembaca dibangun secara berurutan dengan pdfLaTeX/Latexmk, diekstrak,
diperiksa fontnya, dirender pada 144 dpi, dan diperiksa halaman demi halaman.
Metadata peninjauan tidak menyatakan adanya peer review manusia atau peninjauan
penutur asli; koreksi komunitas setelah rilis diterima sebagai versi baru.

## Sumber, atribusi, dan lisensi

- Repositori sumber: <https://github.com/arechnitzer/CLP1>.
- Commit sumber beku: `9f0295936d395bec68dab7915057135a2c7f0414`.
- Penulis asli: Joel Feldman, Andrew Rechnitzer, dan Elyse Yeager.
- Lisensi: Creative Commons Attribution-NonCommercial-ShareAlike 4.0
  International (CC BY-NC-SA 4.0).

Edisi ini merupakan terjemahan dan adaptasi berbantuan AI yang diproduksi atas
arahan pengguna oleh jalur produksi Interlanguage Bahasa Indonesia. Ini bukan
edisi resmi penulis atau University of British Columbia dan tidak menyiratkan
dukungan mereka.

## Membangun dan memeriksa

Instruksi build lengkap terdapat di [BUILD.id-ID.md](BUILD.id-ID.md). Pemeriksaan
hash, halaman, font tertanam, dan ekstraksi dapat diputar ulang dengan:

```powershell
pwsh -NoProfile -File scripts\verify_release_pdfs.ps1 `
  -TextbookPdf output\CLP1_Kalkulus_Diferensial_Bahasa_Indonesia_Buku_Teks.pdf `
  -ProblembookPdf output\CLP1_Kalkulus_Diferensial_Bahasa_Indonesia_Soal_dan_Penyelesaian.pdf
```

Build buku teks harus mendahului buku soal karena label silang buku soal membaca
file AUX buku teks. Aset `_id` sudah dibekukan; tidak perlu digenerasi ulang.

## Koreksi

Laporkan koreksi melalui issue repositori edisi ini. Versi rilis lama tidak
diubah diam-diam: perubahan berikutnya akan diterbitkan sebagai versi dan DOI
versi baru dengan hash serta provenance tersendiri.
