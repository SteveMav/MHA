/**
 * Magic Hoops Academy - High-Performance Responsive Lightbox
 */
document.addEventListener('DOMContentLoaded', function () {
    const triggers = Array.from(document.querySelectorAll('.mha-lightbox-trigger'));
    const modal = document.getElementById('mhaLightbox');
    if (!modal || triggers.length === 0) return;

    const img = document.getElementById('mhaLightboxImg');
    const title = document.getElementById('mhaLightboxTitle');
    const album = document.getElementById('mhaLightboxAlbum');
    const counter = document.getElementById('mhaLightboxCounter');
    const closeBtn = modal.querySelector('.mha-lightbox-close');
    const prevBtn = modal.querySelector('.mha-lightbox-prev');
    const nextBtn = modal.querySelector('.mha-lightbox-next');

    let currentIndex = 0;
    let touchStartX = 0;
    let touchEndX = 0;

    function showPhoto(index) {
        if (index < 0) index = triggers.length - 1;
        if (index >= triggers.length) index = 0;
        currentIndex = index;

        const trigger = triggers[currentIndex];
        const fullUrl = trigger.getAttribute('data-full');
        const captionText = trigger.getAttribute('data-caption') || '';
        const legendText = trigger.getAttribute('data-legend') || '';
        const albumName = trigger.getAttribute('data-album') || '';
        const dateText = trigger.getAttribute('data-date') || '';

        img.src = fullUrl;
        img.alt = captionText;

        let displayTitle = captionText;
        if (legendText && legendText !== captionText) {
            displayTitle += ` — <span style="font-weight:normal; font-size: 0.9em; opacity:0.85;">${legendText}</span>`;
        }
        title.innerHTML = displayTitle;

        let metaInfo = '';
        if (albumName) metaInfo += `📁 ${albumName}`;
        if (dateText) metaInfo += ` &bull; 🗓️ ${dateText}`;
        album.innerHTML = metaInfo;

        counter.textContent = `${currentIndex + 1} / ${triggers.length}`;
    }

    function openModal(index) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        showPhoto(index);
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        img.src = '';
    }

    triggers.forEach((trigger, idx) => {
        trigger.addEventListener('click', () => openModal(idx));
    });

    closeBtn.addEventListener('click', closeModal);
    prevBtn.addEventListener('click', () => showPhoto(currentIndex - 1));
    nextBtn.addEventListener('click', () => showPhoto(currentIndex + 1));

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (!modal.classList.contains('active')) return;
        if (e.key === 'Escape') closeModal();
        if (e.key === 'ArrowLeft') showPhoto(currentIndex - 1);
        if (e.key === 'ArrowRight') showPhoto(currentIndex + 1);
    });

    // Touch support for mobile swipe
    modal.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    modal.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const threshold = 50;
        if (touchEndX < touchStartX - threshold) {
            showPhoto(currentIndex + 1); // Swipe left -> Next
        }
        if (touchEndX > touchStartX + threshold) {
            showPhoto(currentIndex - 1); // Swipe right -> Prev
        }
    }
});
