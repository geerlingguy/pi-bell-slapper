const $ = (id) => document.getElementById(id);

function show(message, type = 'success') {
  const alert = $('alert');
  alert.getAnimations().forEach((a) => a.cancel());
  alert.className = `alert alert-${type}`;
  alert.textContent = message;
  clearTimeout(show.timer);
  show.timer = setTimeout(() => hide(alert), 4000);
}

// Fade out, then collapse so the page slides up.
async function hide(el) {
  const s = getComputedStyle(el);
  try {
    await el.animate({ opacity: [1, 0] }, { duration: 300, fill: 'forwards' }).finished;
    await el.animate({
      height: [s.height, '0px'],
      paddingTop: [s.paddingTop, '0px'],
      paddingBottom: [s.paddingBottom, '0px'],
      marginBottom: [s.marginBottom, '0px'],
      borderWidth: [s.borderTopWidth, '0px'],
    }, { duration: 300, easing: 'ease', fill: 'forwards' }).finished;
  } catch {
    return; // A new message replaced this one.
  }
  el.classList.add('d-none');
  el.getAnimations().forEach((a) => a.cancel());
}

// Slide an element open or closed.
function slide(el, open) {
  el.getAnimations().forEach((a) => a.cancel());
  el.classList.add('show');
  const height = `${el.scrollHeight}px`;
  el.style.overflow = 'hidden';
  el.animate({ height: open ? ['0px', height] : [height, '0px'] }, { duration: 200, easing: 'ease' })
    .onfinish = () => {
      el.style.overflow = '';
      el.classList.toggle('show', open);
    };
}

async function api(method, path, body, type = 'application/json') {
  const res = await fetch(path, {
    method,
    headers: body ? { 'Content-Type': type } : {},
    body: body && type === 'application/json' ? JSON.stringify(body) : body,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function render(data) {
  if (data.sounds) {
    $('sound').replaceChildren(...data.sounds.map((name) => new Option(name, name)));
  }
  if ('volume' in data) {
    $('volume-group').classList.toggle('d-none', data.volume === null);
    $('volume').value = data.volume ?? 0;
    $('volume-value').textContent = $('volume').value;
  }
  if (data.settings) {
    $('sound').value = data.settings.sound;
    $('interval').value = data.settings.interval.toFixed(2);
  }
}

// Bar chart of dings per hour for the last 24 hours, from /api/stats.
async function refreshChart() {
  const { hourly } = await api('GET', '/api/stats').catch(() => ({ hourly: [] }));
  const max = Math.max(1, ...hourly.map(([, n]) => n));
  const hour = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: 'numeric' });
  const chart = $('chart');
  chart.style.height = '100px';
  chart.replaceChildren(...hourly.map(([t, n]) => {
    // Full-height column, so empty hours can be hovered or tapped too.
    const column = document.createElement('div');
    column.className = 'flex-fill h-100 d-flex align-items-end';
    column.dataset.count = n;
    column.setAttribute('aria-label', `${hour(t)}: ${n} ding${n === 1 ? '' : 's'}`);
    const bar = document.createElement('div');
    bar.className = 'w-100 bg-primary rounded-top';
    bar.style.height = `${(n / max) * 100}%`;
    column.append(bar);
    return column;
  }));
  hideChartValue();
  const total = hourly.reduce((sum, [, n]) => sum + n, 0);
  $('chart-total').textContent = `${total} in the last 24 hours`;
  $('chart-labels').replaceChildren(...[0, 6, 12, 18, 23].filter((i) => hourly[i]).map((i) => {
    const label = document.createElement('span');
    label.textContent = i === 23 ? 'Now' : hour(hourly[i][0]);
    return label;
  }));
}

// Show a column's ding count just above its bar.
function showChartValue(column) {
  const value = $('chart-value');
  value.textContent = column.dataset.count;
  value.style.left = `${column.offsetLeft + column.offsetWidth / 2}px`;
  value.style.bottom = `${column.firstChild.offsetHeight + 2}px`;
  value.classList.remove('d-none');
}

function hideChartValue() {
  $('chart-value').classList.add('d-none');
}

async function ding(sound) {
  const count = Number(document.querySelector('[name=count]:checked').value);
  try {
    const { position } = await api('POST', '/api/ding', { count, sound });
    const extra = sound ? ' with sound' : '';
    show(position > 1
      ? `Queued ${count} ding${count > 1 ? 's' : ''}${extra} (#${position} in line).`
      : `Dinging ${count > 1 ? `${count} times` : 'once'}${extra}!`);
    setTimeout(refreshChart, 2000);
  } catch (e) {
    show(e.message, 'warning');
  }
}

async function save(change) {
  try {
    render({ settings: await api('PUT', '/api/settings', change) });
    show('Settings saved.');
  } catch (e) {
    show(e.message, 'danger');
    render(await api('GET', '/api/status'));
  }
}

for (let i = 1; i <= 10; i++) {
  $('count').insertAdjacentHTML('beforeend',
    `<input type="radio" class="btn-check" name="count" id="count${i}" value="${i}"${i === 1 ? ' checked' : ''}>` +
    `<label class="btn btn-outline-primary px-0" for="count${i}">${i}</label>`);
}

$('config-toggle').onclick = () => {
  const open = $('config-toggle').classList.contains('collapsed');
  slide($('config'), open);
  $('config-toggle').classList.toggle('collapsed', !open);
  $('config-toggle').setAttribute('aria-expanded', open);
};
$('chart').onpointerover = (e) => {
  const column = e.target.closest('[data-count]');
  if (column && e.pointerType === 'mouse') showChartValue(column);
};
$('chart').onpointerleave = (e) => {
  if (e.pointerType === 'mouse') hideChartValue();
};
// Tap (or click) a bar to show its count; tap anywhere else to hide it.
document.addEventListener('click', (e) => {
  const column = e.target.closest('#chart [data-count]');
  if (column) showChartValue(column);
  else hideChartValue();
});

$('ding').onclick = () => ding(false);
$('ding-sound').onclick = () => ding(true);
$('interval').onchange = () => save({ interval: $('interval').value });
$('sound').onchange = () => save({ sound: $('sound').value });
$('volume').oninput = () => { $('volume-value').textContent = $('volume').value; };
$('volume').onchange = () => save({ volume: $('volume').value });

$('delete').onclick = async () => {
  const name = $('sound').value;
  if (!name || !confirm(`Delete "${name}"?`)) return;
  try {
    render(await api('DELETE', `/api/sounds/${encodeURIComponent(name)}`));
    show(`Deleted "${name}".`);
  } catch (e) {
    show(e.message, 'danger');
  }
};

$('upload').onclick = async () => {
  const file = $('file').files[0];
  if (!file) return show('Choose a file first.', 'warning');
  const button = $('upload');
  button.disabled = $('file').disabled = true;
  button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Uploading…';
  try {
    const data = await api('POST', `/api/sounds?name=${encodeURIComponent(file.name)}`, file,
      'application/octet-stream');
    render(data);
    await save({ sound: data.name });
    $('file').value = '';
    show(`Uploaded "${data.name}".`);
  } catch (e) {
    show(e.message, 'danger');
  } finally {
    button.disabled = $('file').disabled = false;
    button.textContent = 'Upload';
  }
};

api('GET', '/api/status').then(render).catch((e) => show(e.message, 'danger'));
refreshChart();
setInterval(refreshChart, 60000);
