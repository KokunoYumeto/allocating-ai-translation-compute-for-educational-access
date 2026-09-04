# Prealgebra 2e — Bahasa Indonesia

Edisi Bahasa Indonesia lengkap dari *Prealgebra 2e* OpenStax, dengan reader
HTML yang responsif dan backend modular netral-locale untuk penggunaan ulang
oleh pipeline terjemahan lain.

> Adaptasi ini tidak resmi. Adaptasi ini tidak berafiliasi dengan, disponsori,
> didukung, atau disahkan oleh OpenStax, Rice University, maupun para
> kontributor asli.

Provenance model: **OpenAI Codex gpt-5.6-sol, Ultra**. Semua kredit sumber,
penulis, penelaah, penerbit, dan kontributor manusia dipertahankan.

## Mulai

- Reader rilis: ekstrak `prealgebra-2e-id-ID-v0.2.7-reader-html.zip`, lalu buka
  `index.html`. Tree `output/html-id` adalah output workspace dan tidak
  digandakan ke paket sumber.
- [Unduh versi terbaru melalui DOI konsep Zenodo](https://doi.org/10.5281/zenodo.22058518)
- Rilis sumber portabel saat ini: v0.2.7. Pendahulunya, v0.2.6, tetap
  dipertahankan pada DOI [`10.5281/zenodo.22058519`](https://doi.org/10.5281/zenodo.22058519).
- GitHub/Pages dan Zenodo dipelihara sebagai dua salinan publik dari lineage
  yang sama; setiap salinan diverifikasi dengan readback anonim.
- [Status dan cakupan edisi](README.id-ID.md)
- [Build, reproduksi, dan bukti QA](BUILD.id-ID.md)
- [Kebijakan portabilitas paket sumber](PORTABILITY.id-ID.md)

Edisi mencakup seluruh 75 referensi koleksi: 71 modul instruksional, satu
prakata, dan tiga lampiran. Struktur CNXML, ID asli, MathML, latihan, jawaban,
tautan, aset, dan atribusi dipertahankan. Koreksi sumber dan keputusan
terminologi dicatat secara terpisah.

Setiap versi Zenodo baru wajib melewati unduhan ulang anonim seluruh berkas dan
pencocokan nama, jumlah byte, MD5 Zenodo, serta SHA-256 lokal.

Sumber terjemahan berada di `modules/`; urutan edisi Indonesia berada di
`collections/prealgebra-2e.id-ID.collection.xml`. Reader dibangun ke
`output/html-id`. Backend interoperabilitas v0.2.5 (dipaketkan pada rilis
v0.2.7) berada di
`modular_backend/generated/prealgebra2e-volume`.

## Sumber, lisensi, dan provenance

Sumber beku: [`openstax/osbooks-prealgebra-bundle`](https://github.com/openstax/osbooks-prealgebra-bundle)
pada commit `38cae454e644abf9f0a623e876994553881597c9`. Buku sumber dan
adaptasi ini tersedia di bawah
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/);
lihat [LICENSE](LICENSE). Hak dan atribusi komponen pihak ketiga tetap berlaku
secara terpisah. README dan descriptor tiga-buku upstream yang diwarisi
dipertahankan tanpa perubahan isi di `provenance/`.

OpenStax adalah bagian dari Rice University. Buku sumber resmi tersedia di
[OpenStax Prealgebra 2e](https://openstax.org/details/books/prealgebra-2e).

## English

This repository contains the complete, unofficial Indonesian (`id-ID`)
adaptation of OpenStax *Prealgebra 2e*, plus a centered responsive HTML reader
and a locale-neutral modular backend. It covers only Prealgebra 2e; Elementary
Algebra, Intermediate Algebra, Precalculus, and other sibling corpora are
outside this repository.
