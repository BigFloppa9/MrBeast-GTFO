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
    "nav.logs": "Offenders",
    "nav.status": "Status",
    "nav.servers": "Servers",
    "nav.proxy": "Proxy",
    "nav.settings": "Settings",
    "nav.logout": "Sign out",
    "logs.title": "Offenders",
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
    "state.paused": "Paused",
    "bot.pause": "Pause",
    "bot.resume": "Resume",
    "bot.restart": "Restart",
    "bot.stop": "Stop",
    "bot.start": "Start",
    "bot.controls": "Bot control",
    "bot.paused_hint": "While paused, the bot does not react to image spam. Manual commands still work.",
    "net.title": "Panel addresses",
    "net.hint": "Open the address that matches the network of your other device. If it doesn't open, check the phone's IP in the router and that client isolation is off.",
    "net.wifi": "Wi-Fi",
    "net.vpn": "VPN",
    "net.mobile": "mobile data",
    "net.other": "other",
    "proxy.sub_update": "Update",
    "proxy.sub_count": "{n} servers",
    "proxy.sub_updated": "Subscription updated: {n} servers.",
    "proxy.hint": "Needed if Discord is blocked by your provider. Paste proxy links (socks5, http, vless, vmess, trojan, ss), a JSON config or a subscription link (https://…), one per line. Up to {max} entries.",
    "proxy.placeholder": "socks5://127.0.0.1:2080\nvless://uuid@host:443?type=tcp&security=reality&…\nhttps://example.com/sub/…\n{ JSON config }",
    "proxy.add": "Add",
    "proxy.empty": "No proxies added. The bot connects directly.",
    "proxy.count": "{n} / {max}",
    "proxy.checked": "Last check: {t}",
    "proxy.never": "not yet",
    "proxy.no_internet": "No internet on this device right now, so servers are not marked as failed.",
    "proxy.down_for": "offline {h} h of {limit} h",
    "proxy.ago_min": "{n} min ago",
    "proxy.ago_now": "just now",
    "proxy.active": "in use",
    "proxy.ok": "works",
    "proxy.failed": "not working",
    "proxy.unknown": "not checked yet",
    "proxy.remove": "Remove",
    "proxy.added": "Added: {n}.",
    "proxy.skipped": "Skipped: {list}.",
    "proxy.item": "item {n}: {text}",
    "proxy.xray_downloading": "Downloading the Xray core (needed for SOCKS5 and VLESS)…",
    "proxy.xray_error": "Couldn't download the Xray core: {detail}. Place the xray binary at data/bin/xray manually, or install it so that it is available as xray.",
    "err.query_empty": "Enter a username or ID.",
    "err.proxy_invalid": "Nothing could be added.",
    "err.proxy_limit": "The proxy limit is reached.",
    "err.proxy_missing": "This proxy no longer exists.",
    "err.empty": "Paste at least one proxy.",
    "err.bad_link": "the link is malformed",
    "err.bad_uuid": "the VLESS id is not a valid UUID",
    "err.bad_reality": "REALITY needs the pbk (public key) parameter",
    "err.bad_json": "the JSON could not be read",
    "err.bad_config": "the config is not an object",
    "err.no_outbound": "no proxy outbound found in the config",
    "err.unsupported": "unsupported link type (use socks5://, http:// or vless://)",
    "err.unsupported_transport": "unsupported VLESS transport (use a JSON config for it)",
    "err.unsupported_security": "unsupported VLESS security",
    "err.too_long": "the link is too long",
    "status.err.proxy_failed": "None of the added proxies is working right now, so the bot connects directly. Proxies are re-checked in the background.",
    "err.sub_invalid": "Enter a link starting with http:// or https://.",
    "err.sub_fetch_failed": "Couldn't download the subscription.",
    "err.sub_empty": "No supported servers found in the subscription.",
    "err.crypt_unsupported": "only happ://crypt5 links are supported (older crypt, crypt2–4 are not)",
    "err.sub_html": "The link returned a web page instead of a subscription (the provider may block bots or require a login).",
    "err.sub_too_large": "The subscription is too large.",
    "err.sub_truncated": "The limit is reached, servers not added",
    "err.unsupported_plugin": "shadowsocks plugins are not supported",
    "err.not_git": "This installation is not a git checkout (or git is missing), so it can't be updated here.",
    "err.fetch_failed": "Couldn't reach GitHub to check for updates.",
    "err.update_running": "An update is already running.",
    "status.err.token_unreadable": "The saved token can't be read. Enter it again in Settings.",
    "servers.title": "Server settings",
    "servers.pick": "Server",
    "servers.offline": "The bot is offline, so server settings can't be loaded.",
    "servers.none": "The bot is not on any server yet.",
    "servers.reason": "Timeout reason",
    "servers.reason_hint": "The user the bot punished will see this reason (the bot sends it in a direct message). It is also written to the server's audit log. Leave empty to use the default text.",
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
    "settings.moderator": "Moderator accounts",
    "settings.mod_linked": "Linked account: {name}",
    "settings.mod_none": "No Discord account is linked yet. A linked account can reset the panel password with /log.",
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
    "err.lang_invalid": "Unsupported language.",
    "net.title_one": "Panel address",
    "net.title_many": "Panel addresses",
    "status.console": "Latest log",
    "status.console_empty": "No lines yet.",
    "confirm.yes": "Yes",
    "confirm.no": "No",
    "confirm.pause": "Pause the bot?",
    "confirm.stop": "Stop the bot?",
    "confirm.proxy_remove": "Remove this proxy from the list?",
    "confirm.sub_remove": "Remove this subscription and all of its servers?",
    "confirm.moderator_remove": "Unlink this moderator account?",
    "confirm.erase": "Erase this user's data everywhere? This can't be undone.",
    "servers.search": "Search servers",
    "servers.all": "Servers",
    "servers.search_results": "Search results",
    "servers.nothing": "Nothing found",
    "servers.dm_reason": "Also send the reason to the user in a direct message",
    "servers.punish": "Punishment",
    "servers.punish_hint": "What the bot does after detecting a compromised account. Repeated detections of the same user on this server move through the steps below.",
    "servers.reset_days": "Reset detections after (days)",
    "servers.reset_days_hint": "The counter of a user is cleared after this many days without new detections (1–90). Nothing is kept longer than 90 days.",
    "preset.default": "One action (as before)",
    "preset.ladder": "Escalation: 4 detections, ends with a ban",
    "preset.ladder_ban": "Ban at the first detection",
    "preset.custom": "Custom",
    "step.n": "Step {n}",
    "step.action": "Action",
    "step.timeout": "Timeout",
    "step.ban": "Ban",
    "step.duration": "Timeout length",
    "step.delete": "Delete messages from the last",
    "step.reason": "Reason (empty = default text)",
    "step.add": "Add step",
    "step.remove": "Remove step",
    "step.line_timeout": "Timeout {d}, delete messages from the last {w}",
    "step.line_ban": "Ban, delete messages from the last {w}",
    "step.invalid": "Step {n}: check the values (timeout 1m–28d, deleting up to 7d for a ban).",
    "step.custom_note": "Steps run in order for each new detection of the same user. After the last step it repeats.",
    "err.preset_invalid": "Unknown punishment preset.",
    "err.steps_invalid": "Some step has invalid values.",
    "err.steps_empty": "Add at least one step for the custom preset.",
    "err.reset_days_range": "Days must be between 1 and 90.",
    "err.dm_reason_invalid": "Invalid value.",
    "proxy.edit": "Edit",
    "proxy.form": "Add via form",
    "proxy.dialog_add": "New proxy",
    "proxy.dialog_edit": "Edit proxy",
    "proxy.cancel": "Cancel",
    "proxy.save": "Save",
    "proxy.socket": "Server address",
    "proxy.account": "Credentials (optional)",
    "proxy.f.label": "Name",
    "proxy.f.host": "Host",
    "proxy.f.port": "Port",
    "proxy.f.user": "Login",
    "proxy.f.password": "Password",
    "proxy.f.id": "UUID",
    "proxy.f.flow": "Flow",
    "proxy.f.encryption": "Encryption",
    "proxy.f.network": "Transport",
    "proxy.f.security": "Security",
    "proxy.f.sni": "SNI",
    "proxy.f.fp": "Fingerprint",
    "proxy.f.alpn": "ALPN (comma separated)",
    "proxy.f.allow_insecure": "Allow insecure certificate",
    "proxy.f.pbk": "Public key (pbk)",
    "proxy.f.sid": "Short ID (sid)",
    "proxy.f.spx": "SpiderX (spx)",
    "proxy.f.path": "Path",
    "proxy.f.host_header": "Host header",
    "proxy.f.service": "gRPC service name",
    "proxy.f.mode": "Mode",
    "proxy.f.alter": "Alter ID",
    "proxy.f.cipher": "Cipher",
    "proxy.f.method": "Method",
    "proxy.f.json": "Xray outbound (JSON)",
    "proxy.kind.socks5": "SOCKS5",
    "proxy.kind.http": "HTTP",
    "proxy.kind.vless": "VLESS",
    "proxy.kind.vmess": "VMess",
    "proxy.kind.trojan": "Trojan",
    "proxy.kind.shadowsocks": "Shadowsocks",
    "proxy.kind.xray": "JSON (Xray)",
    "proxy.mt_note": "MTProto and web proxies work only inside Telegram and can't carry Discord traffic, so they are not offered here. tg://socks links are accepted.",
    "err.bad_port": "the port must be between 1 and 65535",
    "err.mtproto_unsupported": "Telegram MTProto proxies can't carry Discord traffic (a tg://socks link works)",
    "err.crypt_failed": "the happ://crypt link could not be decrypted",
    "err.crypt_keys_unavailable": "the key list for happ://crypt5 could not be downloaded (github.com/cylaro/happ-decrypt)",
    "err.crypt_unknown_key": "this happ://crypt5 link uses a key that is not in the list",
    "settings.mod_remove": "Unlink",
    "security.title": "Password recovery",
    "security.lead": "If you forget the panel password you can restore access through a linked Discord account (/log) or by answering your security questions. Answers are stored only as hashes.",
    "security.none": "No security questions set.",
    "security.q_n": "Question {n}",
    "security.q_custom": "Your own question",
    "security.q.pet": "Name of your first pet",
    "security.q.city": "City where you were born",
    "security.q.game": "Your favorite game",
    "security.q.friend": "Nickname of your best friend",
    "security.q.phone": "Model of your first phone",
    "security.q.movie": "Your favorite movie",
    "security.q.street": "Street you grew up on",
    "security.question_text": "Your question",
    "security.answer": "Answer",
    "security.answer_hint": "Latin letters and digits only, no spaces (use _), preferably one word.",
    "security.add": "Add question",
    "security.hint": "Password hint",
    "security.hint_hint": "Shown under the password field after 2 wrong attempts. Don't write the password itself.",
    "security.save": "Save",
    "security.saved": "Saved.",
    "security.fill": "Enter your current password and an answer for every question to save.",
    "err.answers_invalid": "The answers are wrong.",
    "err.answer_invalid": "Answers must use Latin letters, digits, _ . - only (2–64 characters).",
    "err.question_empty": "Write the text of your own question.",
    "err.questions_many": "At most 3 questions.",
    "err.hint_long": "The hint is too long.",
    "login.hint": "Hint: {h}",
    "forgot.questions_title": "Answer your security questions",
    "forgot.questions_submit": "Check answers",
    "forgot.or": "or",
    "forgot.no_method": "No recovery method was set up for this panel: no linked Discord account and no security questions. Sorry, good luck: remove the bot and reinstall it with the command below on the device where it runs ({env}). This deletes all bot data.",
    "forgot.env_termux": "Termux",
    "forgot.env_other": "this device",
    "forgot.copy": "Copy command",
    "forgot.copied": "Copied.",
    "console.title": "Console log",
    "console.hint": "The last {n} lines. Older lines are overwritten. You can export the log and share it when something goes wrong.",
    "console.empty": "No lines yet.",
    "console.refresh": "Refresh",
    "console.export": "Export",
    "console.scope_all": "Everything stored",
    "console.scope_session": "Since the last bot start",
    "data.title": "Transfer settings",
    "data.hint": "Saves server settings, punishment presets, reasons and detection counters to a file. User IDs in the counters are encrypted with the passphrase. Offenders and logs are not included. Anything older than 90 days is dropped on import.",
    "data.passphrase": "Passphrase",
    "data.export": "Export",
    "data.import": "Import",
    "data.file": "Export file",
    "data.imported": "Imported: {g} servers, {n} counters.",
    "data.choose": "Choose a file first.",
    "err.passphrase_short": "The passphrase must be at least 6 characters.",
    "err.import_invalid": "This file is not a valid export.",
    "err.import_passphrase": "Wrong passphrase or damaged file.",
    "privacy.discord": "Log messages deleted in Discord: {n}.",
    "privacy.discord_skipped": "The bot is offline, so Discord log channels were not checked.",
    "privacy.discord_only": "No stored records, but the log channels in Discord will still be checked.",
    "update.label": "Version",
    "update.show": "Show changes",
    "update.hide": "Hide changes",
    "update.no_git": "The change list needs a git installation.",
    "log.ban": "Ban",
    "log.strike": "Detection {n} of {total}",
    "log.deleted_ban": "Messages deleted by the ban (last {w})"
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
    "nav.logs": "Нарушители",
    "nav.status": "Статус",
    "nav.servers": "Серверы",
    "nav.proxy": "Прокси",
    "nav.settings": "Настройки",
    "nav.logout": "Выйти",
    "logs.title": "Нарушители",
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
    "state.paused": "Пауза",
    "bot.pause": "Пауза",
    "bot.resume": "Включить",
    "bot.restart": "Перезагрузить",
    "bot.stop": "Остановить",
    "bot.start": "Запустить",
    "bot.controls": "Управление ботом",
    "bot.paused_hint": "Во время паузы бот не реагирует на спам картинками. Ручные команды продолжают работать.",
    "net.title": "Адреса панели",
    "net.hint": "Откройте адрес из той же сети, в которой находится ваше второе устройство. Если страница не открывается, сверьте IP телефона в роутере и проверьте, что изоляция клиентов выключена.",
    "net.wifi": "Wi-Fi",
    "net.vpn": "VPN",
    "net.mobile": "мобильная сеть",
    "net.other": "другое",
    "proxy.sub_update": "Обновить",
    "proxy.sub_count": "Серверов: {n}",
    "proxy.sub_updated": "Подписка обновлена: серверов {n}.",
    "proxy.hint": "Нужно, если Discord заблокирован у провайдера. Вставьте ссылки на прокси (socks5, http, vless, vmess, trojan, ss), JSON-конфиг или ссылку на подписку (https://…), по одной в строке. До {max} записей.",
    "proxy.placeholder": "socks5://127.0.0.1:2080\nvless://uuid@host:443?type=tcp&security=reality&…\nhttps://example.com/sub/…\n{ JSON-конфиг }",
    "proxy.add": "Добавить",
    "proxy.empty": "Прокси не добавлены. Бот подключается напрямую.",
    "proxy.count": "{n} / {max}",
    "proxy.checked": "Последняя проверка: {t}",
    "proxy.never": "ещё не было",
    "proxy.no_internet": "Сейчас на устройстве нет интернета, поэтому серверы не помечаются как нерабочие.",
    "proxy.down_for": "не отвечает {h} ч из {limit} ч",
    "proxy.ago_min": "{n} мин назад",
    "proxy.ago_now": "только что",
    "proxy.active": "используется",
    "proxy.ok": "работает",
    "proxy.failed": "не работает",
    "proxy.unknown": "ещё не проверялся",
    "proxy.remove": "Удалить",
    "proxy.added": "Добавлено: {n}.",
    "proxy.skipped": "Пропущено: {list}.",
    "proxy.item": "пункт {n}: {text}",
    "proxy.xray_downloading": "Загружается ядро Xray (нужно для SOCKS5 и VLESS)…",
    "proxy.xray_error": "Не удалось загрузить ядро Xray: {detail}. Положите файл xray в data/bin/xray вручную или установите его так, чтобы он был доступен как xray.",
    "err.query_empty": "Введите юзернейм или ID.",
    "err.proxy_invalid": "Ничего не удалось добавить.",
    "err.proxy_limit": "Достигнут лимит прокси.",
    "err.proxy_missing": "Такого прокси уже нет.",
    "err.empty": "Вставьте хотя бы один прокси.",
    "err.bad_link": "ссылка повреждена",
    "err.bad_uuid": "идентификатор VLESS не является корректным UUID",
    "err.bad_reality": "для REALITY нужен параметр pbk (публичный ключ)",
    "err.bad_json": "не удалось прочитать JSON",
    "err.bad_config": "конфиг не является объектом",
    "err.no_outbound": "в конфиге не найден исходящий прокси",
    "err.unsupported": "неподдерживаемый тип ссылки (используйте socks5://, http:// или vless://)",
    "err.unsupported_transport": "неподдерживаемый транспорт VLESS (для него используйте JSON-конфиг)",
    "err.unsupported_security": "неподдерживаемая защита VLESS",
    "err.too_long": "ссылка слишком длинная",
    "status.err.proxy_failed": "Сейчас не работает ни один из добавленных прокси, поэтому бот подключается напрямую. Прокси перепроверяются в фоне.",
    "err.sub_invalid": "Введите ссылку, начинающуюся с http:// или https://.",
    "err.sub_fetch_failed": "Не удалось загрузить подписку.",
    "err.sub_empty": "В подписке не найдено поддерживаемых серверов.",
    "err.crypt_unsupported": "поддерживаются только ссылки happ://crypt5 (старые crypt, crypt2–4 нет)",
    "err.sub_html": "По ссылке открылась веб-страница, а не подписка (провайдер может блокировать ботов или требовать вход).",
    "err.sub_too_large": "Подписка слишком большая.",
    "err.sub_truncated": "Достигнут лимит, серверы не добавлены",
    "err.unsupported_plugin": "плагины shadowsocks не поддерживаются",
    "err.not_git": "Эта установка не является git-копией (или не установлен git), обновить её отсюда нельзя.",
    "err.fetch_failed": "Не удалось связаться с GitHub для проверки обновлений.",
    "err.update_running": "Обновление уже выполняется.",
    "status.err.token_unreadable": "Сохранённый токен не читается. Введите его заново в настройках.",
    "servers.title": "Настройки сервера",
    "servers.pick": "Сервер",
    "servers.offline": "Бот не в сети, поэтому настройки серверов недоступны.",
    "servers.none": "Бот пока не добавлен ни на один сервер.",
    "servers.reason": "Причина таймаута",
    "servers.reason_hint": "Эту причину увидит пользователь, которого наказал бот (бот отправит её в личные сообщения). Она также записывается в журнал аудита сервера. Оставьте пустым, чтобы использовать текст по умолчанию.",
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
    "settings.moderator": "Аккаунты модераторов",
    "settings.mod_linked": "Привязан аккаунт: {name}",
    "settings.mod_none": "Аккаунты Discord пока не привязаны. Привязанный аккаунт может сбросить пароль панели командой /log.",
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
    "err.lang_invalid": "Язык не поддерживается.",
    "net.title_one": "Адрес панели",
    "net.title_many": "Адреса панели",
    "status.console": "Последние логи",
    "status.console_empty": "Пока нет строк.",
    "confirm.yes": "Да",
    "confirm.no": "Нет",
    "confirm.pause": "Поставить бота на паузу?",
    "confirm.stop": "Остановить бота?",
    "confirm.proxy_remove": "Удалить этот прокси из списка?",
    "confirm.sub_remove": "Удалить подписку и все её серверы?",
    "confirm.moderator_remove": "Отвязать этот аккаунт модератора?",
    "confirm.erase": "Стереть данные этого пользователя везде? Это нельзя отменить.",
    "servers.search": "Поиск серверов",
    "servers.all": "Серверы",
    "servers.search_results": "Результаты поиска",
    "servers.nothing": "Ничего не найдено",
    "servers.dm_reason": "Также отправлять причину пользователю в личные сообщения",
    "servers.punish": "Наказание",
    "servers.punish_hint": "Что бот делает после обнаружения взломанного аккаунта. Повторные обнаружения того же пользователя на этом сервере проходят по шагам ниже.",
    "servers.reset_days": "Сбрасывать обнаружения через (дней)",
    "servers.reset_days_hint": "Счётчик пользователя очищается, если столько дней не было новых обнаружений (1–90). Дольше 90 дней ничего не хранится.",
    "preset.default": "Одно действие (как раньше)",
    "preset.ladder": "Нарастающее: 4 обнаружения, в конце бан",
    "preset.ladder_ban": "Бан при первом обнаружении",
    "preset.custom": "Свой",
    "step.n": "Шаг {n}",
    "step.action": "Действие",
    "step.timeout": "Тайм-аут",
    "step.ban": "Бан",
    "step.duration": "Длительность тайм-аута",
    "step.delete": "Удалить сообщения за последние",
    "step.reason": "Причина (пусто = текст по умолчанию)",
    "step.add": "Добавить шаг",
    "step.remove": "Удалить шаг",
    "step.line_timeout": "Тайм-аут {d}, удаление сообщений за {w}",
    "step.line_ban": "Бан, удаление сообщений за {w}",
    "step.invalid": "Шаг {n}: проверьте значения (тайм-аут 1m–28d, при бане удаление до 7d).",
    "step.custom_note": "Шаги выполняются по порядку при каждом новом обнаружении того же пользователя. После последнего шага он повторяется.",
    "err.preset_invalid": "Неизвестный пресет наказания.",
    "err.steps_invalid": "В каком-то шаге неверные значения.",
    "err.steps_empty": "Добавьте хотя бы один шаг для своего пресета.",
    "err.reset_days_range": "Дней должно быть от 1 до 90.",
    "err.dm_reason_invalid": "Неверное значение.",
    "proxy.edit": "Изменить",
    "proxy.form": "Добавить через форму",
    "proxy.dialog_add": "Новый прокси",
    "proxy.dialog_edit": "Редактирование прокси",
    "proxy.cancel": "Отмена",
    "proxy.save": "Сохранить",
    "proxy.socket": "Адрес сервера",
    "proxy.account": "Учётные данные (необязательно)",
    "proxy.f.label": "Название",
    "proxy.f.host": "Хост",
    "proxy.f.port": "Порт",
    "proxy.f.user": "Логин",
    "proxy.f.password": "Пароль",
    "proxy.f.id": "UUID",
    "proxy.f.flow": "Flow",
    "proxy.f.encryption": "Шифрование",
    "proxy.f.network": "Транспорт",
    "proxy.f.security": "Защита",
    "proxy.f.sni": "SNI",
    "proxy.f.fp": "Отпечаток (fingerprint)",
    "proxy.f.alpn": "ALPN (через запятую)",
    "proxy.f.allow_insecure": "Разрешить небезопасный сертификат",
    "proxy.f.pbk": "Публичный ключ (pbk)",
    "proxy.f.sid": "Short ID (sid)",
    "proxy.f.spx": "SpiderX (spx)",
    "proxy.f.path": "Путь",
    "proxy.f.host_header": "Заголовок Host",
    "proxy.f.service": "Имя сервиса gRPC",
    "proxy.f.mode": "Режим",
    "proxy.f.alter": "Alter ID",
    "proxy.f.cipher": "Шифр",
    "proxy.f.method": "Метод",
    "proxy.f.json": "Исходящее Xray (JSON)",
    "proxy.kind.socks5": "SOCKS5",
    "proxy.kind.http": "HTTP",
    "proxy.kind.vless": "VLESS",
    "proxy.kind.vmess": "VMess",
    "proxy.kind.trojan": "Trojan",
    "proxy.kind.shadowsocks": "Shadowsocks",
    "proxy.kind.xray": "JSON (Xray)",
    "proxy.mt_note": "MTProto и веб-прокси работают только внутри Telegram и не могут передавать трафик Discord, поэтому их здесь нет. Ссылки tg://socks принимаются.",
    "err.bad_port": "порт должен быть от 1 до 65535",
    "err.mtproto_unsupported": "прокси Telegram MTProto не передают трафик Discord (ссылка tg://socks подойдёт)",
    "err.crypt_failed": "ссылку happ://crypt не удалось расшифровать",
    "err.crypt_keys_unavailable": "не удалось скачать список ключей для happ://crypt5 (github.com/cylaro/happ-decrypt)",
    "err.crypt_unknown_key": "эта ссылка happ://crypt5 использует ключ, которого нет в списке",
    "settings.mod_remove": "Отвязать",
    "security.title": "Восстановление пароля",
    "security.lead": "Если забудете пароль панели, доступ можно вернуть через привязанный аккаунт Discord (/log) или ответами на контрольные вопросы. Ответы хранятся только в виде хешей.",
    "security.none": "Контрольные вопросы не заданы.",
    "security.q_n": "Вопрос {n}",
    "security.q_custom": "Свой вопрос",
    "security.q.pet": "Кличка первого питомца",
    "security.q.city": "Город, где вы родились",
    "security.q.game": "Любимая игра",
    "security.q.friend": "Ник лучшего друга",
    "security.q.phone": "Модель первого телефона",
    "security.q.movie": "Любимый фильм",
    "security.q.street": "Улица, на которой вы выросли",
    "security.question_text": "Ваш вопрос",
    "security.answer": "Ответ",
    "security.answer_hint": "Только латиница и цифры, без пробелов (используйте _), лучше одним словом.",
    "security.add": "Добавить вопрос",
    "security.hint": "Подсказка к паролю",
    "security.hint_hint": "Показывается под полем пароля после 2 неверных попыток. Не пишите сам пароль.",
    "security.save": "Сохранить",
    "security.saved": "Сохранено.",
    "security.fill": "Для сохранения введите текущий пароль и ответ на каждый вопрос.",
    "err.answers_invalid": "Ответы неверные.",
    "err.answer_invalid": "Ответ: только латиница, цифры и символы _ . - (2–64 символа).",
    "err.question_empty": "Напишите текст своего вопроса.",
    "err.questions_many": "Не больше 3 вопросов.",
    "err.hint_long": "Подсказка слишком длинная.",
    "login.hint": "Подсказка: {h}",
    "forgot.questions_title": "Ответьте на контрольные вопросы",
    "forgot.questions_submit": "Проверить ответы",
    "forgot.or": "или",
    "forgot.no_method": "Для этой панели не настроен ни один способ восстановления: нет привязанного аккаунта Discord и нет контрольных вопросов. К сожалению, удачи: удалите бота и установите заново командой ниже на устройстве, где он запущен ({env}). Все данные бота будут удалены.",
    "forgot.env_termux": "Termux",
    "forgot.env_other": "это устройство",
    "forgot.copy": "Скопировать команду",
    "forgot.copied": "Скопировано.",
    "console.title": "Лог консоли",
    "console.hint": "Последние {n} строк. Более старые затираются. Лог можно экспортировать и прислать, если что-то пошло не так.",
    "console.empty": "Пока нет строк.",
    "console.refresh": "Обновить",
    "console.export": "Экспорт",
    "console.scope_all": "Всё сохранённое",
    "console.scope_session": "С последнего запуска бота",
    "data.title": "Перенос настроек",
    "data.hint": "Сохраняет в файл настройки серверов, пресеты наказаний, причины и счётчики обнаружений. ID пользователей в счётчиках шифруются парольной фразой. Нарушители и логи не включаются. Всё старше 90 дней отбрасывается при импорте.",
    "data.passphrase": "Парольная фраза",
    "data.export": "Экспорт",
    "data.import": "Импорт",
    "data.file": "Файл экспорта",
    "data.imported": "Импортировано: серверов {g}, счётчиков {n}.",
    "data.choose": "Сначала выберите файл.",
    "err.passphrase_short": "Парольная фраза должна быть не короче 6 символов.",
    "err.import_invalid": "Это не файл экспорта.",
    "err.import_passphrase": "Неверная парольная фраза или повреждённый файл.",
    "privacy.discord": "Удалено лог-сообщений в Discord: {n}.",
    "privacy.discord_skipped": "Бот не в сети, поэтому лог-каналы в Discord не проверялись.",
    "privacy.discord_only": "Сохранённых записей нет, но лог-каналы в Discord всё равно будут проверены.",
    "update.label": "Версия",
    "update.show": "Показать изменения",
    "update.hide": "Скрыть изменения",
    "update.no_git": "Для списка изменений нужна установка через git.",
    "log.ban": "Бан",
    "log.strike": "Обнаружение {n} из {total}",
    "log.deleted_ban": "Сообщения удалены баном (за последние {w})"
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
  proxy: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M12 3c3.5 3.2 3.5 14.8 0 18M12 3c-3.5 3.2-3.5 14.8 0 18",
  logout: "M10 5H5v14h5M15 8l4 4-4 4M9 12h10",
  search: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4",
  chevron: "M6 9l6 6 6-6",
  edit: "M4 20h4L19 9l-4-4L4 16v4zM13.5 6.5l4 4"
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

  const action = [];
  if (entry.strike && entry.strike.total > 1) action.push(tr("log.strike", { n: entry.strike.n, total: entry.strike.total }));
  if (entry.action === "ban") {
    action.push(tr("log.ban"), tr("log.deleted_ban", { w: fmtDuration(entry.window) }));
  } else {
    action.push(tr("log.timeout", { d: fmtDuration(entry.timeout) }));
    action.push(entry.window
      ? tr("log.deleted_auto", { n: entry.deleted, w: fmtDuration(entry.window) })
      : tr("log.deleted_manual", { n: entry.deleted }));
  }
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
  const hint = h("div", { class: "msg info", hidden: true });
  const password = h("input", { type: "password", autocomplete: "current-password", required: true, autofocus: true });
  const submit = h("button", { class: "btn block", type: "submit" }, tr("login.submit"));
  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      hint.hidden = true;
      submit.disabled = true;
      const res = await api("POST", "/api/login", { password: password.value });
      submit.disabled = false;
      if (!res.ok) {
        password.value = "";
        showError(error, errorText(res));
        if (res.hint) { hint.textContent = tr("login.hint", { h: res.hint }); hint.hidden = false; }
        password.focus();
        return;
      }
      me.authed = true;
      await enterDashboard();
    }
  },
    h("h1", {}, tr("login.title")),
    h("p", { class: "lead" }, tr("login.lead")),
    error,
    field(tr("login.password"), password),
    hint,
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

  if (!start.ok) {
    mount(authCard(h("div", {}, h("h1", {}, tr("forgot.title")), h("div", { class: "msg error" }, errorText(start)), back), () => renderForgot()));
    return;
  }

  const questions = start.questions || [];
  if (!start.linked && !questions.length) {
    const info = start.reinstall || { env: "other", command: "" };
    const box = h("pre", { class: "detail cmd" }, info.command);
    mount(authCard(h("div", {},
      h("h1", {}, tr("forgot.title")),
      h("div", { class: "msg info" }, tr("forgot.no_method", { env: tr(info.env === "termux" ? "forgot.env_termux" : "forgot.env_other") })),
      box,
      h("div", { class: "actions" },
        h("button", { class: "btn secondary", type: "button", onclick: async () => {
          try { await navigator.clipboard.writeText(info.command); toast(tr("forgot.copied"), "ok"); } catch (e) { const r = document.createRange(); r.selectNodeContents(box); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); }
        } }, tr("forgot.copy")), back)
    ), () => renderForgot()));
    return;
  }

  const parts = [h("h1", {}, tr("forgot.title"))];
  if (start.linked) {
    const error = formError();
    const code = h("input", { type: "text", autocomplete: "off", spellcheck: "false", maxlength: "6", required: true });
    const verify = h("button", { class: "btn block", type: "submit" }, tr("forgot.verify"));
    parts.push(h("form", {
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
      h("div", { class: "msg info" }, tr("forgot.s1") + " ", h("code", {}, "/log"), " " + tr("forgot.s2") + " ", h("strong", {}, tr("forgot.dm")), " " + tr("forgot.s3")),
      error, field(tr("forgot.code"), code), verify));
  }
  if (start.linked && questions.length) parts.push(h("div", { class: "or-sep" }, tr("forgot.or")));
  if (questions.length) {
    const error = formError();
    const inputs = questions.map(() => h("input", { type: "text", autocomplete: "off", spellcheck: "false", required: true }));
    const check = h("button", { class: "btn block", type: "submit" }, tr("forgot.questions_submit"));
    parts.push(h("form", {
      onsubmit: async (event) => {
        event.preventDefault();
        showError(error, "");
        check.disabled = true;
        const res = await api("POST", "/api/forgot/answers", { answers: inputs.map(i => i.value) });
        check.disabled = false;
        if (!res.ok) { inputs.forEach(i => { i.value = ""; }); showError(error, errorText(res)); return; }
        renderNewPassword(res.reset_token);
      }
    },
      h("h3", {}, tr("forgot.questions_title")), error,
      questions.map((q, i) => field(q.id === "custom" ? q.text : tr("security.q." + q.id), inputs[i])), check));
  }
  parts.push(h("div", { class: "actions" }, back));
  mount(authCard(h("div", {}, parts), () => renderForgot()));
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
  ["proxy", "nav.proxy"],
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
  if (status === "starting" || status === "reconnecting" || status === "paused") return "dot wait";
  return "dot";
}

