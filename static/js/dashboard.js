let currentPptId = null;
let currentSlide = 0;
let totalSlides = 0;
let slidesData = [];
let isPresentationMode = false;
let updateInterval = null;

function showStatus(msg, isError = false) {
    document.getElementById('status').textContent = msg;
    document.getElementById('status').style.color = isError ? '#e74c3c' : '#666';
}

function showUploadStatus(msg, isError = false) {
    const el = document.getElementById('uploadStatus');
    el.textContent = msg;
    el.style.color = isError ? '#e74c3c' : '#4CAF50';
}

async function uploadFile() {
    const input = document.getElementById('fileInput');
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showUploadStatus('⏳ Processando... Aguarde alguns segundos');
    document.querySelector('.upload-area').style.opacity = '0.5';

    try {
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.status === 'success') {
            currentPptId = data.ppt_id;
            showUploadStatus('✅ ' + data.message);

            document.getElementById('uploadArea').style.display = 'none';
            document.getElementById('readyState').style.display = 'block';

            const token = data.token || 'erro-ao-gerar';
            document.getElementById('presentationLink').textContent = token;

            await loadSlides(currentPptId);
            showStatus('✅ Pronto! Use o token no celular.');
        } else {
            showUploadStatus('❌ ' + (data.error || 'Erro ao processar'), true);
        }
    } catch (error) {
        showUploadStatus('❌ Erro de conexão', true);
    } finally {
        document.querySelector('.upload-area').style.opacity = '1';
    }
}

async function loadSlides(pptId) {
    try {
        const response = await fetch(`/api/slides/${pptId}`);
        const data = await response.json();

        if (data.error) {
            showStatus('❌ ' + data.error, true);
            return;
        }

        slidesData = data.slides || [];
        totalSlides = data.total || 0;
        currentSlide = data.slide_atual || 0;

        const container = document.getElementById('thumbnails');
        container.innerHTML = '';
        slidesData.forEach((slide, i) => {
            const thumb = document.createElement('div');
            thumb.className = 'thumbnail' + (i === currentSlide ? ' active' : '');
            if (slide.imagem) {
                thumb.innerHTML = `<img src="${slide.imagem}" alt="Slide ${i+1}"><span class="thumb-num">${i+1}</span>`;
            } else {
                thumb.innerHTML = `<span class="thumb-num">${i+1}</span>`;
            }
            thumb.onclick = () => goToSlide(i);
            container.appendChild(thumb);
        });
        document.getElementById('thumbnailsArea').style.display = 'block';

        if (updateInterval) clearInterval(updateInterval);
        updateInterval = setInterval(updateStatus, 1000);

    } catch (error) {
        showStatus('❌ Erro ao carregar slides', true);
    }
}

function startPresentation() {
    if (!slidesData.length) return;
    isPresentationMode = true;

    const mode = document.getElementById('presentationMode');
    const img = document.getElementById('presentationImage');
    const loading = document.getElementById('presentationLoading');

    mode.style.display = 'block';
    img.style.display = 'none';
    loading.style.display = 'block';

    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
    }

    updatePresentationSlide();
    fetch(`/api/start/${currentPptId}`);
}

function exitPresentation() {
    isPresentationMode = false;
    document.getElementById('presentationMode').style.display = 'none';

    if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
    }
}

function updatePresentationSlide() {
    if (!slidesData.length || currentSlide >= slidesData.length) return;

    const slide = slidesData[currentSlide];
    const img = document.getElementById('presentationImage');
    const loading = document.getElementById('presentationLoading');
    const badge = document.getElementById('presentationBadge');

    if (slide && slide.imagem) {
        img.src = slide.imagem;
        img.style.display = 'block';
        loading.style.display = 'none';
        badge.textContent = `${currentSlide + 1} / ${totalSlides}`;
    }
}

async function goToSlide(index) {
    if (index === currentSlide || index < 0 || index >= totalSlides) return;

    while (currentSlide < index) await nextSlide();
    while (currentSlide > index) await prevSlide();
}

async function updateStatus() {
    if (!currentPptId) return;

    try {
        const response = await fetch(`/api/status/${currentPptId}`);
        const data = await response.json();

        if (data.error) return;

        const newSlide = data.slide_atual || 0;
        if (newSlide !== currentSlide) {
            currentSlide = newSlide;

            document.querySelectorAll('.thumbnail').forEach((el, i) => {
                el.classList.toggle('active', i === currentSlide);
            });

            if (isPresentationMode) {
                updatePresentationSlide();
            }
        }
    } catch (error) {}
}

async function nextSlide() {
    if (!currentPptId) return;
    try {
        await fetch(`/api/next/${currentPptId}`);
        await updateStatus();
    } catch (error) {}
}

async function prevSlide() {
    if (!currentPptId) return;
    try {
        await fetch(`/api/prev/${currentPptId}`);
        await updateStatus();
    } catch (error) {}
}

function copyLink() {
    const link = document.getElementById('presentationLink').textContent;
    navigator.clipboard.writeText(link).then(() => {
        alert('✅ Link copiado!');
    });
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isPresentationMode) {
        exitPresentation();
    }
    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevSlide();
    }
});

document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement && isPresentationMode) {
        exitPresentation();
    }
});