export function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
    }
}

export function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

export function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

export function bindLogout(selector = '#logoutBtn') {
    const btn = document.querySelector(selector);
    if (btn) {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}