#!/usr/bin/env python3
"""
Enrich data penyelenggara maganghub Kemnaker
Adds:
- is_jabodetabek (Boolean)
- province (String)
- region (String: Jabodetabek, Jawa Non-Jabodetabek, Sumatera, Kalimantan, Sulawesi, Bali & Nusa Tenggara, Maluku & Papua)
- tier (1: Top Tier, 2: Mid Tier, 3: General)
- tier_label (String)
- tier_reasons (List[String])
- sector (String: "Pemerintahan" vs "Non-Pemerintahan (Perusahaan/Swasta)")
- category_tags (List[String])
- clean_city (String)
"""

import json
import os
import re

# City to Province mapping dictionary
# Covers all 333 cities/regencies found in the Kemnaker dataset
CITY_PROVINCE_MAP = {
    # DKI Jakarta
    "Kota Adm. Jakarta Pusat": "DKI Jakarta",
    "Kota Adm. Jakarta Selatan": "DKI Jakarta",
    "Kota Adm. Jakarta Barat": "DKI Jakarta",
    "Kota Adm. Jakarta Timur": "DKI Jakarta",
    "Kota Adm. Jakarta Utara": "DKI Jakarta",
    "Kab. Adm. Kepulauan Seribu": "DKI Jakarta",
    
    # Banten
    "Kota Tangerang": "Banten",
    "Kota Tangerang Selatan": "Banten",
    "Kab. Tangerang": "Banten",
    "Kota Serang": "Banten",
    "Kab. Serang": "Banten",
    "Kota Cilegon": "Banten",
    "Kab. Lebak": "Banten",
    "Kab. Pandeglang": "Banten",
    
    # Jawa Barat
    "Kota Bogor": "Jawa Barat",
    "Kab. Bogor": "Jawa Barat",
    "Kota Depok": "Jawa Barat",
    "Kota Bekasi": "Jawa Barat",
    "Kab. Bekasi": "Jawa Barat",
    "Kota Bandung": "Jawa Barat",
    "Kab. Bandung": "Jawa Barat",
    "Kab. Bandung Barat": "Jawa Barat",
    "Kota Cimahi": "Jawa Barat",
    "Kota Sukabumi": "Jawa Barat",
    "Kab. Sukabumi": "Jawa Barat",
    "Kota Cirebon": "Jawa Barat",
    "Kab. Cirebon": "Jawa Barat",
    "Kota Tasikmalaya": "Jawa Barat",
    "Kab. Tasikmalaya": "Jawa Barat",
    "Kota Banjar": "Jawa Barat",
    "Kab. Ciamis": "Jawa Barat",
    "Kab. Pangandaran": "Jawa Barat",
    "Kab. Garut": "Jawa Barat",
    "Kab. Kuningan": "Jawa Barat",
    "Kab. Majalengka": "Jawa Barat",
    "Kab. Sumedang": "Jawa Barat",
    "Kab. Indramayu": "Jawa Barat",
    "Kab. Subang": "Jawa Barat",
    "Kab. Purwakarta": "Jawa Barat",
    "Kab. Karawang": "Jawa Barat",
    "Kab. Cianjur": "Jawa Barat",
    
    # DI Yogyakarta
    "Kota Yogyakarta": "DI Yogyakarta",
    "Kab. Sleman": "DI Yogyakarta",
    "Kab. Bantul": "DI Yogyakarta",
    "Kab. Gunungkidul": "DI Yogyakarta",
    "Kab. Kulon Progo": "DI Yogyakarta",
    
    # Jawa Tengah
    "Kota Semarang": "Jawa Tengah",
    "Kab. Semarang": "Jawa Tengah",
    "Kota Surakarta": "Jawa Tengah",
    "Kab. Sukoharjo": "Jawa Tengah",
    "Kab. Klaten": "Jawa Tengah",
    "Kab. Boyolali": "Jawa Tengah",
    "Kab. Sragen": "Jawa Tengah",
    "Kab. Karanganyar": "Jawa Tengah",
    "Kab. Wonogiri": "Jawa Tengah",
    "Kota Magelang": "Jawa Tengah",
    "Kab. Magelang": "Jawa Tengah",
    "Kota Salatiga": "Jawa Tengah",
    "Kota Pekalongan": "Jawa Tengah",
    "Kab. Pekalongan": "Jawa Tengah",
    "Kota Tegal": "Jawa Tengah",
    "Kab. Tegal": "Jawa Tengah",
    "Kab. Brebes": "Jawa Tengah",
    "Kab. Banyumas": "Jawa Tengah",
    "Kab. Cilacap": "Jawa Tengah",
    "Kab. Purbalingga": "Jawa Tengah",
    "Kab. Banjarnegara": "Jawa Tengah",
    "Kab. Kebumen": "Jawa Tengah",
    "Kab. Purworejo": "Jawa Tengah",
    "Kab. Wonosobo": "Jawa Tengah",
    "Kab. Temanggung": "Jawa Tengah",
    "Kab. Kendal": "Jawa Tengah",
    "Kab. Batang": "Jawa Tengah",
    "Kab. Demak": "Jawa Tengah",
    "Kab. Kudus": "Jawa Tengah",
    "Kab. Jepara": "Jawa Tengah",
    "Kab. Pati": "Jawa Tengah",
    "Kab. Rembang": "Jawa Tengah",
    "Kab. Blora": "Jawa Tengah",
    "Kab. Grobogan": "Jawa Tengah",
    
    # Jawa Timur
    "Kota Surabaya": "Jawa Timur",
    "Kota Malang": "Jawa Timur",
    "Kab. Malang": "Jawa Timur",
    "Kota Batu": "Jawa Timur",
    "Kab. Sidoarjo": "Jawa Timur",
    "Kab. Gresik": "Jawa Timur",
    "Kab. Mojokerto": "Jawa Timur",
    "Kota Mojokerto": "Jawa Timur",
    "Kota Kediri": "Jawa Timur",
    "Kab. Kediri": "Jawa Timur",
    "Kota Blitar": "Jawa Timur",
    "Kab. Blitar": "Jawa Timur",
    "Kota Madiun": "Jawa Timur",
    "Kab. Madiun": "Jawa Timur",
    "Kota Probolinggo": "Jawa Timur",
    "Kab. Probolinggo": "Jawa Timur",
    "Kota Pasuruan": "Jawa Timur",
    "Kab. Pasuruan": "Jawa Timur",
    "Kab. Jember": "Jawa Timur",
    "Kab. Banyuwangi": "Jawa Timur",
    "Kab. Bondowoso": "Jawa Timur",
    "Kab. Situbondo": "Jawa Timur",
    "Kab. Lumajang": "Jawa Timur",
    "Kab. Nganjuk": "Jawa Timur",
    "Kab. Jombang": "Jawa Timur",
    "Kab. Lamongan": "Jawa Timur",
    "Kab. Bojonegoro": "Jawa Timur",
    "Kab. Tuban": "Jawa Timur",
    "Kab. Ngawi": "Jawa Timur",
    "Kab. Magetan": "Jawa Timur",
    "Kab. Ponorogo": "Jawa Timur",
    "Kab. Pacitan": "Jawa Timur",
    "Kab. Trenggalek": "Jawa Timur",
    "Kab. Tulungagung": "Jawa Timur",
    "Kab. Bangkalan": "Jawa Timur",
    "Kab. Sampang": "Jawa Timur",
    "Kab. Pamekasan": "Jawa Timur",
    "Kab. Sumenep": "Jawa Timur",
    
    # Bali
    "Kota Denpasar": "Bali",
    "Kab. Badung": "Bali",
    "Kab. Gianyar": "Bali",
    "Kab. Tabanan": "Bali",
    "Kab. Buleleng": "Bali",
    "Kab. Klungkung": "Bali",
    "Kab. Karangasem": "Bali",
    "Kab. Bangli": "Bali",
    "Kab. Jembrana": "Bali",
    
    # Nusa Tenggara Barat & Timur
    "Kota Mataram": "Nusa Tenggara Barat",
    "Kab. Lombok Barat": "Nusa Tenggara Barat",
    "Kab. Lombok Tengah": "Nusa Tenggara Barat",
    "Kab. Lombok Timur": "Nusa Tenggara Barat",
    "Kab. Lombok Utara": "Nusa Tenggara Barat",
    "Kab. Sumbawa": "Nusa Tenggara Barat",
    "Kab. Sumbawa Barat": "Nusa Tenggara Barat",
    "Kab. Bima": "Nusa Tenggara Barat",
    "Kota Bima": "Nusa Tenggara Barat",
    "Kab. Dompu": "Nusa Tenggara Barat",
    "Kota Kupang": "Nusa Tenggara Timur",
    "Kab. Kupang": "Nusa Tenggara Timur",
    "Kab. Belu": "Nusa Tenggara Timur",
    "Kab. Alor": "Nusa Tenggara Timur",
    "Kab. Ende": "Nusa Tenggara Timur",
    "Kab. Flores Timur": "Nusa Tenggara Timur",
    "Kab. Lembata": "Nusa Tenggara Timur",
    "Kab. Manggarai": "Nusa Tenggara Timur",
    "Kab. Manggarai Barat": "Nusa Tenggara Timur",
    "Kab. Manggarai Timur": "Nusa Tenggara Timur",
    "Kab. Nagekeo": "Nusa Tenggara Timur",
    "Kab. Ngada": "Nusa Tenggara Timur",
    "Kab. Rote Ndao": "Nusa Tenggara Timur",
    "Kab. Sabu Raijua": "Nusa Tenggara Timur",
    "Kab. Sikka": "Nusa Tenggara Timur",
    "Kab. Sumba Barat": "Nusa Tenggara Timur",
    "Kab. Sumba Barat Daya": "Nusa Tenggara Timur",
    "Kab. Sumba Tengah": "Nusa Tenggara Timur",
    "Kab. Sumba Timur": "Nusa Tenggara Timur",
    "Kab. Timor Tengah Selatan": "Nusa Tenggara Timur",
    "Kab. Timor Tengah Utara": "Nusa Tenggara Timur",
    "Kab. Malaka": "Nusa Tenggara Timur",
    
    # Sumatera
    "Kota Banda Aceh": "Aceh",
    "Kota Sabang": "Aceh",
    "Kota Lhokseumawe": "Aceh",
    "Kota Langsa": "Aceh",
    "Kota Subulussalam": "Aceh",
    "Kab. Aceh Barat": "Aceh",
    "Kab. Aceh Barat Daya": "Aceh",
    "Kab. Aceh Besar": "Aceh",
    "Kab. Aceh Jaya": "Aceh",
    "Kab. Aceh Selatan": "Aceh",
    "Kab. Aceh Singkil": "Aceh",
    "Kab. Aceh Tamiang": "Aceh",
    "Kab. Aceh Tengah": "Aceh",
    "Kab. Aceh Tenggara": "Aceh",
    "Kab. Aceh Timur": "Aceh",
    "Kab. Aceh Utara": "Aceh",
    "Kab. Bener Meriah": "Aceh",
    "Kab. Bireuen": "Aceh",
    "Kab. Gayo Lues": "Aceh",
    "Kab. Nagan Raya": "Aceh",
    "Kab. Pidie": "Aceh",
    "Kab. Pidie Jaya": "Aceh",
    "Kab. Simeulue": "Aceh",
    
    "Kota Medan": "Sumatera Utara",
    "Kota Binjai": "Sumatera Utara",
    "Kota Pematangsiantar": "Sumatera Utara",
    "Kota Tanjungbalai": "Sumatera Utara",
    "Kota Tebing Tinggi": "Sumatera Utara",
    "Kota Sibolga": "Sumatera Utara",
    "Kota Padangsidimpuan": "Sumatera Utara",
    "Kota Gunungsitoli": "Sumatera Utara",
    "Kab. Deli Serdang": "Sumatera Utara",
    "Kab. Asahan": "Sumatera Utara",
    "Kab. Batubara": "Sumatera Utara",
    "Kab. Batu Bara": "Sumatera Utara",
    "Kab. Dairi": "Sumatera Utara",
    "Kab. Humbang Hasundutan": "Sumatera Utara",
    "Kab. Karo": "Sumatera Utara",
    "Kab. Labuhanbatu": "Sumatera Utara",
    "Kab. Labuhanbatu Selatan": "Sumatera Utara",
    "Kab. Labuhanbatu Utara": "Sumatera Utara",
    "Kab. Langkat": "Sumatera Utara",
    "Kab. Mandailing Natal": "Sumatera Utara",
    "Kab. Nias": "Sumatera Utara",
    "Kab. Nias Barat": "Sumatera Utara",
    "Kab. Nias Selatan": "Sumatera Utara",
    "Kab. Nias Utara": "Sumatera Utara",
    "Kab. Padang Lawas": "Sumatera Utara",
    "Kab. Padang Lawas Utara": "Sumatera Utara",
    "Kab. Pakpak Bharat": "Sumatera Utara",
    "Kab. Samosir": "Sumatera Utara",
    "Kab. Serdang Bedagai": "Sumatera Utara",
    "Kab. Simalungun": "Sumatera Utara",
    "Kab. Tapanuli Selatan": "Sumatera Utara",
    "Kab. Tapanuli Tengah": "Sumatera Utara",
    "Kab. Tapanuli Utara": "Sumatera Utara",
    "Kab. Toba": "Sumatera Utara",
    "Kab. Toba Samosir": "Sumatera Utara",
    
    "Kota Padang": "Sumatera Barat",
    "Kota Bukittinggi": "Sumatera Barat",
    "Kota Padang Panjang": "Sumatera Barat",
    "Kota Pariaman": "Sumatera Barat",
    "Kota Payakumbuh": "Sumatera Barat",
    "Kota Sawahlunto": "Sumatera Barat",
    "Kota Solok": "Sumatera Barat",
    "Kab. Agam": "Sumatera Barat",
    "Kab. Dharmasraya": "Sumatera Barat",
    "Kab. Kepulauan Mentawai": "Sumatera Barat",
    "Kab. Lima Puluh Kota": "Sumatera Barat",
    "Kab. Padang Pariaman": "Sumatera Barat",
    "Kab. Pasaman": "Sumatera Barat",
    "Kab. Pasaman Barat": "Sumatera Barat",
    "Kab. Pesisir Selatan": "Sumatera Barat",
    "Kab. Sijunjung": "Sumatera Barat",
    "Kab. Solok": "Sumatera Barat",
    "Kab. Solok Selatan": "Sumatera Barat",
    "Kab. Tanah Datar": "Sumatera Barat",
    
    "Kota Pekanbaru": "Riau",
    "Kota Dumai": "Riau",
    "Kab. Bengkalis": "Riau",
    "Kab. Indragiri Hilir": "Riau",
    "Kab. Indragiri Hulu": "Riau",
    "Kab. Kampar": "Riau",
    "Kab. Kepulauan Meranti": "Riau",
    "Kab. Kuantan Singingi": "Riau",
    "Kab. Pelalawan": "Riau",
    "Kab. Rokan Hilir": "Riau",
    "Kab. Rokan Hulu": "Riau",
    "Kab. Siak": "Riau",
    
    "Kota Batam": "Kepulauan Riau",
    "Kota Tanjungpinang": "Kepulauan Riau",
    "Kab. Bintan": "Kepulauan Riau",
    "Kab. Karimun": "Kepulauan Riau",
    "Kab. Kepulauan Anambas": "Kepulauan Riau",
    "Kab. Lingga": "Kepulauan Riau",
    "Kab. Natuna": "Kepulauan Riau",
    
    "Kota Jambi": "Jambi",
    "Kota Sungai Penuh": "Jambi",
    "Kab. Batanghari": "Jambi",
    "Kab. Bungo": "Jambi",
    "Kab. Kerinci": "Jambi",
    "Kab. Merangin": "Jambi",
    "Kab. Muaro Jambi": "Jambi",
    "Kab. Sarolangun": "Jambi",
    "Kab. Tanjung Jabung Barat": "Jambi",
    "Kab. Tanjung Jabung Timur": "Jambi",
    "Kab. Tebo": "Jambi",
    
    "Kota Palembang": "Sumatera Selatan",
    "Kota Pagar Alam": "Sumatera Selatan",
    "Kota Lubuklinggau": "Sumatera Selatan",
    "Kota Prabumulih": "Sumatera Selatan",
    "Kab. Banyuasin": "Sumatera Selatan",
    "Kab. Empat Lawang": "Sumatera Selatan",
    "Kab. Lahat": "Sumatera Selatan",
    "Kab. Muara Enim": "Sumatera Selatan",
    "Kab. Musi Banyuasin": "Sumatera Selatan",
    "Kab. Musi Rawas": "Sumatera Selatan",
    "Kab. Musi Rawas Utara": "Sumatera Selatan",
    "Kab. Ogan Ilir": "Sumatera Selatan",
    "Kab. Ogan Komering Ilir": "Sumatera Selatan",
    "Kab. Ogan Komering Ulu": "Sumatera Selatan",
    "Kab. Ogan Komering Ulu Selatan": "Sumatera Selatan",
    "Kab. Ogan Komering Ulu Timur": "Sumatera Selatan",
    "Kab. Penukal Abab Lematang Ilir": "Sumatera Selatan",
    
    "Kota Pangkalpinang": "Bangka Belitung",
    "Kab. Bangka": "Bangka Belitung",
    "Kab. Bangka Barat": "Bangka Belitung",
    "Kab. Bangka Selatan": "Bangka Belitung",
    "Kab. Bangka Tengah": "Bangka Belitung",
    "Kab. Belitung": "Bangka Belitung",
    "Kab. Belitung Timur": "Bangka Belitung",
    
    "Kota Bengkulu": "Bengkulu",
    "Kab. Bengkulu Selatan": "Bengkulu",
    "Kab. Bengkulu Tengah": "Bengkulu",
    "Kab. Bengkulu Utara": "Bengkulu",
    "Kab. Kaur": "Bengkulu",
    "Kab. Kepahiang": "Bengkulu",
    "Kab. Lebong": "Bengkulu",
    "Kab. Mukomuko": "Bengkulu",
    "Kab. Rejang Lebong": "Bengkulu",
    "Kab. Seluma": "Bengkulu",
    
    "Kota Bandar Lampung": "Lampung",
    "Kota Metro": "Lampung",
    "Kab. Lampung Barat": "Lampung",
    "Kab. Lampung Selatan": "Lampung",
    "Kab. Lampung Tengah": "Lampung",
    "Kab. Lampung Timur": "Lampung",
    "Kab. Lampung Utara": "Lampung",
    "Kab. Mesuji": "Lampung",
    "Kab. Pesawaran": "Lampung",
    "Kab. Pesisir Barat": "Lampung",
    "Kab. Pringsewu": "Lampung",
    "Kab. Tanggamus": "Lampung",
    "Kab. Tulang Bawang": "Lampung",
    "Kab. Tulang Bawang Barat": "Lampung",
    "Kab. Way Kanan": "Lampung",
    
    # Kalimantan
    "Kota Pontianak": "Kalimantan Barat",
    "Kota Singkawang": "Kalimantan Barat",
    "Kab. Bengkayang": "Kalimantan Barat",
    "Kab. Kapuas Hulu": "Kalimantan Barat",
    "Kab. Kayong Utara": "Kalimantan Barat",
    "Kab. Ketapang": "Kalimantan Barat",
    "Kab. Kubu Raya": "Kalimantan Barat",
    "Kab. Landak": "Kalimantan Barat",
    "Kab. Melawi": "Kalimantan Barat",
    "Kab. Mempawah": "Kalimantan Barat",
    "Kab. Sambas": "Kalimantan Barat",
    "Kab. Sanggau": "Kalimantan Barat",
    "Kab. Sekadau": "Kalimantan Barat",
    "Kab. Sintang": "Kalimantan Barat",
    
    "Kota Palangka Raya": "Kalimantan Tengah",
    "Kab. Barito Selatan": "Kalimantan Tengah",
    "Kab. Barito Timur": "Kalimantan Tengah",
    "Kab. Barito Utara": "Kalimantan Tengah",
    "Kab. Gunung Mas": "Kalimantan Tengah",
    "Kab. Kapuas": "Kalimantan Tengah",
    "Kab. Katingan": "Kalimantan Tengah",
    "Kab. Kotawaringin Barat": "Kalimantan Tengah",
    "Kab. Kotawaringin Timur": "Kalimantan Tengah",
    "Kab. Lamandau": "Kalimantan Tengah",
    "Kab. Murung Raya": "Kalimantan Tengah",
    "Kab. Pulang Pisau": "Kalimantan Tengah",
    "Kab. Sukamara": "Kalimantan Tengah",
    "Kab. Seruyan": "Kalimantan Tengah",
    
    "Kota Banjarmasin": "Kalimantan Selatan",
    "Kota Banjarbaru": "Kalimantan Selatan",
    "Kab. Balangan": "Kalimantan Selatan",
    "Kab. Banjar": "Kalimantan Selatan",
    "Kab. Barito Kuala": "Kalimantan Selatan",
    "Kab. Hulu Sungai Selatan": "Kalimantan Selatan",
    "Kab. Hulu Sungai Tengah": "Kalimantan Selatan",
    "Kab. Hulu Sungai Utara": "Kalimantan Selatan",
    "Kab. Kotabaru": "Kalimantan Selatan",
    "Kab. Tabalong": "Kalimantan Selatan",
    "Kab. Tanah Bumbu": "Kalimantan Selatan",
    "Kab. Tanah Laut": "Kalimantan Selatan",
    "Kab. Tapin": "Kalimantan Selatan",
    
    "Kota Samarinda": "Kalimantan Timur",
    "Kota Balikpapan": "Kalimantan Timur",
    "Kota Bontang": "Kalimantan Timur",
    "Kab. Berau": "Kalimantan Timur",
    "Kab. Kutai Barat": "Kalimantan Timur",
    "Kab. Kutai Kartanegara": "Kalimantan Timur",
    "Kab. Kutai Timur": "Kalimantan Timur",
    "Kab. Mahakam Ulu": "Kalimantan Timur",
    "Kab. Paser": "Kalimantan Timur",
    "Kab. Penajam Paser Utara": "Kalimantan Timur",
    
    "Kota Tarakan": "Kalimantan Utara",
    "Kab. Bulungan": "Kalimantan Utara",
    "Kab. Malinau": "Kalimantan Utara",
    "Kab. Nunukan": "Kalimantan Utara",
    "Kab. Tana Tidung": "Kalimantan Utara",
    
    # Sulawesi
    "Kota Manado": "Sulawesi Utara",
    "Kota Bitung": "Sulawesi Utara",
    "Kota Kotamobagu": "Sulawesi Utara",
    "Kota Tomohon": "Sulawesi Utara",
    "Kab. Bolaang Mongondow": "Sulawesi Utara",
    "Kab. Bolaang Mongondow Selatan": "Sulawesi Utara",
    "Kab. Bolaang Mongondow Timur": "Sulawesi Utara",
    "Kab. Bolaang Mongondow Utara": "Sulawesi Utara",
    "Kab. Kepulauan Sangihe": "Sulawesi Utara",
    "Kab. Kepulauan Siau Tagulandang Biaro": "Sulawesi Utara",
    "Kab. Kepulauan Talaud": "Sulawesi Utara",
    "Kab. Minahasa": "Sulawesi Utara",
    "Kab. Minahasa Selatan": "Sulawesi Utara",
    "Kab. Minahasa Tenggara": "Sulawesi Utara",
    "Kab. Minahasa Utara": "Sulawesi Utara",
    
    "Kota Gorontalo": "Gorontalo",
    "Kab. Boalemo": "Gorontalo",
    "Kab. Bone Bolango": "Gorontalo",
    "Kab. Gorontalo": "Gorontalo",
    "Kab. Gorontalo Utara": "Gorontalo",
    "Kab. Pohuwato": "Gorontalo",
    
    "Kota Palu": "Sulawesi Tengah",
    "Kab. Banggai": "Sulawesi Tengah",
    "Kab. Banggai Kepulauan": "Sulawesi Tengah",
    "Kab. Banggai Laut": "Sulawesi Tengah",
    "Kab. Buol": "Sulawesi Tengah",
    "Kab. Donggala": "Sulawesi Tengah",
    "Kab. Morowali": "Sulawesi Tengah",
    "Kab. Morowali Utara": "Sulawesi Tengah",
    "Kab. Parigi Moutong": "Sulawesi Tengah",
    "Kab. Poso": "Sulawesi Tengah",
    "Kab. Sigi": "Sulawesi Tengah",
    "Kab. Tojo Una-Una": "Sulawesi Tengah",
    "Kab. Toli-Toli": "Sulawesi Tengah",
    
    "Kota Mamuju": "Sulawesi Barat",
    "Kab. Majene": "Sulawesi Barat",
    "Kab. Mamasa": "Sulawesi Barat",
    "Kab. Mamuju": "Sulawesi Barat",
    "Kab. Mamuju Tengah": "Sulawesi Barat",
    "Kab. Pasangkayu": "Sulawesi Barat",
    "Kab. Polewali Mandar": "Sulawesi Barat",
    
    "Kota Makassar": "Sulawesi Selatan",
    "Kota Palopo": "Sulawesi Selatan",
    "Kota Parepare": "Sulawesi Selatan",
    "Kab. Bantaeng": "Sulawesi Selatan",
    "Kab. Barru": "Sulawesi Selatan",
    "Kab. Bone": "Sulawesi Selatan",
    "Kab. Bulukumba": "Sulawesi Selatan",
    "Kab. Enrekang": "Sulawesi Selatan",
    "Kab. Gowa": "Sulawesi Selatan",
    "Kab. Jeneponto": "Sulawesi Selatan",
    "Kab. Kepulauan Selayar": "Sulawesi Selatan",
    "Kab. Luwu": "Sulawesi Selatan",
    "Kab. Luwu Timur": "Sulawesi Selatan",
    "Kab. Luwu Utara": "Sulawesi Selatan",
    "Kab. Maros": "Sulawesi Selatan",
    "Kab. Pangkajene dan Kepulauan": "Sulawesi Selatan",
    "Kab. Pinrang": "Sulawesi Selatan",
    "Kab. Sidenreng Rappang": "Sulawesi Selatan",
    "Kab. Sinjai": "Sulawesi Selatan",
    "Kab. Soppeng": "Sulawesi Selatan",
    "Kab. Takalar": "Sulawesi Selatan",
    "Kab. Tana Toraja": "Sulawesi Selatan",
    "Kab. Toraja Utara": "Sulawesi Selatan",
    "Kab. Wajo": "Sulawesi Selatan",
    
    "Kota Kendari": "Sulawesi Tenggara",
    "Kota Baubau": "Sulawesi Tenggara",
    "Kab. Bombana": "Sulawesi Tenggara",
    "Kab. Buton": "Sulawesi Tenggara",
    "Kab. Buton Selatan": "Sulawesi Tenggara",
    "Kab. Buton Tengah": "Sulawesi Tenggara",
    "Kab. Buton Utara": "Sulawesi Tenggara",
    "Kab. Kolaka": "Sulawesi Tenggara",
    "Kab. Kolaka Timur": "Sulawesi Tenggara",
    "Kab. Kolaka Utara": "Sulawesi Tenggara",
    "Kab. Konawe": "Sulawesi Tenggara",
    "Kab. Konawe Kepulauan": "Sulawesi Tenggara",
    "Kab. Konawe Selatan": "Sulawesi Tenggara",
    "Kab. Konawe Utara": "Sulawesi Tenggara",
    "Kab. Muna": "Sulawesi Tenggara",
    "Kab. Muna Barat": "Sulawesi Tenggara",
    "Kab. Wakatobi": "Sulawesi Tenggara",
    
    # Maluku
    "Kota Ambon": "Maluku",
    "Kota Tual": "Maluku",
    "Kab. Buru": "Maluku",
    "Kab. Buru Selatan": "Maluku",
    "Kab. Kepulauan Aru": "Maluku",
    "Kab. Kepulauan Tanimbar": "Maluku",
    "Kab. Maluku Barat Daya": "Maluku",
    "Kab. Maluku Tengah": "Maluku",
    "Kab. Maluku Tenggara": "Maluku",
    "Kab. Seram Bagian Barat": "Maluku",
    "Kab. Seram Bagian Timur": "Maluku",
    
    "Kota Ternate": "Maluku Utara",
    "Kota Tidore Kepulauan": "Maluku Utara",
    "Kab. Halmahera Barat": "Maluku Utara",
    "Kab. Halmahera Tengah": "Maluku Utara",
    "Kab. Halmahera Timur": "Maluku Utara",
    "Kab. Halmahera Selatan": "Maluku Utara",
    "Kab. Halmahera Utara": "Maluku Utara",
    "Kab. Kepulauan Sula": "Maluku Utara",
    "Kab. Pulau Morotai": "Maluku Utara",
    "Kab. Pulau Taliabu": "Maluku Utara",
    
    # Papua
    "Kota Jayapura": "Papua",
    "Kab. Jayapura": "Papua",
    "Kab. Keerom": "Papua",
    "Kab. Sarmi": "Papua",
    "Kab. Mamberamo Raya": "Papua",
    "Kab. Biak Numfor": "Papua",
    "Kab. Supiori": "Papua",
    "Kab. Kepulauan Yapen": "Papua",
    "Kab. Waropen": "Papua",
    "Kota Sorong": "Papua Barat Daya",
    "Kab. Sorong": "Papua Barat Daya",
    "Kab. Sorong Selatan": "Papua Barat Daya",
    "Kab. Raja Ampat": "Papua Barat Daya",
    "Kab. Tambrauw": "Papua Barat Daya",
    "Kab. Maybrat": "Papua Barat Daya",
    "Kab. Manokwari": "Papua Barat",
    "Kab. Manokwari Selatan": "Papua Barat",
    "Kab. Pegunungan Arfak": "Papua Barat",
    "Kab. Teluk Bintuni": "Papua Barat",
    "Kab. Teluk Wondama": "Papua Barat",
    "Kab. Kaimana": "Papua Barat",
    "Kab. Fakfak": "Papua Barat",
    "Kab. Merauke": "Papua Selatan",
    "Kab. Boven Digoel": "Papua Selatan",
    "Kab. Mappi": "Papua Selatan",
    "Kab. Asmat": "Papua Selatan",
    "Kab. Nabire": "Papua Tengah",
    "Kab. Mimika": "Papua Tengah",
    "Kab. Paniai": "Papua Tengah",
    "Kab. Dogiyai": "Papua Tengah",
    "Kab. Deiyai": "Papua Tengah",
    "Kab. Intan Jaya": "Papua Tengah",
    "Kab. Puncak": "Papua Tengah",
    "Kab. Puncak Jaya": "Papua Tengah",
    "Kab. Jayawijaya": "Papua Pegunungan",
    "Kab. Pegunungan Bintang": "Papua Pegunungan",
    "Kab. Yahukimo": "Papua Pegunungan",
    "Kab. Tolikara": "Papua Pegunungan",
    "Kab. Mamberamo Tengah": "Papua Pegunungan",
    "Kab. Yalimo": "Papua Pegunungan",
    "Kab. Lanny Jaya": "Papua Pegunungan",
    "Kab. Nduga": "Papua Pegunungan",
}