function renderDashboard() {
  stopTimers();
  logs = [];
  lastLogId = 0;
  const content = h("div", { class: "content", id: "content" });
  const banner = h("div", { class: "msg error banner", hidden: true, role: "alert" });
  const title = h("div", {});
  const pill = h("div", { class: "pill top", id: "pill" });
  const nav = h("div", { class: "nav" });
  const brandName = h("span", { id: "brand-name" }, "MrBeast GTFO");
  const brand = h("div", { class: "brand" }, h("div", { class: "avatar fallback", id: "brand-avatar" }, "M"), brandName);

  function paintNav() {
    nav.replaceChildren(...TABS.map(([id, label]) => h("button", {
      class: ui.tab === id ? "active" : "",
      type: "button",
      onclick: () => { ui.tab = id; paintNav(); paintTab(); }
    }, icon(id), h("span", {}, tr(label)))));
    title.textContent = tr(TABS.find(t => t[0] === ui.tab)[1]);
  }

  function paintPill() {
    const status = statusData && statusData.ok ? statusData.bot.status : "stopped";
    pill.replaceChildren(h("span", { class: stateDotClass(status) }), h("span", { class: "label" }, tr("state." + status)));
    if (status === "paused") pill.firstChild.className = "dot wait";
    const problem = statusData && statusData.ok ? statusData.bot.error : "";
    banner.textContent = problem ? tr("status.err." + problem) : "";
    banner.hidden = !problem;
    const bot = statusData && statusData.ok ? statusData.bot.user : null;
    const holder = document.getElementById("brand-avatar");
    if (holder && bot) holder.replaceWith(Object.assign(avatarNode(bot), { id: "brand-avatar" }));
    if (bot && bot.name) brandName.textContent = bot.name;
  }

  paintPillFn = paintPill;

  async function paintTab() {
    if (ui.tab === "logs") renderLogsTab(content);
    else if (ui.tab === "status") { await refreshConsole(20); if (ui.tab === "status") renderStatusTab(content); }
    else if (ui.tab === "servers") renderServersTab(content);
    else if (ui.tab === "proxy") renderProxyTab(content);
    else renderSettingsTab(content);
  }

  const logout = h("button", {
    class: "btn secondary small block", type: "button",
    onclick: async () => { await api("POST", "/api/logout", {}); me.authed = false; stopTimers(); renderLogin(); }
  }, icon("logout"), h("span", { class: "label" }, tr("nav.logout")));

  mount(h("div", { class: "shell" },
    h("aside", { class: "side" }, brand, nav, h("div", { class: "side-foot" }, langInline(), logout)),
    h("section", { class: "main" },
      h("header", { class: "topbar" }, h("div", { class: "top-left" }, title, pill),
        h("a", { class: "byline", href: "https://github.com/BigFloppa9", target: "_blank", rel: "noopener noreferrer" }, "By BigFloppa9")),
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
    if (ui.tab === "status") { await refreshConsole(20); renderStatusTab(content); }
    if (ui.tab === "servers" && previousStatus !== null && previousStatus !== current && (previousStatus === "stopped" || current === "stopped")) renderServersTab(content);
    if (ui.tab === "settings") renderModerator();
    if (ui.tab === "proxy" && proxyRefresh) proxyRefresh();
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

let paintPillFn = null;

async function botAction(action, content) {
  if (action === "pause" && !(await confirmDialog(tr("confirm.pause")))) return;
  if (action === "stop" && !(await confirmDialog(tr("confirm.stop")))) return;
  const res = await api("POST", "/api/bot/" + action, {});
  if (!res.ok) { toast(errorText(res), "error"); return; }
  const status = await api("GET", "/api/status");
  if (status.ok) statusData = status;
  if (paintPillFn) paintPillFn();
  renderStatusTab(content);
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
  nodes.push(h("div", { class: "stat-grid wide-grid" },
    stat(tr("stat.status"), tr("state." + bot.status)),
    stat(tr("stat.ping"), bot.latency === null ? "—" : bot.latency + " ms"),
    stat(tr("stat.uptime"), fmtUptime(bot.uptime)),
    stat(tr("stat.servers"), String(bot.guilds.length))
  ));
  const stopped = statusData.bot_state === "stopped";
  const paused = statusData.bot_state === "paused";
  const buttons = stopped
    ? [h("button", { class: "btn", type: "button", onclick: () => botAction("start", content) }, tr("bot.start"))]
    : [
        h("button", { class: "btn secondary", type: "button", onclick: () => botAction(paused ? "resume" : "pause", content) }, tr(paused ? "bot.resume" : "bot.pause")),
        h("button", { class: "btn secondary", type: "button", onclick: () => botAction("restart", content) }, tr("bot.restart")),
        h("button", { class: "btn danger", type: "button", onclick: () => botAction("stop", content) }, tr("bot.stop"))
      ];
  nodes.push(h("div", { class: "status-cards" },
    h("div", { class: "section fit" }, h("h3", {}, tr("bot.controls")),
      paused ? h("p", { class: "meta" }, tr("bot.paused_hint")) : null,
      h("div", { class: "actions" }, buttons)),
    (() => {
      const net = statusData.network;
      if (!net || !net.addresses.length) return null;
      return h("div", { class: "section fit" }, h("h3", {}, tr(net.addresses.length > 1 ? "net.title_many" : "net.title_one")),
        h("p", { class: "meta" }, tr("net.hint")),
        net.addresses.map(item => h("div", { class: "addr" },
          h("a", { href: "http://" + item.ip + ":" + net.port }, "http://" + item.ip + ":" + net.port),
          h("span", { class: "meta" }, tr("net." + item.kind) + (item.iface ? " · " + item.iface : "")))));
    })()));
  nodes.push(h("div", { class: "section" }, h("h3", {}, tr("status.console")),
    h("pre", { class: "console-box" }, consoleCache.length ? consoleCache.map(consoleLine).join("\n") : tr("status.console_empty"))));
  content.replaceChildren(h("div", { class: "panel wide" }, nodes));
}

function guildIcon(guild) {
  const fallback = () => h("div", { class: "avatar fallback" }, guild.name.charAt(0).toUpperCase());
  if (!guild.icon) return fallback();
  const img = h("img", { class: "avatar", src: guild.icon, alt: "" });
  img.addEventListener("error", () => img.replaceWith(fallback()));
  return img;
}

function renderServersTab(content) {
  const bot = statusData && statusData.ok ? statusData.bot : null;
  if (!bot || bot.status === "stopped" || !bot.user) {
    content.replaceChildren(h("div", { class: "panel" }, h("div", { class: "msg info" }, tr("servers.offline"))));
    return;
  }
  if (!bot.guilds.length) {
    content.replaceChildren(h("div", { class: "panel" }, h("div", { class: "empty" }, tr("status.no_servers"))));
    return;
  }
  if (!ui.guild || !bot.guilds.some(g => g.id === ui.guild)) ui.guild = bot.guilds[0].id;
  const body = h("div", {});
  const picker = serverPicker(bot.guilds, ui.guild, (guild) => { ui.guild = guild.id; loadGuild(body, ui.guild); });
  content.replaceChildren(h("div", { class: "panel" }, h("div", { class: "section" }, h("h3", {}, tr("status.servers")), picker), body));
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
  const resetDays = h("input", { type: "number", min: "1", max: "90", value: s.warn_reset_days });
  const dm = h("input", { type: "checkbox" });
  dm.checked = s.dm_reason;
  const save = h("button", { class: "btn", type: "submit" }, tr("servers.save"));

  const preset = h("select", {}, ["default", "ladder", "ladder_ban", "custom"].map(id => h("option", { value: id }, tr("preset." + id))));
  preset.value = s.punish_preset;
  let custom = (s.custom_steps || []).map(step => ({ action: step.action, duration: fmtDuration(step.duration || 60), delete: fmtDuration(step.delete), reason: step.reason || "" }));
  const defaultBox = h("div", {},
    field(tr("servers.reason"), reason, tr("servers.reason_hint")),
    h("div", { class: "row" },
      field(tr("servers.timeout"), timeout, tr("servers.timeout_hint")),
      field(tr("servers.delete"), del, tr("servers.delete_hint"))));
  const stepsBox = h("div", {});

  function previewOf(id) {
    return (s.preview[id] || []).map(step => ({ action: step.action, duration: fmtDuration(step.duration || 60), delete: fmtDuration(step.delete), reason: step.reason }));
  }

  function paintSteps() {
    const id = preset.value;
    defaultBox.hidden = id !== "default";
    if (id === "default") { stepsBox.replaceChildren(); return; }
    if (id !== "custom") {
      stepsBox.replaceChildren(...s.preview[id].map((step, i) => h("div", { class: "step" },
        h("div", { class: "step-head" }, h("b", {}, tr("step.n", { n: i + 1 })), h("span", { class: "meta" }, stepSummary(step))),
        h("div", { class: "meta step-reason" }, step.reason))));
      return;
    }
    if (!custom.length) custom = previewOf("ladder_ban").length ? previewOf("ladder_ban") : [{ action: "timeout", duration: "1d", delete: "1d", reason: "" }];
    const nodes = custom.map((step, i) => {
      const action = h("select", { onchange: () => { step.action = action.value; paintSteps(); } },
        h("option", { value: "timeout" }, tr("step.timeout")), h("option", { value: "ban" }, tr("step.ban")));
      action.value = step.action;
      const dur = h("input", { type: "text", value: step.duration, autocomplete: "off", oninput: () => { step.duration = dur.value; } });
      const delIn = h("input", { type: "text", value: step.delete, autocomplete: "off", oninput: () => { step.delete = delIn.value; } });
      const why = h("textarea", { maxlength: "512", rows: "2", oninput: () => { step.reason = why.value; } }, step.reason);
      return h("div", { class: "step" },
        h("div", { class: "step-head" }, h("b", {}, tr("step.n", { n: i + 1 })),
          custom.length > 1 ? h("button", { class: "btn secondary small", type: "button", title: tr("step.remove"), onclick: () => { custom.splice(i, 1); paintSteps(); } }, "×") : null),
        h("div", { class: "row" }, field(tr("step.action"), action),
          step.action === "timeout" ? field(tr("step.duration"), dur) : null,
          field(tr("step.delete"), delIn)),
        field(tr("step.reason"), why));
    });
    if (custom.length < s.max_steps) nodes.push(h("button", { class: "btn secondary", type: "button", onclick: () => { const last = custom[custom.length - 1]; custom.push({ ...last }); paintSteps(); } }, tr("step.add")));
    nodes.push(h("p", { class: "meta" }, tr("step.custom_note")));
    stepsBox.replaceChildren(...nodes);
  }

  let lastPreset = preset.value;
  preset.addEventListener("change", () => {
    if (preset.value === "custom" && !custom.length && lastPreset !== "default") custom = previewOf(lastPreset);
    lastPreset = preset.value;
    paintSteps();
  });

  function collectSteps() {
    const out = [];
    for (let i = 0; i < custom.length; i++) {
      const step = custom[i];
      const d = step.action === "timeout" ? parseMinutes(step.duration) : 0;
      const w = parseMinutes(step.delete);
      if (w === null || (step.action === "timeout" && (d === null || d < 1 || d > 40320)) || w > (step.action === "ban" ? 10080 : 525600)) return { error: tr("step.invalid", { n: i + 1 }) };
      out.push({ action: step.action, duration: d, delete: w, reason: step.reason.trim() });
    }
    return { steps: out };
  }

  const form = h("form", {
    onsubmit: async (event) => {
      event.preventDefault();
      showError(error, "");
      const payload = {
        timeout_reason: reason.value, timeout: timeout.value, delete_window: del.value,
        log_channel: channel.value, auto_min_images: images.value,
        auto_min_channels: channels.value, auto_window_seconds: windowSeconds.value,
        punish_preset: preset.value, warn_reset_days: resetDays.value, dm_reason: dm.checked
      };
      if (preset.value === "custom") {
        const collected = collectSteps();
        if (collected.error) { showError(error, collected.error); return; }
        payload.custom_steps = collected.steps;
      }
      save.disabled = true;
      const result = await api("PUT", "/api/guilds/" + encodeURIComponent(guildId) + "/settings", payload);
      save.disabled = false;
      if (!result.ok) {
        if (result.error === "validation") showError(error, result.errors.map(code => errorText({ error: code })).join("\n"));
        else showError(error, errorText(result));
        error.style.whiteSpace = "pre-line";
        return;
      }
      Object.assign(s, result.settings);
      timeout.value = s.timeout;
      del.value = s.delete_window;
      toast(tr("servers.saved"), "ok");
    }
  },
    error,
    h("div", { class: "section" },
      h("h3", {}, tr("servers.punish")),
      h("p", { class: "meta" }, tr("servers.punish_hint")),
      field(tr("servers.punish"), preset),
      defaultBox,
      stepsBox,
      h("div", { class: "row" }, field(tr("servers.reset_days"), resetDays, tr("servers.reset_days_hint"))),
      h("label", { class: "check" }, dm, h("span", {}, tr("servers.dm_reason"))),
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
  paintSteps();
  body.replaceChildren(form);
}

function moderatorSection() {
  return h("div", { class: "section", id: "moderator" });
}

function renderModerator() {
  const box = document.getElementById("moderator");
  if (!box || !statusData || !statusData.ok) return;
  const mods = statusData.moderators || [];
  const nodes = [h("h3", {}, tr("settings.moderator"))];
  if (!mods.length) nodes.push(h("div", { class: "msg info" }, tr("settings.mod_none")));
  for (const mod of mods) {
    nodes.push(h("div", { class: "mod-row" },
      h("div", { class: "mod-name" }, h("div", {}, mod.name || "—"), h("div", { class: "meta mono" }, mod.id)),
      h("button", { class: "btn secondary small", type: "button", onclick: async () => {
        if (!(await confirmDialog(tr("confirm.moderator_remove")))) return;
        const res = await api("DELETE", "/api/moderator/" + encodeURIComponent(mod.id), {});
        if (!res.ok) { toast(errorText(res), "error"); return; }
        const status = await api("GET", "/api/status");
        if (status.ok) statusData = status;
        renderModerator();
      } }, tr("settings.mod_remove"))));
  }
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
      regCode = { code: res.code };
      const status = await api("GET", "/api/status");
      if (status.ok) statusData = status;
      renderModerator();
    }
  }, tr("settings.mod_generate"))));
  box.replaceChildren(...nodes);
}

function updateSection() {
  const result = h("div", {});
  const changes = h("div", { class: "changes-box", hidden: true });
  const password = h("input", { type: "password", autocomplete: "current-password" });
  const version = h("b", {}, "…");
  const checkButton = h("button", { class: "btn secondary small", type: "button", onclick: () => check() }, tr("update.check"));
  let loaded = false;
  const toggleButton = h("button", { class: "btn secondary small", type: "button", onclick: () => toggle() }, icon("chevron"), h("span", {}, tr("update.show")));

  api("GET", "/api/update/info").then(info => { if (info.ok) version.textContent = "v" + info.version; });

  async function toggle() {
    const opening = changes.hidden;
    changes.hidden = !opening;
    toggleButton.classList.toggle("open", opening);
    toggleButton.lastChild.textContent = tr(opening ? "update.hide" : "update.show");
    if (!opening || loaded) return;
    changes.replaceChildren(h("p", { class: "meta" }, "…"));
    const info = await api("GET", "/api/update/info");
    if (!info.ok || !info.git) { changes.replaceChildren(h("p", { class: "meta" }, tr("update.no_git"))); return; }
    loaded = true;
    changes.replaceChildren(...info.commits.map(commit => h("div", { class: "commit" },
      h("div", { class: "commit-head" }, h("b", {}, commit.title), h("span", { class: "meta" }, commit.date + " · " + commit.hash)),
      commit.body ? h("ul", {}, commit.body.split("\n").filter(Boolean).map(line => h("li", {}, line.replace(/^[-–•]\s*/, "")))) : null)));
  }

  async function check() {
    checkButton.disabled = true;
    result.replaceChildren(h("p", { class: "meta" }, tr("update.checking")));
    const res = await api("GET", "/api/update/check");
    checkButton.disabled = false;
    if (!res.ok) { result.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
    const nodes = [];
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

  return h("div", { class: "update-card" },
    h("div", { class: "update-top" }, h("div", { class: "update-version" }, h("span", { class: "meta" }, tr("update.label")), version),
      h("div", { class: "update-buttons" }, toggleButton, checkButton)),
    changes, result);
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
    const digits = /^\d{15,25}$/.test(q.replace(/^@/, ""));
    if (!res.count && !digits) { out.replaceChildren(h("div", { class: "msg info" }, tr("privacy.none"))); return; }
    out.replaceChildren(
      h("div", { class: "msg info" }, res.count ? tr("privacy.found", { n: res.count }) : tr("privacy.discord_only")),
      h("button", { class: "btn danger", type: "button", onclick: erase }, tr("privacy.erase"))
    );
  }

  async function erase() {
    if (!(await confirmDialog(tr("confirm.erase")))) return;
    const res = await api("POST", "/api/privacy/erase", { query: query.value.trim(), confirm: true });
    if (!res.ok) { toast(errorText(res), "error"); return; }
    query.value = "";
    logs = [];
    lastLogId = 0;
    const lines = [h("div", { class: "msg ok" }, tr("privacy.done", { n: res.count }))];
    if (res.discord) lines.push(h("div", { class: "msg info" }, res.discord.skipped ? tr("privacy.discord_skipped") : tr("privacy.discord", { n: res.discord.deleted })));
    out.replaceChildren(...lines);
  }

  return h("div", { class: "section" },
    h("h3", {}, tr("privacy.title")),
    h("p", { class: "meta" }, tr("privacy.hint")),
    field(tr("privacy.query"), query),
    h("div", { class: "actions" }, h("button", { class: "btn secondary", type: "button", onclick: search }, tr("privacy.find"))),
    out
  );
}

let proxyRefresh = null;

function agoText(ts) {
  if (!ts) return tr("proxy.never");
  const minutes = Math.floor((Date.now() / 1000 - ts) / 60);
  return minutes < 1 ? tr("proxy.ago_now") : tr("proxy.ago_min", { n: minutes });
}

function proxySection() {
  const text = h("textarea", { class: "proxy-input", spellcheck: "false", placeholder: tr("proxy.placeholder"), maxlength: "400000" });
  const list = h("div", { class: "proxy-list" });
  const note = h("div", {});
  const count = h("span", { class: "meta" });
  const checked = h("span", { class: "meta" });
  const addButton = h("button", { class: "btn", type: "button" }, tr("proxy.add"));
  const subs = h("div", { class: "proxy-list" });

  function statusOf(row, limit) {
    if (row.active) return ["online", tr("proxy.active") + (row.status && row.status.ms ? " · " + row.status.ms + " ms" : "")];
    if (!row.status) return ["", tr("proxy.unknown")];
    if (row.status.ok) return ["online", tr("proxy.ok")];
    const hours = Math.floor((row.down || 0) / 3600);
    return ["error", hours > 0 ? tr("proxy.down_for", { h: hours, limit: Math.round(limit / 3600) }) : tr("proxy.failed")];
  }

  function paint(data) {
    count.textContent = tr("proxy.count", { n: data.entries.length, max: data.max });
    checked.textContent = tr("proxy.checked", { t: agoText(data.checked) });
    const notes = [];
    if (data.binary.state === "downloading") notes.push(h("div", { class: "msg info" }, tr("proxy.xray_downloading")));
    if (data.binary.state === "error") notes.push(h("div", { class: "msg error" }, tr("proxy.xray_error", { detail: data.binary.detail })));
    if (data.internet === false) notes.push(h("div", { class: "msg info" }, tr("proxy.no_internet")));
    note.replaceChildren(...notes);
    subs.replaceChildren(...data.subs.map(sub => h("div", { class: "proxy-row sub" },
      h("span", { class: "badge" }, "sub"),
      h("span", { class: "proxy-label" }, sub.label),
      h("span", { class: "proxy-state" }, tr("proxy.sub_count", { n: sub.count })),
      h("button", { class: "btn secondary small", type: "button", onclick: () => updateSub(sub.id) }, tr("proxy.sub_update")),
      h("button", { class: "btn secondary small", type: "button", title: tr("proxy.remove"), onclick: () => removeSub(sub.id) }, "×"))));
    if (!data.entries.length) { list.replaceChildren(h("div", { class: "empty" }, tr("proxy.empty"))); return; }
    list.replaceChildren(...data.entries.map((row, index) => {
      const [dot, label] = statusOf(row, data.limit || 86400);
      return h("div", { class: "proxy-row" },
        h("span", { class: "proxy-num" }, String(index + 1)),
        h("span", { class: "badge" }, row.type),
        h("span", { class: "proxy-label" }, row.label),
        h("span", { class: "proxy-state" }, h("span", { class: "dot " + dot }), label),
        h("button", { class: "btn secondary small icon-btn", type: "button", title: tr("proxy.edit"), onclick: () => openProxyDialog(row.id, (res) => { paint(res); }) }, icon("edit")),
        h("button", { class: "btn secondary small", type: "button", title: tr("proxy.remove"), onclick: () => remove(row.id) }, "×")
      );
    }));
  }

  async function refresh() {
    const res = await api("GET", "/api/proxy");
    if (res.ok) paint(res);
  }

  async function remove(id) {
    if (!(await confirmDialog(tr("confirm.proxy_remove")))) return;
    const res = await api("DELETE", "/api/proxy/" + encodeURIComponent(id), {});
    if (!res.ok) { toast(errorText(res), "error"); return; }
    paint(res);
  }

  async function updateSub(id) {
    const res = await api("POST", "/api/proxy/sub/" + encodeURIComponent(id) + "/update", {});
    if (!res.ok) { toast(errorText(res) + (res.detail ? " (" + res.detail + ")" : ""), "error"); return; }
    paint(res);
    toast(tr("proxy.sub_updated", { n: res.subs.find(s => s.id === id)?.count ?? 0 }), "ok");
  }

  async function removeSub(id) {
    if (!(await confirmDialog(tr("confirm.sub_remove")))) return;
    const res = await api("DELETE", "/api/proxy/sub/" + encodeURIComponent(id), {});
    if (!res.ok) { toast(errorText(res), "error"); return; }
    paint(res);
  }

  addButton.addEventListener("click", async () => {
    addButton.disabled = true;
    const res = await api("POST", "/api/proxy", { text: text.value });
    addButton.disabled = false;
    const lines = (res.errors || []).map(e => tr("proxy.item", { n: e.n, text: errorText({ error: e.code }) + (e.detail ? " (" + e.detail + ")" : "") }));
    if (!res.ok) {
      note.replaceChildren(h("div", { class: "msg error" }, [errorText(res), ...lines].join("\n")));
      return;
    }
    text.value = "";
    paint(res);
    if (lines.length) note.append(h("div", { class: "msg info" }, tr("proxy.added", { n: res.added }) + " " + tr("proxy.skipped", { list: lines.join("; ") })));
    else toast(tr("proxy.added", { n: res.added }), "ok");
  });

  proxyRefresh = refresh;
  refresh();

  return h("div", { class: "section" },
    h("p", { class: "meta" }, tr("proxy.hint", { max: 100 })),
    h("div", { class: "proxy-meta" }, count, checked),
    note,
    subs,
    list,
    text,
    h("div", { class: "actions" }, addButton,
      h("button", { class: "btn secondary", type: "button", onclick: () => openProxyDialog(null, (res) => { paint(res); toast(tr("proxy.added", { n: 1 }), "ok"); }) }, tr("proxy.form")))
  );
}

function renderProxyTab(content) {
  content.replaceChildren(h("div", { class: "panel" }, proxySection()));
}

function confirmDialog(message, yesLabel) {
  return new Promise(resolve => {
    const onKey = (event) => { if (event.key === "Escape") done(false); };
    const done = (value) => { back.remove(); document.removeEventListener("keydown", onKey); resolve(value); };
    const back = h("div", { class: "modal-back", onclick: (event) => { if (event.target === back) done(false); } },
      h("div", { class: "modal small", role: "dialog", "aria-modal": "true" },
        h("p", { class: "modal-text" }, message),
        h("div", { class: "modal-actions" },
          h("button", { class: "btn secondary", type: "button", onclick: () => done(false) }, tr("confirm.no")),
          h("button", { class: "btn danger", type: "button", onclick: () => done(true) }, yesLabel || tr("confirm.yes")))));
    document.addEventListener("keydown", onKey);
    document.body.append(back);
  });
}

function parseMinutes(text) {
  const value = String(text || "").trim().toLowerCase();
  if (!value) return null;
  if (/^\d+$/.test(value)) return parseInt(value, 10);
  const re = /(\d+)\s*([dhm])/g;
  let total = 0, used = 0, m;
  while ((m = re.exec(value))) {
    total += parseInt(m[1], 10) * ({ d: 1440, h: 60, m: 1 })[m[2]];
    used += m[0].length;
  }
  return used && used === value.replace(/\s+/g, "").length ? total : null;
}

function consoleLine(item) {
  const d = new Date(item.ts * 1000);
  return pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()) + " " + item.level + " " + item.msg;
}

let consoleCache = [];

async function refreshConsole(limit) {
  const res = await api("GET", "/api/console?limit=" + limit);
  if (res.ok) consoleCache = res.lines;
}

function langInline() {
  return langSwitch(async () => {
    const res = await api("PUT", "/api/config", { panel_lang: LANG });
    if (res.ok) me.panel_lang = res.config.panel_lang;
    renderDashboard();
  });
}

const LAYOUT_EN = "qwertyuiop[]asdfghjkl;'zxcvbnm,.`";

const LAYOUT_RU = "йцукенгшщзхъфывапролджэячсмитьбюё";

function swapLayout(text) {
  let out = "";
  for (const ch of text.toLowerCase()) {
    const a = LAYOUT_EN.indexOf(ch);
    const b = LAYOUT_RU.indexOf(ch);
    out += a >= 0 ? LAYOUT_RU[a] : b >= 0 ? LAYOUT_EN[b] : ch;
  }
  return out;
}

function normText(text) {
  return String(text || "").toLowerCase().replace(/ё/g, "е").replace(/[^\p{L}\p{N}]+/gu, " ").trim();
}

function editDistance(a, b, max) {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let older = null;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const row = [i];
    let best = i;
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      row[j] = Math.min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + cost);
      if (older && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) row[j] = Math.min(row[j], older[j - 2] + 1);
      best = Math.min(best, row[j]);
    }
    if (best > max) return max + 1;
    older = prev;
    prev = row;
  }
  return prev[b.length];
}

