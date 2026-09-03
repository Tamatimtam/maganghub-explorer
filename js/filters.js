/**
 * filters.js - Filter & Sorting Engine
 * Logika inti untuk pencarian, multi-kriteria filter, sorting tier & lowongan,
 * dan kalkulasi analitik ringkas.
 */

class FilterEngine {
  constructor(allData) {
    this.allData = allData || [];
    this.state = {
      search: '',
      jabodetabek: 'all', // 'all', 'yes', 'no'
      sector: 'all',      // 'all', 'gov', 'corp'
      sort: 'tier_desc',  // 'tier_desc', 'tier_asc', 'vacancies_desc', 'vacancies_asc', 'name_asc', 'name_desc', 'city_asc'
      tier: 'all',        // 'all', '1', '2', '3'
      province: 'all',    // 'all' atau nama provinsi
      city: 'all',        // 'all' atau nama kota
      vacancyRange: 'all',// 'all', 'massive', 'large', 'medium', 'small'
      selectedTags: new Set(),
      onlyFavorites: false
    };
  }

  /**
   * Update state filter
   * @param {Object} partialState 
   */
  updateState(partialState) {
    this.state = { ...this.state, ...partialState };
  }

  /**
   * Reset filter ke nilai default
   */
  reset() {
    this.state = {
      search: '',
      jabodetabek: 'all',
      sector: 'all',
      sort: 'tier_desc',
      tier: 'all',
      province: 'all',
      city: 'all',
      vacancyRange: 'all',
      selectedTags: new Set(),
      onlyFavorites: false
    };
  }

  /**
   * Eksekusi filter dan sorting berdasarkan state aktif
   * @returns {Object[]} Array data terfilter dan tersortir
   */
  getFilteredAndSortedData() {
    const favorites = new Set(window.AppStorage ? window.AppStorage.getFavorites() : []);
    const q = this.state.search.trim().toLowerCase();

    // 1. Filtering
    const filtered = this.allData.filter(item => {
      // Filter Bookmark / Favorit
      if (this.state.onlyFavorites && !favorites.has(item.id)) {
        return false;
      }

      // Filter Jabodetabek
      if (this.state.jabodetabek === 'yes' && !item.is_jabodetabek) return false;
      if (this.state.jabodetabek === 'no' && item.is_jabodetabek) return false;

      // Filter Sektor
      if (this.state.sector === 'gov' && !item.is_government) return false;
      if (this.state.sector === 'corp' && item.is_government) return false;

      // Filter Tier
      if (this.state.tier !== 'all' && String(item.tier) !== String(this.state.tier)) {
        return false;
      }

      // Filter Provinsi
      if (this.state.province !== 'all' && item.province !== this.state.province) {
        return false;
      }

      // Filter Kota
      if (this.state.city !== 'all' && item.city_name !== this.state.city) {
        return false;
      }

      // Filter Kuota Lowongan
      const vac = item.total_active_vacancies || 0;
      if (this.state.vacancyRange === 'massive' && vac <= 50) return false;
      if (this.state.vacancyRange === 'large' && (vac < 21 || vac > 50)) return false;
      if (this.state.vacancyRange === 'medium' && (vac < 6 || vac > 20)) return false;
      if (this.state.vacancyRange === 'small' && (vac < 1 || vac > 5)) return false;

      // Filter Tag Kategori
      if (this.state.selectedTags.size > 0) {
        const itemTags = new Set(item.category_tags || []);
        let hasAllTags = true;
        for (const tag of this.state.selectedTags) {
          if (!itemTags.has(tag)) {
            hasAllTags = false;
            break;
          }
        }
        if (!hasAllTags) return false;
      }

      // Filter Keyword Search
      if (q) {
        const nameMatch = (item.name || '').toLowerCase().includes(q);
        const cityMatch = (item.city_name || '').toLowerCase().includes(q);
        const provMatch = (item.province || '').toLowerCase().includes(q);
        const addrMatch = (item.address || '').toLowerCase().includes(q);
        const descMatch = (item.description || '').toLowerCase().includes(q);
        const typeMatch = (item.type || '').toLowerCase().includes(q);
        
        if (!nameMatch && !cityMatch && !provMatch && !addrMatch && !descMatch && !typeMatch) {
          return false;
        }
      }

      return true;
    });

    // 2. Sorting
    filtered.sort((a, b) => {
      switch (this.state.sort) {
        case 'tier_desc': {
          // Tier 1 -> Tier 2 -> Tier 3
          if (a.tier !== b.tier) return a.tier - b.tier; // 1 duluan, lalu 2, lalu 3
          // Jika tier sama, urutkan dari lowongan terbanyak
          return (b.total_active_vacancies || 0) - (a.total_active_vacancies || 0);
        }
        case 'tier_asc': {
          // Tier 3 -> Tier 2 -> Tier 1
          if (a.tier !== b.tier) return b.tier - a.tier;
          return (b.total_active_vacancies || 0) - (a.total_active_vacancies || 0);
        }
        case 'vacancies_desc': {
          // Lowongan terbanyak
          const diff = (b.total_active_vacancies || 0) - (a.total_active_vacancies || 0);
          if (diff !== 0) return diff;
          return a.tier - b.tier;
        }
        case 'vacancies_asc': {
          // Lowongan tersedikit
          return (a.total_active_vacancies || 0) - (b.total_active_vacancies || 0);
        }
        case 'name_asc': {
          return (a.name || '').localeCompare(b.name || '', 'id', { sensitivity: 'base' });
        }
        case 'name_desc': {
          return (b.name || '').localeCompare(a.name || '', 'id', { sensitivity: 'base' });
        }
        case 'city_asc': {
          const cityComp = (a.city_name || '').localeCompare(b.city_name || '', 'id');
          if (cityComp !== 0) return cityComp;
          return (a.name || '').localeCompare(b.name || '', 'id');
        }
        default:
          return 0;
      }
    });

    return filtered;
  }

