let step = 1;

function showMessage(msg, type = 'success') {
    const el = document.getElementById('message');
    el.textContent = msg;
    el.className = 'message ' + type;
}

function hideMessage() {
    document.getElementById('message').className = 'message';
    document.getElementById('message').textContent = '';
}

async function sendOldEmailCode() {
    const btn = document.getElementById('btnSendOldCode');
    btn.disabled = true;
    btn.textContent = '⏳ Enviando...';
    hideMessage();

    try {
        const response = await fetch('/api/send_old_email_code', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, 'success');
            document.getElementById('oldCodeArea').classList.remove('hidden');
        } else {
            showMessage('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão', 'error');
    }

    btn.disabled = false;
    btn.textContent = '📧 Enviar código para o email atual';
}

async function verifyOldEmailCode() {
    const code = document.getElementById('oldCodeInput').value.trim();
    if (!code || code.length < 6) {
        showMessage('❌ Digite o código de 6 dígitos', 'error');
        return;
    }

    hideMessage();

    try {
        const response = await fetch('/api/verify_old_email_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, 'success');
            document.getElementById('step1').classList.add('hidden');
            document.getElementById('step2').classList.remove('hidden');
        } else {
            showMessage('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão', 'error');
    }
}

async function sendNewEmailCode() {
    const btn = document.querySelector('#step2 .btn-primary');
    const newEmail = document.getElementById('newEmailInput').value.trim();

    if (!newEmail) {
        showMessage('❌ Digite o novo email primeiro', 'error');
        return;
    }

    btn.disabled = true;
    btn.textContent = '⏳ Enviando...';
    hideMessage();

    try {
        const response = await fetch('/api/send_new_email_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_email: newEmail })
        });
        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, 'success');
            document.getElementById('newCodeArea').classList.remove('hidden');
        } else {
            showMessage('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão', 'error');
    }

    btn.disabled = false;
    btn.textContent = '📧 Enviar código para o novo email';
}

async function verifyNewEmailCode() {
    const code = document.getElementById('newCodeInput').value.trim();
    if (!code || code.length < 6) {
        showMessage('❌ Digite o código de 6 dígitos', 'error');
        return;
    }

    hideMessage();

    try {
        const response = await fetch('/api/verify_new_email_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message + '! Recarregando...', 'success');
            setTimeout(() => location.reload(), 2000);
        } else {
            showMessage('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão', 'error');
    }
}

async function changePassword() {
    const current = document.getElementById('current_password').value;
    const new_pass = document.getElementById('new_password').value;

    if (!current || !new_pass) {
        showMessage('❌ Preencha todos os campos', 'error');
        return;
    }

    if (new_pass.length < 6) {
        showMessage('❌ A nova senha deve ter pelo menos 6 caracteres', 'error');
        return;
    }

    hideMessage();

    try {
        const response = await fetch('/api/change_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_password: current, new_password: new_pass })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, 'success');
            document.getElementById('current_password').value = '';
            document.getElementById('new_password').value = '';
        } else {
            showMessage('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão', 'error');
    }
}

async function deleteAccount() {
    if (!confirm('⚠️ Tem certeza que deseja excluir sua conta? Esta ação é irreversível!')) return;

    try {
        const response = await fetch('/api/delete_account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showMessage('✅ ' + data.message, 'success');
            setTimeout(() => window.location.href = '/login', 1500);
        } else {
            showMessage('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('❌ Erro de conexão', 'error');
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        if (document.getElementById('oldCodeInput').value) {
            verifyOldEmailCode();
        } else if (document.getElementById('newCodeInput').value) {
            verifyNewEmailCode();
        }
    }
});