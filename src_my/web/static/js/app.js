
const state = {
  login:     null,   
  password:  null,   
  userId:    null,   
  gameId:    null,   
  game:      null,   
  mySymbol:  null,   
  pollTimer: null,   
  lastState: null,   
  lastBoard: null,  
};

const API = window.location.origin;
const POLL_INTERVAL = 2000; 





function authHeader() {
  if (!state.login) return {};
  return { 'Authorization': 'Basic ' + btoa(state.login + ':' + state.password) };
}


async function api(method, path, body = null, silent = false) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeader() },
  };
  if (body) opts.body = JSON.stringify(body);

  if (!silent) log('→ ' + method + ' ' + path, 'dim');

  try {
    const resp = await fetch(API + path, opts);
    const data = await resp.json().catch(() => ({}));
    if (!silent) log('← ' + resp.status + ' ' + JSON.stringify(data).slice(0, 120), resp.ok ? 'ok' : 'err');
    return { ok: resp.ok, status: resp.status, data };
  } catch (e) {
    if (!silent) log('✕ ОШИБКА: ' + e.message, 'err');
    return { ok: false, data: {} };
  }
}



function startPolling() {
  stopPolling();
  document.getElementById('poll-indicator').classList.remove('hidden');
  state.pollTimer = setInterval(pollGame, POLL_INTERVAL);
}

function stopPolling() {
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
  document.getElementById('poll-indicator').classList.add('hidden');
}

async function pollGame() {
  if (!state.gameId || !state.login) return;


  const dot = document.getElementById('poll-dot');
  dot.classList.add('active');
  setTimeout(() => dot.classList.remove('active'), 300);


  const r = await api('GET', '/games/' + state.gameId, null, true);
  if (!r.ok) return;

  const g        = r.data;
  const boardStr = JSON.stringify(g.board.matrix);


  if (g.state !== state.lastState || boardStr !== state.lastBoard) {
    state.game      = g;
    state.lastBoard = boardStr;
    renderGame();


    if (g.state !== state.lastState) {
      if (state.lastState === 'waiting' && g.state === 'turn') {
        log('✓ Второй игрок присоединился! Игра началась.', 'ok');
      } else if (g.state === 'turn' && g.current_turn === state.userId) {
        log('▶ Твой ход!', 'ok');
      } else if (g.state === 'turn' && g.current_turn !== state.userId) {
        log('⏳ Ход соперника...', 'info');
      } else if (g.state === 'win') {
        const iWon = g.current_turn === state.userId;
        log(iWon ? '🏆 Ты победил!' : '✕ Ты проиграл', iWon ? 'ok' : 'err');
        stopPolling();
        return;
      } else if (g.state === 'draw') {
        log('≈ Ничья!', 'info');
        stopPolling();
        return;
      }
    }

    state.lastState = g.state;
  }
}




async function doLogin() {
  const login    = document.getElementById('login-input').value.trim();
  const password = document.getElementById('password-input').value;
  if (!login || !password) return log('✕ Введи логин и пароль', 'err');

  state.login    = login;
  state.password = password;

  const r = await api('POST', '/auth/login');

  if (r.ok) {
    state.userId = r.data.user_id;
    document.getElementById('auth-status').className   = 'auth-status logged-in';
    document.getElementById('auth-status').textContent = '● ВОШЁЛ: ' + login;
    document.getElementById('user-uuid-box').classList.remove('hidden');
    document.getElementById('user-uuid-val').textContent = state.userId;
    log('✓ Авторизован как ' + login, 'ok');
  } else {
    state.login = state.password = null;
    log('✕ Неверный логин или пароль', 'err');
  }
}

function doLogout() {
  stopPolling();
  state.login = state.password = state.userId = null;
  document.getElementById('auth-status').className   = 'auth-status logged-out';
  document.getElementById('auth-status').textContent = '○ НЕ АВТОРИЗОВАН';
  document.getElementById('user-uuid-box').classList.add('hidden');
  log('✓ Вышел из аккаунта', 'info');
}

