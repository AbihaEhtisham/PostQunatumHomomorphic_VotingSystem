// static/js/signup.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('signupForm');
  const password = document.getElementById('password');
  const confirm = document.getElementById('confirmPassword');
  const msg = document.getElementById('signupMsg');

  const reqLength = document.getElementById('req-length');
  const reqUpper = document.getElementById('req-uppercase');
  const reqSpecial = document.getElementById('req-special');

  // live password validation
  password.addEventListener('input', () => {
    const val = password.value;
    reqLength.textContent = val.length >= 10 ? '✅ At least 10 characters' : '❌ At least 10 characters';
    reqUpper.textContent = /[A-Z]/.test(val) ? '✅ 1 uppercase letter' : '❌ 1 uppercase letter';
    reqSpecial.textContent = /[!@#$%^&*(),.?":{}|<>]/.test(val) ? '✅ 1 special character' : '❌ 1 special character';
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';

    const data = {
      name: document.getElementById('name').value.trim(),
      cnic: document.getElementById('cnic').value.trim(),
      email: document.getElementById('email').value.trim(),
      password: password.value,
      confirmPassword: confirm.value
    };

    // confirm password match
    if (data.password !== data.confirmPassword) {
      msg.textContent = 'Passwords do not match';
      return;
    }

    // check password requirements
    if (data.password.length < 10 || !/[A-Z]/.test(data.password) || !/[!@#$%^&*(),.?":{}|<>]/.test(data.password)) {
      msg.textContent = 'Password does not meet requirements';
      return;
    }

    try {
      const res = await fetch('/signup', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });

      const response = await res.json();
      if (res.ok) {
        msg.style.color = 'green';
        msg.textContent = response.message;
        form.reset();
      } else {
        msg.style.color = 'red';
        msg.textContent = response.message;
      }
    } catch (err) {
      console.error(err);
      msg.textContent = 'Network error';
    }
  });
});
