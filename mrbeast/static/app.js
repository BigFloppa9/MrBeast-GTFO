"use strict";

const I18N = {
  en: {
    "setup.title": "Set up MrBeast GTFO",
    "setup.lead": "Create the bot in the Discord Developer Portal and paste its token below.",
    "setup.token": "Bot token",
    "setup.token_hint": "Developer Portal → your application → Bot → Reset Token. It is stored encrypted on this device.",
    "setup.password": "Panel password",
    "setup.password_hint": "At least {n} characters. You will need it to open this panel.",
    "setup.repeat": "Repeat password",
    "setup.panel_lang": "Panel language",
    "setup.bot_lang": "Bot language",
    "setup.submit": "Save and start the bot",
    "login.title": "Welcome back",
    "login.lead": "Enter the panel password to continue.",
    "login.password": "Password",
    "login.submit": "Sign in",
    "login.forgot": "Forgot password?",
    "forgot.title": "Reset password",
    "forgot.unlinked": "No moderator account is linked, so the password can't be reset through Discord. Stop the panel, delete the file data/auth.json and start it again to repeat the setup.",
    "forgot.s1": "Send the bot the command",
    "forgot.s2": "in",
    "forgot.dm": "DIRECT",
    "forgot.s3": "messages (not on a server). If your account is the linked moderator, the bot replies with a code.",
    "forgot.code": "Code from the bot",
    "forgot.verify": "Continue",
    "forgot.new": "New password",
    "forgot.repeat": "Repeat new password",
    "forgot.save": "Save new password",
    "forgot.done": "Password changed. Sign in with the new password.",
    "forgot.back": "Back to sign in",
    "nav.logs": "Logs",
    "nav.status": "Status",
    "nav.servers": "Servers",
    "nav.settings": "Settings",
    "nav.logout": "Sign out",
    "logs.title": "Logs",
    "logs.empty": "No actions yet. Logs appear here when the bot takes action.",
    "log.auto": "🚨 MrBeast (Auto)",
    "log.manual": "🚨 MrBeast (Manual)",
    "log.offender": "Offender",
    "log.trigger": "Trigger",
    "log.moderator": "Moderator",
    "log.action": "Action",
    "log.timeout": "⏱️ Timeout: {d}",
    "log.deleted_auto": "🗑️ Deleted {n} messages (last {w})",
    "log.deleted_manual": "🗑️ Deleted {n} messages",
    "log.image": "[image]",
    "log.open_image": "Open image",
    "status.title": "Status",
    "state.online": "Online",
    "state.starting": "Starting…",
    "state.reconnecting": "Reconnecting…",
    "state.error": "Error",
    "state.stopped": "Stopped",
    "stat.status": "Status",
    "stat.bot": "Bot",
    "stat.ping": "Ping",
    "stat.uptime": "Uptime",
    "stat.servers": "Servers",
    "status.servers": "Servers with the bot",
    "status.members": "{n} members",
    "status.no_servers": "The bot is not on any server yet. Invite it using the link from the README.",
    "status.err.token_invalid": "Discord rejected the token. Replace it in Settings.",
    "status.err.intents": "Enable Server Members Intent and Message Content Intent in the Developer Portal (Bot tab), then restart the bot.",
    "status.err.network": "Can't reach Discord from this device. If Discord is blocked by your provider, a VPN or proxy is needed. The bot keeps retrying.",
    "setup.unverified": "Couldn't reach Discord to check the token. It was saved and the bot keeps trying to connect.",
    "setup.bot_lang_hint": "Language of the messages the bot sends in Discord.",
    "log.deleted": "[deleted]",
    "update.title": "Updates",
    "update.version": "Version {v} ({h})",
    "update.check": "Check for updates",
    "update.checking": "Checking…",
    "update.latest": "You are running the latest version.",
    "update.available": "Update available: {n} new change(s).",
    "update.dirty": "Local files were modified, the update may fail and will be rolled back.",
    "update.hint": "The bot stops, files and dependencies are updated and the bot starts again. Your data and settings are kept. You will need to sign in again.",
    "update.password": "Panel password",
    "update.apply": "Update now",
    "update.running": "Updating…",
    "update.step.stopping": "Stopping the bot",
    "update.step.pulling": "Downloading the update",
    "update.step.deps": "Checking dependencies",
    "update.step.checking": "Verifying the new files",
    "update.step.restarting": "Restarting",
    "update.failed": "The update failed and the previous version was restored.",
    "update.ok": "OK",
    "privacy.title": "Remove user data",
    "privacy.hint": "Replaces the display name, username and ID of a user in all log records with null and removes the stored text and images of their messages. Enter the username (not the display name) or the ID.",
    "privacy.query": "Username or ID",
    "privacy.find": "Find records",
    "privacy.found": "Records found: {n}.",
    "privacy.none": "No records found.",
    "privacy.erase": "Erase data",
    "privacy.done": "Data erased in {n} record(s).",
    "err.query_empty": "Enter a username or ID.",
    "err.not_git": "This installation is not a git checkout (or git is missing), so it can't be updated here.",
    "err.fetch_failed": "Couldn't reach GitHub to check for updates.",
    "err.update_running": "An update is already running.",
    "status.err.token_unreadable": "The saved token can't be read. Enter it again in Settings.",
    "servers.title": "Server settings",
    "servers.pick": "Server",
    "servers.offline": "The bot is offline, so server settings can't be loaded.",
    "servers.none": "The bot is not on any server yet.",
    "servers.reason": "Timeout reason",
    "servers.reason_hint": "Shown to the user in the audit log. Leave empty to use the default text.",
    "servers.timeout": "Timeout duration",
    "servers.timeout_hint": "Examples: 1d, 12h, 30m, 1d12h. Maximum 28d.",
    "servers.delete": "Delete messages from the last",
    "servers.delete_hint": "Examples: 24h, 7d, 30m.",
    "servers.log_channel": "Log channel",
    "servers.log_none": "— none —",
    "servers.auto": "Auto-detection",
    "servers.auto_hint": "The bot acts when a user posts at least this many images in at least this many channels within the time window.",
    "servers.min_images": "Images",
    "servers.min_channels": "Channels",
    "servers.window": "Time window (seconds)",
    "servers.save": "Save changes",
    "servers.saved": "Saved",
    "settings.title": "Settings",
    "settings.languages": "Languages",
    "settings.panel_lang": "Panel language",
    "settings.bot_lang": "Bot language",
    "settings.token": "Bot token",
    "settings.token_hint": "The token is stored encrypted. Enter your panel password to replace it; the bot restarts with the new token.",
    "settings.password": "Panel password",
    "settings.new_token": "New bot token",
    "settings.token_save": "Replace token",
    "settings.token_done": "Token replaced. The bot is restarting.",
    "settings.moderator": "Moderator account",
    "settings.mod_linked": "Linked account: {name}",
    "settings.mod_none": "No account is linked. A linked account is needed to reset the panel password through Discord.",
    "settings.mod_generate": "Generate code",
    "settings.mod_s1": "Send the bot the command",
    "settings.mod_s2": "in",
    "settings.mod_dm": "DIRECT",
    "settings.mod_s3": "messages. The code expires in {m} min.",
    "settings.mod_regen": "Generate a new code to link another account.",
    "err.generic": "Something went wrong. Try again.",
    "err.network_panel": "Can't reach the panel. Check that it is still running.",
    "err.bad_password": "Wrong password.",
    "err.locked": "Too many attempts. Try again in {seconds} s.",
    "err.password_short": "The password must be at least {n} characters.",
    "err.password_mismatch": "Passwords don't match.",
    "err.token_empty": "Enter the bot token.",
    "err.token_invalid": "Discord rejected this token.",
    "err.token_network": "Can't reach Discord. Check the internet connection.",
    "err.token_http": "Discord returned an unexpected response. Try again.",
    "err.code_invalid": "Wrong or expired code.",
    "err.reset_expired": "The reset session expired. Start again.",
    "err.already_configured": "The panel is already set up.",
    "err.timeout_invalid": "Invalid timeout. Use 1d, 12h, 30m or a combination.",
    "err.timeout_long": "The timeout can't be longer than 28d.",
    "err.timeout_short": "The timeout must be at least 1m.",
    "err.delete_invalid": "Invalid delete period. Use 24h, 7d, 30m or a combination.",
    "err.delete_long": "The delete period is too long (maximum 365d).",
    "err.delete_short": "The delete period must be at least 1m.",
    "err.reason_long": "The reason is longer than 512 characters.",
    "err.reason_invalid": "Invalid reason.",
    "err.auto_min_images_range": "Images must be between 1 and 50.",
    "err.auto_min_channels_range": "Channels must be between 1 and 50.",
    "err.auto_window_seconds_range": "The time window must be between 1 and 3600 seconds.",
    "err.channel_invalid": "This channel can't be used for logs.",
    "err.log_missing_perms": "The bot lacks permissions in this channel: {missing}.",
    "err.guild_unavailable": "Server unavailable. Is the bot online?",
    "err.lang_invalid": "Unsupported language."
  },
  ru: {
    "setup.title": "Настройка MrBeast GTFO",
    "setup.lead": "Создайте бота в Discord Developer Portal и вставьте его токен ниже.",
    "setup.token": "Токен бота",
    "setup.token_hint": "Developer Portal → ваше приложение → Bot → Reset Token. Токен хранится на этом устройстве в зашифрованном виде.",
    "setup.password": "Пароль панели",
    "setup.password_hint": "Не короче {n} символов. Он понадобится для входа в панель.",
    "setup.repeat": "Повторите пароль",
    "setup.panel_lang": "Язык панели",
    "setup.bot_lang": "Язык бота",
    "setup.submit": "Сохранить и запустить бота",
    "login.title": "С возвращением",
    "login.lead": "Введите пароль от панели, чтобы продолжить.",
    "login.password": "Пароль",
    "login.submit": "Войти",
    "login.forgot": "Забыли пароль?",
    "forgot.title": "Сброс пароля",
    "forgot.unlinked": "Аккаунт модератора не привязан, поэтому сбросить пароль через Discord нельзя. Остановите панель, удалите файл data/auth.json и запустите её снова, чтобы пройти настройку заново.",
    "forgot.s1": "Отправьте боту команду",
    "forgot.s2": "в",
    "forgot.dm": "ЛИЧНЫЕ",
    "forgot.s3": "сообщения (не на сервере). Если ваш аккаунт привязан как модератор, бот ответит кодом.",
    "forgot.code": "Код от бота",
    "forgot.verify": "Продолжить",
    "forgot.new": "Новый пароль",
    "forgot.repeat": "Повторите новый пароль",
    "forgot.save": "Сохранить новый пароль",
    "forgot.done": "Пароль изменён. Войдите с новым паролем.",
    "forgot.back": "Назад ко входу",
    "nav.logs": "Логи",
    "nav.status": "Статус",
    "nav.servers": "Серверы",
    "nav.settings": "Настройки",
    "nav.logout": "Выйти",
    "logs.title": "Логи",
    "logs.empty": "Пока действий нет. Логи появятся здесь, когда бот сработает.",
    "log.auto": "🚨 MrBeast (Авто)",
    "log.manual": "🚨 MrBeast (Вручную)",
    "log.offender": "Нарушитель",
    "log.trigger": "Триггер",
    "log.moderator": "Модератор",
    "log.action": "Действие",
    "log.timeout": "⏱️ Таймаут: {d}",
    "log.deleted_auto": "🗑️ Удалено сообщений: {n} (за последние {w})",
    "log.deleted_manual": "🗑️ Удалено сообщений: {n}",
    "log.image": "[изображение]",
    "log.open_image": "Открыть изображение",
    "status.title": "Статус",
    "state.online": "В сети",
    "state.starting": "Запускается…",
    "state.reconnecting": "Переподключение…",
    "state.error": "Ошибка",
    "state.stopped": "Остановлен",
    "stat.status": "Статус",
    "stat.bot": "Бот",
    "stat.ping": "Пинг",
    "stat.uptime": "Аптайм",
    "stat.servers": "Серверы",
    "status.servers": "Серверы с ботом",
    "status.members": "Участников: {n}",
    "status.no_servers": "Бот пока не добавлен ни на один сервер. Пригласите его по ссылке из README.",
    "status.err.token_invalid": "Discord отклонил токен. Замените его в настройках.",
    "status.err.intents": "Включите Server Members Intent и Message Content Intent в Developer Portal (вкладка Bot) и перезапустите бота.",
    "status.err.network": "С этого устройства нет связи с Discord. Если Discord заблокирован у вашего провайдера, нужен VPN или прокси. Бот продолжает пробовать подключиться.",
    "setup.unverified": "Не удалось связаться с Discord, чтобы проверить токен. Он сохранён, бот продолжает пытаться подключиться.",
    "setup.bot_lang_hint": "Язык сообщений, которые бот отправляет в Discord.",
    "log.deleted": "[удалено]",
    "update.title": "Обновления",
    "update.version": "Версия {v} ({h})",
    "update.check": "Проверить обновления",
    "update.checking": "Проверка…",
    "update.latest": "Установлена последняя версия.",
    "update.available": "Доступно обновление: изменений {n}.",
    "update.dirty": "Локальные файлы изменены, обновление может не пройти и будет откачено.",
    "update.hint": "Бот остановится, файлы и зависимости обновятся, затем бот запустится снова. Данные и настройки сохраняются. Потребуется заново войти в панель.",
    "update.password": "Пароль панели",
    "update.apply": "Обновить сейчас",
    "update.running": "Обновление…",
    "update.step.stopping": "Остановка бота",
    "update.step.pulling": "Загрузка обновления",
    "update.step.deps": "Проверка зависимостей",
    "update.step.checking": "Проверка новых файлов",
    "update.step.restarting": "Перезапуск",
    "update.failed": "Обновление не удалось, прежняя версия восстановлена.",
    "update.ok": "Понятно",
    "privacy.title": "Удаление данных пользователя",
    "privacy.hint": "Заменяет отображаемое имя, юзернейм и ID пользователя во всех записях логов на null и удаляет сохранённые текст и картинки его сообщений. Введите юзернейм (не отображаемое имя) или ID.",
    "privacy.query": "Юзернейм или ID",
    "privacy.find": "Найти записи",
    "privacy.found": "Найдено записей: {n}.",
    "privacy.none": "Записей не найдено.",
    "privacy.erase": "Стереть данные",
    "privacy.done": "Данные стёрты в записях: {n}.",
    "err.query_empty": "Введите юзернейм или ID.",
    "err.not_git": "Эта установка не является git-копией (или не установлен git), обновить её отсюда нельзя.",
    "err.fetch_failed": "Не удалось связаться с GitHub для проверки обновлений.",
    "err.update_running": "Обновление уже выполняется.",
    "status.err.token_unreadable": "Сохранённый токен не читается. Введите его заново в настройках.",
    "servers.title": "Настройки сервера",
    "servers.pick": "Сервер",
    "servers.offline": "Бот не в сети, поэтому настройки серверов недоступны.",
    "servers.none": "Бот пока не добавлен ни на один сервер.",
    "servers.reason": "Причина таймаута",
    "servers.reason_hint": "Показывается пользователю в журнале аудита. Оставьте пустым, чтобы использовать текст по умолчанию.",
    "servers.timeout": "Длительность таймаута",
    "servers.timeout_hint": "Примеры: 1d, 12h, 30m, 1d12h. Максимум 28d.",
    "servers.delete": "Удалять сообщения за последние",
    "servers.delete_hint": "Примеры: 24h, 7d, 30m.",
    "servers.log_channel": "Канал логов",
    "servers.log_none": "— нет —",
    "servers.auto": "Автоопределение",
    "servers.auto_hint": "Бот срабатывает, когда пользователь отправляет столько изображений в стольких каналах за указанное время.",
    "servers.min_images": "Изображений",
    "servers.min_channels": "Каналов",
    "servers.window": "Окно времени (секунды)",
    "servers.save": "Сохранить изменения",
    "servers.saved": "Сохранено",
    "settings.title": "Настройки",
    "settings.languages": "Языки",
    "settings.panel_lang": "Язык панели",
    "settings.bot_lang": "Язык бота",
    "settings.token": "Токен бота",
    "settings.token_hint": "Токен хранится в зашифрованном виде. Для замены введите пароль панели; бот перезапустится с новым токеном.",
    "settings.password": "Пароль панели",
    "settings.new_token": "Новый токен бота",
    "settings.token_save": "Заменить токен",
    "settings.token_done": "Токен заменён. Бот перезапускается.",
    "settings.moderator": "Аккаунт модератора",
    "settings.mod_linked": "Привязан аккаунт: {name}",
    "settings.mod_none": "Аккаунт не привязан. Он нужен, чтобы сбросить пароль панели через Discord.",
    "settings.mod_generate": "Сгенерировать код",
    "settings.mod_s1": "Отправьте боту команду",
    "settings.mod_s2": "в",
    "settings.mod_dm": "ЛИЧНЫЕ",
    "settings.mod_s3": "сообщения. Код действует {m} мин.",
    "settings.mod_regen": "Сгенерируйте новый код, чтобы привязать другой аккаунт.",
    "err.generic": "Что-то пошло не так. Попробуйте ещё раз.",
    "err.network_panel": "Нет связи с панелью. Проверьте, что она ещё запущена.",
    "err.bad_password": "Неверный пароль.",
    "err.locked": "Слишком много попыток. Повторите через {seconds} с.",
    "err.password_short": "Пароль должен быть не короче {n} символов.",
    "err.password_mismatch": "Пароли не совпадают.",
    "err.token_empty": "Введите токен бота.",
    "err.token_invalid": "Discord отклонил этот токен.",
    "err.token_network": "Нет связи с Discord. Проверьте интернет.",
    "err.token_http": "Discord вернул неожиданный ответ. Попробуйте ещё раз.",
    "err.code_invalid": "Неверный или просроченный код.",
    "err.reset_expired": "Сессия сброса истекла. Начните заново.",
    "err.already_configured": "Панель уже настроена.",
    "err.timeout_invalid": "Неверный таймаут. Используйте 1d, 12h, 30m или их сочетание.",
    "err.timeout_long": "Таймаут не может быть длиннее 28d.",
    "err.timeout_short": "Таймаут должен быть не короче 1m.",
    "err.delete_invalid": "Неверный период удаления. Используйте 24h, 7d, 30m или их сочетание.",
    "err.delete_long": "Период удаления слишком большой (максимум 365d).",
    "err.delete_short": "Период удаления должен быть не короче 1m.",
    "err.reason_long": "Причина длиннее 512 символов.",
    "err.reason_invalid": "Неверная причина.",
    "err.auto_min_images_range": "Изображений должно быть от 1 до 50.",
    "err.auto_min_channels_range": "Каналов должно быть от 1 до 50.",
    "err.auto_window_seconds_range": "Окно времени: от 1 до 3600 секунд.",
    "err.channel_invalid": "Этот канал нельзя использовать для логов.",
    "err.log_missing_perms": "У бота не хватает прав в этом канале: {missing}.",
    "err.guild_unavailable": "Сервер недоступен. Бот в сети?",
    "err.lang_invalid": "Язык не поддерживается."
  }
};

