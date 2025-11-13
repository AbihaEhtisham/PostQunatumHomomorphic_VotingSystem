// static/js/login.js 
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const msg = document.getElementById('loginMsg');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';

    const name = document.getElementById('name').value.trim();
    const cnic = document.getElementById('cnic').value.trim();
    const password = document.getElementById('password').value;

    if (!name) {
      msg.textContent = 'Name is required.';
      return;
    }

    if (!/^\d{13}$/.test(cnic)) {
      msg.textContent = 'CNIC must be 13 digits.';
      return;
    }

    try {
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name, cnic, password })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        // Redirect directly to vote page
        window.location.href = '/vote';
      } else {
        msg.textContent = data.message || 'Login failed';
      }
    } catch (err) {
      console.error(err);
      msg.textContent = 'Network error';
    }
  });
});
