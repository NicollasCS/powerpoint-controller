const token = new URLSearchParams(window.location.search).get('token');

function showMessage(msg, isError = true) {
    const el = document.getElementById('message');
    el.textContent = msg;
    el.className = isError ? 'error' : 'success';
}

async function resetPassword() {
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;

    if (!password || !confirm) {
        showMessage('Preencha todos os campos');
        return;
    }

    if (password !== confirm) {
        showMessage('As senhas não coincidem');
        return;
    }

    if (password.length < 6) {
        showMessage('A senha deve ter pelo menos 6 caracteres');
        return;
    }

    try {
        const response = await fetch('/api/reset_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, new_password: password })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, false);
            setTimeout(() => window.location.href = '/login', 2000);
        } else {
            showMessage('❌ ' + data.error);
        }
    } catch (error) {
        showMessage('❌ Erro de conexão');
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') resetPassword();
});