let LANG = "en";

function storeLang(code) {
  try { localStorage.setItem("mb_lang", code); } catch (e) {}
}

function loadLang() {
  try { return localStorage.getItem("mb_lang"); } catch (e) { return null; }
}
let me = { configured: false, authed: false, panel_lang: "en", bot_lang: "en", min_password: 8 };
let timers = [];
let statusData = null;
let logs = [];
let lastLogId = 0;
let ui = { tab: "logs" };
let regCode = null;

function tr(key, vars) {
  const table = I18N[LANG] || I18N.en;
  let text = table[key];
  if (text === undefined) text = I18N.en[key];
  if (text === undefined) text = key;
  if (vars) for (const name in vars) text = text.split("{" + name + "}").join(String(vars[name]));
  return text;
}

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === false || value === null || value === undefined) continue;
    if (key === "class") el.className = value;
    else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else if (key === "value") el.value = value;
    else el.setAttribute(key, value === true ? "" : value);
  }
  for (const kid of kids.flat()) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

const SVG_NS = "http://www.w3.org/2000/svg";
const ICONS = {
  logs: "M4 6h16M4 12h16M4 18h10",
  status: "M3 12h4l3-8 4 16 3-8h4",
  servers: "M4 5h16v5H4zM4 14h16v5H4zM8 7.5h.01M8 16.5h.01",
  settings: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2-1.2L14.2 3h-4l-.4 2.7a7 7 0 0 0-2 1.2l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2 1.2l.4 2.7h4l.4-2.7a7 7 0 0 0 2-1.2l2.3 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z",
  logout: "M10 5H5v14h5M15 8l4 4-4 4M9 12h10"
};

