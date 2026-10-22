# DWG Translator — aplikasi web (versi DXF)

Aplikasi Streamlit yang menerjemahkan teks Mandarin pada DXF ke Bahasa Indonesia. Geometri dan parameter gambar tidak sengaja diubah; hanya field teks yang ditulis ulang. Hasil perlu diaudit di perangkat CAD, terutama wrapping MTEXT dan font.

## Jalankan lokal untuk pengujian
`pip install -r requirements.txt`
`streamlit run app.py`

## Online tanpa instalasi pada komputer pengguna
1. Upload `app.py` dan `requirements.txt` ke repositori GitHub privat.
2. Deploy lewat Streamlit Community Cloud (atau server Streamlit pribadi) dengan entrypoint `app.py`.
3. Bagikan URL aplikasi; pengguna cukup membuka browser.

## Batasan
- File DWG biner **belum didukung** langsung. Untuk produksi, integrasikan layanan konversi DWG ↔ DXF di backend dengan ODA File Converter sesuai lisensinya, lalu uji roundtrip terhadap berkas asli. Jangan menjanjikan preservasi sempurna pada setiap DWG.
- Aplikasi menggunakan Google Translate melalui `deep-translator` dan mengirim teks untuk diterjemahkan ke layanan eksternal. Jangan unggah gambar rahasia tanpa izin.
- Tidak menerjemahkan XREF, raster, teks outline, atau definisi blok yang tidak diinstansiasi. DIMENSION override opsional dan nilai pengukuran tidak dihitung ulang.
- Format CAD kompleks dalam MTEXT perlu pemeriksaan manual. Font Indonesia yang dipilih harus memiliki glyph Latin.
