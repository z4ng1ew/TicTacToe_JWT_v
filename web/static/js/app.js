const state = {
    accessToken:  null,
    refreshToken: null,
    userId:       null,
    login:        null,
    gameId:       null,
    game:         null,
    mySymbol:     null,
    pollTimer:    null,
    lastState:    null,
    lastBoard:    null,
};

const API           = window.location.origin;
const POLL_INTERVAL = 2000;
const LS_ACCESS     = 'ttt_access';
const LS_REFRESH    = 'ttt_refresh';
const LS_USER       = 'ttt_user';




function shortToken(token) {
    if (token === null || token === undefined) {
        return '';
    } else {
        return token.slice(0, 20) + '…' + token.slice(-10);
    }
}

function saveSession() {
    if (state.accessToken !== null) {
        localStorage.setItem(LS_ACCESS,  state.accessToken);
        localStorage.setItem(LS_REFRESH, state.refreshToken);
        localStorage.setItem(LS_USER,    JSON.stringify({ id: state.userId, login: state.login }));
    } else {
        localStorage.removeItem(LS_ACCESS);
        localStorage.removeItem(LS_REFRESH);
        localStorage.removeItem(LS_USER);
    }
}

function restoreSession() {
    const access  = localStorage.getItem(LS_ACCESS);
    const refresh = localStorage.getItem(LS_REFRESH);
    const userStr = localStorage.getItem(LS_USER);

    if (access !== null && refresh !== null && userStr !== null) {
        const user        = JSON.parse(userStr);
        state.accessToken = access;
        state.refreshToken= refresh;
        state.userId      = user.id;
        state.login       = user.login;
        updateAuthUI();
        log('✓ Сессия восстановлена для ' + user.login + '.', 'ok');
    }
}

function updateAuthUI() {
    if (state.accessToken === null) {
        document.getElementById('auth-status').className   = 'auth-status logged-out';
        document.getElementById('auth-status').textContent = '○ Не авторизован';
        document.getElementById('user-uuid-box').classList.add('hidden');
        document.getElementById('token-box').classList.add('hidden');
    } else {
        document.getElementById('auth-status').className   = 'auth-status logged-in';
        document.getElementById('auth-status').textContent = '● Вошёл: ' + state.login;
        document.getElementById('user-uuid-box').classList.remove('hidden');
        document.getElementById('user-uuid-val').textContent = state.userId;
        document.getElementById('token-box').classList.remove('hidden');
        document.getElementById('access-val').textContent  = shortToken(state.accessToken);
        document.getElementById('refresh-val').textContent = shortToken(state.refreshToken);
    }
}




function authHeader() {
    if (state.accessToken === null) {
        return {};
    } else {
        return { 'Authorization': 'Bearer ' + state.accessToken };
    }
}

async function api(method, path, body = null, silent = false, allowRetry = true) {
    const options = {
        method:  method,
        headers: { 'Content-Type': 'application/json', ...authHeader() },
    };

    if (body !== null) {
        options.body = JSON.stringify(body);
    }

    if (!silent) {
        log('→ ' + method + ' ' + path, 'dim');
    }

    let response;
    try {
        response = await fetch(API + path, options);
    } catch (error) {
        if (!silent) {
            log('✕ Сеть: ' + error.message, 'err');
        }
        return { ok: false, status: 0, data: {} };
    }

    if (response.status === 401 && allowRetry && state.refreshToken !== null && path !== '/auth/login' && path !== '/auth/access') {
        const ok = await tryRefreshAccess(silent);
        if (ok) {
            return await api(method, path, body, silent, false);
        }
    }

    const data = await response.json().catch(() => ({}));

    if (!silent) {
        const summary = JSON.stringify(data).slice(0, 120);
        log('← ' + response.status + ' ' + summary, response.ok ? 'ok' : 'err');
    }

    return { ok: response.ok, status: response.status, data: data };
}

async function tryRefreshAccess(silent) {
    if (!silent) {
        log('↺ Access истёк — пробуем обновить...', 'info');
    }

    const response = await fetch(API + '/auth/access', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ refreshToken: state.refreshToken }),
    });

    if (!response.ok) {
        log('✕ Refresh-токен невалидный. Войди заново.', 'err');
        doLogout();
        return false;
    }

    const data        = await response.json();
    state.accessToken = data.accessToken;
    saveSession();
    updateAuthUI();
    log('✓ Access-токен обновлён.', 'ok');
    return true;
}