function icon(name) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  const path = document.createElementNS(SVG_NS, "path");
  path.setAttribute("d", ICONS[name]);
  svg.append(path);
  return svg;
}

function stopTimers() {
  timers.forEach(clearInterval);
  timers = [];
}

function every(ms, fn) {
  fn();
  timers.push(setInterval(fn, ms));
}

let toastTimer = null;
function toast(message, kind) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.className = "show " + (kind || "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = ""; }, 3500);
}

function errorText(res) {
  if (!res) return tr("err.generic");
  const key = "err." + (res.error || "generic");
  const vars = { seconds: res.seconds, n: me.min_password, missing: (res.missing || []).join(", ") };
  const text = tr(key, vars);
  return text === key ? tr("err.generic") : text;
}

async function api(method, path, body) {
  const options = { method, credentials: "same-origin", headers: {} };
  if (method !== "GET") {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body || {});
  }
  let response;
  try {
    response = await fetch(path, options);
  } catch (e) {
    return { ok: false, error: "network_panel" };
  }
  let data;
  try {
    data = await response.json();
  } catch (e) {
    data = { ok: false, error: "generic" };
  }
  if (response.status === 401 && data.error === "unauthorized" && me.authed) {
    me.authed = false;
    stopTimers();
    renderLogin();
  }
  return data;
}

