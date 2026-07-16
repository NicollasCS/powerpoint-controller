function showMessage(msg, isError = true) {
    const el = document.getElementById('message');
    el.textContent = msg;
    el.className = isError ? 'error' : 'success';
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showMessage('Preencha todos os campos');
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ Login realizado!', false);
            // Redireciona para a página inicial
            window.location.href = data.redirect || '/';
        } else {
            showMessage('❌ ' + data.error);
        }
    } catch (error) {
        showMessage('❌ Erro de conexão');
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') login();
});