async function doRegister() {
  const login    = document.getElementById('reg-login').value.trim();
  const password = document.getElementById('reg-password').value;
  if (!login || !password) return log('✕ Введи логин и пароль', 'err');

  const r = await api('POST', '/auth/register', { login, password });
  if (r.ok) {
    log('✓ Пользователь ' + login + ' зарегистрирован', 'ok');
  } else {
    log('✕ ' + (r.data.error || 'Ошибка регистрации'), 'err');
  }
}



async function createGame() {
  if (!state.login) return log('✕ Войди в аккаунт', 'err');

  const opponent_type = document.getElementById('opponent-type').value;
  const r = await api('POST', '/games', { opponent_type });

  if (r.ok) {
    state.gameId    = r.data.id;
    state.game      = r.data;
    state.lastState = r.data.state;
    state.lastBoard = JSON.stringify(r.data.board.matrix);
    state.mySymbol  = 1; 

    renderGame();
    startPolling();
    log('✓ Игра создана — ты играешь за X', 'ok');

    if (opponent_type === 'user') {
      log('⏳ Ожидаем второго игрока...', 'info');
    }
  }
}

async function joinGame(gameId) {
  if (!state.login) return log('✕ Войди в аккаунт', 'err');

  const r = await api('POST', '/games/' + gameId + '/join');

  if (r.ok) {
    state.gameId    = gameId;
    state.game      = r.data;
    state.lastState = r.data.state;
    state.lastBoard = JSON.stringify(r.data.board.matrix);
    state.mySymbol  = 2; 

    renderGame();
    startPolling();
    log('✓ Присоединился к игре — ты играешь за O', 'ok');
  }
}

async function makeMove() {
  if (!state.gameId) return log('✕ Нет активной игры', 'err');

  const row = parseInt(document.getElementById('move-row').value);
  const col = parseInt(document.getElementById('move-col').value);
  const r   = await api('PATCH', '/games/' + state.gameId, { row, col });

  if (r.ok) {
    state.game      = r.data;
    state.lastState = r.data.state;
    state.lastBoard = JSON.stringify(r.data.board.matrix);
    renderGame();
  }
}

async function makeCellMove(row, col) {
  document.getElementById('move-row').value = row;
  document.getElementById('move-col').value = col;
  await makeMove();
}

async function refreshGame() {
  if (!state.gameId) return log('✕ Нет активной игры', 'err');
  const r = await api('GET', '/games/' + state.gameId);
  if (r.ok) { state.game = r.data; renderGame(); }
}

function clearGame() {
  stopPolling();
  state.gameId    = null;
  state.game      = null;
  state.mySymbol  = null;
  state.lastState = null;
  state.lastBoard = null;

  document.getElementById('game-id-box').classList.add('hidden');
  document.getElementById('my-symbol').classList.add('hidden');

  renderGame();
  log('✓ Игра сброшена', 'info');
}

async function loadGames() {
  if (!state.login) return log('✕ Войди в аккаунт', 'err');

  const r    = await api('GET', '/games');
  const list = document.getElementById('games-list');

  if (!r.ok) return;

  if (!r.data.length) {
    list.innerHTML = '<div class="empty-msg">Нет доступных игр</div>';
    return;
  }

  list.innerHTML = r.data.map(g => `
    <div class="game-item">
      <div>
        <div class="game-id">${g.id}</div>
        <span class="badge badge-waiting">WAITING</span>
        <span class="badge badge-user">${g.opponent_type}</span>
      </div>
      <button class="btn btn-info btn-sm" onclick="joinGame('${g.id}')">JOIN</button>
    </div>
  `).join('');
}

async function getUser() {
  const id = document.getElementById('search-uuid').value.trim();
  if (!id) return log('✕ Введи UUID', 'err');

  const r = await api('GET', '/users/' + id);

  if (r.ok) {
    document.getElementById('user-info').classList.remove('hidden');
    document.getElementById('ui-id').textContent    = r.data.id;
    document.getElementById('ui-login').textContent = r.data.login;
  }
}



