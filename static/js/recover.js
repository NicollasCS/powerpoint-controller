function showMessage(msg, isError = true) {
    const el = document.getElementById('message');
    el.textContent = msg;
    el.className = isError ? 'error' : 'success';
}

async function recover() {
    const email = document.getElementById('email').value;

    if (!email) {
        showMessage('Digite seu email');
        return;
    }

    try {
        const response = await fetch('/api/recover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, false);
        } else {
            showMessage('❌ ' + data.error);
        }
    } catch (error) {
        showMessage('❌ Erro de conexão');
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') recover();
});