function startPolling() {
    stopPolling();
    document.getElementById('poll-indicator').classList.remove('hidden');
    state.pollTimer = setInterval(pollGame, POLL_INTERVAL);
}

function stopPolling() {
    if (state.pollTimer !== null) {
        clearInterval(state.pollTimer);
        state.pollTimer = null;
    }
    document.getElementById('poll-indicator').classList.add('hidden');
}

async function pollGame() {
    if (state.gameId === null || state.accessToken === null) {
        return;
    }

    const dot = document.getElementById('poll-dot');
    dot.classList.add('active');
    setTimeout(() => dot.classList.remove('active'), 300);

    const response = await api('GET', '/games/' + state.gameId, null, true);
    if (!response.ok) {
        return;
    }

    const game     = response.data;
    const boardStr = JSON.stringify(game.board.matrix);

    if (game.state === state.lastState && boardStr === state.lastBoard) {
        return;
    }

    state.game      = game;
    state.lastBoard = boardStr;
    renderGame();

    if (game.state !== state.lastState) {
        if (state.lastState === 'waiting' && game.state === 'turn') {
            log('✓ Второй игрок присоединился. Игра началась.', 'ok');
        } else if (game.state === 'turn' && game.current_turn === state.userId) {
            log('▶ Твой ход.', 'ok');
        } else if (game.state === 'turn' && game.current_turn !== state.userId) {
            log('⏳ Ход соперника...', 'info');
        } else if (game.state === 'win') {
            const iWon = game.current_turn === state.userId;
            log(iWon ? '🏆 Ты победил.' : '✕ Ты проиграл.', iWon ? 'ok' : 'err');
            stopPolling();
        } else if (game.state === 'draw') {
            log('≈ Ничья.', 'info');
            stopPolling();
        }
    }

    state.lastState = game.state;
}




async function doLogin() {
    const login    = document.getElementById('login-input').value.trim();
    const password = document.getElementById('password-input').value;

    if (login === '' || password === '') {
        log('✕ Введи логин и пароль.', 'err');
        return;
    }

    const response = await api('POST', '/auth/login', { login: login, password: password }, false, false);

    if (response.ok) {
        state.accessToken  = response.data.accessToken;
        state.refreshToken = response.data.refreshToken;
        state.login        = login;

        const meResp = await api('GET', '/auth/me', null, true);
        if (meResp.ok) {
            state.userId = meResp.data.id;
        }

        saveSession();
        updateAuthUI();
        log('✓ Авторизован как ' + login + '. Получены access + refresh токены.', 'ok');
    } else {
        log('✕ Неверный логин или пароль.', 'err');
    }
}

function doLogout() {
    stopPolling();
    state.accessToken  = null;
    state.refreshToken = null;
    state.userId       = null;
    state.login        = null;
    saveSession();
    updateAuthUI();
    log('✓ Вышел из аккаунта.', 'info');
}

async function doRegister() {
    const login    = document.getElementById('reg-login').value.trim();
    const password = document.getElementById('reg-password').value;

    if (login === '' || password === '') {
        log('✕ Введи логин и пароль.', 'err');
        return;
    }

    const response = await api('POST', '/auth/register', { login: login, password: password }, false, false);

    if (response.ok) {
        log('✓ Пользователь "' + login + '" зарегистрирован.', 'ok');
    } else {
        log('✕ ' + (response.data.error || 'Ошибка регистрации.'), 'err');
    }
}

async function refreshAccess() {
    if (state.refreshToken === null) {
        log('✕ Нет refresh-токена.', 'err');
        return;
    }

    const ok = await tryRefreshAccess(false);
    if (ok) {
        updateAuthUI();
    }
}

async function refreshRefresh() {
    if (state.refreshToken === null) {
        log('✕ Нет refresh-токена.', 'err');
        return;
    }

    const response = await api('POST', '/auth/refresh', { refreshToken: state.refreshToken }, false, false);

    if (response.ok) {
        state.accessToken  = response.data.accessToken;
        state.refreshToken = response.data.refreshToken;
        saveSession();
        updateAuthUI();
        log('✓ Обновлены оба токена.', 'ok');
    }
}

async function getMe() {
    const response = await api('GET', '/auth/me');

    if (response.ok) {
        log('✓ /me → ' + response.data.login + ' (' + response.data.id + ')', 'ok');
    }
}




