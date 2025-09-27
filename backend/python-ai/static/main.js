async function postJSON(path, obj) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj),
  });
  return res.json();
}

document.getElementById('btn-classify').addEventListener('click', async () => {
  const text = document.getElementById('class-text').value || '';
  const out = document.getElementById('class-result');
  out.textContent = 'Working...';
  try {
    const data = await postJSON('/api/classify', { text });
    out.innerHTML = `<b>Label:</b> ${data.label} &nbsp; <b>Score:</b> ${data.score} <br/><b>Matched:</b> ${data.matched.join(', ')}`;
  } catch (e) {
    out.textContent = 'Error: ' + e;
  }
});

document.getElementById('btn-summarize').addEventListener('click', async () => {
  const text = document.getElementById('sum-text').value || '';
  const out = document.getElementById('sum-result');
  out.textContent = 'Working...';
  try {
    const data = await postJSON('/api/summarize', { text });
    out.innerHTML = `<b>Summary:</b> <p>${data.summary}</p>`;
  } catch (e) {
    out.textContent = 'Error: ' + e;
  }
});

document.getElementById('btn-compress').addEventListener('click', async () => {
  const fileInput = document.getElementById('img-file');
  const out = document.getElementById('img-result');
  if (!fileInput.files || fileInput.files.length === 0) {
    out.textContent = 'Select an image first.';
    return;
  }
  const file = fileInput.files[0];
  out.textContent = 'Uploading & compressing...';
  try {
    const form = new FormData();
    form.append('image', file);
    const resp = await fetch('/api/compress', { method: 'POST', body: form });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ error: 'unknown' }));
      out.textContent = 'Error: ' + JSON.stringify(err);
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    out.innerHTML = `<img src="${url}" alt="compressed" style="max-width:300px;display:block;margin:10px 0;"/> <a href="${url}" download="compressed.jpg">Download</a>`;
  } catch (e) {
    out.textContent = 'Error: ' + e;
  }
});
