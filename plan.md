Halo, AI Engineers!

Selamat kepada teman-teman yang telah menyelesaikan seluruh rangkaian training AI Engineer Intermediate. Kini saatnya kita lanjutkan ke agenda terakhir: pengerjaan Final Project.

Final Project bisa dikerjakan mulai hari Selasa hingga hari Minggu pkl 23.59 WIB (waktu maksimal pengerjaan).

Bentuk Final Project adalah backend service FastAPI yang dideploy ke cloud + laporan teknis dalam README.md. Tidak ada Jupyter Notebook, tidak ada video, yang kita bangun adalah layanan API sungguhan yang bisa dipanggil via internet.

Peran & Skenario
Anda adalah seorang AI Engineer (Intermediate) di organisasi fiktif “NusantaraCare”, sebuah perusahaan yang memiliki banyak dokumen internal: SOP, kebijakan, FAQ, dan panduan teknis.

Masalahnya:

Karyawan kesulitan mencari jawaban karena dokumen tersebar dan panjang.
Pencarian keyword biasa gagal menangkap konteks.
Jawaban harus bisa ditelusuri ke sumber, tidak boleh mengarang.
Manajemen meminta Anda membangun asisten GenAI berbasis RAG yang:

Menjawab hanya berdasarkan dokumen (bukan mengarang)
Menyertakan kutipan sumber di setiap jawaban
Menolak pertanyaan di luar cakupan dokumen
Menangkal instruksi berbahaya (prompt injection)
Bisa diakses sebagai API melalui internet (FastAPI Cloud)
Sumber Dokumen (Knowledge Base)
Wajib: Setiap submission menggunakan satu dokumen yang sudah disediakan: 

Unduh Nusantaracare Panduan Operasional Internal

 

Dokumen ini adalah panduan operasional internal NusantaraCare v2.0 yang berisi SOP, FAQ, matriks keputusan, dan riwayat perubahan. Tidak boleh menambah, mengganti, atau memodifikasi dokumen. Dokumen ini wajib dikomit di repositori Anda apa adanya.

⚠️ Perhatian: Dokumen juga memuat arsip v1.4 yang sudah NONAKTIF sejak 1 Juli 2026. Sistem Anda harus bisa membedakan ketentuan v2.0 (aktif) dari v1.4 (tidak berlaku).

Minimum Requirement
Layanan backend Anda wajib memiliki 4 Bagian dalam README.md sebagai laporan teknis:

1. Problem & Success Criteria
Jelaskan tujuan bisnis, kriteria sukses, jenis pertanyaan yang ditargetkan, dan batasan sistem.

2. Knowledge Base Understanding
Deskripsikan isi dan struktur dokumen NusantaraCare. Catat metadata: doc_id, doc_version, effective_date, is_active, dll. Tunjukkan pemahaman tentang perbedaan v1.4 vs v2.0.

3. RAG Design & Data Preparation (20 poin)
Jelaskan Design RAG yang ingin dibuat, misalnya menjelaskan :

Chunking: ukuran chunk, overlap, dan alasannya
Metadata per chunk: doc_id, chunk_id, doc_title, section_title, doc_version, is_active, dll.
Vector database: pilihan dan justifikasi (FAISS, ChromaDB, dsb.)
Retrieval: top-k, threshold, filtering
Prompt: instruksi “jawab hanya dari konteks”
Dokumen nonaktif/konflik: bagaimana menangani v1.4 vs v2.0
4. Kesimpulan & Dokumentasi (5 poin)
Rangkum performa sistem, rekomendasi perbaikan. Tulis README.md lengkap dengan Bagian: Problem, KB Understanding, RAG Design, Arsitektur, Kontrak API, Cara Menjalankan Lokal, Deployment, Keterbatasan (jika ada), Kesimpulan & Rekomendasi.

Format Submission
Kumpulkan dua tautan:

URL repositori GitHub publik
URL aplikasi FastAPI Cloud (https://<app>.fastapicloud.dev)
Struktur repositori yang disarankan (boleh berubah):

repository/
├── README.md                   # Laporan teknis (wajib, 9 seksi)
├── data/raw_docs/
│   └── nusantaracare_panduan_operasional_internal_v2.md   # Wajib, tanpa modifikasi
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── schemas.py              # Pydantic models
│   └── services/
│       ├── rag.py              # Pipeline RAG
│       └── agent.py            # Router agentic
├── requirements.txt            # ATAU pyproject.toml (pilih satu)
├── .env.example                # Daftar variabel lingkungan (tanpa nilai rahasia)
├── .gitignore                  # Wajib sertakan .env
Rubrik Penilaian
No	Komponen	Poin
1	Business & Knowledge Understanding	20
2	Code, Design & Implementation	30
3	Pengujian Pertanyaan Terhadap Dokumen	35
4	FastAPI Cloud Deployment + Dokumentasi	10
5	Penjelasan README	5
Total	 	100
Keamanan (PENTING!)
JANGAN commit .env atau API key ke repository
Sediakan .env.example tanpa nilai rahasia
.gitignore wajib menyertakan .env
 Kredensial LLM disimpan sebagai FastAPI Cloud secret environment variable
Setiap respons API wajib memiliki 3 field:

Field	Deskripsi	Contoh
answer	Jawaban final	"Ajukan melalui Service Portal..."
confidence_label	"high", "medium", "low"	"high"
reason_code	Alasan sistem	"answered", "no_relevant_context"
Jika pertanyaan tidak ada di dokumen → jawab “tidak ditemukan dalam dokumen”, jangan mengarang.

Selamat mengerjakan. Fokus pada pemahaman alur, jawaban yang jujur terhadap dokumen, dan deployment yang aman. Prototipe yang jujur lebih baik daripada demo yang mengarang. 