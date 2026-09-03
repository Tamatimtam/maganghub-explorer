/**
 * storage.js - LocalStorage Helper
 * Mengelola penyimpanan lokal untuk data favorit dan preferensi tema.
 */

const STORAGE_KEYS = {
  FAVORITES: 'maganghub_favorites',
  THEME: 'maganghub_theme'
};

const AppStorage = {
  /**
   * Mengambil daftar ID instansi yang ditandai favorit
   * @returns {string[]} Array of company IDs
   */
  getFavorites() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.FAVORITES);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.warn('Gagal membaca favorit dari localStorage:', e);
      return [];
    }
  },

  /**
   * Menambahkan atau menghapus ID instansi dari daftar favorit
   * @param {string} id Company ID
   * @returns {boolean} True jika sekarang favorit, false jika dihapus
   */
  toggleFavorite(id) {
    if (!id) return false;
    const favorites = new Set(this.getFavorites());
    let isFav = false;
    if (favorites.has(id)) {
      favorites.delete(id);
      isFav = false;
    } else {
      favorites.add(id);
      isFav = true;
    }
    try {
      localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(Array.from(favorites)));
    } catch (e) {
      console.warn('Gagal menyimpan favorit ke localStorage:', e);
    }
    return isFav;
  },

  /**
   * Mengecek apakah sebuah instansi favorit
   * @param {string} id Company ID
   * @returns {boolean}
   */
  isFavorite(id) {
    const favorites = new Set(this.getFavorites());
    return favorites.has(id);
  },

  /**
   * Mengambil preferensi tema ('light' atau 'dark', default: 'light')
   * @returns {string}
   */
  getTheme() {
    try {
      return localStorage.getItem(STORAGE_KEYS.THEME) || 'light';
    } catch (e) {
      return 'light';
    }
  },

  /**
   * Menyimpan preferensi tema
   * @param {string} theme 'dark' atau 'light'
   */
  setTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEYS.THEME, theme);
    } catch (e) {
      console.warn('Gagal menyimpan preferensi tema:', e);
    }
  }
};

window.AppStorage = AppStorage;