function pad(n) { return String(n).padStart(2, "0"); }

function formatStamp(ts) {
  const d = new Date(ts * 1000);
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function dayKey(ts) {
  const d = new Date(ts * 1000);
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`;
}

function fmtDuration(minutes) {
  const d = Math.floor(minutes / 1440);
  const rest = minutes % 1440;
  const hh = Math.floor(rest / 60);
  const m = rest % 60;
  const parts = [];
  if (d) parts.push(d + "d");
  if (hh) parts.push(hh + "h");
  if (m) parts.push(m + "m");
  return parts.join(" ") || "0m";
}

function fmtUptime(seconds) {
  if (seconds === null || seconds === undefined) return "—";
  const d = Math.floor(seconds / 86400);
  const hh = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d) return `${d}d ${hh}h`;
  if (hh) return `${hh}h ${m}m`;
  return `${m}m`;
}

const INLINE = /(`[^`\n]+`)|(\*\*[^*\n]+?\*\*)|(__[^_\n]+?__)|(~~[^~\n]+?~~)|(\*[^*\n]+?\*)|(_[^_\n]+?_)|(https?:\/\/[^\s<>]+)|(<a?:(\w+):\d+>)|(<@[!&]?\d+>)|(<#\d+>)/g;

function renderInline(text, parent) {
  let last = 0;
  const pattern = new RegExp(INLINE.source, "g");
  let match;
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) parent.append(text.slice(last, match.index));
    const raw = match[0];
    if (match[1]) {
      parent.append(h("code", {}, raw.slice(1, -1)));
    } else if (match[2]) {
      const el = h("strong"); renderInline(raw.slice(2, -2), el); parent.append(el);
    } else if (match[3]) {
      const el = h("u"); renderInline(raw.slice(2, -2), el); parent.append(el);
    } else if (match[4]) {
      const el = h("s"); renderInline(raw.slice(2, -2), el); parent.append(el);
    } else if (match[5] || match[6]) {
      const el = h("em"); renderInline(raw.slice(1, -1), el); parent.append(el);
    } else if (match[7]) {
      const href = raw.replace(/[.,;:!?)\]]+$/, "");
      parent.append(h("a", { href, target: "_blank", rel: "noopener noreferrer nofollow" }, href));
      parent.append(raw.slice(href.length));
    } else if (match[8]) {
      parent.append(":" + match[9] + ":");
    } else if (match[10]) {
      parent.append(h("span", { class: "mention" }, raw.startsWith("<@&") ? "@role" : "@user"));
    } else if (match[11]) {
      parent.append(h("span", { class: "mention" }, "#channel"));
    }
    last = match.index + raw.length;
  }
  if (last < text.length) parent.append(text.slice(last));
}

function renderMarkdown(text, parent) {
  const fence = /```(?:[\w-]*\n)?([\s\S]*?)```/g;
  let last = 0;
  let match;
  const blocks = [];
  while ((match = fence.exec(text)) !== null) {
    if (match.index > last) blocks.push({ type: "text", value: text.slice(last, match.index) });
    blocks.push({ type: "code", value: match[1] });
    last = match.index + match[0].length;
  }
  if (last < text.length) blocks.push({ type: "text", value: text.slice(last) });
  for (const block of blocks) {
    if (block.type === "code") {
      parent.append(h("pre", {}, block.value.replace(/\n$/, "")));
      continue;
    }
    const lines = block.value.split("\n");
    let quote = null;
    lines.forEach((line, index) => {
      const quoted = /^>\s?/.test(line);
      if (quoted) {
        if (!quote) { quote = h("blockquote"); parent.append(quote); }
        renderInline(line.replace(/^>\s?/, ""), quote);
      } else {
        quote = null;
        renderInline(line, parent);
        if (index < lines.length - 1) parent.append("\n");
      }
    });
  }
}

function personBlock(person) {
  if (person.id === null) return h("div", { class: "fval person" }, h("div", { class: "muted" }, tr("log.deleted")));
  return h("div", { class: "fval person" },
    h("div", { class: "display" }, person.display),
    h("div", {}, person.username),
    h("div", {}, h("span", { class: "mono" }, person.id))
  );
}

function avatarNode(bot, cls) {
  const name = (bot && bot.name) || "M";
  const fallback = () => h("div", { class: (cls || "avatar") + " avatar fallback" }, name.charAt(0).toUpperCase());
  if (bot && bot.avatar) {
    const img = h("img", { class: cls || "avatar", src: bot.avatar, alt: "" });
    img.addEventListener("error", () => img.replaceWith(fallback()));
    return img;
  }
  return fallback();
}

function openLightbox(src) {
  const box = document.getElementById("lightbox");
  box.replaceChildren(h("img", { src, alt: "" }));
  box.hidden = false;
  box.onclick = () => { box.hidden = true; box.replaceChildren(); };
}

