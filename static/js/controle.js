let currentSlide = 0;
let totalSlides = 0;
let pptId = null;
let updateInterval = null;

function showToast(msg, duration = 1500) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
        toast.style.display = 'none';
    }, duration);
}

function showTokenMessage(msg, isError = true) {
    const el = document.getElementById('tokenMessage');
    el.textContent = msg;
    el.className = isError ? 'error' : 'success';
}

async function validateToken() {
    const token = document.getElementById('tokenInput').value.trim();
    const btn = document.getElementById('connectBtn');

    if (!token) {
        showTokenMessage('Digite o token');
        return;
    }

    btn.disabled = true;
    btn.textContent = '⏳ Conectando...';

    try {
        const response = await fetch('/api/validate_token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showTokenMessage('✅ Conectado!', false);
            document.getElementById('connectedUser').textContent = 'Conectado como: ' + data.user_email;
            document.getElementById('tokenScreen').style.display = 'none';
            document.getElementById('controlsScreen').style.display = 'block';
            await loadPresentation(token);
        } else {
            showTokenMessage('❌ ' + data.error);
        }
    } catch (error) {
        showTokenMessage('❌ Erro de conexão');
    }

    btn.disabled = false;
    btn.textContent = 'Conectar';
}

async function loadPresentation(token) {
    try {
        const response = await fetch('/api/get_presentation_by_token?token=' + token);
        const data = await response.json();

        if (data.ppt_id) {
            pptId = data.ppt_id;
            totalSlides = data.total_slides || 0;
            updateDisplay();
            startPolling();
        } else {
            document.getElementById('status').textContent = '⚠️ Nenhuma apresentação ativa';
        }
    } catch (error) {
        document.getElementById('status').textContent = '⚠️ Erro ao carregar';
    }
}

function updateDisplay() {
    document.getElementById('slideNumber').textContent = currentSlide + 1;
    document.getElementById('totalSlides').textContent = totalSlides;
    const progress = totalSlides > 0 ? ((currentSlide + 1) / totalSlides) * 100 : 0;
    document.getElementById('progressFill').style.width = progress + '%';
}

function startPolling() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(updateStatus, 1000);
}

async function updateStatus() {
    if (!pptId) return;
    try {
        const response = await fetch(`/api/status/${pptId}`);
        const data = await response.json();
        if (data.error) return;

        const newSlide = data.slide_atual || 0;
        if (newSlide !== currentSlide) {
            currentSlide = newSlide;
            updateDisplay();
        }
        document.getElementById('status').textContent = '✅ Conectado';
    } catch (error) {
        document.getElementById('status').textContent = '⚠️ Erro de conexão';
    }
}

async function nextSlide() {
    if (!pptId) return;
    try {
        await fetch(`/api/next/${pptId}`);
        showToast('⏩ Avançou');
        await updateStatus();
    } catch (error) {
        showToast('❌ Erro', 1000);
    }
}

async function prevSlide() {
    if (!pptId) return;
    try {
        await fetch(`/api/prev/${pptId}`);
        showToast('⏪ Voltou');
        await updateStatus();
    } catch (error) {
        showToast('❌ Erro', 1000);
    }
}

// ===== EVENTOS =====

// Teclado
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevSlide();
    }
});

// Enter no input de token
document.getElementById('tokenInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') validateToken();
});

// Swipe (toque)
let touchStartX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, { passive: true });

document.addEventListener('touchend', (e) => {
    const diff = touchStartX - e.changedTouches[0].screenX;
    if (Math.abs(diff) > 50) {
        if (diff > 0) {
            nextSlide();
        } else {
            prevSlide();
        }
    }
}, { passive: true });

// Previne zoom duplo-toque no celular
document.addEventListener('dblclick', (e) => {
    e.preventDefault();
}, { passive: false });