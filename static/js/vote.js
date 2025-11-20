// static/js/vote.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('voteForm');
  const msg = document.getElementById('voteMsg');
  const logoutBtn = document.getElementById('logoutBtn');

  logoutBtn.addEventListener('click', async () => {
    await fetch('/logout', { method: 'POST' });
    window.location.href = '/';
  });

  form.addEventListener('submit', async (e) => {
  e.preventDefault();
  msg.textContent = '';

  const candidate = form.elements['candidate'].value;
  const comment = document.getElementById('comment').value;

  const formData = new FormData();
  formData.append('candidate', candidate);
  formData.append('comment', comment);

  try {
    const res = await fetch('/submit_vote', {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const html = await res.text();  // Flask returns rendered receipt.html
      msg.innerHTML = 'Vote submitted. See receipt below:<br>' + html;
      form.querySelector('button[type="submit"]').disabled = true;
    } else {
      const text = await res.text();
      msg.textContent = text || 'Submission failed';
    }
  } catch (err) {
    console.error(err);
    msg.textContent = 'Network error';
  }
});
});