function logEntryNode(entry, bot) {
  const auto = entry.kind === "auto";
  const embed = h("div", { class: "embed " + (auto ? "auto" : "manual") });
  embed.append(h("div", { class: "title" }, tr(auto ? "log.auto" : "log.manual")));

  embed.append(h("div", { class: "field" }, h("div", { class: "fname" }, tr("log.offender")), personBlock(entry.offender)));

  if (entry.trigger) {
    const value = h("div", { class: "fval" });
    if (entry.trigger.text) renderMarkdown(entry.trigger.text, value);
    else value.append(h("span", { class: "muted" }, tr(entry.trigger.text === null ? "log.deleted" : "log.image")));
    const field = h("div", { class: "field" }, h("div", { class: "fname" }, tr("log.trigger")), value);
    if (entry.trigger.images && entry.trigger.images.length) {
      const thumbs = h("div", { class: "thumbs" });
      for (const image of entry.trigger.images) {
        const src = "/api/image/" + encodeURIComponent(image.file);
        const button = h("button", { class: "thumb", type: "button", title: tr("log.open_image"), onclick: () => openLightbox(src) },
          h("img", { src, alt: "", loading: "lazy" }),
          image.count > 1 ? h("span", { class: "count" }, "×" + image.count) : null
        );
        thumbs.append(button);
      }
      field.append(thumbs);
    }
    embed.append(field);
  }

  if (entry.moderator) {
    embed.append(h("div", { class: "field" }, h("div", { class: "fname" }, tr("log.moderator")), personBlock(entry.moderator)));
  }

  const action = [tr("log.timeout", { d: fmtDuration(entry.timeout) })];
  action.push(entry.window
    ? tr("log.deleted_auto", { n: entry.deleted, w: fmtDuration(entry.window) })
    : tr("log.deleted_manual", { n: entry.deleted }));
  embed.append(h("div", { class: "field" }, h("div", { class: "fname" }, tr("log.action")), h("div", { class: "fval" }, action.join("\n"))));

  const foot = h("div", { class: "foot" });
  if (entry.trigger && entry.trigger.channel) {
    foot.append(h("a", { href: entry.trigger.url, target: "_blank", rel: "noopener noreferrer" }, "#" + entry.trigger.channel), " • ");
  }
  foot.append(formatStamp(entry.ts));
  embed.append(foot);

  const name = (bot && bot.name) || "MrBeast_GTFO";
  return h("div", { class: "logmsg" },
    avatarNode(bot),
    h("div", {},
      h("div", { class: "head" },
        h("span", { class: "bot-name" }, name),
        h("span", { class: "tag" }, "BOT"),
        h("span", { class: "stamp" }, formatStamp(entry.ts))
      ),
      embed
    )
  );
}

function langSwitch(onChange) {
  const wrap = h("div", { class: "lang-switch" });
  for (const code of ["en", "ru"]) {
    wrap.append(h("button", {
      type: "button",
      class: LANG === code ? "active" : "",
      onclick: () => { LANG = code; storeLang(code); onChange(); }
    }, code.toUpperCase()));
  }
  return wrap;
}

function field(label, input, hint) {
  return h("label", { class: "field" }, h("span", {}, label), input, hint ? h("small", {}, hint) : null);
}

function langSelect(value) {
  const select = h("select", {},
    h("option", { value: "en" }, "English"),
    h("option", { value: "ru" }, "Русский")
  );
  select.value = value;
  return select;
}

function mount(node) {
  document.getElementById("app").replaceChildren(node);
}

function authCard(children, onLang) {
  return h("div", { class: "center-screen" },
    h("div", { class: "auth-card" },
      h("div", { class: "auth-top" }, langSwitch(onLang)),
      children
    )
  );
}

function formError() {
  return h("div", { class: "msg error", hidden: true, role: "alert" });
}

function showError(box, message) {
  box.textContent = message;
  box.hidden = !message;
}

function renderSetup(prefill = {}) {
  stopTimers();
  const error = formError();
  const token = h("input", { type: "password", autocomplete: "off", spellcheck: "false", required: true, value: prefill.token || "" });
  const password = h("input", { type: "password", autocomplete: "new-password", required: true, value: prefill.password || "" });
  const repeat = h("input", { type: "password", autocomplete: "new-password", required: true, value: prefill.repeat || "" });
  const botLang = langSelect(prefill.botLang || "en");
  const submit = h("button", { class: "btn block", type: "submit" }, tr("setup.submit"));

  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      submit.disabled = true;
      const res = await api("POST", "/api/setup", {
        token: token.value, password: password.value, repeat: repeat.value,
        panel_lang: LANG, bot_lang: botLang.value
      });
      submit.disabled = false;
      if (!res.ok) { showError(error, errorText(res)); return; }
      me.configured = true;
      me.authed = true;
      await enterDashboard();
      if (res.warning) toast(tr("setup.unverified"), "error");
    }
  },
    h("h1", {}, tr("setup.title")),
    h("p", { class: "lead" }, tr("setup.lead")),
    error,
    field(tr("setup.token"), token, tr("setup.token_hint")),
    field(tr("setup.password"), password, tr("setup.password_hint", { n: me.min_password })),
    field(tr("setup.repeat"), repeat),
    field(tr("setup.bot_lang"), botLang, tr("setup.bot_lang_hint")),
    submit
  );

  mount(authCard(form, () => renderSetup({ token: token.value, password: password.value, repeat: repeat.value, botLang: botLang.value })));
}

function renderLogin() {
  stopTimers();
  const error = formError();
  const password = h("input", { type: "password", autocomplete: "current-password", required: true, autofocus: true });
  const submit = h("button", { class: "btn block", type: "submit" }, tr("login.submit"));
  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      submit.disabled = true;
      const res = await api("POST", "/api/login", { password: password.value });
      submit.disabled = false;
      if (!res.ok) { showError(error, errorText(res)); password.select(); return; }
      me.authed = true;
      await enterDashboard();
    }
  },
    h("h1", {}, tr("login.title")),
    h("p", { class: "lead" }, tr("login.lead")),
    error,
    field(tr("login.password"), password),
    submit,
    h("div", { class: "actions" }, h("button", { class: "btn link", type: "button", onclick: () => renderForgot() }, tr("login.forgot")))
  );
  mount(authCard(form, renderLogin));
  password.focus();
}

async function renderForgot() {
  stopTimers();
  const start = await api("POST", "/api/forgot/start", {});
  const back = h("button", { class: "btn link", type: "button", onclick: renderLogin }, tr("forgot.back"));

  if (!start.ok || !start.linked) {
    mount(authCard(h("div", {},
      h("h1", {}, tr("forgot.title")),
      h("div", { class: "msg info" }, start.ok ? tr("forgot.unlinked") : errorText(start)),
      back
    ), () => renderForgot()));
    return;
  }

  const error = formError();
  const code = h("input", { type: "text", autocomplete: "off", spellcheck: "false", maxlength: "6", required: true });
  const verify = h("button", { class: "btn block", type: "submit" }, tr("forgot.verify"));
  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      verify.disabled = true;
      const res = await api("POST", "/api/forgot/verify", { code: code.value.trim() });
      verify.disabled = false;
      if (!res.ok) { showError(error, errorText(res)); return; }
      renderNewPassword(res.reset_token);
    }
  },
    h("h1", {}, tr("forgot.title")),
    h("div", { class: "msg info" },
      tr("forgot.s1") + " ", h("code", {}, "/log"), " " + tr("forgot.s2") + " ",
      h("strong", {}, tr("forgot.dm")), " " + tr("forgot.s3")
    ),
    error,
    field(tr("forgot.code"), code),
    verify,
    h("div", { class: "actions" }, back)
  );
  mount(authCard(form, () => renderForgot()));
  code.focus();
}

