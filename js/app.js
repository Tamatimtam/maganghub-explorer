/**
 * app.js - UI Controller & Event Handling (Minimalist & Clean)
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Elements Reference
  const elThemeToggle = document.getElementById('btn-theme-toggle');
  const elSearchInput = document.getElementById('search-input');
  const elSearchClear = document.getElementById('search-clear-btn');
  const elSortSelect = document.getElementById('sort-select');
  const elTierSelect = document.getElementById('tier-select');
  const elProvinceSelect = document.getElementById('province-select');
  const elCitySelect = document.getElementById('city-select');
  const elVacancyRangeSelect = document.getElementById('vacancy-range-select');
  const elPerPageSelect = document.getElementById('per-page-select');
  const elCategoryPills = document.getElementById('category-pills');
  const elResetFilters = document.getElementById('btn-reset-filters');
  const elEmptyReset = document.getElementById('btn-empty-reset');
  const elFavToggle = document.getElementById('btn-favorites-toggle');
  const elFavBadge = document.getElementById('fav-count-badge');
  const elBtnExport = document.getElementById('btn-export');
  const elBtnToggleAdv = document.getElementById('btn-toggle-advanced');
  const elAdvDrawer = document.getElementById('advanced-filters-drawer');

  // Summary Elements
  const elHeadline = document.getElementById('results-headline');
  const elCounter = document.getElementById('results-counter');
  const elCompaniesGrid = document.getElementById('companies-grid');
  const elEmptyState = document.getElementById('empty-state');
  const elActiveChipsBar = document.getElementById('active-chips-bar');
  const elActiveChipsList = document.getElementById('active-chips-list');
  const elBtnClearAllChips = document.getElementById('btn-clear-all-chips');

  // Pagination Elements
  const elPaginationNav = document.getElementById('pagination-nav');
  const elBtnPrevPage = document.getElementById('btn-prev-page');
  const elBtnNextPage = document.getElementById('btn-next-page');
  const elPageNumbers = document.getElementById('page-numbers');

  // Modal Elements
  const elModalBackdrop = document.getElementById('detail-modal-backdrop');
  const elModalClose = document.getElementById('modal-close-btn');
  const elModalLogoWrap = document.getElementById('modal-logo-wrap');
  const elModalBadges = document.getElementById('modal-badges');
  const elModalTitle = document.getElementById('modal-title');
  const elModalType = document.getElementById('modal-type');
  const elModalVacancies = document.getElementById('modal-vacancies');
  const elModalRegion = document.getElementById('modal-region');
  const elModalTier = document.getElementById('modal-tier');
  const elModalDesc = document.getElementById('modal-desc');
  const elModalAddress = document.getElementById('modal-address');
  const elModalReasonsTags = document.getElementById('modal-reasons-tags');
  const elModalBtnFav = document.getElementById('modal-btn-fav');
  const elModalFavText = document.getElementById('modal-fav-text');
  const elModalLinkMaganghub = document.getElementById('modal-link-maganghub');
  const elBtnCopyAddress = document.getElementById('btn-copy-address');
  const elLinkGmaps = document.getElementById('link-gmaps');
  const elToastContainer = document.getElementById('toast-container');

  // State Management
  let allData = [];
  let engine = null;
  let currentPage = 1;
  let itemsPerPage = 24;
  let activeModalItem = null;
  let searchDebounceTimer = null;

  // 1. Theme (Default to Light Mode)
  function initTheme() {
    let saved = window.AppStorage.getTheme();
    if (!saved || saved === 'dark') {
      saved = 'light';
      window.AppStorage.setTheme('light');
    }
    document.documentElement.setAttribute('data-theme', 'light');
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    window.AppStorage.setTheme(next);
  }
  elThemeToggle.addEventListener('click', toggleTheme);
  initTheme();

  // 2. Toast Notifications
  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    elToastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(6px)';
      toast.style.transition = 'all 150ms ease';
      setTimeout(() => toast.remove(), 150);
    }, 2000);
  }

  // 3. Load Data
  async function loadInitialData() {
    if (window.PENYELENGGARA_DATA && Array.isArray(window.PENYELENGGARA_DATA)) {
      return window.PENYELENGGARA_DATA;
    }
    try {
      const res = await fetch('data/penyelenggara_enriched.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('Gagal memuat via fetch, mencoba fallback...', e);
      const res2 = await fetch('penyelenggara.json');
      return await res2.json();
    }
  }

  allData = await loadInitialData();
  engine = new window.FilterEngine(allData);

  // 4. Populate Dropdowns (Provinsi & Kota)
  function populateLocationDropdowns() {
    const provinces = new Set();
    for (const d of allData) {
      if (d.province) provinces.add(d.province);
    }

    const sortedProvinces = Array.from(provinces).sort((a, b) => {
      if (a === 'DKI Jakarta') return -1;
      if (b === 'DKI Jakarta') return 1;
      if (a === 'Jawa Barat') return -1;
      if (b === 'Jawa Barat') return 1;
      return a.localeCompare(b, 'id');
    });

    elProvinceSelect.innerHTML = '<option value="all">Semua Provinsi</option>';
    for (const prov of sortedProvinces) {
      const count = allData.filter(d => d.province === prov).length;
      const opt = document.createElement('option');
      opt.value = prov;
      opt.textContent = `${prov} (${count})`;
      elProvinceSelect.appendChild(opt);
    }

    updateCityDropdown();
  }

  function updateCityDropdown() {
    const selectedProv = elProvinceSelect.value;
    const citiesCount = new Map();

    for (const d of allData) {
      if (selectedProv !== 'all' && d.province !== selectedProv) continue;
      if (!d.city_name) continue;
      citiesCount.set(d.city_name, (citiesCount.get(d.city_name) || 0) + 1);
    }

    const sortedCities = Array.from(citiesCount.entries()).sort((a, b) => b[1] - a[1]);

    elCitySelect.innerHTML = '<option value="all">Semua Kota</option>';
    for (const [cityName, count] of sortedCities) {
      const opt = document.createElement('option');
      opt.value = cityName;
      opt.textContent = `${cityName} (${count})`;
      elCitySelect.appendChild(opt);
    }
  }

  populateLocationDropdowns();

  // 5. Update Favorite Badge Count
  function updateFavoritesCount() {
    const count = window.AppStorage.getFavorites().length;
    elFavBadge.textContent = count;
    if (engine.state.onlyFavorites) {
      elFavToggle.classList.add('active');
    } else {
      elFavToggle.classList.remove('active');
    }
  }
  updateFavoritesCount();

  // 6. Advanced Drawer Toggle
  elBtnToggleAdv.addEventListener('click', () => {
    const isHidden = elAdvDrawer.classList.contains('hidden');
    elAdvDrawer.classList.toggle('hidden', !isHidden);
    elBtnToggleAdv.classList.toggle('open', isHidden);
    elBtnToggleAdv.setAttribute('aria-expanded', String(isHidden));
  });

  // 7. Quick Filter Pills Handler
  const quickPillButtons = document.querySelectorAll('.pill[data-filter]');
  function syncQuickPills() {
    quickPillButtons.forEach(btn => {
      const filter = btn.dataset.filter;
      let isActive = false;
      if (filter === 'all') {
        isActive = engine.state.jabodetabek === 'all' && 
                   engine.state.sector === 'all' && 
                   engine.state.tier === 'all' && 
                   engine.state.vacancyRange === 'all' &&
                   !engine.state.onlyFavorites;
      } else if (filter === 'jabo') {
        isActive = engine.state.jabodetabek === 'yes';
      } else if (filter === 'luar-jabo') {
        isActive = engine.state.jabodetabek === 'no';
      } else if (filter === 'gov') {
        isActive = engine.state.sector === 'gov';
      } else if (filter === 'corp') {
        isActive = engine.state.sector === 'corp';
      } else if (filter === 'tier-1') {
        isActive = String(engine.state.tier) === '1';
      } else if (filter === 'massive') {
        isActive = engine.state.vacancyRange === 'massive';
      }
      btn.classList.toggle('active', isActive);
    });
  }

  quickPillButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      if (filter === 'all') {
        engine.updateState({
          jabodetabek: 'all',
          sector: 'all',
          tier: 'all',
          vacancyRange: 'all',
          onlyFavorites: false
        });
        elTierSelect.value = 'all';
        elVacancyRangeSelect.value = 'all';
      } else if (filter === 'jabo') {
        const next = engine.state.jabodetabek === 'yes' ? 'all' : 'yes';
        engine.updateState({ jabodetabek: next });
      } else if (filter === 'luar-jabo') {
        const next = engine.state.jabodetabek === 'no' ? 'all' : 'no';
        engine.updateState({ jabodetabek: next });
      } else if (filter === 'gov') {
        const next = engine.state.sector === 'gov' ? 'all' : 'gov';
        engine.updateState({ sector: next });
      } else if (filter === 'corp') {
        const next = engine.state.sector === 'corp' ? 'all' : 'corp';
        engine.updateState({ sector: next });
      } else if (filter === 'tier-1') {
        const next = String(engine.state.tier) === '1' ? 'all' : '1';
        engine.updateState({ tier: next });
        elTierSelect.value = next;
      } else if (filter === 'massive') {
        const next = engine.state.vacancyRange === 'massive' ? 'all' : 'massive';
        engine.updateState({ vacancyRange: next });
        elVacancyRangeSelect.value = next;
      }

      currentPage = 1;
      renderApp();
    });
  });

  // 8. Render Active Filter Chips
  function renderActiveChips() {
    elActiveChipsList.innerHTML = '';
    const chips = [];

    if (engine.state.search) {
      chips.push({ label: `Kata kunci: "${engine.state.search}"`, clear: () => {
        engine.updateState({ search: '' });
        elSearchInput.value = '';
        elSearchClear.classList.add('hidden');
      }});
    }

    if (engine.state.jabodetabek === 'yes') {
      chips.push({ label: 'Jabodetabek', clear: () => engine.updateState({ jabodetabek: 'all' })});
    } else if (engine.state.jabodetabek === 'no') {
      chips.push({ label: 'Luar Jabodetabek', clear: () => engine.updateState({ jabodetabek: 'all' })});
    }

    if (engine.state.sector === 'gov') {
      chips.push({ label: 'Instansi Pemerintah', clear: () => engine.updateState({ sector: 'all' })});
    } else if (engine.state.sector === 'corp') {
      chips.push({ label: 'Swasta & BUMN', clear: () => engine.updateState({ sector: 'all' })});
    }

    if (engine.state.tier !== 'all') {
      chips.push({ label: `Tier ${engine.state.tier}`, clear: () => {
        engine.updateState({ tier: 'all' });
        elTierSelect.value = 'all';
      }});
    }

    if (engine.state.province !== 'all') {
      chips.push({ label: `Provinsi: ${engine.state.province}`, clear: () => {
        engine.updateState({ province: 'all' });
        elProvinceSelect.value = 'all';
        updateCityDropdown();
      }});
    }

    if (engine.state.city !== 'all') {
      chips.push({ label: `Kota: ${engine.state.city}`, clear: () => {
        engine.updateState({ city: 'all' });
        elCitySelect.value = 'all';
      }});
    }

    if (engine.state.vacancyRange !== 'all') {
      const labels = {
        massive: 'Lowongan > 50',
        large: 'Lowongan 21-50',
        medium: 'Lowongan 6-20',
        small: 'Lowongan 1-5'
      };
      chips.push({ label: labels[engine.state.vacancyRange] || 'Kuota', clear: () => {
        engine.updateState({ vacancyRange: 'all' });
        elVacancyRangeSelect.value = 'all';
      }});
    }

    if (engine.state.onlyFavorites) {
      chips.push({ label: 'Favorit', clear: () => {
        engine.updateState({ onlyFavorites: false });
        updateFavoritesCount();
      }});
    }

    for (const tag of engine.state.selectedTags) {
      chips.push({ label: tag, clear: () => {
        engine.state.selectedTags.delete(tag);
        document.querySelectorAll(`.tag-btn[data-tag="${tag}"]`).forEach(p => p.classList.remove('active'));
      }});
    }

    if (chips.length > 0) {
      elActiveChipsBar.classList.remove('hidden');
      for (const chip of chips) {
        const item = document.createElement('div');
        item.className = 'chip-item';
        item.innerHTML = `<span>${chip.label}</span><button class="chip-remove" type="button" aria-label="Hapus filter">&times;</button>`;
        item.querySelector('.chip-remove').addEventListener('click', () => {
          chip.clear();
          currentPage = 1;
          renderApp();
        });
        elActiveChipsList.appendChild(item);
      }
    } else {
      elActiveChipsBar.classList.add('hidden');
    }
  }

  // 9. Initials Fallback
  function getInitials(name) {
    if (!name) return 'MH';
    const clean = name.replace(/^(PT|CV|PERSERO|PERUSAHAAN|KEMENTERIAN|BALAI)\s+/i, '');
    const parts = clean.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return clean.slice(0, 2).toUpperCase();
  }

  // 10. Create Company Card (Minimalist & Clean)
  function createCompanyCard(item) {
    const card = document.createElement('article');
    card.className = 'company-card';
    card.dataset.id = item.id;

    const isFav = window.AppStorage.isFavorite(item.id);

    // Badges
    let tierBadge = `<span class="clean-badge badge-tier-3">Tier 3</span>`;
    if (item.tier === 1) tierBadge = `<span class="clean-badge badge-tier-1">Tier 1</span>`;
    else if (item.tier === 2) tierBadge = `<span class="clean-badge badge-tier-2">Tier 2</span>`;

    const jaboBadge = item.is_jabodetabek 
      ? `<span class="clean-badge badge-jabo">Jabodetabek</span>`
      : `<span class="clean-badge badge-luar">Luar Jabo</span>`;

    const sectorBadge = item.is_government
      ? `<span class="clean-badge badge-gov">Pemerintah</span>`
      : `<span class="clean-badge badge-corp">Swasta/BUMN</span>`;

    // Logo
    const logoHtml = item.logo_url
      ? `<img src="${item.logo_url}" alt="Logo" class="card-logo-img" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<span class=\\'card-logo-fallback\\'>${getInitials(item.name)}</span>';">`
      : `<span class="card-logo-fallback">${getInitials(item.name)}</span>`;

    // Category tags
    const tagsHtml = (item.category_tags || []).slice(0, 2).map(tag => 
      `<span class="tag-label">${tag}</span>`
    ).join('');

    card.innerHTML = `
      <div class="card-top">
        <div class="card-logo-box">
          ${logoHtml}
        </div>
        <button class="btn-star ${isFav ? 'starred' : ''}" type="button" aria-label="${isFav ? 'Hapus dari favorit' : 'Simpan ke favorit'}">
          <svg class="icon" viewBox="0 0 24 24" fill="${isFav ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </button>
      </div>

      <div class="badges-row">
        ${tierBadge}
        ${jaboBadge}
        ${sectorBadge}
      </div>

      <div class="card-content">
        <h3 class="card-title" title="${item.name}">${item.name}</h3>
        <div class="card-meta-row">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <span>${item.city_name || item.province}</span>
        </div>
      </div>

      <div class="card-vacancies">
        <span class="text-muted">Lowongan Tersedia</span>
        <span class="vacancies-count">${item.total_active_vacancies} Posisi</span>
      </div>

      <div class="card-tags">
        ${tagsHtml}
      </div>

      <div class="card-actions">
        <button class="btn-card-detail" type="button">Detail</button>
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="btn-card-external" title="Buka di Maganghub Kemnaker">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
        </a>
      </div>
    `;

    // Listeners
    const starBtn = card.querySelector('.btn-star');
    starBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const updatedFav = window.AppStorage.toggleFavorite(item.id);
      starBtn.classList.toggle('starred', updatedFav);
      const starSvg = starBtn.querySelector('svg');
      if (updatedFav) {
        starSvg.setAttribute('fill', 'currentColor');
      } else {
        starSvg.setAttribute('fill', 'none');
      }
      updateFavoritesCount();
      showToast(updatedFav ? `Disimpan ke favorit: ${item.name}` : `Dihapus dari favorit`);

      if (engine.state.onlyFavorites && !updatedFav) {
        renderApp();
      }
    });

    const detailBtn = card.querySelector('.btn-card-detail');
    detailBtn.addEventListener('click', () => openModal(item));

    return card;
  }

  // 11. Render Grid & Pagination
  function renderApp() {
    syncQuickPills();
    renderActiveChips();

    const filtered = engine.getFilteredAndSortedData();
    const stats = engine.calculateStats(filtered);

    // Summary Text
    elHeadline.textContent = `${stats.total.toLocaleString('id-ID')} instansi`;
    elCounter.textContent = `${stats.totalVacancies.toLocaleString('id-ID')} lowongan aktif (${stats.jaboCount} di Jabodetabek, ${stats.govCount} pemerintah)`;

    const totalResults = filtered.length;

    if (totalResults === 0) {
      elCompaniesGrid.innerHTML = '';
      elEmptyState.classList.remove('hidden');
      elPaginationNav.classList.add('hidden');
      return;
    }

    elEmptyState.classList.add('hidden');

    const effectivePerPage = itemsPerPage === 'all' ? totalResults : parseInt(itemsPerPage, 10);
    const totalPages = Math.ceil(totalResults / effectivePerPage);
    if (currentPage > totalPages) currentPage = 1;

    const startIdx = (currentPage - 1) * effectivePerPage;
    const endIdx = itemsPerPage === 'all' ? totalResults : Math.min(startIdx + effectivePerPage, totalResults);
    const paginatedItems = filtered.slice(startIdx, endIdx);

    elCompaniesGrid.innerHTML = '';
    const fragment = document.createDocumentFragment();
    for (const item of paginatedItems) {
      fragment.appendChild(createCompanyCard(item));
    }
    elCompaniesGrid.appendChild(fragment);

    renderPagination(totalPages);
  }

  // 12. Pagination
  function renderPagination(totalPages) {
    if (totalPages <= 1 || itemsPerPage === 'all') {
      elPaginationNav.classList.add('hidden');
      return;
    }

    elPaginationNav.classList.remove('hidden');
    elBtnPrevPage.disabled = currentPage === 1;
    elBtnNextPage.disabled = currentPage === totalPages;

    elPageNumbers.innerHTML = '';

    let pagesToShow = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pagesToShow.push(i);
    } else {
      pagesToShow.push(1);
      if (currentPage > 3) pagesToShow.push('...');
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      for (let i = start; i <= end; i++) pagesToShow.push(i);
      if (currentPage < totalPages - 2) pagesToShow.push('...');
      pagesToShow.push(totalPages);
    }

    for (const p of pagesToShow) {
      if (p === '...') {
        const elEllipsis = document.createElement('span');
        elEllipsis.className = 'page-ellipsis';
        elEllipsis.textContent = '...';
        elPageNumbers.appendChild(elEllipsis);
      } else {
        const btn = document.createElement('button');
        btn.className = `page-num ${p === currentPage ? 'active' : ''}`;
        btn.textContent = p;
        btn.type = 'button';
        btn.addEventListener('click', () => {
          currentPage = p;
          renderApp();
          window.scrollTo({ top: elHeadline.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
        });
        elPageNumbers.appendChild(btn);
      }
    }
  }

  elBtnPrevPage.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      renderApp();
      window.scrollTo({ top: elHeadline.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
    }
  });

  elBtnNextPage.addEventListener('click', () => {
    currentPage++;
    renderApp();
    window.scrollTo({ top: elHeadline.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
  });

  // 13. Modal Management
  function openModal(item) {
    activeModalItem = item;

    // Badges
    let tierBadge = `<span class="clean-badge badge-tier-3">Tier 3</span>`;
    if (item.tier === 1) tierBadge = `<span class="clean-badge badge-tier-1">Tier 1: High Tier</span>`;
    else if (item.tier === 2) tierBadge = `<span class="clean-badge badge-tier-2">Tier 2: Mid Tier</span>`;

    const jaboBadge = item.is_jabodetabek 
      ? `<span class="clean-badge badge-jabo">Jabodetabek</span>`
      : `<span class="clean-badge badge-luar">Luar Jabodetabek</span>`;

    const sectorBadge = item.is_government
      ? `<span class="clean-badge badge-gov">Instansi Pemerintah</span>`
      : `<span class="clean-badge badge-corp">Swasta / BUMN</span>`;

    elModalBadges.innerHTML = `${tierBadge} ${jaboBadge} ${sectorBadge}`;
    elModalTitle.textContent = item.name;
    elModalType.textContent = `${item.type} • ${item.province}`;

    // Logo
    if (item.logo_url) {
      elModalLogoWrap.innerHTML = `<img src="${item.logo_url}" alt="Logo" class="card-logo-img" onerror="this.onerror=null; this.parentElement.innerHTML='<span class=\\'card-logo-fallback\\'>${getInitials(item.name)}</span>';">`;
    } else {
      elModalLogoWrap.innerHTML = `<span class="card-logo-fallback">${getInitials(item.name)}</span>`;
    }

    // Metrics
    elModalVacancies.textContent = `${item.total_active_vacancies} Posisi`;
    elModalRegion.textContent = `${item.city_name || '-'}`;
    elModalTier.textContent = item.tier_label || `Tier ${item.tier}`;

    // Description
    if (item.description && item.description.trim()) {
      elModalDesc.textContent = item.description;
    } else {
      elModalDesc.innerHTML = `<em>Instansi belum menyertakan deskripsi pada profil Kemnaker. Silakan cek lowongan di tautan resmi Maganghub.</em>`;
    }

    // Address & Links
    elModalAddress.textContent = item.address || 'Alamat kantor tidak dicantumkan secara lengkap.';
    elModalLinkMaganghub.href = item.url;
    elLinkGmaps.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((item.name + ' ' + (item.address || item.city_name)).trim())}`;

    // Reasons
    elModalReasonsTags.innerHTML = '';
    const reasons = item.tier_reasons || [];
    for (const r of reasons) {
      const tag = document.createElement('span');
      tag.className = 'clean-badge badge-tier-1';
      tag.textContent = r;
      elModalReasonsTags.appendChild(tag);
    }
    for (const t of (item.category_tags || [])) {
      const tag = document.createElement('span');
      tag.className = 'clean-badge badge-corp';
      tag.textContent = t;
      elModalReasonsTags.appendChild(tag);
    }

    updateModalFavButton();
    elModalBackdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    elModalBackdrop.classList.add('hidden');
    document.body.style.overflow = '';
    activeModalItem = null;
  }

  function updateModalFavButton() {
    if (!activeModalItem) return;
    const isFav = window.AppStorage.isFavorite(activeModalItem.id);
    const favSvg = elModalBtnFav.querySelector('svg');
    if (isFav) {
      favSvg.setAttribute('fill', 'currentColor');
      elModalFavText.textContent = 'Hapus dari Favorit';
    } else {
      favSvg.setAttribute('fill', 'none');
      elModalFavText.textContent = 'Simpan Favorit';
    }
  }

  elModalClose.addEventListener('click', closeModal);
  elModalBackdrop.addEventListener('click', (e) => {
    if (e.target === elModalBackdrop) closeModal();
  });
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !elModalBackdrop.classList.contains('hidden')) {
      closeModal();
    }
  });

  elModalBtnFav.addEventListener('click', () => {
    if (!activeModalItem) return;
    const updated = window.AppStorage.toggleFavorite(activeModalItem.id);
    updateModalFavButton();
    updateFavoritesCount();
    showToast(updated ? `Disimpan ke favorit` : `Dihapus dari favorit`);
    renderApp();
  });

  elBtnCopyAddress.addEventListener('click', () => {
    if (!activeModalItem || !activeModalItem.address) return;
    navigator.clipboard.writeText(activeModalItem.address).then(() => {
      showToast('Alamat disalin ke clipboard');
    }).catch(() => {
      showToast('Gagal menyalin alamat');
    });
  });

  // 14. Event Listeners for Filters
  elSearchInput.addEventListener('input', (e) => {
    const val = e.target.value;
    if (val) elSearchClear.classList.remove('hidden');
    else elSearchClear.classList.add('hidden');

    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      engine.updateState({ search: val });
      currentPage = 1;
      renderApp();
    }, 180);
  });

  elSearchClear.addEventListener('click', () => {
    elSearchInput.value = '';
    elSearchClear.classList.add('hidden');
    engine.updateState({ search: '' });
    currentPage = 1;
    renderApp();
  });

  elSortSelect.addEventListener('change', (e) => {
    engine.updateState({ sort: e.target.value });
    currentPage = 1;
    renderApp();
  });

  elTierSelect.addEventListener('change', (e) => {
    engine.updateState({ tier: e.target.value });
    currentPage = 1;
    renderApp();
  });

  elProvinceSelect.addEventListener('change', (e) => {
    engine.updateState({ province: e.target.value, city: 'all' });
    updateCityDropdown();
    currentPage = 1;
    renderApp();
  });

  elCitySelect.addEventListener('change', (e) => {
    engine.updateState({ city: e.target.value });
    currentPage = 1;
    renderApp();
  });

  elVacancyRangeSelect.addEventListener('change', (e) => {
    engine.updateState({ vacancyRange: e.target.value });
    currentPage = 1;
    renderApp();
  });

  elPerPageSelect.addEventListener('change', (e) => {
    itemsPerPage = e.target.value;
    currentPage = 1;
    renderApp();
  });

  // Category Pills Toggle
  elCategoryPills.addEventListener('click', (e) => {
    const pill = e.target.closest('.tag-btn');
    if (!pill) return;
    const tag = pill.dataset.tag;
    if (engine.state.selectedTags.has(tag)) {
      engine.state.selectedTags.delete(tag);
      pill.classList.remove('active');
    } else {
      engine.state.selectedTags.add(tag);
      pill.classList.add('active');
    }
    currentPage = 1;
    renderApp();
  });

  // Reset All
  function resetAllFilters() {
    engine.reset();
    elSearchInput.value = '';
    elSearchClear.classList.add('hidden');
    elSortSelect.value = 'tier_desc';
    elTierSelect.value = 'all';
    elProvinceSelect.value = 'all';
    updateCityDropdown();
    elCitySelect.value = 'all';
    elVacancyRangeSelect.value = 'all';
    document.querySelectorAll('.tag-btn').forEach(p => p.classList.remove('active'));
    updateFavoritesCount();
    currentPage = 1;
    renderApp();
    showToast('Filter direset');
  }

  elResetFilters.addEventListener('click', resetAllFilters);
  elEmptyReset.addEventListener('click', resetAllFilters);
  elBtnClearAllChips.addEventListener('click', resetAllFilters);

  // Favorites Toggle in Header
  elFavToggle.addEventListener('click', () => {
    engine.updateState({ onlyFavorites: !engine.state.onlyFavorites });
    updateFavoritesCount();
    currentPage = 1;
    renderApp();
  });

  // Export CSV
  elBtnExport.addEventListener('click', () => {
    const filtered = engine.getFilteredAndSortedData();
    if (filtered.length === 0) {
      showToast('Tidak ada data untuk diekspor');
      return;
    }

    const csvData = engine.exportToCSV(filtered);
    const blob = new Blob(['\uFEFF' + csvData], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const timestamp = new Date().toISOString().slice(0, 10);
    link.download = `penyelenggara_maganghub_${timestamp}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    showToast(`${filtered.length.toLocaleString('id-ID')} instansi diekspor ke CSV`);
  });

  // Render initial
  renderApp();
});