function renderGame() {
  const board    = document.getElementById('board');
  const statusEl = document.getElementById('game-status');
  const idBox    = document.getElementById('game-id-box');
  const symBox   = document.getElementById('my-symbol');

  if (!state.game) {
    board.innerHTML = '';
    for (let i = 0; i < 9; i++) {
      const cell     = document.createElement('div');
      cell.className = 'cell blocked';
      board.appendChild(cell);
    }
    statusEl.className   = 'game-status gs-idle';
    statusEl.textContent = 'ИГРА НЕ НАЧАТА';
    return;
  }

  const g        = state.game;
  const matrix   = g.board.matrix;
  const gameOver = g.state === 'win' || g.state === 'draw';
  const isMyTurn = g.state === 'turn' && g.current_turn === state.userId;

  idBox.classList.remove('hidden');
  document.getElementById('game-uuid-val').textContent = g.id;

  if (state.mySymbol) {
    symBox.classList.remove('hidden');
    symBox.className   = 'my-symbol-box ' + (state.mySymbol === 1 ? 'x' : 'o');
    symBox.textContent = 'ТЫ ИГРАЕШЬ ЗА: ' + (state.mySymbol === 1 ? 'X ✕' : 'O ○');
  }

  statusEl.className = 'game-status ';
  if (g.state === 'waiting') {
    statusEl.className  += 'gs-waiting';
    statusEl.textContent = '⏳ ОЖИДАНИЕ ВТОРОГО ИГРОКА...';
  } else if (g.state === 'turn' && isMyTurn) {
    statusEl.className  += 'gs-turn';
    statusEl.textContent = '▶ ТВОЙ ХОД ' + (state.mySymbol === 1 ? '(X)' : '(O)');
  } else if (g.state === 'turn' && !isMyTurn) {
    statusEl.className  += 'gs-enemy';
    statusEl.textContent = '⏳ ХОД СОПЕРНИКА...';
  } else if (g.state === 'win') {
    const iWon          = g.current_turn === state.userId;
    statusEl.className  += iWon ? 'gs-win' : 'gs-lose';
    statusEl.textContent = iWon ? '🏆 ТЫ ПОБЕДИЛ!' : '✕ ТЫ ПРОИГРАЛ';
  } else if (g.state === 'draw') {
    statusEl.className  += 'gs-draw';
    statusEl.textContent = '≈ НИЧЬЯ';
  }

  board.innerHTML = '';
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const val      = matrix[r][c];
      const sym      = val === 1 ? 'X' : val === 2 ? 'O' : '';
      const symClass = val === 1 ? ' x' : val === 2 ? ' o' : '';

      const canClick = val === 0 && isMyTurn && !gameOver;

      const cell       = document.createElement('div');
      cell.className   = 'cell' + symClass + (canClick ? ' clickable' : ' blocked');
      cell.textContent = sym;

      if (canClick) {
        cell.onclick = ((row, col) => () => makeCellMove(row, col))(r, c);
      }

      board.appendChild(cell);
    }
  }
}


function log(msg, type = 'info') {
  const el  = document.getElementById('log');
  const div = document.createElement('div');
  div.className   = 'log-entry ' + type;
  div.textContent = msg;
  el.appendChild(div);
  el.scrollTop = el.scrollHeight; 
}

function clearLog() {
  document.getElementById('log').innerHTML =
    '<div class="log-entry dim">// Лог очищен</div>';
}


function switchTab(btn, tabId) {
  const panel = btn.closest('.panel');
  panel.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  panel.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  panel.querySelector('#' + tabId).classList.add('active');
}


renderGame();
log('// Приложение запущено. Войди в аккаунт.', 'info');
log('// В режиме двух игроков поле обновляется автоматически каждые 2 сек.', 'dim');