function renderNewPassword(resetToken) {
  const error = formError();
  const password = h("input", { type: "password", autocomplete: "new-password", required: true });
  const repeat = h("input", { type: "password", autocomplete: "new-password", required: true });
  const submit = h("button", { class: "btn block", type: "submit" }, tr("forgot.save"));
  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      submit.disabled = true;
      const res = await api("POST", "/api/forgot/finish", { reset_token: resetToken, password: password.value, repeat: repeat.value });
      submit.disabled = false;
      if (!res.ok) {
        showError(error, errorText(res));
        if (res.error === "reset_expired") setTimeout(renderForgot, 1500);
        return;
      }
      me.authed = false;
      renderLogin();
      toast(tr("forgot.done"), "ok");
    }
  },
    h("h1", {}, tr("forgot.title")),
    error,
    field(tr("forgot.new"), password, tr("setup.password_hint", { n: me.min_password })),
    field(tr("forgot.repeat"), repeat),
    submit
  );
  mount(authCard(form, () => renderNewPassword(resetToken)));
  password.focus();
}

const TABS = [
  ["logs", "nav.logs"],
  ["status", "nav.status"],
  ["servers", "nav.servers"],
  ["settings", "nav.settings"]
];

async function enterDashboard() {
  const res = await api("GET", "/api/status");
  if (res.ok) {
    LANG = res.config.panel_lang;
    me.panel_lang = LANG;
    me.bot_lang = res.config.bot_lang;
    statusData = res;
  }
  renderDashboard();
}

function stateDotClass(status) {
  if (status === "online") return "dot online";
  if (status === "error") return "dot error";
  if (status === "starting" || status === "reconnecting") return "dot wait";
  return "dot";
}

function renderDashboard() {
  stopTimers();
  logs = [];
  lastLogId = 0;
  const content = h("div", { class: "content", id: "content" });
  const banner = h("div", { class: "msg error banner", hidden: true, role: "alert" });
  const title = h("div", {});
  const pill = h("div", { class: "pill", id: "pill" });
  const nav = h("div", { class: "nav" });
  const brand = h("div", { class: "brand" }, h("div", { class: "avatar fallback", id: "brand-avatar" }, "M"), h("span", {}, "MrBeast GTFO"));

  function paintNav() {
    nav.replaceChildren(...TABS.map(([id, label]) => h("button", {
      class: ui.tab === id ? "active" : "",
      type: "button",
      onclick: () => { ui.tab = id; paintNav(); paintTab(); }
    }, icon(id === "logs" ? "logs" : id), h("span", {}, tr(label)))));
    title.textContent = tr(TABS.find(t => t[0] === ui.tab)[1]);
  }

  function paintPill() {
    const status = statusData && statusData.ok ? statusData.bot.status : "stopped";
    pill.replaceChildren(h("span", { class: stateDotClass(status) }), h("span", { class: "label" }, tr("state." + status)));
    const problem = statusData && statusData.ok ? statusData.bot.error : "";
    banner.textContent = problem ? tr("status.err." + problem) : "";
    banner.hidden = !problem;
    const bot = statusData && statusData.ok ? statusData.bot.user : null;
    const holder = document.getElementById("brand-avatar");
    if (holder && bot) holder.replaceWith(Object.assign(avatarNode(bot), { id: "brand-avatar" }));
  }

  function paintTab() {
    if (ui.tab === "logs") renderLogsTab(content);
    else if (ui.tab === "status") renderStatusTab(content);
    else if (ui.tab === "servers") renderServersTab(content);
    else renderSettingsTab(content);
  }

  const logout = h("button", {
    class: "btn secondary small", type: "button",
    onclick: async () => { await api("POST", "/api/logout", {}); me.authed = false; stopTimers(); renderLogin(); }
  }, icon("logout"), h("span", { class: "label" }, tr("nav.logout")));

  mount(h("div", { class: "shell" },
    h("aside", { class: "side" }, brand, nav, h("div", { class: "side-foot" }, pill)),
    h("section", { class: "main" },
      h("header", { class: "topbar" }, title, logout),
      banner,
      content
    )
  ));

  paintNav();
  paintPill();
  paintTab();

  let previousStatus = null;
  every(5000, async () => {
    const res = await api("GET", "/api/status");
    if (!res.ok) return;
    statusData = res;
    paintPill();
    const current = res.bot.status;
    if (ui.tab === "status") renderStatusTab(content);
    if (ui.tab === "servers" && previousStatus !== null && previousStatus !== current) renderServersTab(content);
    if (ui.tab === "settings") renderModerator();
    if (ui.tab === "logs") repaintFeed();
    previousStatus = current;
  });
  every(3000, pollLogs);
}

async function pollLogs() {
  const res = await api("GET", "/api/logs?after=" + lastLogId);
  if (!res.ok || !res.logs.length) return;
  for (const entry of res.logs) {
    logs.push(entry);
    lastLogId = Math.max(lastLogId, entry.id);
  }
  if (logs.length > 300) logs = logs.slice(logs.length - 300);
  repaintFeed();
}

function currentBot() {
  return statusData && statusData.ok ? statusData.bot.user : null;
}

let feedKey = "";
function repaintFeed() {
  const feed = document.getElementById("feed");
  if (!feed) return;
  const bot = currentBot();
  const key = lastLogId + ":" + logs.length + ":" + (bot ? bot.avatar : "") + ":" + LANG;
  if (key === feedKey) return;
  feedKey = key;
  const nodes = [];
  let day = null;
  for (let i = logs.length - 1; i >= 0; i--) {
    const entry = logs[i];
    const entryDay = dayKey(entry.ts);
    if (entryDay !== day) {
      day = entryDay;
      nodes.push(h("div", { class: "day-sep" }, day));
    }
    nodes.push(logEntryNode(entry, bot));
  }
  if (!nodes.length) nodes.push(h("div", { class: "empty" }, tr("logs.empty")));
  feed.replaceChildren(...nodes);
}

function renderLogsTab(content) {
  feedKey = "";
  content.replaceChildren(h("div", { class: "feed", id: "feed" }));
  repaintFeed();
}

function stat(label, value) {
  return h("div", { class: "stat" }, h("b", {}, value), h("span", {}, label));
}

