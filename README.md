# 💼 MagangHub Explorer — Filter & Ranking Penyelenggara Magang Kemnaker

Web application modern, cepat, dan interaktif untuk mengeksplorasi, memfilter, dan mengurutkan **1.700 penyelenggara magang resmi** dari portal **Kemnaker RI Maganghub**.

Web app ini dibuat dengan arsitektur **Zero-Backend (Static Frontend murni)** sehingga:
- ⚡ **Super Cepat**: Semua data (1.700 instansi) difilter secara instan di browser dalam hitungan milidetik.
- 🚀 **100% Siap GitHub Pages**: Lu bisa langsung deploy ke internet secara gratis tanpa perlu bayar VPS/server sama sekali.
- 📱 **Mobile Friendly**: Nyaman diakses dari HP, tablet, maupun laptop/PC.

---

## ✨ Fitur-Fitur Utama

### 1. 🔍 Mesin Filter Lengkap
- **Pencarian Cerdas**: Cari instansi berdasarkan nama perusahaan, instansi, nama kota, alamat kantor, industri, atau kata kunci deskripsi.
- **Filter Wilayah Jabodetabek**:
  - Tombol instan: `Semua` | `Hanya Jabodetabek` (600 instansi) | `Luar Jabodetabek` (1.100 instansi).
- **Filter Sektor**:
  - `🏛️ Instansi Pemerintah` (Kementerian, Balai Pelatihan, Dinas, Balai Pemasyarakatan, Pengadilan, dll.)
  - `🏢 Swasta & BUMN` (Korporasi, Perusahaan Publik Tbk, BUMN/BUMD, Startup, dll.)
- **Filter Tier Organisasi**:
  - **🌟 Tier 1 (High Tier)**: BUMN/Persero, Kementerian Pusat, Lembaga Negara, Korporasi Tbk, Tech Giant, dan instansi berkuota lowongan masif (50+ lowongan).
  - **🔷 Tier 2 (Mid Tier)**: Pemerintah Daerah, Balai UPT, Rumah Sakit/RSUD, Universitas/Politeknik, dan perusahaan menengah (15–49 lowongan).
  - **⚪ Tier 3 (General / SME)**: Perusahaan swasta lokal, startup tahap awal, dsb.
- **Filter Wilayah & Kota Dinamis**: Dropdown provinsi seluruh Indonesia (DKI Jakarta, Jawa Barat, Jawa Timur, Sumatera Utara, Bali, dll.) dengan kota/kabupaten yang otomatis menyesuaikan.
- **Filter Kuota Lowongan**: Kuota masif (>50), besar (21–50), menengah (6–20), atau minimal (1–5).
- **Tag Khusus**: BUMN/BUMD, Tbk, Rumah Sakit, Edukasi, Tech & Media, Finansial, dan Retail.

### 2. 📊 Sorting (Pengurutan Data Fleksibel)
- **Tier: High Tier ➔ General / Lokal** *(Default — instansi bergengsi muncul di atas)*
- **Tier: General / Lokal ➔ High Tier**
- **Lowongan Terbanyak ➔ Tersedikit** *(Lihat instansi yang buka kuota magang terbesar)*
- **Lowongan Tersedikit ➔ Terbanyak**
- **Nama Instansi (A ➔ Z) & (Z ➔ A)**
- **Kota / Lokasi (A ➔ Z)**

### 3. 🛠️ Fitur Produktivitas
- **⭐ Sistem Favorit / Bookmark**: Tandai instansi incaranmu dengan tombol bintang. Disimpan otomatis di browser (`localStorage`).
- **📥 Export ke CSV**: Download hasil filter langsung ke file spreadsheet Excel/CSV.
- **📋 Modal Detail & Lokasi**: Lihat deskripsi lengkap, salin alamat kantor dengan satu klik, dan tombol pintas ke Google Maps.
- **🔗 Direct Kemnaker Link**: Tombol cepat untuk membuka halaman pendaftaran resmi di portal Maganghub Kemnaker.
- **🔗 URL Query Sync**: Filter tersimpan di link URL (`?q=bumn&jabo=yes`), jadi bisa dicopy dan dibagikan ke teman.
- **🌓 Dark & Light Mode**: Desain nyaman di mata dengan palet warna modern.

---

## 📂 Struktur File

```text
siapkerja_backup/
├── index.html                   # Halaman web utama
├── css/
│   └── styles.css               # Styling Vanilla CSS modern & responsive
├── js/
│   ├── app.js                   # Controller UI, rendering kartu, modal, & event listener
│   ├── filters.js               # Mesin pencarian, filtering, & sorting
│   └── storage.js               # Helper localStorage untuk favorit & tema
├── data/
│   ├── penyelenggara.json          # Data mentah asli
│   ├── penyelenggara_enriched.json # Data dengan tier, tag, & mapping provinsi
│   └── penyelenggara_data.js       # Fallback bundle agar bisa dibuka langsung tanpa server
├── scripts/
│   └── enrich_data.py           # Script Python untuk memproses & klasifikasi data
├── package.json                 # Script utilitas dev server
├── .gitignore                   # Ignore file build & cache
└── README.md                    # Dokumentasi lengkap (file ini)
```

