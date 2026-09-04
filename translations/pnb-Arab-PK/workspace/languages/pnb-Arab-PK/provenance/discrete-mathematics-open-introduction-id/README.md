# Matematika Diskret: Sebuah Pengantar Terbuka — Edisi Keempat, Bahasa Indonesia

Edisi Bahasa Indonesia lengkap dan independen dari *Discrete Mathematics: An
Open Introduction*, edisi keempat, karya Oscar Levin. Edisi ini bukan terbitan
resmi Oscar Levin atau University of Northern Colorado dan tidak menyiratkan
dukungan mereka.

Provenans terjemahan: **OpenAI Codex gpt-5.6-sol, Ultra.**

- Pembaca HTML interaktif: <https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/>
- PDF, sumber rilis, dan provenance: <https://doi.org/10.5281/zenodo.21973438>
- Sumber Inggris yang dibekukan: <https://github.com/oscarlevin/discrete-book/tree/82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799>

Pembaca mencakup seluruh buku: tujuh bab, latihan, petunjuk dan penyelesaian
terpilih, diagram, kode Python dan Sage, GeoGebra, serta 243 latihan WeBWorK.
HTML adalah permukaan aksesibilitas utama dan memuat antarmuka interaktif
Bahasa Indonesia. PDF berjumlah 613 halaman dan tidak memiliki struktur tag
PDF; pembaca yang memerlukan teknologi bantu sebaiknya menggunakan HTML.

## Lisensi

Teks buku dan terjemahannya tersedia di bawah CC BY-NC-SA 4.0. Berkas soal
yang berasal dari WeBWorK Open Problem Library mempertahankan lisensi
komponennya, umumnya CC BY-NC-SA 3.0 kecuali dinyatakan lain. Lihat
[LICENSE](LICENSE) dan [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Membangun dari sumber

Sumber utama ditulis dalam PreTeXt. Lingkungan yang diterima memakai
PreTeXt 2.27.0, sebagaimana dipatok di `requirements.txt`.

```powershell
python -m pip install -r requirements.txt
pretext build print
pretext build web4
python scripts/finalize_html_id.py output/web4 --apply
python scripts/finalize_html_id.py output/web4
python scripts/qa_html_reader_id.py output/web4
```

Representasi WeBWorK dan aset LaTeX yang telah dibekukan disertakan agar hasil
yang diterbitkan dapat direproduksi tanpa mengandalkan perubahan layanan luar.
Layanan penskoran atau komputasi eksternal tetap bergantung pada ketersediaan
penyedia masing-masing.

## Melaporkan masalah

Gunakan *Issues* repositori ini untuk masalah khusus edisi Bahasa Indonesia.
Kesalahan yang juga terdapat dalam sumber Inggris akan diringkas dan dilaporkan
secara terpisah ke repositori hulu dengan lokasi dan reproduksi yang tepat.
