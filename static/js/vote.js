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

    // PROTOTYPE: simple JSON POST (server will accept this for now)
    // LATER: replace this with Kyber encapsulate + AES encrypt + Dilithium sign,
    // and send { kem_ciphertext, enc_payload, signature } as base64 fields.
    const payload = { candidate, comment };

    try {
      const res = await fetch('/vote', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok) {
        msg.textContent = 'Vote submitted. Thank you!';
        // disable submission
        form.querySelector('button[type="submit"]').disabled = true;
      } else {
        msg.textContent = data.message || 'Submission failed';
      }
    } catch (err) {
      console.error(err);
      msg.textContent = 'Network error';
    }
  });
});