function isSubsequence(small, big) {
  let i = 0;
  for (const ch of big) if (ch === small[i]) i++;
  return i === small.length;
}

function wordScore(token, words) {
  let best = 0;
  words.forEach((word, index) => {
    const early = index === 0 ? 4 : 0;
    let score = 0;
    if (word === token) score = 80 + early;
    else if (word.startsWith(token)) score = 70 + early;
    else if (word.includes(token)) score = 50;
    else if (token.length >= 3 && editDistance(word.slice(0, token.length), token, 1) <= 1) score = 40 + early;
    else if (token.length >= 4 && editDistance(word, token, 1) <= 1) score = 35;
    else if (token.length >= 3 && isSubsequence(token, word)) score = 20;
    best = Math.max(best, score);
  });
  return best;
}

function nameScore(name, query) {
  const nameN = normText(name);
  const words = nameN.split(" ").filter(Boolean);
  let best = 0;
  for (const variant of new Set([normText(query), normText(swapLayout(query))])) {
    if (!variant) continue;
    if (nameN === variant) return 100;
    if (nameN.startsWith(variant)) best = Math.max(best, 90);
    const squeezed = nameN.replace(/ /g, ""), flat = variant.replace(/ /g, "");
    if (flat.length >= 2) {
      if (squeezed.startsWith(flat)) best = Math.max(best, 85);
      else if (squeezed.includes(flat)) best = Math.max(best, 60);
      else if (flat.length >= 4 && editDistance(squeezed.slice(0, flat.length), flat, 1) <= 1) best = Math.max(best, 45);
    }
    const tokens = variant.split(" ").filter(Boolean);
    const scores = tokens.map(token => wordScore(token, words));
    if (scores.length && scores.every(v => v > 0)) best = Math.max(best, scores.reduce((a, b) => a + b, 0) / scores.length);
  }
  return best;
}

