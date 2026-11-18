const $ = (id) => document.getElementById(id);

function show(message, type = 'success') {
  const alert = $('alert');
  alert.className = `alert alert-${type}`;
  alert.textContent = message;
  clearTimeout(show.timer);
  show.timer = setTimeout(() => alert.classList.add('d-none'), 4000);
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

async function ding(sound) {
  const count = Number(document.querySelector('[name=count]:checked').value);
  try {
    const { position } = await api('POST', '/api/ding', { count, sound });
    const what = `${count} ding${count > 1 ? 's' : ''}${sound ? ' with sound' : ''}`;
    show(position > 1 ? `Queued ${what} (#${position} in line).` : `Dinging ${what}!`);
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
  const open = $('config').classList.toggle('show');
  $('config-toggle').classList.toggle('collapsed', !open);
  $('config-toggle').setAttribute('aria-expanded', open);
};
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
