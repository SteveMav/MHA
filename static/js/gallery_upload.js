/**
 * Magic Hoops Academy - Asynchronous Photo Uploader
 * Téléversement photo par photo avec calcul du pourcentage global en temps réel,
 * prévisualisations, optimisation client-side, limite stricte de 3 Mo et suppression des timeouts.
 */

(function () {
    'use strict';

    const MAX_ALLOWED_FILE_SIZE = 3 * 1024 * 1024; // Limite stricte : 3 Mo (3 145 728 octets)

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
     * Réduit considérablement la taille des photos 48MP de smartphone (de ~12 Mo à ~1 Mo)
     * tout en conservant une excellente résolution (jusqu'à 2560px).
     */
    function compressImage(file, maxWidth = 2560, maxHeight = 2560, quality = 0.88) {
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

                    if (width <= maxWidth && height <= maxHeight && file.size < 1.5 * 1024 * 1024) {
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
     * Garantit que le fichier respecte la limite de 3 Mo (3 145 728 octets).
     * Si l'optimisation est demandée et que le fichier dépasse 2 Mo, il est automatiquement
     * compressé côté client en Canvas pour conserver un rendu HD tout en garantissant un poids < 3 Mo.
     */
    async function prepareImageUnder3MB(file, optimize = true) {
        if (!file.type.startsWith('image/')) {
            if (file.size > MAX_ALLOWED_FILE_SIZE) {
                throw new Error(`Le fichier '${file.name}' (${formatBytes(file.size)}) dépasse la limite de 3 Mo.`);
            }
            return file;
        }

        if (!optimize) {
            if (file.size > MAX_ALLOWED_FILE_SIZE) {
                throw new Error(`La photo '${file.name}' (${formatBytes(file.size)}) dépasse 3 Mo et l'optimisation est désactivée.`);
            }
            return file;
        }

        // Si le fichier fait déjà 2 Mo ou moins, aucune compression nécessaire
        if (file.size <= 2 * 1024 * 1024) {
            return file;
        }

        // Palier 1 : 2560px max, 88% qualité
        let optimized = await compressImage(file, 2560, 2560, 0.88);

        // Si encore > 3 Mo, Palier 2 : 2048px max, 82% qualité
        if (optimized.size > MAX_ALLOWED_FILE_SIZE) {
            optimized = await compressImage(optimized, 2048, 2048, 0.82);
        }

        // Si encore > 3 Mo, Palier 3 : 1920px max, 75% qualité
        if (optimized.size > MAX_ALLOWED_FILE_SIZE) {
            optimized = await compressImage(optimized, 1920, 1920, 0.75);
        }

        if (optimized.size > MAX_ALLOWED_FILE_SIZE) {
            throw new Error(`Même après optimisation, la photo '${file.name}' reste supérieure à 3 Mo (${formatBytes(optimized.size)}).`);
        }

        return optimized;
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

            const shouldOptimize = this.optimizeCheckbox ? this.optimizeCheckbox.checked : true;
            const extremeFiles = [];

            validFiles.forEach(f => {
                // Fichier disproportionné (> 50 Mo) ou non optimisable si switch décoché
                if (f.size > 50 * 1024 * 1024) {
                    extremeFiles.push(f);
                } else if (!shouldOptimize && f.size > MAX_ALLOWED_FILE_SIZE) {
                    extremeFiles.push(f);
                } else {
                    const previewUrl = URL.createObjectURL(f);
                    this.filesQueue.push({
                        file: f,
                        status: 'pending', // 'pending', 'optimizing', 'uploading', 'done', 'error'
                        loadedBytes: 0,
                        totalBytes: f.size,
                        previewUrl: previewUrl,
                        id: 'photo-' + Math.random().toString(36).substr(2, 9),
                        errorMsg: '',
                        optimizedFile: null
                    });
                }
            });

            if (extremeFiles.length > 0) {
                const listStr = extremeFiles.map(f => `• ${f.name} (${formatBytes(f.size)})`).join('\n');
                alert(`⚠️ ${extremeFiles.length} fichier(s) rejeté(s) car dépassant 50 Mo ou supérieurs à 3 Mo (avec optimisation désactivée) :\n\n${listStr}`);
            }

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
                const isOverLimit = item.totalBytes > MAX_ALLOWED_FILE_SIZE;
                let badgeHtml = '';
                if (item.status === 'done') {
                    badgeHtml = '<span class="badge bg-success"><i class="bi bi-check me-1"></i>Téléversé</span>';
                } else if (isOverLimit) {
                    badgeHtml = shouldOptimize 
                        ? '<span class="badge bg-info text-dark" title="Sera automatiquement compressé sous 3 Mo"><i class="bi bi-magic me-1"></i>Auto-compressé</span>' 
                        : '<span class="badge bg-danger" title="Dépasse 3 Mo">> 3 Mo</span>';
                } else {
                    badgeHtml = '<span class="badge bg-light text-secondary border">&le; 3 Mo</span>';
                }

                return `
                <div class="col-6 col-sm-4 col-md-3" id="item-${item.id}">
                    <div class="card h-100 border shadow-sm rounded-3 overflow-hidden position-relative">
                        <img src="${item.previewUrl}" alt="${item.file.name}" style="height: 90px; width: 100%; object-fit: cover;">
                        <div class="p-2 small">
                            <div class="text-truncate fw-semibold" style="font-size: 0.78rem;" title="${item.file.name}">${item.file.name}</div>
                            <div class="d-flex align-items-center justify-content-between my-1" style="font-size: 0.7rem;">
                                <span class="${isOverLimit && !shouldOptimize ? 'text-danger fw-bold' : 'text-muted'}">${formatBytes(item.totalBytes)}</span>
                                ${badgeHtml}
                            </div>
                            <div class="status-indicator" style="font-size: 0.72rem;">
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
                    return '<span class="text-info"><i class="spinner-border spinner-border-sm me-1" style="width: 10px; height: 10px;"></i> Compression HD...</span>';
                case 'uploading':
                    const pct = Math.round((item.loadedBytes / (item.totalBytes || 1)) * 100);
                    return `<span class="text-primary fw-bold"><i class="bi bi-arrow-repeat spin me-1"></i> ${pct}%</span>`;
                case 'done':
                    const optNote = (item.optimizedFile && item.optimizedFile.size < item.file.size) 
                        ? ` <small class="text-muted">(${formatBytes(item.optimizedFile.size)})</small>` 
                        : '';
                    return `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Téléversé${optNote}</span>`;
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
                    if (shouldOptimize && item.file.size > 2 * 1024 * 1024) {
                        item.status = 'optimizing';
                        this.updateItemStatus(item);
                        if (this.progressStatus) {
                            this.progressStatus.textContent = `Compression HD (${formatBytes(item.file.size)}) cliché ${i + 1}/${totalCount}...`;
                        }
                    }
                    fileToSend = await prepareImageUnder3MB(item.file, shouldOptimize);
                    item.optimizedFile = fileToSend;
                    item.totalBytes = fileToSend.size;
                } catch (sizeErr) {
                    item.status = 'error';
                    item.errorMsg = sizeErr.message || 'Fichier supérieur à 3 Mo';
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
                                <strong>Succès !</strong> ${successCount} photo(s) (toutes &le; 3 Mo) ajoutée(s) avec succès.
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
                if (this.csrfToken) {
                    xhr.setRequestHeader('X-CSRFToken', this.csrfToken);
                }

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



    function setupFileValidators() {
        // Validation instantanée & optimisation pour les fichiers uniques (ex: couverture)
        document.querySelectorAll('.check-3mb-file').forEach(input => {
            input.addEventListener('change', async function () {
                const feedback = this.parentElement.querySelector('.file-size-feedback') 
                    || document.getElementById(this.id ? this.id.replace('Input', 'Feedback') : '');
                const file = this.files && this.files[0];

                if (!file) {
                    this.classList.remove('is-invalid', 'is-valid');
                    if (feedback) feedback.innerHTML = '';
                    return;
                }

                if (file.size > 40 * 1024 * 1024) {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                    this.value = '';
                    if (feedback) {
                        feedback.innerHTML = `<span class="text-danger fw-bold"><i class="bi bi-x-circle-fill me-1"></i> Fichier supérieur à 40 Mo.</span>`;
                    }
                    alert(`❌ Le fichier "${file.name}" dépasse 40 Mo.`);
                    return;
                }

                if (file.size > 2 * 1024 * 1024) {
                    this.classList.remove('is-invalid');
                    if (feedback) {
                        feedback.innerHTML = `<span class="text-info"><i class="spinner-border spinner-border-sm me-1"></i> Photo de ${formatBytes(file.size)} détectée. Optimisation automatique en cours...</span>`;
                    }
                    try {
                        const optimized = await prepareImageUnder3MB(file, true);
                        if (window.DataTransfer) {
                            const dt = new DataTransfer();
                            dt.items.add(optimized);
                            this.files = dt.files;
                        }
                        this.classList.add('is-valid');
                        if (feedback) {
                            feedback.innerHTML = `<span class="text-success fw-semibold"><i class="bi bi-magic me-1"></i> "${file.name}" optimisé automatiquement : ${formatBytes(file.size)} ➔ ${formatBytes(optimized.size)} (HD &le; 3 Mo)</span>`;
                        }
                    } catch (err) {
                        if (feedback) {
                            feedback.innerHTML = `<span class="text-warning fw-semibold"><i class="bi bi-info-circle me-1"></i> Sera optimisé lors de l'envoi (&le; 3 Mo).</span>`;
                        }
                    }
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    if (feedback) {
                        feedback.innerHTML = `<span class="text-success fw-semibold"><i class="bi bi-check-circle-fill me-1"></i> "${file.name}" (${formatBytes(file.size)}) : Conforme (&le; 3 Mo)</span>`;
                    }
                }
            });
        });

        // Validation & information transparente pour les sélections multiples (photos d'album)
        document.querySelectorAll('.check-3mb-multiple').forEach(input => {
            input.addEventListener('change', function () {
                const feedback = this.parentElement.querySelector('.file-size-feedback')
                    || document.getElementById(this.id ? this.id.replace('Input', 'Feedback') : '');
                const files = this.files ? Array.from(this.files) : [];

                if (files.length === 0) {
                    this.classList.remove('is-invalid', 'is-valid');
                    if (feedback) feedback.innerHTML = '';
                    return;
                }

                const heavyFiles = files.filter(f => f.size > MAX_ALLOWED_FILE_SIZE);
                const totalBytes = files.reduce((acc, f) => acc + f.size, 0);

                this.classList.remove('is-invalid');
                this.classList.add('is-valid');

                if (heavyFiles.length > 0) {
                    if (feedback) {
                        feedback.innerHTML = `<span class="text-primary fw-semibold"><i class="bi bi-magic me-1"></i> ${files.length} photo(s) sélectionnée(s) (${formatBytes(totalBytes)}). ${heavyFiles.length} photo(s) lourdes seront automatiquement compressées sous 3 Mo en HD lors de l'envoi.</span>`;
                    }
                } else {
                    if (feedback) {
                        feedback.innerHTML = `<span class="text-success fw-semibold"><i class="bi bi-check-circle-fill me-1"></i> ${files.length} photo(s) sélectionnée(s) (${formatBytes(totalBytes)} au total, toutes &le; 3 Mo).</span>`;
                    }
                }
            });
        });
    }

    // Initialisation automatique sur tous les conteneurs d'upload de la page
    document.addEventListener('DOMContentLoaded', () => {
        setupFileValidators();

        document.querySelectorAll('.async-photo-uploader').forEach(el => {
            new AsyncPhotoUploader(el);
        });

        // Gestion de la création d'album avec multi-photos asynchrones et auto-compression sous 3 Mo
        const createAlbumForm = document.getElementById('createAlbumForm');
        if (createAlbumForm) {
            createAlbumForm.addEventListener('submit', async function (e) {
                const photosInput = createAlbumForm.querySelector('input[name="photos"]');
                const selectedFiles = photosInput && photosInput.files ? Array.from(photosInput.files) : [];
                const couvertureInput = createAlbumForm.querySelector('input[name="couverture"]');
                const dateInput = createAlbumForm.querySelector('input[name="date_evenement"]');

                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const todayIso = `${year}-${month}-${day}`;

                // 0. Vérification date pour tous les cas
                if (dateInput && dateInput.value && dateInput.value > todayIso) {
                    e.preventDefault();
                    alert("La date de l'événement ne peut pas être dans le futur (au maximum aujourd'hui).");
                    return;
                }

                // 1. Couverture : si > 2 Mo, tentative d'optimisation
                if (couvertureInput && couvertureInput.files && couvertureInput.files.length > 0) {
                    const covFile = couvertureInput.files[0];
                    if (covFile.size > 40 * 1024 * 1024) {
                        e.preventDefault();
                        alert(`❌ La photo de couverture "${covFile.name}" dépasse 40 Mo.`);
                        return;
                    }
                }

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
                    // Créer l'album d'abord (sans les photos multiples)
                    const formData = new FormData(createAlbumForm);
                    formData.delete('photos'); // Les photos seront envoyées asynchronement ensuite
                    formData.append('is_ajax', '1');

                    // Optimisation automatique de la couverture si > 2 Mo
                    if (couvertureInput && couvertureInput.files && couvertureInput.files.length > 0) {
                        const covFile = couvertureInput.files[0];
                        if (covFile.size > 2 * 1024 * 1024) {
                            if (progressText) progressText.textContent = "Optimisation de la photo de couverture...";
                            try {
                                const optCov = await prepareImageUnder3MB(covFile, true);
                                formData.set('couverture', optCov);
                            } catch (cErr) {
                                console.warn("Optimisation couverture :", cErr);
                            }
                        }
                    }

                    let targetUrl = createAlbumForm.dataset.actionUrl || createAlbumForm.getAttribute('action') || '/gestion/galerie/';
                    if (typeof targetUrl !== 'string' || targetUrl.includes('[object')) {
                        targetUrl = '/gestion/galerie/';
                    }
                    if (!targetUrl.endsWith('/')) {
                        targetUrl += '/';
                    }

                    const csrfToken = formData.get('csrfmiddlewaretoken') 
                        || (document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '');

                    const response = await fetch(targetUrl, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    });

                    let res;
                    const responseText = await response.text();
                    try {
                        res = JSON.parse(responseText);
                    } catch (parseErr) {
                        console.error("Réponse reçue non-JSON du serveur:", responseText);
                        throw new Error(`Le serveur a renvoyé une réponse inattendue (statut ${response.status}).`);
                    }

                    if (!response.ok || !res.success || !res.album_id) {
                        throw new Error(res.error || "Erreur lors de la création de l'album");
                    }

                    const albumId = res.album_id;
                    const uploadUrl = `/gestion/galerie/album/${albumId}/upload-async/`;

                    // Téléversement asynchrone photo par photo avec compression intelligente sous 3 Mo
                    const total = selectedFiles.length;

                    for (let i = 0; i < total; i++) {
                        const rawFile = selectedFiles[i];

                        if (progressText) {
                            progressText.textContent = `Optimisation du cliché ${i + 1}/${total} : ${rawFile.name} (${formatBytes(rawFile.size)})...`;
                        }

                        // Auto-compression en Canvas si > 2 Mo
                        let fileToSend = rawFile;
                        try {
                            fileToSend = await prepareImageUnder3MB(rawFile, true);
                        } catch (optErr) {
                            console.warn("Optimisation échouée, essai direct :", optErr);
                        }

                        if (progressText) {
                            const optLabel = fileToSend.size < rawFile.size ? ` (optimisé à ${formatBytes(fileToSend.size)})` : '';
                            progressText.textContent = `Envoi du cliché ${i + 1}/${total} : ${rawFile.name}${optLabel}`;
                        }

                        await new Promise((resolve, reject) => {
                            const xhr = new XMLHttpRequest();
                            xhr.open('POST', uploadUrl, true);
                            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                            xhr.setRequestHeader('X-CSRFToken', csrfToken);

                            xhr.upload.onprogress = (ev) => {
                                if (ev.lengthComputable) {
                                    const filePct = ev.loaded / ev.total;
                                    const overallPct = Math.min(99, Math.round(((i + filePct) / total) * 100));
                                    if (progressBar) progressBar.style.width = `${overallPct}%`;
                                    if (progressPercent) progressPercent.textContent = `${overallPct}%`;
                                }
                            };

                            xhr.onload = () => {
                                if (xhr.status >= 200 && xhr.status < 300) {
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
                            xhr.onerror = () => reject(new Error('Erreur de connexion réseau'));

                            const photoData = new FormData();
                            photoData.append('csrfmiddlewaretoken', csrfToken);
                            photoData.append('photo', fileToSend);
                            xhr.send(photoData);
                        });

                        const pct = Math.min(100, Math.round(((i + 1) / total) * 100));
                        if (progressBar) progressBar.style.width = `${pct}%`;
                        if (progressPercent) progressPercent.textContent = `${pct}%`;
                    }

                    if (progressText) {
                        progressText.innerHTML = `<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Album et ${total} photos optimisées créés avec succès ! Redirection...</span>`;
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