function rankGuilds(guilds, query) {
  if (!query.trim()) return [...guilds].sort((a, b) => a.name.localeCompare(b.name));
  return guilds
    .map(guild => ({ guild, score: nameScore(guild.name, query) }))
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score || a.guild.name.localeCompare(b.guild.name))
    .map(item => item.guild);
}

function serverPicker(guilds, selectedId, onPick) {
  let open = false;
  let hot = 0;
  let shown = [];
  const root = h("div", { class: "picker" });
  const button = h("button", { class: "picker-btn", type: "button", onclick: () => toggle() });
  const input = h("input", { class: "picker-input", type: "text", autocomplete: "off", spellcheck: "false", placeholder: tr("servers.search") });
  const clear = h("button", { class: "picker-clear", type: "button", hidden: true, title: "×", onclick: () => { input.value = ""; refresh(); input.focus(); } }, "×");
  const label = h("div", { class: "picker-label" });
  const list = h("div", { class: "picker-list", role: "listbox" });
  const pop = h("div", { class: "picker-pop", hidden: true }, h("div", { class: "picker-search" }, icon("search"), input, clear), label, list);

  function row(guild, index) {
    const item = h("button", {
      class: "picker-row" + (index === hot ? " hot" : "") + (guild.id === selectedId ? " current" : ""), type: "button", role: "option",
      onmouseenter: () => { hot = index; markHot(); },
      onclick: () => choose(guild)
    }, guildIcon(guild), h("div", { class: "picker-text" }, h("div", { class: "name" }, guild.name), h("div", { class: "meta" }, tr("status.members", { n: guild.members ?? "?" }))));
    return item;
  }

  function markHot() {
    [...list.children].forEach((node, index) => node.classList.toggle("hot", index === hot));
    const node = list.children[hot];
    if (node && node.scrollIntoView) node.scrollIntoView({ block: "nearest" });
  }

  function refresh() {
    const query = input.value;
    clear.hidden = !query;
    shown = rankGuilds(guilds, query);
    hot = 0;
    label.textContent = tr(query.trim() ? "servers.search_results" : "servers.all");
    list.replaceChildren(...(shown.length ? shown.map(row) : [h("div", { class: "empty" }, tr("servers.nothing"))]));
  }

  function paintButton() {
    const guild = guilds.find(g => g.id === selectedId) || guilds[0];
    button.replaceChildren(guildIcon(guild), h("div", { class: "picker-text" }, h("div", { class: "name" }, guild.name), h("div", { class: "meta" }, tr("status.members", { n: guild.members ?? "?" }))), icon("chevron"));
  }

  function choose(guild) {
    selectedId = guild.id;
    paintButton();
    close();
    onPick(guild);
  }

  function onDocument(event) { if (!root.contains(event.target)) close(); }

  function onKey(event) {
    if (event.key === "ArrowDown") { event.preventDefault(); hot = Math.min(hot + 1, shown.length - 1); markHot(); }
    else if (event.key === "ArrowUp") { event.preventDefault(); hot = Math.max(hot - 1, 0); markHot(); }
    else if (event.key === "Enter") { event.preventDefault(); if (shown[hot]) choose(shown[hot]); }
    else if (event.key === "Escape") { close(); button.focus(); }
  }

  function toggle() { open ? close() : openPop(); }
  function openPop() {
    open = true;
    pop.hidden = false;
    root.classList.add("open");
    input.value = "";
    refresh();
    document.addEventListener("mousedown", onDocument);
    input.focus();
  }
  function close() {
    open = false;
    pop.hidden = true;
    root.classList.remove("open");
    document.removeEventListener("mousedown", onDocument);
  }

  input.addEventListener("input", refresh);
  input.addEventListener("keydown", onKey);
  paintButton();
  root.append(button, pop);
  return root;
}