---

## 🚀 Cara Menjalankan di Komputer Lokal

Ada 2 cara yang sangat gampang:

### Cara 1: Buka Langsung (Paling Praktis)
Tinggal klik dua kali (double-click) file `index.html` di file explorer komputer lu. Web app langsung terbuka di Google Chrome / browser default tanpa perlu setup apapun!

### Cara 2: Pakai Local Server
Kalau mau pakai local server via terminal:

```bash
# Opsi A: Menggunakan Python (sudah bawaan Linux/Mac)
python3 -m http.server 3000

# Opsi B: Menggunakan Node.js
npx serve .
```
Lalu buka browser di: `http://localhost:3000`

---

## 🌐 Cara Push ke GitHub & Mengaktifkan GitHub Pages (Agar Online Gratis)

Web app ini sudah dirancang statis di root directory, jadi sangat gampang di-hosting di **GitHub Pages**:

### Langkah 1: Inisialisasi Git dan Commit
Buka terminal di folder proyek ini (`/home/tama/Documents/code/siapkerja_backup`):

```bash
# 1. Inisialisasi git jika belum
git init

# 2. Tambahkan semua file
git add .

# 3. Buat commit pertama
git commit -m "feat: initial commit maganghub explorer with complete filtering and tier sorting"
```

### Langkah 2: Buat Repository di GitHub
1. Buka [github.com](https://github.com) dan login ke akun lu.
2. Klik tombol **New** (Buat Repository Baru).
3. Beri nama repository, misalnya: `maganghub-explorer` atau `kemnaker-penyelenggara`.
4. Pilih **Public** (agar bisa pakai GitHub Pages gratis).
5. Biarkan centang "Add a README file" kosong (karena kita sudah punya README).
6. Klik **Create repository**.

### Langkah 3: Hubungkan dan Push ke GitHub
Di terminal lu, jalankan perintah berikut (ganti `USERNAME` dan `REPO_NAME` dengan akun GitHub lu):

```bash
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

### Langkah 4: Aktifkan GitHub Pages (Web Langsung Online!)
1. Di halaman repository GitHub lu, klik tab **Settings** (⚙️).
2. Di sidebar kiri, klik menu **Pages**.
3. Pada bagian **Build and deployment**:
   - Source: pilih **Deploy from a branch**.
   - Branch: pilih **main** dan folder `/(root)`.
4. Klik tombol **Save**.
5. Tunggu sekitar 1–2 menit, web app lu sudah online dan bisa diakses seluruh dunia di:
   ```text
   https://USERNAME.github.io/REPO_NAME/
   ```

---

## 🧠 Bagaimana Cara Kerja Klasifikasi Tier?

Algoritma pengelompokan tier di `scripts/enrich_data.py` bekerja dengan aturan transparan:

1. **Tier 1 (High Tier / Enterprise / Kementerian)**:
   - Kementerian RI & Lembaga Pemerintah Pusat (Kemnaker, Kemenkes, Kemenkeu, BPS, ANRI, BRIN, BSN, dll).
   - Seluruh BUMN & Afiliasi BUMN (Bank Mandiri, Telkom, BRI, Pertamina, Wijaya Karya, Pupuk Kujang, PT PAL, dll).
   - Perusahaan Terbuka (Tbk), Unicorn/Tech Giants (Ruangguru, Blibli, Paragon, Alfamart, Indofood, Trans TV, dll).
   - Kuota lowongan masif (50+ lowongan aktif).
2. **Tier 2 (Mid Tier / Pemda / Balai / RS / Reguler)**:
   - Balai Pelatihan Vokasi, Balai Pemasyarakatan (Bapas), Dinas Daerah, Pengadilan, Kejaksaan, Kantor Pertanahan (BPN).
   - Fasilitas Kesehatan Regional (RSUD & RS Swasta).
   - Institusi Pendidikan (Universitas, Politeknik, Institut).
   - Perusahaan dengan kuota 15–49 lowongan.
3. **Tier 3 (General / Swasta Lokal / SME)**:
   - Perusahaan swasta lokal, CV, dan unit usaha umum dengan kuota 1–14 lowongan.

---

## 📜 Lisensi & Sumber Data
- Data: Portal resmi **Kemnaker RI Maganghub Nasional** (September 2026).
- Lisensi Kode: **MIT License**. Bebas digunakan, dimodifikasi, dan dibagikan.