PROVINCE_REGION_MAP = {
    "DKI Jakarta": "Jabodetabek",
    "Jawa Barat": "Jawa Non-Jabodetabek",  # Jabodetabek cities in Jabar will be dynamically classified
    "Banten": "Jawa Non-Jabodetabek",      # Jabodetabek cities in Banten will be dynamically classified
    "Jawa Tengah": "Jawa Non-Jabodetabek",
    "DI Yogyakarta": "Jawa Non-Jabodetabek",
    "Jawa Timur": "Jawa Non-Jabodetabek",
    "Aceh": "Sumatera",
    "Sumatera Utara": "Sumatera",
    "Sumatera Barat": "Sumatera",
    "Riau": "Sumatera",
    "Kepulauan Riau": "Sumatera",
    "Jambi": "Sumatera",
    "Sumatera Selatan": "Sumatera",
    "Bangka Belitung": "Sumatera",
    "Bengkulu": "Sumatera",
    "Lampung": "Sumatera",
    "Kalimantan Barat": "Kalimantan",
    "Kalimantan Tengah": "Kalimantan",
    "Kalimantan Selatan": "Kalimantan",
    "Kalimantan Timur": "Kalimantan",
    "Kalimantan Utara": "Kalimantan",
    "Sulawesi Utara": "Sulawesi",
    "Gorontalo": "Sulawesi",
    "Sulawesi Tengah": "Sulawesi",
    "Sulawesi Barat": "Sulawesi",
    "Sulawesi Selatan": "Sulawesi",
    "Sulawesi Tenggara": "Sulawesi",
    "Bali": "Bali & Nusa Tenggara",
    "Nusa Tenggara Barat": "Bali & Nusa Tenggara",
    "Nusa Tenggara Timur": "Bali & Nusa Tenggara",
    "Maluku": "Maluku & Papua",
    "Maluku Utara": "Maluku & Papua",
    "Papua": "Maluku & Papua",
    "Papua Barat": "Maluku & Papua",
    "Papua Barat Daya": "Maluku & Papua",
    "Papua Selatan": "Maluku & Papua",
    "Papua Tengah": "Maluku & Papua",
    "Papua Pegunungan": "Maluku & Papua",
}