function stepSummary(step) {
  return step.action === "ban"
    ? tr("step.line_ban", { w: fmtDuration(step.delete) })
    : tr("step.line_timeout", { d: fmtDuration(step.duration), w: fmtDuration(step.delete) });
}

function securitySection() {
  const box = h("div", { class: "section" });
  const error = formError();
  let model = null;

  async function load() {
    const res = await api("GET", "/api/security");
    if (!res.ok) { box.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
    model = { questions: res.questions.map(q => ({ id: q.id, text: q.text, answer: "" })), hint: res.hint, max: 3 };
    paint(res.questions.length > 0);
  }

  function paint(has) {
    const password = h("input", { type: "password", autocomplete: "current-password" });
    const hint = h("textarea", { maxlength: String(200), rows: "2" }, model.hint);
    const rows = model.questions.map((q, i) => {
      const select = h("select", { onchange: () => { q.id = select.value; paint(has); } },
        ["pet", "city", "game", "friend", "phone", "movie", "street"].map(id => h("option", { value: id }, tr("security.q." + id))),
        h("option", { value: "custom" }, tr("security.q_custom")));
      select.value = q.id;
      const answer = h("input", { type: "text", autocomplete: "off", spellcheck: "false", maxlength: "64", value: q.answer, oninput: () => { q.answer = answer.value.replace(/\s+/g, "_"); if (answer.value !== q.answer) answer.value = q.answer; } });
      const text = h("input", { type: "text", maxlength: "120", value: q.text, oninput: () => { q.text = text.value; } });
      return h("div", { class: "step" },
        h("div", { class: "step-head" }, h("b", {}, tr("security.q_n", { n: i + 1 })),
          h("button", { class: "btn secondary small", type: "button", onclick: () => { model.questions.splice(i, 1); paint(has); } }, "×")),
        field(tr("security.q_n", { n: i + 1 }), select),
        q.id === "custom" ? field(tr("security.question_text"), text) : null,
        field(tr("security.answer"), answer, tr("security.answer_hint")));
    });
    const add = model.questions.length < model.max
      ? h("button", { class: "btn secondary", type: "button", onclick: () => { model.questions.push({ id: "pet", text: "", answer: "" }); paint(has); } }, tr("security.add"))
      : null;
    const save = h("button", { class: "btn", type: "button", onclick: async () => {
      showError(error, "");
      if (model.questions.some(q => !q.answer)) { showError(error, tr("security.fill")); return; }
      save.disabled = true;
      const res = await api("PUT", "/api/security", { password: password.value, hint: hint.value, questions: model.questions.map(q => ({ id: q.id, text: q.id === "custom" ? q.text : "", answer: q.answer })) });
      save.disabled = false;
      if (!res.ok) { showError(error, errorText(res)); return; }
      password.value = "";
      toast(tr("security.saved"), "ok");
      load();
    } }, tr("security.save"));
    box.replaceChildren(
      h("h3", {}, tr("security.title")), h("p", { class: "meta" }, tr("security.lead")),
      has || model.questions.length ? null : h("div", { class: "msg info" }, tr("security.none")),
      error, ...rows, add,
      field(tr("security.hint"), hint, tr("security.hint_hint")),
      field(tr("settings.password"), password), save);
  }
  load();
  return box;
}

function consoleSection() {
  const box = h("pre", { class: "console-box tall" }, "…");
  const scope = h("select", {}, h("option", { value: "all" }, tr("console.scope_all")), h("option", { value: "session" }, tr("console.scope_session")));
  const format = h("select", {}, ["txt", "json", "csv"].map(f => h("option", { value: f }, f.toUpperCase())));
  async function refresh() {
    const res = await api("GET", "/api/console?limit=100");
    box.textContent = res.ok && res.lines.length ? res.lines.map(consoleLine).join("\n") : tr("console.empty");
    box.scrollTop = box.scrollHeight;
  }
  refresh();
  return h("div", { class: "section" }, h("h3", {}, tr("console.title")), h("p", { class: "meta" }, tr("console.hint", { n: 100 })), box,
    h("div", { class: "row" }, field(tr("console.export"), scope), field(" ", format)),
    h("div", { class: "actions" },
      h("button", { class: "btn secondary", type: "button", onclick: refresh }, tr("console.refresh")),
      h("button", { class: "btn", type: "button", onclick: () => { window.location.href = "/api/console/export?format=" + format.value + "&scope=" + scope.value; } }, tr("console.export"))));
}

function dataSection() {
  const out = h("div", {});
  const passphrase = h("input", { type: "password", autocomplete: "off" });
  const file = h("input", { type: "file", accept: "application/json,.json" });

  async function doExport() {
    const res = await api("POST", "/api/data/export", { passphrase: passphrase.value });
    if (!res.ok) { out.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
    const blob = new Blob([JSON.stringify(res.export, null, 1)], { type: "application/json" });
    const link = h("a", { href: URL.createObjectURL(blob), download: "mrbeast-gtfo-export.json" });
    document.body.append(link);
    link.click();
    link.remove();
    out.replaceChildren();
  }

  async function doImport() {
    if (!file.files.length) { out.replaceChildren(h("div", { class: "msg error" }, tr("data.choose"))); return; }
    let parsed;
    try { parsed = JSON.parse(await file.files[0].text()); } catch (e) { out.replaceChildren(h("div", { class: "msg error" }, tr("err.import_invalid"))); return; }
    const res = await api("POST", "/api/data/import", { export: parsed, passphrase: passphrase.value });
    if (!res.ok) { out.replaceChildren(h("div", { class: "msg error" }, errorText(res))); return; }
    out.replaceChildren(h("div", { class: "msg ok" }, tr("data.imported", { g: res.guilds, n: res.strikes })));
  }

  return h("div", { class: "section" }, h("h3", {}, tr("data.title")), h("p", { class: "meta" }, tr("data.hint")),
    field(tr("data.passphrase"), passphrase),
    h("div", { class: "actions" }, h("button", { class: "btn secondary", type: "button", onclick: doExport }, tr("data.export"))),
    field(tr("data.file"), file),
    h("div", { class: "actions" }, h("button", { class: "btn secondary", type: "button", onclick: doImport }, tr("data.import"))),
    out);
}

const KIND_LIST = ["socks5", "http", "vless", "vmess", "trojan", "shadowsocks", "xray"];

const NETWORKS = ["tcp", "ws", "grpc", "httpupgrade", "xhttp"];

const FINGERPRINTS = ["", "chrome", "firefox", "safari", "ios", "android", "edge", "random", "randomized"];

const SS_METHODS = ["aes-128-gcm", "aes-256-gcm", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305", "2022-blake3-aes-128-gcm", "2022-blake3-aes-256-gcm", "2022-blake3-chacha20-poly1305"];

async function openProxyDialog(entryId, done) {
  let data = { kind: "socks5", label: "", host: "", port: "", user: "", password: "" };
  let kinds = KIND_LIST.filter(k => k !== "xray");
  if (entryId) {
    const res = await api("GET", "/api/proxy/" + encodeURIComponent(entryId));
    if (!res.ok) { toast(errorText(res), "error"); return; }
    data = res.fields;
    kinds = ["socks5", "http"].includes(data.kind) ? ["socks5", "http"] : [data.kind];
  }
  const error = formError();
  const fieldsBox = h("div", { class: "dialog-fields" });
  const radios = h("div", { class: "radio-list" });

  const close = () => { back.remove(); document.removeEventListener("keydown", onKey); };
  const onKey = (event) => { if (event.key === "Escape") close(); };

  function bound(name, type, options) {
    const label = tr("proxy.f." + name);
    let input;
    if (type === "select") {
      input = h("select", { onchange: () => { data[name] = input.value; if (["network", "security"].includes(name)) paintFields(); } }, options.map(o => h("option", { value: o }, o === "" ? "—" : o)));
      input.value = data[name] ?? options[0];
      if (data[name] === undefined || data[name] === null) data[name] = options[0];
    } else if (type === "check") {
      input = h("input", { type: "checkbox", onchange: () => { data[name] = input.checked; } });
      input.checked = !!data[name];
      return h("label", { class: "check" }, input, h("span", {}, label));
    } else if (type === "area") {
      input = h("textarea", { rows: "10", spellcheck: "false", oninput: () => { data[name] = input.value; } }, data[name] ?? "");
    } else {
      input = h("input", { type: type === "password" ? "text" : type, autocomplete: "off", spellcheck: "false", value: data[name] ?? "", oninput: () => { data[name] = input.value; } });
    }
    return field(label, input);
  }

  function streamFields() {
    const out = [];
    if (!data.network) data.network = "tcp";
    if (!data.security) data.security = data.kind === "trojan" ? "tls" : "none";
    out.push(bound("network", "select", NETWORKS), bound("security", "select", ["none", "tls", "reality"]));
    if (data.security === "tls") out.push(bound("sni", "text"), bound("fp", "select", FINGERPRINTS), bound("alpn", "text"), bound("allow_insecure", "check"));
    if (data.security === "reality") out.push(bound("sni", "text"), bound("fp", "select", FINGERPRINTS.filter(Boolean)), bound("pbk", "text"), bound("sid", "text"), bound("spx", "text"));
    if (["ws", "httpupgrade", "xhttp"].includes(data.network)) out.push(bound("path", "text"), bound("host_header", "text"));
    if (data.network === "grpc") out.push(bound("service", "text"), bound("mode", "select", ["gun", "multi"]));
    if (data.network === "xhttp") out.push(bound("mode", "select", ["auto", "packet-up", "stream-up", "stream-one"]));
    return out;
  }

  function paintFields() {
    const kind = data.kind;
    const nodes = [bound("label", "text")];
    if (kind === "xray") {
      nodes.push(bound("json", "area"));
    } else {
      nodes.push(h("h4", {}, tr("proxy.socket")), h("div", { class: "row" }, bound("host", "text"), bound("port", "number")));
      if (kind === "socks5" || kind === "http") nodes.push(h("h4", {}, tr("proxy.account")), bound("user", "text"), bound("password", "password"));
      if (kind === "shadowsocks") nodes.push(bound("method", "select", SS_METHODS), bound("password", "password"));
      if (kind === "trojan") nodes.push(bound("password", "password"), ...streamFields());
      if (kind === "vless") nodes.push(bound("id", "text"), bound("flow", "select", ["", "xtls-rprx-vision"]), bound("encryption", "text"), ...streamFields());
      if (kind === "vmess") nodes.push(bound("id", "text"), bound("alter", "number"), bound("cipher", "select", ["auto", "aes-128-gcm", "chacha20-poly1305", "none", "zero"]), ...streamFields());
    }
    fieldsBox.replaceChildren(...nodes);
  }

  function paintRadios() {
    radios.replaceChildren(...kinds.map(kind => {
      const input = h("input", { type: "radio", name: "proxy-kind", value: kind, onchange: () => { data.kind = kind; if (!entryId) data = { ...data, network: undefined, security: undefined, mode: undefined }; paintFields(); } });
      input.checked = data.kind === kind;
      return h("label", { class: "radio" }, input, h("span", {}, tr("proxy.kind." + kind)));
    }));
  }

  const save = h("button", { class: "btn link", type: "button", onclick: async () => {
    showError(error, "");
    save.disabled = true;
    const body = { kind: data.kind, fields: data };
    const res = entryId ? await api("PUT", "/api/proxy/" + encodeURIComponent(entryId), body) : await api("POST", "/api/proxy/form", body);
    save.disabled = false;
    if (!res.ok) { showError(error, errorText(res)); return; }
    close();
    done(res);
  } }, tr("proxy.save"));

  const back = h("div", { class: "modal-back", onclick: (event) => { if (event.target === back) close(); } },
    h("div", { class: "modal", role: "dialog", "aria-modal": "true" },
      h("h3", {}, tr(entryId ? "proxy.dialog_edit" : "proxy.dialog_add")),
      radios, error, fieldsBox,
      entryId ? null : h("p", { class: "meta" }, tr("proxy.mt_note")),
      h("div", { class: "modal-actions" }, h("button", { class: "btn link", type: "button", onclick: close }, tr("proxy.cancel")), save)));
  document.addEventListener("keydown", onKey);
  document.body.append(back);
  paintRadios();
  paintFields();
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

  content.replaceChildren(h("div", { class: "settings-grid" },
    h("div", { class: "panel" },
      h("div", { class: "section" }, h("h3", {}, tr("settings.languages")),
        h("div", { class: "row" }, field(tr("settings.panel_lang"), panelLang), field(tr("settings.bot_lang"), botLang))),
      securitySection(),
      moderatorSection(),
      h("div", { class: "section" }, h("h3", {}, tr("settings.token")), h("p", { class: "meta" }, tr("settings.token_hint")), tokenForm),
      consoleSection(),
      dataSection(),
      privacySection()
    ),
    h("aside", { class: "settings-side" }, updateSection())
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

const KOS_REMOTE = "https://sun1-13.userapi.com/s/v1/ig2/6ik4I-I0a9zOuDvPmcE45LYfduxHpbV2E2WexX5hHhrxVSPn-iaon8XhyfC0LDViMa0lCd_KDBoi2zKITAiR_RfY.jpg?quality=95&as=32x17,48x25,72x38,108x57,160x85,240x127,360x191,480x255,540x287,640x340,720x382,968x514&from=bu&cs=968x0";

async function loadKosBackground() {
  let source = KOS_REMOTE;
  try {
    const res = await fetch("/api/kos-bg", { method: "HEAD", cache: "no-store" });
    if (res.ok) source = "/api/kos-bg";
  } catch (e) {}
  document.documentElement.style.setProperty("--kos-bg", 'url("' + source + '")');
}

function toggleKos() {
  const on = document.documentElement.toggleAttribute("data-kos");
  try { localStorage.setItem("mb_kos", on ? "1" : "0"); } catch (e) {}
  if (on) loadKosBackground();
}

try {
  if (localStorage.getItem("mb_kos") === "1") {
    document.documentElement.setAttribute("data-kos", "");
    loadKosBackground();
  }
} catch (e) {}

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
