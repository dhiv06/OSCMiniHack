function insertEmoji(emoji, targetId) {
  const textarea = document.getElementById(targetId);
  if (textarea && textarea.tagName === 'TEXTAREA') {
    textarea.focus(); // ensure focus
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    textarea.value = text.slice(0, start) + emoji + text.slice(end);
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
  }
}

function toggleEmojiPicker(id) {
  const picker = document.getElementById(id);
  picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
}

async function postJSON(path, obj) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj),
  });
  return res.json();
}

// 🔧 Helper: Submit on Enter, newline on Shift+Enter
function handleKeySubmit(e, buttonId) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    document.getElementById(buttonId).click();
  }
}

// 🔍 Classifier
const classText = document.getElementById('class-text');
const classResult = document.getElementById('class-result');

classText.addEventListener('keydown', (e) => handleKeySubmit(e, 'btn-classify'));
document.getElementById('btn-classify').addEventListener('click', async () => {
  const text = classText.value || '';
  classResult.style.display = 'block';
  classResult.textContent = 'Working...';
  try {
    const data = await postJSON('/api/classify', { text });
    classResult.innerHTML = `<b>Label:</b> ${data.label} &nbsp; <b>Score:</b> ${data.score} <br/><b>Matched:</b> ${data.matched.join(', ')}`;
  } catch (e) {
    classResult.textContent = 'Error: ' + e;
  }
  document.activeElement.blur();
});

// 🔍 Summarizer
const sumText = document.getElementById('sum-text');
const sumResult = document.getElementById('sum-result');

sumText.addEventListener('keydown', (e) => handleKeySubmit(e, 'btn-summarize'));
document.getElementById('btn-summarize').addEventListener('click', async () => {
  const text = sumText.value || '';
  sumResult.style.display = 'block';
  sumResult.textContent = 'Working...';
  try {
    const data = await postJSON('/api/summarize', { text });
    sumResult.innerHTML = `<b>Summary:</b> <p>${data.summary}</p>`;
  } catch (e) {
    sumResult.textContent = 'Error: ' + e;
  }
  document.activeElement.blur();
});

// 🖼️ Compressor
const imgFile = document.getElementById('img-file');
const imgResult = document.getElementById('img-result');

document.getElementById('btn-compress').addEventListener('click', async () => {
  if (!imgFile.files || imgFile.files.length === 0) {
    imgResult.style.display = 'block';
    imgResult.textContent = 'Select an image first.';
    return;
  }
  const file = imgFile.files[0];
  imgResult.style.display = 'block';
  imgResult.textContent = 'Uploading & compressing...';
  try {
    const form = new FormData();
    form.append('image', file);
    const resp = await fetch('/api/compress', { method: 'POST', body: form });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ error: 'unknown' }));
      imgResult.textContent = 'Error: ' + JSON.stringify(err);
      return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    imgResult.innerHTML = `<img src="${url}" alt="compressed" style="max-width:300px;display:block;margin:10px 0;"/> <a href="${url}" download="compressed.jpg">Download</a>`;
  } catch (e) {
    imgResult.textContent = 'Error: ' + e;
  }
  document.activeElement.blur();
});


// 👓 Colorblind Mode toggle
document.addEventListener("DOMContentLoaded", () => {
  const colorblindBtn = document.getElementById("btn-colorblind");
  if (colorblindBtn) {
    colorblindBtn.addEventListener("click", () => {
      document.body.classList.toggle("colorblind-mode");
    });
  }
});