async function createGame() {
    if (state.accessToken === null) {
        log('✕ Войди в аккаунт.', 'err');
        return;
    }

    const opponentType = document.getElementById('opponent-type').value;
    const response     = await api('POST', '/games', { opponent_type: opponentType });

    if (!response.ok) {
        return;
    }

    state.gameId    = response.data.id;
    state.game      = response.data;
    state.lastState = response.data.state;
    state.lastBoard = JSON.stringify(response.data.board.matrix);
    state.mySymbol  = 1;

    renderGame();
    startPolling();
    log('✓ Игра создана — ты играешь за X.', 'ok');

    if (opponentType === 'user') {
        log('⏳ Ожидаем второго игрока...', 'info');
    }
}

async function joinGame(gameId) {
    if (state.accessToken === null) {
        log('✕ Войди в аккаунт.', 'err');
        return;
    }

    const response = await api('POST', '/games/' + gameId + '/join');

    if (!response.ok) {
        return;
    }

    state.gameId    = gameId;
    state.game      = response.data;
    state.lastState = response.data.state;
    state.lastBoard = JSON.stringify(response.data.board.matrix);
    state.mySymbol  = 2;

    renderGame();
    startPolling();
    log('✓ Присоединился к игре — ты играешь за O.', 'ok');
}

async function makeMove() {
    if (state.gameId === null) {
        log('✕ Нет активной игры.', 'err');
        return;
    }

    const row      = parseInt(document.getElementById('move-row').value, 10);
    const col      = parseInt(document.getElementById('move-col').value, 10);
    const response = await api('PATCH', '/games/' + state.gameId, { row: row, col: col });

    if (response.ok) {
        state.game      = response.data;
        state.lastState = response.data.state;
        state.lastBoard = JSON.stringify(response.data.board.matrix);
        renderGame();
    }
}

async function makeCellMove(row, col) {
    document.getElementById('move-row').value = row;
    document.getElementById('move-col').value = col;
    await makeMove();
}

async function refreshGame() {
    if (state.gameId === null) {
        log('✕ Нет активной игры.', 'err');
        return;
    }

    const response = await api('GET', '/games/' + state.gameId);

    if (response.ok) {
        state.game = response.data;
        renderGame();
    }
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
    log('✓ Игра сброшена.', 'info');
}

async function loadGames() {
    if (state.accessToken === null) {
        log('✕ Войди в аккаунт.', 'err');
        return;
    }

    const response = await api('GET', '/games');
    const list     = document.getElementById('games-list');

    if (!response.ok) {
        return;
    }

    if (response.data.length === 0) {
        list.innerHTML = '<div class="empty-msg">Нет доступных игр</div>';
        return;
    }

    list.innerHTML = response.data.map(game => `
        <div class="game-item">
            <div>
                <div class="game-id">${game.id}</div>
                <span class="badge badge-waiting">Waiting</span>
                <span class="badge badge-user">${game.opponent_type}</span>
            </div>
            <button class="btn btn-info btn-sm" onclick="joinGame('${game.id}')">Join</button>
        </div>
    `).join('');
}

async function getUser() {
    const id = document.getElementById('search-uuid').value.trim();

    if (id === '') {
        log('✕ Введи UUID.', 'err');
        return;
    }

    const response = await api('GET', '/users/' + id);

    if (response.ok) {
        document.getElementById('user-info').classList.remove('hidden');
        document.getElementById('ui-id').textContent    = response.data.id;
        document.getElementById('ui-login').textContent = response.data.login;
    }
}




async function loadHistory() {
    if (state.accessToken === null) {
        log('✕ Войди в аккаунт.', 'err');
        return;
    }

    const response = await api('GET', '/games/history');
    const list     = document.getElementById('history-list');

    if (!response.ok) {
        return;
    }

    if (response.data.length === 0) {
        list.innerHTML = '<div class="empty-msg">У тебя пока нет завершённых игр</div>';
        return;
    }

    list.innerHTML = response.data.map(game => {
        let outcome    = '';
        let outcomeCls = '';

        if (game.state === 'draw') {
            outcome    = 'Ничья';
            outcomeCls = 'badge-user';
        } else if (game.state === 'win' && game.current_turn === state.userId) {
            outcome    = 'Победа';
            outcomeCls = 'badge-waiting';
        } else {
            outcome    = 'Поражение';
            outcomeCls = 'badge-user';
        }

        return `
            <div class="game-item">
                <div>
                    <div class="game-id">${game.id}</div>
                    <span class="badge ${outcomeCls}">${outcome}</span>
                    <span class="badge badge-user">${game.opponent_type}</span>
                </div>
            </div>
        `;
    }).join('');
}

