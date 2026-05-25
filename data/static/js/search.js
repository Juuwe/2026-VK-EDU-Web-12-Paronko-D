document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchDropdown = document.getElementById('search-results-dropdown');

    if (!searchInput || !searchDropdown) return;

    let currentAbortController = null;

    const debounce = (fn, delay = 300) => {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn.apply(this, args), delay);
        };
    };

    const performSearch = async (query) => {
        if (query.length < 2) {
            searchDropdown.classList.remove('show');
            return;
        }

        if (currentAbortController) {
            currentAbortController.abort();
        }

        currentAbortController = new AbortController();
        const signal = currentAbortController.signal;

        try {
            const response = await fetch(`/api/questions/search/?q=${encodeURIComponent(query)}`, { signal });
            if (!response.ok) throw new Error('Ошибка сети');

            const data = await response.json();

            searchDropdown.innerHTML = '';

            if (data.results && data.results.length > 0) {
                data.results.forEach(item => {
                    searchDropdown.insertAdjacentHTML('beforeend', `
                        <li><a class="dropdown-item text-truncate" href="${item.url}">${item.title}</a></li>
                    `);
                });
            } else {
                searchDropdown.insertAdjacentHTML('beforeend', `
                    <li><span class="dropdown-item-text text-muted">Ничего не найдено</span></li>
                `);
            }

            searchDropdown.classList.add('show');

        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            
            console.error('Ошибка поиска:', error);
        }
    };

    searchInput.addEventListener('input', debounce((e) => {
        performSearch(e.target.value.trim());
    }, 300));

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
            searchDropdown.classList.remove('show');
        }
    });
});