JABODETABEK_CITIES = {
    "Kota Adm. Jakarta Pusat",
    "Kota Adm. Jakarta Selatan",
    "Kota Adm. Jakarta Barat",
    "Kota Adm. Jakarta Timur",
    "Kota Adm. Jakarta Utara",
    "Kab. Adm. Kepulauan Seribu",
    "Kota Bogor",
    "Kab. Bogor",
    "Kota Depok",
    "Kota Tangerang",
    "Kota Tangerang Selatan",
    "Kab. Tangerang",
    "Kota Bekasi",
    "Kab. Bekasi",
}

def resolve_location(city_name, address):
    city_str = city_name or ""
    clean_city = city_str.strip()
    
    # Check Jabodetabek
    is_jabo = clean_city in JABODETABEK_CITIES
    if not is_jabo and address:
        # Fallback keyword match in address
        addr_lower = address.lower()
        if any(j in addr_lower for j in ["jakarta", "bogor", "depok", "tangerang", "bekasi"]):
            is_jabo = True
            
    # Resolve Province
    province = CITY_PROVINCE_MAP.get(clean_city)
    if not province:
        # Fuzzy match with address or city
        combined = f"{clean_city} {address}".lower()
        for prov in PROVINCE_REGION_MAP.keys():
            if prov.lower() in combined:
                province = prov
                break
        if not province:
            province = "Lainnya"
            
    # Resolve Region
    if is_jabo:
        region = "Jabodetabek"
    else:
        region = PROVINCE_REGION_MAP.get(province, "Lainnya")
        
    return clean_city, province, region, is_jabo

