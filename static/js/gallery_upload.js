/**
 * Magic Hoops Academy - Asynchronous Photo Uploader
 * Téléversement photo par photo avec calcul du pourcentage global en temps réel,
 * prévisualisations, optimisation client-side, limite stricte de 2 Mo et suppression des timeouts.
 */

(function () {
    'use strict';

    const MAX_ALLOWED_FILE_SIZE = 2 * 1024 * 1024; // Limite stricte : 2 Mo (2 097 152 octets)

    function formatBytes(bytes, decimals = 1) {
        if (!bytes || bytes === 0) return '0 Octet';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Octets', 'Ko', 'Mo', 'Go'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    /**
     * Compression/redimensionnement d'image via Canvas côté navigateur.
     * Réduit considérablement la taille des photos 48MP de smartphone (de ~12 Mo à ~800 Ko)
     * tout en conservant une excellente résolution (jusqu'à 2560px).
     */
    function compressImage(file, maxWidth = 2560, maxHeight = 2560, quality = 0.86) {
        return new Promise((resolve) => {
            if (!file.type.startsWith('image/') || file.type === 'image/gif' || file.type === 'image/svg+xml') {
                return resolve(file);
            }

            const reader = new FileReader();
            reader.onload = function (e) {
                const img = new Image();
                img.onload = function () {
                    let width = img.width;
                    let height = img.height;

                    if (width <= maxWidth && height <= maxHeight && file.size < 1.2 * 1024 * 1024) {
                        return resolve(file);
                    }

                    if (width > height) {
                        if (width > maxWidth) {
                            height = Math.round((height * maxWidth) / width);
                            width = maxWidth;
                        }
                    } else {
                        if (height > maxHeight) {
                            width = Math.round((width * maxHeight) / height);
                            height = maxHeight;
                        }
                    }

                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);

                    canvas.toBlob(
                        function (blob) {
                            if (!blob || blob.size >= file.size) {
                                resolve(file);
                            } else {
                                const optimized = new File([blob], file.name.replace(/\.[^/.]+$/, "") + ".jpg", {
                                    type: 'image/jpeg',
                                    lastModified: Date.now()
                                });
                                resolve(optimized);
                            }
                        },
                        'image/jpeg',
                        quality
                    );
                };
                img.onerror = () => resolve(file);
                img.src = e.target.result;
            };
            reader.onerror = () => resolve(file);
            reader.readAsDataURL(file);
        });
    }

    /**
     * Garantit que le fichier envoyé respecte la limite stricte de 2 Mo.
     * Si shouldOptimize est activé, compresse et adapte la résolution pour passer sous les 2 Mo.
     * Si l'optimisation est désactivée et que le fichier fait > 2 Mo, une exception explicite est levée.
     */
    async function prepareImageUnder2MB(file, shouldOptimize = true) {
        if (!shouldOptimize) {
            if (file.size > MAX_ALLOWED_FILE_SIZE) {
                throw new Error(`La photo fait ${formatBytes(file.size)}, ce qui dépasse la limite maximale de 2 Mo. Veuillez activer l'optimisation web pour la compresser automatiquement.`);
            }
            return file;
        }

        // Si déjà très léger (< 600 Ko) et conforme
        if (file.size <= MAX_ALLOWED_FILE_SIZE && file.size < 600 * 1024) {
            return file;
        }

        let maxWidth = 2560;
        let quality = 0.85;
        let processed = await compressImage(file, maxWidth, maxWidth, quality);

        // Réduction itérative si la photo dépasse toujours 2 Mo
        let attempts = 0;
        while (processed.size > MAX_ALLOWED_FILE_SIZE && attempts < 4) {
            maxWidth = Math.round(maxWidth * 0.8);
            quality = Math.max(0.55, quality - 0.12);
            processed = await compressImage(file, maxWidth, maxWidth, quality);
            attempts++;
        }

        if (processed.size > MAX_ALLOWED_FILE_SIZE) {
            throw new Error(`Le fichier (${formatBytes(processed.size)}) dépasse la limite maximale de 2 Mo même après optimisation.`);
        }

        return processed;
    }

    /**
     * Classe gérant l'expérience d'upload dans un modal donné.
     */
    class AsyncPhotoUploader {
        constructor(container) {
            this.container = container;
            this.albumId = container.dataset.albumId;
            this.uploadUrl = container.dataset.uploadUrl;
            this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

            this.fileInput = container.querySelector('.async-file-input');
            this.dropZone = container.querySelector('.async-dropzone');
            this.previewList = container.querySelector('.async-preview-list');
            this.summaryBadge = container.querySelector('.async-summary-badge');
            this.optimizeCheckbox = container.querySelector('.async-optimize-checkbox');
            this.startBtn = container.querySelector('.async-start-btn');
            this.cancelBtn = container.querySelector('.async-cancel-btn');
            this.closeBtn = container.querySelector('.async-close-btn');

            this.progressContainer = container.querySelector('.async-progress-container');
            this.progressBar = container.querySelector('.async-progress-bar');
            this.progressPercent = container.querySelector('.async-progress-percent');
            this.progressStatus = container.querySelector('.async-progress-status');
            this.progressBytes = container.querySelector('.async-progress-bytes');
            this.successAlert = container.querySelector('.async-success-alert');

            this.filesQueue = []; // { file, status, loadedBytes, totalBytes, previewUrl, id, errorMsg }
            this.isUploading = false;
            this.aborted = false;
            this.activeXhr = null;

            this.initEvents();
        }

        initEvents() {
            if (this.fileInput) {
                this.fileInput.addEventListener('change', (e) => this.handleFilesSelected(e.target.files));
            }

            if (this.dropZone) {
                ['dragenter', 'dragover'].forEach(eventName => {
                    this.dropZone.addEventListener(eventName, (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.dropZone.classList.add('border-primary', 'bg-light');
                    }, false);
                });

                ['dragleave', 'drop'].forEach(eventName => {
                    this.dropZone.addEventListener(eventName, (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.dropZone.classList.remove('border-primary', 'bg-light');
                    }, false);
                });

                this.dropZone.addEventListener('drop', (e) => {
                    if (e.dataTransfer && e.dataTransfer.files) {
                        this.handleFilesSelected(e.dataTransfer.files);
                    }
                });

                this.dropZone.addEventListener('click', (e) => {
                    if (e.target.tagName !== 'INPUT' && !this.isUploading) {
                        this.fileInput.click();
                    }
                });
            }

            if (this.optimizeCheckbox) {
                this.optimizeCheckbox.addEventListener('change', () => {
                    this.renderPreviewList();
                    this.updateSummary();
                });
            }

            if (this.startBtn) {
                this.startBtn.addEventListener('click', () => this.startUpload());
            }

            if (this.cancelBtn) {
                this.cancelBtn.addEventListener('click', () => this.cancelUpload());
            }
        }

        handleFilesSelected(files) {
            if (!files || files.length === 0) return;
            if (this.isUploading) return;

            const validFiles = Array.from(files).filter(f => f.type.startsWith('image/'));
            if (validFiles.length === 0) {
                alert("Veuillez sélectionner uniquement des fichiers images (JPG, PNG, WEBP).");
                return;
            }

            validFiles.forEach(f => {
                const previewUrl = URL.createObjectURL(f);
                this.filesQueue.push({
                    file: f,
                    status: 'pending', // 'pending', 'optimizing', 'uploading', 'done', 'error'
                    loadedBytes: 0,
                    totalBytes: f.size,
                    previewUrl: previewUrl,
                    id: 'photo-' + Math.random().toString(36).substr(2, 9),
                    errorMsg: ''
                });
            });

            this.renderPreviewList();
            this.updateSummary();
        }

        removeFile(id) {
            if (this.isUploading) return;
            const index = this.filesQueue.findIndex(item => item.id === id);
            if (index !== -1) {
                URL.revokeObjectURL(this.filesQueue[index].previewUrl);
                this.filesQueue.splice(index, 1);
            }
            this.renderPreviewList();
            this.updateSummary();
        }

        updateSummary() {
            const count = this.filesQueue.length;
            const totalBytes = this.filesQueue.reduce((acc, cur) => acc + cur.totalBytes, 0);

            if (count > 0) {
                if (this.summaryBadge) {
                    this.summaryBadge.textContent = `${count} photo(s) prête(s) (${formatBytes(totalBytes)})`;
                    this.summaryBadge.classList.remove('d-none');
                }
                if (this.startBtn) {
                    this.startBtn.disabled = false;
                    this.startBtn.innerHTML = `<i class="bi bi-cloud-arrow-up-fill me-1"></i> Téléverser ${count} cliché(s)`;
                }
            } else {
                if (this.summaryBadge) this.summaryBadge.classList.add('d-none');
                if (this.startBtn) {
                    this.startBtn.disabled = true;
                    this.startBtn.innerHTML = `<i class="bi bi-cloud-arrow-up-fill me-1"></i> Téléverser les clichés`;
                }
            }
        }

        renderPreviewList() {
            if (!this.previewList) return;
            if (this.filesQueue.length === 0) {
                this.previewList.innerHTML = '';
                this.previewList.classList.add('d-none');
                return;
            }

            const shouldOptimize = this.optimizeCheckbox ? this.optimizeCheckbox.checked : true;

            this.previewList.classList.remove('d-none');
            this.previewList.innerHTML = this.filesQueue.map(item => {
                const isOver2MB = item.totalBytes > MAX_ALLOWED_FILE_SIZE;
                return `
                <div class="col-6 col-sm-4 col-md-3" id="item-${item.id}">
                    <div class="card h-100 border shadow-sm rounded-3 overflow-hidden position-relative">
                        <img src="${item.previewUrl}" alt="${item.file.name}" style="height: 90px; width: 100%; object-fit: cover;">
                        <div class="p-2 small">
                            <div class="text-truncate fw-semibold" style="font-size: 0.78rem;" title="${item.file.name}">${item.file.name}</div>
                            <div class="d-flex align-items-center justify-content-between" style="font-size: 0.7rem;">
                                <span class="${isOver2MB && !shouldOptimize ? 'text-danger fw-bold' : 'text-muted'}">${formatBytes(item.totalBytes)}</span>
                                ${isOver2MB ? (shouldOptimize ? '<span class="badge bg-info text-dark" title="Sera réduit sous 2 Mo">Adapté</span>' : '<span class="badge bg-danger" title="Dépasse 2 Mo">> 2 Mo</span>') : ''}
                            </div>
                            <div class="status-indicator mt-1" style="font-size: 0.72rem;">
                                ${this.renderStatusBadge(item)}
                            </div>
                        </div>
                        ${!this.isUploading ? `
                        <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-1 rounded-circle p-0" style="width: 20px; height: 20px; line-height: 1;" data-remove-id="${item.id}" title="Retirer">
                            &times;
                        </button>
                        ` : ''}
                    </div>
                </div>
            `;
            }).join('');

            this.previewList.querySelectorAll('[data-remove-id]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.removeFile(btn.dataset.removeId);
                });
            });
        }

        renderStatusBadge(item) {
            switch (item.status) {
                case 'optimizing':
                    return '<span class="text-info"><i class="spinner-border spinner-border-sm me-1" style="width: 10px; height: 10px;"></i> Optimisation (< 2 Mo)...</span>';
                case 'uploading':
                    const pct = Math.round((item.loadedBytes / (item.totalBytes || 1)) * 100);
                    return `<span class="text-primary fw-bold"><i class="bi bi-arrow-repeat spin me-1"></i> ${pct}%</span>`;
                case 'done':
                    return '<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Téléversé</span>';
                case 'error':
                    return `<span class="text-danger fw-bold" title="${item.errorMsg || 'Erreur'}"><i class="bi bi-exclamation-circle-fill me-1"></i> ${item.errorMsg ? (item.errorMsg.length > 22 ? item.errorMsg.substring(0, 22) + '...' : item.errorMsg) : 'Échec'}</span>`;
                default:
                    return '<span class="text-muted"><i class="bi bi-clock me-1"></i> En attente</span>';
            }
        }

        updateItemStatus(item) {
            const itemEl = document.getElementById(`item-${item.id}`);
            if (!itemEl) return;
            const indicator = itemEl.querySelector('.status-indicator');
            if (indicator) {
                indicator.innerHTML = this.renderStatusBadge(item);
            }
        }

        async startUpload() {
            if (this.filesQueue.length === 0 || this.isUploading) return;

            this.isUploading = true;
            this.aborted = false;

            if (this.startBtn) this.startBtn.disabled = true;
            if (this.fileInput) this.fileInput.disabled = true;
            if (this.dropZone) this.dropZone.style.pointerEvents = 'none';
            if (this.cancelBtn) this.cancelBtn.classList.remove('d-none');
            if (this.progressContainer) this.progressContainer.classList.remove('d-none');
            if (this.successAlert) this.successAlert.classList.add('d-none');

            this.renderPreviewList();

            const shouldOptimize = this.optimizeCheckbox ? this.optimizeCheckbox.checked : true;
            let successCount = 0;
            let errorCount = 0;

            const totalCount = this.filesQueue.length;

            for (let i = 0; i < totalCount; i++) {
                if (this.aborted) break;

                const item = this.filesQueue[i];
                if (item.status === 'done') {
                    successCount++;
                    continue;
                }

                if (this.progressStatus) {
                    this.progressStatus.textContent = `Préparation cliché ${i + 1}/${totalCount} : ${item.file.name}`;
                }

                let fileToSend = item.file;
                try {
                    item.status = 'optimizing';
                    this.updateItemStatus(item);
                    fileToSend = await prepareImageUnder2MB(item.file, shouldOptimize);
                    item.totalBytes = fileToSend.size;
                } catch (sizeErr) {
                    item.status = 'error';
                    item.errorMsg = sizeErr.message || 'Fichier supérieur à 2 Mo';
                    this.updateItemStatus(item);
                    errorCount++;
                    continue;
                }

                if (this.aborted) break;

                item.status = 'uploading';
                this.updateItemStatus(item);

                try {
                    await this.uploadSingleFile(item, fileToSend, i + 1, totalCount);
                    item.status = 'done';
                    item.loadedBytes = item.totalBytes;
                    this.updateItemStatus(item);
                    successCount++;
                } catch (err) {
                    item.status = 'error';
                    item.errorMsg = err.message || 'Erreur réseau';
                    this.updateItemStatus(item);
                    errorCount++;
                }

                this.updateGlobalProgress(i + 1, totalCount);
            }

            this.isUploading = false;
            if (this.cancelBtn) this.cancelBtn.classList.add('d-none');
            if (this.dropZone) this.dropZone.style.pointerEvents = 'auto';

            if (this.aborted) {
                if (this.progressStatus) {
                    this.progressStatus.innerHTML = `<span class="text-warning"><i class="bi bi-pause-circle me-1"></i> Téléversement interrompu (${successCount} photo(s) envoyée(s)).</span>`;
                }
                return;
            }

            if (successCount > 0 && errorCount === 0) {
                if (this.successAlert) {
                    this.successAlert.innerHTML = `
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <i class="bi bi-check-circle-fill me-2 fs-5"></i>
                                <strong>Succès !</strong> ${successCount} photo(s) (toutes < 2 Mo) ajoutée(s) avec succès.
                            </div>
                            <button type="button" class="btn btn-sm btn-outline-success" onclick="window.location.reload();">
                                <i class="bi bi-arrow-clockwise me-1"></i> Actualiser
                            </button>
                        </div>
                    `;
                    this.successAlert.classList.remove('d-none');
                }
                if (this.progressStatus) {
                    this.progressStatus.innerHTML = `<span class="text-success fw-bold"><i class="bi bi-check2-all me-1"></i> Téléversement terminé à 100% (${successCount}/${totalCount})</span>`;
                }

                setTimeout(() => {
                    window.location.reload();
                }, 1800);
            } else if (errorCount > 0) {
                if (this.progressStatus) {
                    this.progressStatus.innerHTML = `<span class="text-danger fw-bold"><i class="bi bi-exclamation-triangle me-1"></i> ${successCount} réussie(s), ${errorCount} rejetée(s) ou en échec.</span>`;
                }
                if (this.startBtn) {
                    this.startBtn.disabled = false;
                    this.startBtn.innerHTML = `<i class="bi bi-arrow-clockwise me-1"></i> Réessayer les clichés non envoyés`;
                }
            }
        }

        uploadSingleFile(item, file, currentIndex, totalCount) {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                this.activeXhr = xhr;

                xhr.open('POST', this.uploadUrl, true);
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

                xhr.upload.onprogress = (e) => {
                    if (e.lengthComputable) {
                        item.loadedBytes = e.loaded;
                        item.totalBytes = e.total;
                        this.updateItemStatus(item);
                        this.updateGlobalProgress(currentIndex, totalCount, e.loaded, e.total);
                    }
                };

                xhr.onload = () => {
                    this.activeXhr = null;
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const res = JSON.parse(xhr.responseText);
                            if (res.success) {
                                resolve(res);
                            } else {
                                reject(new Error(res.error || 'Erreur serveur'));
                            }
                        } catch (e) {
                            reject(new Error('Réponse invalide du serveur'));
                        }
                    } else {
                        try {
                            const res = JSON.parse(xhr.responseText);
                            reject(new Error(res.error || `Erreur HTTP ${xhr.status}`));
                        } catch (e) {
                            reject(new Error(`Erreur HTTP ${xhr.status}`));
                        }
                    }
                };

                xhr.onerror = () => {
                    this.activeXhr = null;
                    reject(new Error('Connexion perdue ou coupée'));
                };

                xhr.onabort = () => {
                    this.activeXhr = null;
                    reject(new Error('Téléversement annulé'));
                };

                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', this.csrfToken);
                formData.append('photo', file);

                xhr.send(formData);
            });
        }

        updateGlobalProgress(currentIndex, totalCount, currentLoaded = 0, currentTotal = 0) {
            const totalBytes = this.filesQueue.reduce((acc, cur) => acc + cur.totalBytes, 0) || 1;
            let loadedBytes = 0;

            this.filesQueue.forEach(item => {
                if (item.status === 'done') {
                    loadedBytes += item.totalBytes;
                } else if (item.status === 'uploading') {
                    loadedBytes += item.loadedBytes;
                }
            });

            let percent = Math.min(100, Math.round((loadedBytes / totalBytes) * 100));

            if (this.progressBar) {
                this.progressBar.style.width = `${percent}%`;
                this.progressBar.setAttribute('aria-valuenow', percent);
            }
            if (this.progressPercent) {
                this.progressPercent.textContent = `${percent}%`;
            }
            if (this.progressBytes) {
                this.progressBytes.textContent = `${formatBytes(loadedBytes)} / ${formatBytes(totalBytes)} (Cliché ${currentIndex}/${totalCount})`;
            }
        }

        cancelUpload() {
            this.aborted = true;
            if (this.activeXhr) {
                this.activeXhr.abort();
            }
            this.isUploading = false;
        }
    }

    // Initialisation automatique sur tous les conteneurs d'upload de la page
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.async-photo-uploader').forEach(el => {
            new AsyncPhotoUploader(el);
        });

        // Gestion de la création d'album avec multi-photos asynchrones et limite de 2 Mo
        const createAlbumForm = document.getElementById('createAlbumForm');
        if (createAlbumForm) {
            createAlbumForm.addEventListener('submit', async function (e) {
                const photosInput = createAlbumForm.querySelector('input[name="photos"]');
                const selectedFiles = photosInput && photosInput.files ? Array.from(photosInput.files) : [];

                // Si pas de photos supplémentaires, on laisse le submit classique opérer
                if (selectedFiles.length === 0) {
                    return; // standard submit
                }

                // S'il y a des photos, on fait la création de l'album via AJAX puis l'upload asynchrone des photos
                e.preventDefault();

                const submitBtn = createAlbumForm.querySelector('button[type="submit"]');
                const progressBox = document.getElementById('createAlbumProgressBox');
                const progressBar = document.getElementById('createAlbumProgressBar');
                const progressPercent = document.getElementById('createAlbumProgressPercent');
                const progressText = document.getElementById('createAlbumProgressText');

                if (submitBtn) submitBtn.disabled = true;
                if (progressBox) progressBox.classList.remove('d-none');
                if (progressText) progressText.textContent = "Création de l'album...";

                try {
                    // 1. Vérifier et adapter la couverture si présente
                    const couvertureInput = createAlbumForm.querySelector('input[name="couverture"]');
                    if (couvertureInput && couvertureInput.files && couvertureInput.files.length > 0) {
                        const covFile = couvertureInput.files[0];
                        if (covFile.size > MAX_ALLOWED_FILE_SIZE) {
                            try {
                                const optCov = await prepareImageUnder2MB(covFile, true);
                                const dt = new DataTransfer();
                                dt.items.add(optCov);
                                couvertureInput.files = dt.files;
                            } catch (covErr) {
                                throw new Error("L'image de couverture dépasse 2 Mo. Veuillez choisir une image plus légère.");
                            }
                        }
                    }

                    // 2. Créer l'album d'abord (sans les photos multiples)
                    const formData = new FormData(createAlbumForm);
                    formData.delete('photos'); // Les photos seront envoyées asynchronement ensuite
                    formData.append('is_ajax', '1');

                    const response = await fetch(createAlbumForm.action || window.location.href, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    const res = await response.json();
                    if (!res.success || !res.album_id) {
                        throw new Error(res.error || "Erreur lors de la création de l'album");
                    }

                    const albumId = res.album_id;
                    const uploadUrl = `/gestion/galerie/album/${albumId}/upload-async/`;
                    const csrfToken = formData.get('csrfmiddlewaretoken');

                    // 3. Téléversement asynchrone photo par photo
                    const total = selectedFiles.length;
                    let loadedTotalBytes = 0;
                    const totalBytes = selectedFiles.reduce((a, b) => a + b.size, 0);

                    for (let i = 0; i < total; i++) {
                        const file = selectedFiles[i];
                        if (progressText) {
                            progressText.textContent = `Traitement du cliché ${i + 1}/${total} : ${file.name}`;
                        }

                        // Optimisation et garantie <= 2 Mo
                        let optimized = file;
                        try {
                            optimized = await prepareImageUnder2MB(file, true);
                        } catch (e) {
                            console.warn("Fichier trop lourd non réductible :", e.message);
                            continue;
                        }

                        await new Promise((resolve, reject) => {
                            const xhr = new XMLHttpRequest();
                            xhr.open('POST', uploadUrl, true);
                            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

                            xhr.upload.onprogress = (ev) => {
                                if (ev.lengthComputable) {
                                    const currentOverall = loadedTotalBytes + ev.loaded;
                                    const pct = Math.min(100, Math.round((currentOverall / totalBytes) * 100));
                                    if (progressBar) progressBar.style.width = `${pct}%`;
                                    if (progressPercent) progressPercent.textContent = `${pct}%`;
                                }
                            };

                            xhr.onload = () => {
                                if (xhr.status >= 200 && xhr.status < 300) {
                                    loadedTotalBytes += optimized.size;
                                    resolve();
                                } else {
                                    try {
                                        const errRes = JSON.parse(xhr.responseText);
                                        reject(new Error(errRes.error || `Erreur ${xhr.status}`));
                                    } catch (_) {
                                        reject(new Error(`Erreur ${xhr.status}`));
                                    }
                                }
                            };
                            xhr.onerror = () => reject(new Error('Erreur réseau'));

                            const photoData = new FormData();
                            photoData.append('csrfmiddlewaretoken', csrfToken);
                            photoData.append('photo', optimized);
                            xhr.send(photoData);
                        });

                        const pct = Math.min(100, Math.round(((i + 1) / total) * 100));
                        if (progressBar) progressBar.style.width = `${pct}%`;
                        if (progressPercent) progressPercent.textContent = `${pct}%`;
                    }

                    if (progressText) {
                        progressText.innerHTML = `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Album et photos créés avec succès ! Redirection...</span>`;
                    }
                    setTimeout(() => window.location.reload(), 1200);

                } catch (err) {
                    alert("Une erreur est survenue : " + err.message);
                    if (submitBtn) submitBtn.disabled = false;
                    if (progressBox) progressBox.classList.add('d-none');
                }
            });
        }
    });

    window.AsyncPhotoUploader = AsyncPhotoUploader;
})();