function renderStatusTab(content) {
  if (!statusData || !statusData.ok) { content.replaceChildren(h("div", { class: "empty" }, "…")); return; }
  const bot = statusData.bot;
  const nodes = [];
  if (bot.error) {
    nodes.push(h("div", { class: "msg error" }, tr("status.err." + bot.error)));
  } else if (!statusData.token_ready) {
    nodes.push(h("div", { class: "msg error" }, tr("status.err.token_unreadable")));
  }
  nodes.push(h("div", { class: "stat-grid" },
    stat(tr("stat.status"), tr("state." + bot.status)),
    stat(tr("stat.bot"), bot.user ? bot.user.name : "—"),
    stat(tr("stat.ping"), bot.latency === null ? "—" : bot.latency + " ms"),
    stat(tr("stat.uptime"), fmtUptime(bot.uptime)),
    stat(tr("stat.servers"), String(bot.guilds.length))
  ));
  const list = h("div", { class: "section" }, h("h3", {}, tr("status.servers")));
  if (!bot.guilds.length) list.append(h("div", { class: "empty" }, tr("status.no_servers")));
  for (const guild of bot.guilds) {
    const icon = guild.icon
      ? h("img", { class: "avatar", src: guild.icon, alt: "" })
      : h("div", { class: "avatar fallback" }, guild.name.charAt(0).toUpperCase());
    list.append(h("div", { class: "guild" }, icon,
      h("div", {}, h("div", { class: "name" }, guild.name), h("div", { class: "meta" }, tr("status.members", { n: guild.members ?? "?" })))));
  }
  nodes.push(list);
  content.replaceChildren(h("div", { class: "panel" }, nodes));
}

function renderServersTab(content) {
  const bot = statusData && statusData.ok ? statusData.bot : null;
  if (!bot || bot.status !== "online") {
    content.replaceChildren(h("div", { class: "panel" }, h("div", { class: "msg info" }, tr("servers.offline"))));
    return;
  }
  if (!bot.guilds.length) {
    content.replaceChildren(h("div", { class: "panel" }, h("div", { class: "empty" }, tr("servers.none"))));
    return;
  }
  const select = h("select", {}, bot.guilds.map(g => h("option", { value: g.id }, g.name)));
  const body = h("div", {});
  if (ui.guild && bot.guilds.some(g => g.id === ui.guild)) select.value = ui.guild;
  else ui.guild = select.value;
  select.addEventListener("change", () => { ui.guild = select.value; loadGuild(body, ui.guild); });
  content.replaceChildren(h("div", { class: "panel" },
    h("div", { class: "section" }, field(tr("servers.pick"), select)),
    body
  ));
  loadGuild(body, ui.guild);
}

async function loadGuild(body, guildId) {
  body.replaceChildren(h("div", { class: "empty" }, "…"));
  const res = await api("GET", "/api/guilds/" + encodeURIComponent(guildId) + "/settings");
  if (!res.ok) { body.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
  const s = res.settings;
  const error = formError();
  const reason = h("textarea", { maxlength: "512", placeholder: res.default_reason }, s.timeout_reason);
  const timeout = h("input", { type: "text", value: s.timeout, autocomplete: "off" });
  const del = h("input", { type: "text", value: s.delete_window, autocomplete: "off" });
  const channel = h("select", {}, h("option", { value: "" }, tr("servers.log_none")), res.channels.map(c => h("option", { value: c.id }, "#" + c.name)));
  channel.value = s.log_channel;
  const images = h("input", { type: "number", min: "1", max: "50", value: s.auto_min_images });
  const channels = h("input", { type: "number", min: "1", max: "50", value: s.auto_min_channels });
  const windowSeconds = h("input", { type: "number", min: "1", max: "3600", value: s.auto_window_seconds });
  const save = h("button", { class: "btn", type: "submit" }, tr("servers.save"));

  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      save.disabled = true;
      const result = await api("PUT", "/api/guilds/" + encodeURIComponent(guildId) + "/settings", {
        timeout_reason: reason.value, timeout: timeout.value, delete_window: del.value,
        log_channel: channel.value, auto_min_images: images.value,
        auto_min_channels: channels.value, auto_window_seconds: windowSeconds.value
      });
      save.disabled = false;
      if (!result.ok) {
        if (result.error === "validation") showError(error, result.errors.map(code => errorText({ error: code })).join("\n"));
        else showError(error, errorText(result));
        error.style.whiteSpace = "pre-line";
        return;
      }
      const next = result.settings;
      timeout.value = next.timeout;
      del.value = next.delete_window;
      toast(tr("servers.saved"), "ok");
    }
  },
    error,
    h("div", { class: "section" },
      field(tr("servers.reason"), reason, tr("servers.reason_hint")),
      h("div", { class: "row" },
        field(tr("servers.timeout"), timeout, tr("servers.timeout_hint")),
        field(tr("servers.delete"), del, tr("servers.delete_hint"))
      ),
      field(tr("servers.log_channel"), channel)
    ),
    h("div", { class: "section" },
      h("h3", {}, tr("servers.auto")),
      h("p", { class: "meta" }, tr("servers.auto_hint")),
      h("div", { class: "row" },
        field(tr("servers.min_images"), images),
        field(tr("servers.min_channels"), channels),
        field(tr("servers.window"), windowSeconds)
      )
    ),
    save
  );
  body.replaceChildren(form);
}

function moderatorSection() {
  return h("div", { class: "section", id: "moderator" });
}

function renderModerator() {
  const box = document.getElementById("moderator");
  if (!box || !statusData || !statusData.ok) return;
  const mod = statusData.moderator;
  if (regCode && mod.linked && regCode.linkedBefore !== mod.id) regCode = null;
  const nodes = [h("h3", {}, tr("settings.moderator"))];
  nodes.push(h("div", { class: mod.linked ? "msg ok" : "msg info" },
    mod.linked ? tr("settings.mod_linked", { name: mod.name }) : tr("settings.mod_none")));
  if (regCode && statusData.reg.active) {
    nodes.push(h("div", { class: "code-box" }, regCode.code));
    nodes.push(h("p", { class: "meta" },
      tr("settings.mod_s1") + " ", h("code", {}, "/reg " + regCode.code), " " + tr("settings.mod_s2") + " ",
      h("strong", {}, tr("settings.mod_dm")), " " + tr("settings.mod_s3", { m: Math.max(1, Math.ceil(statusData.reg.remaining / 60)) })));
  } else {
    regCode = null;
  }
  nodes.push(h("div", { class: "actions" }, h("button", {
    class: "btn secondary", type: "button",
    onclick: async () => {
      const res = await api("POST", "/api/moderator/code", {});
      if (!res.ok) { toast(errorText(res), "error"); return; }
      regCode = { code: res.code, linkedBefore: statusData.moderator.id };
      const status = await api("GET", "/api/status");
      if (status.ok) statusData = status;
      renderModerator();
    }
  }, tr("settings.mod_generate"))));
  box.replaceChildren(...nodes);
}

