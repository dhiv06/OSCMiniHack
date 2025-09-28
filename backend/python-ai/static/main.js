// 🔧 Emoji Insertion with Bounce + Auto-close
function insertEmoji(emoji, targetId, pickerId, event) {
  const textarea = document.getElementById(targetId);
  if (textarea && textarea.tagName === 'TEXTAREA') {
    textarea.focus();
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    textarea.value = text.slice(0, start) + emoji + text.slice(end);
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;

    const picker = document.getElementById(pickerId);
    if (picker) picker.style.display = 'none';

    if (event && event.target) {
      const span = event.target;
      span.classList.add('emoji-bounce');
      setTimeout(() => span.classList.remove('emoji-bounce'), 300);
    }
  }
}

// 🔧 Toggle Emoji Picker
function toggleEmojiPicker(id) {
  const picker = document.getElementById(id);
  picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
}

// 🔧 Submit on Enter, newline on Shift+Enter
function handleKeySubmit(e, buttonId) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    document.getElementById(buttonId).click();
  }
}

// 🔧 POST Helper
async function postJSON(path, obj) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj),
  });
  return res.json();
}

// 🧠 Word Count Tracker
function updateWordCount(id, countId) {
  const textarea = document.getElementById(id);
  const counter = document.getElementById(countId);
  if (textarea && counter) {
    counter.textContent = `${textarea.value.length} characters`;
    textarea.addEventListener('input', () => {
      counter.textContent = `${textarea.value.length} characters`;
    });
  }
}

// 🔍 Classifier
document.addEventListener('DOMContentLoaded', () => {
  const classText = document.getElementById('class-text');
  const classResult = document.getElementById('class-result');
  const classOutput = document.getElementById('class-output');

  updateWordCount('class-text', 'class-count');

  classText.addEventListener('keydown', (e) => handleKeySubmit(e, 'btn-classify'));
  document.getElementById('btn-classify').addEventListener('click', async () => {
    const text = classText.value || '';
    classResult.style.display = 'block';
    classOutput.textContent = 'Working...';
    try {
      const data = await postJSON('/api/classify', { text });
      classOutput.innerHTML = `<span class="status-icon">🛰️</span><b>Label:</b> ${data.label} &nbsp; <b>Score:</b> ${data.score} <br/><b>Matched:</b> ${data.matched.join(', ')}`;
    } catch (e) {
      classOutput.textContent = 'Error: ' + e;
    }
    document.activeElement.blur();
  });

  // 🔍 Summarizer
  const sumText = document.getElementById('sum-text');
  const sumResult = document.getElementById('sum-result');
  const sumOutput = document.getElementById('sum-output');

  updateWordCount('sum-text', 'sum-count');

  sumText.addEventListener('keydown', (e) => handleKeySubmit(e, 'btn-summarize'));
  document.getElementById('btn-summarize').addEventListener('click', async () => {
    const text = sumText.value || '';
    sumResult.style.display = 'block';
    sumOutput.textContent = 'Working...';
    try {
      const data = await postJSON('/api/summarize', { text });
      sumOutput.innerHTML = `<span class="status-icon">🐥</span><b>Summary:</b> <p>${data.summary}</p>`;
    } catch (e) {
      sumOutput.textContent = 'Error: ' + e;
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

  // 👓 Colorblind Mode
  const colorblindBtn = document.getElementById('btn-colorblind');
  if (colorblindBtn) {
    colorblindBtn.addEventListener('click', () => {
      document.body.classList.toggle('colorblind-mode');
    });
  }

  // 🧪 Demo Mode
  const demoToggle = document.getElementById('demo-mode');
  if (demoToggle) {
    demoToggle.addEventListener('change', () => {
      const isDemo = demoToggle.checked;
      classText.value = isDemo ? '🚨 trapped in basement, need help' : '';
      sumText.value = isDemo ? 'We are a group of 4 people stuck in a flooded building. Water is rising quickly. We need urgent rescue and medical assistance.' : '';
      updateWordCount('class-text', 'class-count');
      updateWordCount('sum-text', 'sum-count');
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const testToggle = document.getElementById('test-mode');
  if (testToggle) {
    testToggle.addEventListener('change', () => {
      const isTest = testToggle.checked;
      console.log('Test Mode:', isTest ? 'ON' : 'OFF');
      // Add any test-specific logic here
    });
  }
});

async function sendMessage(text) {
  const response = await fetch('/api/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });
  const data = await response.json();
  console.log('Server replied:', data);
}



/* dhivyas only
function makeDraggable(id) {
  const el = document.getElementById(id);
  let offsetX = 0, offsetY = 0, isDragging = false;

  el.addEventListener('mousedown', (e) => {
    isDragging = true;
    offsetX = e.clientX - el.offsetLeft;
    offsetY = e.clientY - el.offsetTop;
    el.style.cursor = 'grabbing';
  });

  document.addEventListener('mousemove', (e) => {
    if (isDragging) {
      el.style.left = `${e.clientX - offsetX}px`;
      el.style.top = `${e.clientY - offsetY}px`;
    }
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
    el.style.cursor = 'move';
  });
}

function toggleDemoMode() {
  const isDemo = document.getElementById('demo-mode').checked;
  const classText = document.getElementById('class-text');
  const sumText = document.getElementById('sum-text');

  if (isDemo) {
    classText.value = '🚨 trapped in basement, need help';
    sumText.value = 'We are a group of 4 people stuck in a flooded building. Water is rising quickly. We need urgent rescue and medical assistance.';
  } else {
    classText.value = '';
    sumText.value = '';
  }
}

function insertEmoji(emoji, targetId, pickerId, event) {
  const textarea = document.getElementById(targetId);
  if (textarea && textarea.tagName === 'TEXTAREA') {
    textarea.focus();
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    textarea.value = text.slice(0, start) + emoji + text.slice(end);
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;

    // Auto-close picker
    const picker = document.getElementById(pickerId);
    if (picker) picker.style.display = 'none';

    // Bounce animation
    if (event && event.target) {
      const span = event.target;
      span.classList.add('emoji-bounce');
      setTimeout(() => span.classList.remove('emoji-bounce'), 300);
    }
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
*/