async function loadLeaderboard() {
    if (state.accessToken === null) {
        log('✕ Войди в аккаунт.', 'err');
        return;
    }

    const n        = parseInt(document.getElementById('top-n').value, 10) || 10;
    const response = await api('GET', '/leaderboard?n=' + n);
    const list     = document.getElementById('leaders-list');

    if (!response.ok) {
        return;
    }

    if (response.data.length === 0) {
        list.innerHTML = '<div class="empty-msg">Завершённых игр ещё нет</div>';
        return;
    }

    list.innerHTML = response.data.map((entry, idx) => `
        <div class="game-item">
            <div>
                <div style="font-weight:600;font-size:0.92rem;">#${idx + 1} — ${entry.login}</div>
                <div class="game-id">${entry.user_id}</div>
                <span class="badge badge-waiting">W:${entry.wins}</span>
                <span class="badge badge-user">L:${entry.losses} D:${entry.draws}</span>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-weight:700;color:var(--green);">
                ${entry.win_ratio}
            </div>
        </div>
    `).join('');
}




function renderGame() {
    const board    = document.getElementById('board');
    const statusEl = document.getElementById('game-status');
    const idBox    = document.getElementById('game-id-box');
    const symBox   = document.getElementById('my-symbol');

    if (state.game === null) {
        board.innerHTML = '';
        for (let i = 0; i < 9; i++) {
            const cell     = document.createElement('div');
            cell.className = 'cell blocked';
            board.appendChild(cell);
        }
        statusEl.className   = 'game-status gs-idle';
        statusEl.textContent = 'Игра не начата';
        return;
    }

    const game     = state.game;
    const matrix   = game.board.matrix;
    const gameOver = game.state === 'win' || game.state === 'draw';
    const isMyTurn = game.state === 'turn' && game.current_turn === state.userId;

    idBox.classList.remove('hidden');
    document.getElementById('game-uuid-val').textContent = game.id;

    if (state.mySymbol !== null) {
        symBox.classList.remove('hidden');
        symBox.className   = 'my-symbol-box ' + (state.mySymbol === 1 ? 'x' : 'o');
        symBox.textContent = 'Ты играешь за: ' + (state.mySymbol === 1 ? 'X ✕' : 'O ○');
    }

    if (game.state === 'waiting') {
        statusEl.className   = 'game-status gs-waiting';
        statusEl.textContent = '⏳ Ожидание второго игрока...';
    } else if (game.state === 'turn' && isMyTurn) {
        statusEl.className   = 'game-status gs-turn';
        statusEl.textContent = '▶ Твой ход ' + (state.mySymbol === 1 ? '(X)' : '(O)');
    } else if (game.state === 'turn' && !isMyTurn) {
        statusEl.className   = 'game-status gs-enemy';
        statusEl.textContent = '⏳ Ход соперника...';
    } else if (game.state === 'win') {
        const iWon           = game.current_turn === state.userId;
        statusEl.className   = 'game-status ' + (iWon ? 'gs-win' : 'gs-lose');
        statusEl.textContent = iWon ? '🏆 Ты победил!' : '✕ Ты проиграл';
    } else if (game.state === 'draw') {
        statusEl.className   = 'game-status gs-draw';
        statusEl.textContent = '≈ Ничья';
    }

    board.innerHTML = '';

    for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
            const value    = matrix[r][c];
            const canClick = value === 0 && isMyTurn && !gameOver;

            let symbol   = '';
            let symClass = '';

            if (value === 1) {
                symbol   = 'X';
                symClass = ' x';
            } else if (value === 2) {
                symbol   = 'O';
                symClass = ' o';
            }

            const cell       = document.createElement('div');
            cell.className   = 'cell' + symClass + (canClick ? ' clickable' : ' blocked');
            cell.textContent = symbol;

            if (canClick) {
                cell.onclick = ((row, col) => () => makeCellMove(row, col))(r, c);
            }

            board.appendChild(cell);
        }
    }
}




function log(message, type = 'info') {
    const container = document.getElementById('log');
    const entry     = document.createElement('div');
    entry.className   = 'log-entry ' + type;
    entry.textContent = message;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function clearLog() {
    document.getElementById('log').innerHTML =
        '<div class="log-entry dim">// Лог очищен</div>';
}

function switchTab(button, tabId) {
    const panel = button.closest('.panel');
    panel.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    panel.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    button.classList.add('active');
    panel.querySelector('#' + tabId).classList.add('active');
}




restoreSession();
renderGame();
log('// Приложение запущено. JWT (Bearer) авторизация.', 'info');
log('// При 401 access-токен автообновляется через refresh.', 'dim');