function updateSection() {
  const result = h("div", {});
  const password = h("input", { type: "password", autocomplete: "current-password" });
  const checkButton = h("button", { class: "btn secondary", type: "button", onclick: () => check() }, tr("update.check"));

  async function check() {
    checkButton.disabled = true;
    result.replaceChildren(h("p", { class: "meta" }, tr("update.checking")));
    const res = await api("GET", "/api/update/check");
    checkButton.disabled = false;
    if (!res.ok) { result.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
    const nodes = [h("p", { class: "meta" }, tr("update.version", { v: res.version, h: res.head }))];
    if (!res.behind) {
      nodes.push(h("div", { class: "msg ok" }, tr("update.latest")));
    } else {
      nodes.push(h("div", { class: "msg info" }, tr("update.available", { n: res.behind })));
      nodes.push(h("ul", { class: "changes" }, res.changes.map(line => h("li", {}, line))));
      if (res.dirty) nodes.push(h("div", { class: "msg error" }, tr("update.dirty")));
      nodes.push(h("p", { class: "meta" }, tr("update.hint")));
      nodes.push(field(tr("update.password"), password));
      nodes.push(h("div", { class: "actions" }, h("button", { class: "btn", type: "button", onclick: apply }, tr("update.apply"))));
    }
    result.replaceChildren(...nodes);
  }

  async function apply() {
    const res = await api("POST", "/api/update/apply", { password: password.value });
    if (!res.ok) { toast(errorText(res), "error"); return; }
    stopTimers();
    const label = h("p", { class: "meta" }, tr("update.running"));
    result.replaceChildren(label);
    const id = setInterval(async () => {
      if (!me.authed) { clearInterval(id); return; }
      const status = await api("GET", "/api/update/status");
      if (!status.ok) return;
      if (status.error) {
        clearInterval(id);
        result.replaceChildren(
          h("div", { class: "msg error" }, tr("update.failed") + " (" + status.error + ")"),
          status.detail ? h("pre", { class: "detail" }, status.detail) : null,
          h("div", { class: "actions" }, h("button", { class: "btn secondary", type: "button", onclick: renderDashboard }, tr("update.ok")))
        );
        return;
      }
      if (status.step) label.textContent = tr("update.step." + status.step);
    }, 1500);
  }

  return h("div", { class: "section" }, h("h3", {}, tr("update.title")), h("div", { class: "actions" }, checkButton), result);
}

function privacySection() {
  const query = h("input", { type: "text", autocomplete: "off", spellcheck: "false", placeholder: "username / 766477798482509835" });
  const out = h("div", {});
  query.addEventListener("input", () => out.replaceChildren());

  async function search() {
    const q = query.value.trim();
    if (!q) { out.replaceChildren(); return; }
    const res = await api("POST", "/api/privacy/erase", { query: q, confirm: false });
    if (!res.ok) { out.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
    if (!res.count) { out.replaceChildren(h("div", { class: "msg info" }, tr("privacy.none"))); return; }
    out.replaceChildren(
      h("div", { class: "msg info" }, tr("privacy.found", { n: res.count })),
      h("button", { class: "btn danger", type: "button", onclick: erase }, tr("privacy.erase"))
    );
  }

  async function erase() {
    const res = await api("POST", "/api/privacy/erase", { query: query.value.trim(), confirm: true });
    if (!res.ok) { toast(errorText(res), "error"); return; }
    query.value = "";
    logs = [];
    lastLogId = 0;
    out.replaceChildren(h("div", { class: "msg ok" }, tr("privacy.done", { n: res.count })));
  }

  return h("div", { class: "section" },
    h("h3", {}, tr("privacy.title")),
    h("p", { class: "meta" }, tr("privacy.hint")),
    field(tr("privacy.query"), query),
    h("div", { class: "actions" }, h("button", { class: "btn secondary", type: "button", onclick: search }, tr("privacy.find"))),
    out
  );
}

function renderSettingsTab(content) {
  const panelLang = langSelect(me.panel_lang);
  const botLang = langSelect(me.bot_lang);

  async function saveLanguages() {
    const res = await api("PUT", "/api/config", { panel_lang: panelLang.value, bot_lang: botLang.value });
    if (!res.ok) { toast(errorText(res), "error"); return; }
    const panelChanged = res.config.panel_lang !== me.panel_lang;
    me.panel_lang = res.config.panel_lang;
    me.bot_lang = res.config.bot_lang;
    if (panelChanged) {
      LANG = me.panel_lang;
      storeLang(LANG);
      renderDashboard();
      return;
    }
    toast(tr("servers.saved"), "ok");
  }
  panelLang.addEventListener("change", saveLanguages);
  botLang.addEventListener("change", saveLanguages);

  const tokenError = formError();
  const password = h("input", { type: "password", autocomplete: "current-password", required: true });
  const token = h("input", { type: "password", autocomplete: "off", spellcheck: "false", required: true });
  const tokenSave = h("button", { class: "btn", type: "submit" }, tr("settings.token_save"));
  const tokenForm = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(tokenError, "");
      tokenSave.disabled = true;
      const res = await api("PUT", "/api/token", { password: password.value, token: token.value });
      tokenSave.disabled = false;
      if (!res.ok) { showError(tokenError, errorText(res)); return; }
      password.value = "";
      token.value = "";
      toast(tr("settings.token_done"), "ok");
    }
  },
    tokenError,
    field(tr("settings.password"), password),
    field(tr("settings.new_token"), token),
    tokenSave
  );

  content.replaceChildren(h("div", { class: "panel" },
    h("div", { class: "section" }, h("h3", {}, tr("settings.languages")),
      h("div", { class: "row" }, field(tr("settings.panel_lang"), panelLang), field(tr("settings.bot_lang"), botLang))),
    moderatorSection(),
    h("div", { class: "section" }, h("h3", {}, tr("settings.token")), h("p", { class: "meta" }, tr("settings.token_hint")), tokenForm),
    updateSection(),
    privacySection()
  ));
  renderModerator();
}

const KOS_KEYS = "KeyK,KeyO,KeyS";
let kosBuffer = [];
let kosTimer = null;

function typingNow() {
  const el = document.activeElement;
  return !!el && (["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName) || el.isContentEditable);
}

function toggleKos() {
  const on = document.documentElement.toggleAttribute("data-kos");
  try { localStorage.setItem("mb_kos", on ? "1" : "0"); } catch (e) {}
}

try { if (localStorage.getItem("mb_kos") === "1") document.documentElement.setAttribute("data-kos", ""); } catch (e) {}

document.addEventListener("keydown", (event) => {
  if (event.ctrlKey || event.metaKey || event.altKey || event.repeat || typingNow()) { kosBuffer = []; return; }
  kosBuffer = kosBuffer.concat(event.code).slice(-3);
  clearTimeout(kosTimer);
  kosTimer = setTimeout(() => { kosBuffer = []; }, 2000);
  if (kosBuffer.join() === KOS_KEYS) { kosBuffer = []; toggleKos(); }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const box = document.getElementById("lightbox");
    if (!box.hidden) { box.hidden = true; box.replaceChildren(); }
  }
});

async function boot() {
  const res = await api("GET", "/api/state");
  if (!res.ok) {
    mount(h("div", { class: "center-screen" }, h("div", { class: "auth-card" }, h("div", { class: "msg error" }, errorText(res)))));
    return;
  }
  me = Object.assign(me, res);
  LANG = loadLang() || res.panel_lang || "en";
  if (!I18N[LANG]) LANG = "en";
  if (!res.configured) renderSetup();
  else if (!res.authed) renderLogin();
  else await enterDashboard();
}

boot();
