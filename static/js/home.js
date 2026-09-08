(() => {
    const menu = document.querySelector('.mobile-menu');
    if (!menu) return;
    const trigger = menu.querySelector('summary');
    menu.addEventListener('toggle', () => trigger.setAttribute('aria-expanded', String(menu.open)));
    trigger.setAttribute('aria-expanded', String(menu.open));
    menu.addEventListener('click', (event) => {
        const link = event.target.closest('a');
        if (!link) return;
        menu.open = false;
        const href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
            const target = document.getElementById(href.slice(1));
            if (target) {
                target.setAttribute('tabindex', '-1');
                target.focus({ preventScroll: true });
            }
        }
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && menu.open) {
            menu.open = false;
            trigger.focus();
        }
    });
    document.addEventListener('click', (event) => {
        if (menu.open && !menu.contains(event.target)) menu.open = false;
        document.querySelectorAll('.nav-user-dropdown[open]').forEach((dropdown) => {
            if (!dropdown.contains(event.target)) dropdown.open = false;
        });
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', (event) => {
        if (event.matches) menu.open = false;
    });
})();