def classify_tier_and_tags(item):
    name = (item.get("name") or "").strip()
    nl = name.lower()
    item_type = item.get("type") or ""
    vacancies = item.get("total_active_vacancies") or 0
    desc = (item.get("description") or "").lower()
    
    tags = set()
    reasons = []
    
    # Check Top Tier Indicators
    kementerian_pusat = [
        "kementerian", "kemdikbud", "kemenkes", "kemnaker", "kemenkeu", "kominfo", "komdigi",
        "anri", "bps ri", "badan pusat statistik", "brin", "bsn", "bssn", "ojk", "otoritas jasa keuangan",
        "bank indonesia", "sekretariat negara", "setneg", "bpkp", "lkpp", "bmkg", "basarnas",
        "kejaksaan agung", "mahkamah agung", "komisi yudisial", "komisi pemberantasan korupsi"
    ]
    is_kem_pusat = any(k in nl for k in kementerian_pusat) or (name.upper() == "ANRI")
    
    bumn_indicators = [
        "persero", "bumn", "bank mandiri", "telkom", "pertamina", "perusahaan listrik negara", "pln",
        "bank rakyat indonesia", "bank negara indonesia", "bank tabungan negara", "pelindo",
        "wijaya karya", "waskita", "adhi karya", "pupuk kujang", "pupuk indonesia", "pal indonesia",
        "bio farma", "kimia farma", "perumnas", "kereta api indonesia", "pt kai", "pos indonesia",
        "angkasa pura", "jasa marga", "injourney", "pindad", "bukit asam", "timah", "antam",
        "asuransi kredit indonesia", "sucofindo", "surveyor indonesia", "damri", "jasaraharja"
    ]
    is_bumn = any(b in nl for b in bumn_indicators)
    
    top_giants = [
        "ruang raya indonesia", "paragon technology", "global digital niaga", "sumber alfaria trijaya",
        "midi utama indonesia", "btpn syariah", "televisi transformasi indonesia", "mnc televisi",
        "hadji kalla", "sodexo", "great giant pineapple", "mass rapid transit jakarta", "astra",
        "indofood", "unilever", "kalbe", "djarum", "sampoerna", "grab", "gojek", "shopee",
        "bukalapak", "traveloka", "tiket.com", "tokopedia", "lazada", "blibli"
    ]
    is_tbk = "tbk" in nl.split() or "(tbk)" in nl or "tbk." in nl
    is_giant = any(g in nl for g in top_giants) or is_tbk
    
    is_top_hospital = any(h in nl for h in ["cipto mangun kusumo", "fatmawati", "dharmais", "harapan kita", "hasan sadikin"])
    
    # Categorization Tags (Clean without emojis)
    if is_bumn or "persero" in nl:
        tags.add("BUMN / BUMD")
    if item_type == "Kementerian/Lembaga":
        tags.add("Instansi Pemerintah")
    if is_tbk:
        tags.add("Perusahaan Terbuka (Tbk)")
    if any(h in nl for h in ["rumah sakit", "rsud", "klinik", "kesehatan", "medika", "pharma"]):
        tags.add("Kesehatan & Rumah Sakit")
    if any(u in nl for u in ["universitas", "politeknik", "institut", "sekolah", "pendidikan", "diklat"]):
        tags.add("Pendidikan & Pelatihan")
    if any(b in nl for b in ["bank ", "bank,", "syariah", "sekuritas", "asuransi", "finance", "finansial"]):
        tags.add("Perbankan & Finansial")
    if any(t in nl for t in ["teknologi", "digital", "software", "solution", "telekomunikasi", "media", "televisi", "ruang raya"]):
        tags.add("Teknologi & Media")
    if any(r in nl for r in ["alfaria", "midi utama", "retail", "supermarket", "mart", "pineapple", "food", "beverage"]):
        tags.add("Retail & FMCG")
    if vacancies >= 20:
        tags.add("Kuota Besar (≥20)")
        
    # Tier assignment
    if is_kem_pusat:
        reasons.append("Kementerian / Lembaga Pusat")
    if is_bumn:
        reasons.append("BUMN / Afiliasi BUMN")
    if is_giant:
        reasons.append("National Enterprise / Tbk")
    if is_top_hospital:
        reasons.append("Rumah Sakit Rujukan Nasional")
    if vacancies >= 50:
        reasons.append(f"Kapasitas Kuota Masif ({vacancies} Lowongan)")
        
    if reasons:
        return 1, "Tier 1: High Tier (BUMN / Kementerian / Giant)", reasons, list(tags)
        
    # Check Mid Tier Indicators
    mid_indicators = [
        "balai", "dinas", "pengadilan", "kejaksaan", "kantor pertanahan", "pemerintah kota",
        "pemerintah kabupaten", "pemkab", "pemkot", "rsud", "rumah sakit", "klinik", "universitas",
        "politeknik", "institut", "sekolah tinggi", "perseroda", "bank daerah", "bank jatim",
        "bank bjb", "bank jateng", "pdam"
    ]
    is_mid = any(m in nl for m in mid_indicators) or (item_type == "Kementerian/Lembaga") or (vacancies >= 15)
    
    mid_reasons = []
    if item_type == "Kementerian/Lembaga":
        mid_reasons.append("Instansi Pemerintah")
    if any(m in nl for m in ["balai", "dinas", "pengadilan", "kejaksaan", "kantor pertanahan"]):
        mid_reasons.append("Unit Pelaksana Daerah / UPT")
    if "rumah sakit" in nl or "rsud" in nl or "klinik" in nl:
        mid_reasons.append("Fasilitas Kesehatan Regional")
    if any(u in nl for u in ["universitas", "politeknik", "institut", "sekolah"]):
        mid_reasons.append("Institusi Pendidikan")
    if vacancies >= 15:
        mid_reasons.append(f"Kapasitas Kuota Besar ({vacancies} Lowongan)")
        
    if is_mid:
        return 2, "Tier 2: Mid Tier (Pemda / Balai / RS / Reguler)", mid_reasons or ["Perusahaan / Instansi Menengah"], list(tags)
        
    # Default Tier 3
    return 3, "Tier 3: General / SME / Swasta Lokal", ["Swasta / Usaha Lokal"], list(tags)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, "data", "penyelenggara.json")
    output_path = os.path.join(base_dir, "data", "penyelenggara_enriched.json")
    
    if not os.path.exists(input_path):
        input_path = os.path.join(base_dir, "penyelenggara.json")
        
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    print(f"Processing {len(raw_data)} records...")
    enriched_data = []
    
    tier_counts = {1: 0, 2: 0, 3: 0}
    jabo_count = 0
    gov_count = 0
    
    for item in raw_data:
        city_raw = item.get("city")
        city_name = city_raw.get("name") if isinstance(city_raw, dict) else (str(city_raw) if city_raw else "")
        address = item.get("address") or ""
        
        clean_city, province, region, is_jabo = resolve_location(city_name, address)
        tier, tier_label, tier_reasons, category_tags = classify_tier_and_tags(item)
        
        is_gov = (item.get("type") == "Kementerian/Lembaga")
        sector = "Pemerintahan" if is_gov else "Non-Pemerintahan (Perusahaan/Swasta)"
        
        tier_counts[tier] += 1
        if is_jabo:
            jabo_count += 1
        if is_gov:
            gov_count += 1
            
        enriched_item = {
            "id": item.get("id"),
            "name": item.get("name"),
            "type": item.get("type"),
            "sector": sector,
            "is_government": is_gov,
            "description": item.get("description") or "",
            "address": address,
            "city_name": clean_city,
            "province": province,
            "region": region,
            "is_jabodetabek": is_jabo,
            "logo_url": item.get("logo_url") or "",
            "total_active_vacancies": item.get("total_active_vacancies") or 0,
            "url": item.get("url") or f"https://maganghub.kemnaker.go.id/magang-nasional/penyelenggara/{item.get('id')}",
            "scraped_at": item.get("scraped_at") or "",
            "tier": tier,
            "tier_label": tier_label,
            "tier_reasons": tier_reasons,
            "category_tags": category_tags,
        }
        enriched_data.append(enriched_item)
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully created {output_path}")
    print(f"Total: {len(enriched_data)} items")
    print(f"Tiers: Tier 1 = {tier_counts[1]}, Tier 2 = {tier_counts[2]}, Tier 3 = {tier_counts[3]}")
    print(f"Jabodetabek: {jabo_count} items")
    print(f"Pemerintahan: {gov_count} items, Non-Pemerintahan: {len(enriched_data) - gov_count} items")

if __name__ == "__main__":
    main()
