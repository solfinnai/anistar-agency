const search = document.getElementById('q');
const filter = document.getElementById('division-filter');
const divisions = [...document.querySelectorAll('.division')];
const resultCount = document.getElementById('result-count');
const emptyState = document.getElementById('none');
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.getElementById('primary-nav');

function updateDirectory() {
  const term = search.value.trim().toLowerCase();
  let visibleCategories = 0;

  divisions.forEach((division) => {
    const inDivision = filter.value === 'all' || filter.value === division.dataset.division;
    let matches = 0;

    division.querySelectorAll('.category').forEach((category) => {
      const match = !term || category.dataset.search.includes(term);
      category.hidden = !match;
      if (match) matches += 1;
    });

    division.hidden = !inDivision || matches === 0;
    if (!division.hidden) {
      visibleCategories += matches;
      if (term || filter.value !== 'all') division.open = true;
    }
  });

  resultCount.textContent = `Showing ${visibleCategories} ${visibleCategories === 1 ? 'specialty' : 'specialties'}`;
  emptyState.hidden = visibleCategories > 0;
}

search.addEventListener('input', updateDirectory);
filter.addEventListener('change', updateDirectory);

menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  navigation.classList.toggle('open', open);
});

navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'Open navigation');
  navigation.classList.remove('open');
}));