  /**
   * Menghitung statistik ringkas dari dataset hasil filter
   * @param {Object[]} filteredData 
   * @returns {Object}
   */
  calculateStats(filteredData) {
    const total = filteredData.length;
    let totalVacancies = 0;
    let jaboCount = 0;
    let govCount = 0;

    for (const item of filteredData) {
      totalVacancies += (item.total_active_vacancies || 0);
      if (item.is_jabodetabek) jaboCount++;
      if (item.is_government) govCount++;
    }

    const corpCount = total - govCount;
    const jaboPct = total > 0 ? Math.round((jaboCount / total) * 100) : 0;

    return {
      total,
      totalVacancies,
      jaboCount,
      jaboPct,
      govCount,
      corpCount
    };
  }

  /**
   * Ekspor data terfilter ke format CSV
   * @param {Object[]} dataToExport 
   * @returns {string} CSV text string
   */
  exportToCSV(dataToExport) {
    const headers = [
      'ID',
      'Nama Penyelenggara',
      'Sektor',
      'Tipe Organisasi',
      'Tier',
      'Total Lowongan Aktif',
      'Jabodetabek',
      'Kota / Kabupaten',
      'Provinsi',
      'Alamat',
      'Link Maganghub'
    ];

    const rows = dataToExport.map(item => [
      item.id,
      item.name,
      item.sector,
      item.type,
      item.tier_label || `Tier ${item.tier}`,
      item.total_active_vacancies,
      item.is_jabodetabek ? 'Ya (Jabodetabek)' : 'Bukan Jabodetabek',
      item.city_name,
      item.province,
      item.address,
      item.url
    ]);

    const escapeCsv = (str) => {
      if (str === null || str === undefined) return '""';
      const s = String(str).replace(/"/g, '""');
      return `"${s}"`;
    };

    const csvContent = [
      headers.map(escapeCsv).join(','),
      ...rows.map(row => row.map(escapeCsv).join(','))
    ].join('\r\n');

    return csvContent;
  }
}

window.FilterEngine = FilterEngine;
