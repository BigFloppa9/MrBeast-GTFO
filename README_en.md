<div align="center">

<h1>🦁 MrBeast GTFO</h1>

<p><b>A test custom Discord moderation bot against the fraudulent "Mr. Beast" scam messages</b></p>

<p>🌍 <b>Language / Язык:</b> <a href="README.md">Русский</a> · English</p>

</div>

---

<h2 align="center">About</h2>

The bot detects an account that blasts the same images across several channels within seconds, puts it in timeout, deletes its messages and posts a report. The project was designed for **Termux** from the start: the bot and its web control panel run directly on your phone.

<h2 align="center">Features</h2>

- 🚨 Auto-detection: N images in M channels within K seconds (defaults 4 / 2 / 10)
- ⏱️ Timeout for the offender with an explanation in the audit log
- 🗑️ Deletion of the offender's messages in all channels for a chosen period
- 📋 Reports in a log channel and in the web panel
- 🖥️ Dark Discord-style web panel: logs, status, per-server settings, languages
- 🔄 Update the bot from the panel with one button, without reinstalling or losing data
- 🔐 Password login; the token, password, logs and images are stored in protected form
- 🔑 Password reset through Discord (linked administrator account)
- 🧹 Removal of a user's data from the logs by username or ID
- 🌐 English and Russian: bot language and panel language are separate settings

---

<h2 align="center">Install on Termux</h2>

> Install Termux from **F-Droid** or **GitHub**: the Google Play version is outdated.

One command installs all dependencies and starts the bot right away:

```bash
pkg install -y git && git clone https://github.com/BigFloppa9/MrBeast-GTFO && cd MrBeast-GTFO && bash install.sh
```

The script detects where it runs (Termux, Docker or a regular Linux server) and installs everything without asking questions.

After the start the console prints two links:

```
http://192.168.x.x:8080   ← from any device on your Wi-Fi network
http://localhost:8080     ← from the device the bot runs on
```

Open either one and complete the first-time setup. If port 8080 is busy, the next free port is used; the current address is always printed in the console.

**Starting again** (after the phone was turned off or Termux was closed):

```bash
cd MrBeast-GTFO && bash start.sh
```

<details>
<summary><b>Reinstall and uninstall</b></summary>

<br>

If the installation is already done and you are inside the `MrBeast-GTFO` folder (after `cd`), running the install command again creates a folder inside the folder. Use the commands below to uninstall or reinstall.

**Uninstall** (together with all data: token, settings, logs):

```bash
cd ~ && rm -rf MrBeast-GTFO
```

**Reinstall from scratch** (data will be deleted):

```bash
cd ~ && rm -rf MrBeast-GTFO && pkg install -y git && git clone https://github.com/BigFloppa9/MrBeast-GTFO && cd MrBeast-GTFO && bash install.sh
```

**Reinstall keeping the data:**

```bash
cd ~ && cp -r MrBeast-GTFO/data ~/mrbeast-data-backup && rm -rf MrBeast-GTFO && git clone https://github.com/BigFloppa9/MrBeast-GTFO && cp -r ~/mrbeast-data-backup MrBeast-GTFO/data && cd MrBeast-GTFO && bash install.sh
```

A regular update does not require a reinstall: use the button in the panel (Settings section) or `cd MrBeast-GTFO && git pull`.

</details>

<details>
<summary><b>Docker and other servers</b></summary>

<br>

Run `install.sh` inside the container or on the server the same way as in Termux. In Docker, publish the panel port with `-p 8080:8080`. Port, address and data folder can be set with environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `MRBEAST_PORT` | `8080` | First panel port (the next one is used if busy) |
| `MRBEAST_HOST` | `0.0.0.0` | Listen address (`127.0.0.1` keeps the panel reachable from the device only) |
| `MRBEAST_DATA_DIR` | `./data` | Folder for settings, logs and keys |

</details>

---

<h2 align="center">Creating the bot in Discord</h2>

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2. Go to the **Bot** tab → **Reset Token** and copy the token. It is required during the panel's first setup. Do not share it with anyone.
3. On the same page, under **Privileged Gateway Intents**, enable:
   - **Server Members Intent**
   - **Message Content Intent**
4. Go to **OAuth2 → URL Generator** and select:
   - **Scopes:** `bot` and `applications.commands`
   - **Bot Permissions** (the minimum, **required**):

   | Permission | Purpose |
   |---|---|
   | View Channels | access to channels |
   | Read Message History | finding the offender's messages |
   | Manage Messages | deleting the offender's messages |
   | Moderate Members | applying timeouts |
   | Send Messages | reports in the log channel |
   | Embed Links | reports are sent as embeds |

5. Open the generated URL at the bottom of the page and add the bot to your server.

⚠️ **The bot's role must be above the roles of the users it applies timeouts to** (Server Settings → Roles). Discord does not allow timeouts for administrators or the server owner.

For the bot to grant itself access to the log channel, additionally give it **Manage Channels** (optional). Without it, allow the bot to post in the log channel manually.

---

<h2 align="center">First panel launch</h2>

1. Open the link printed in the console.
2. Paste the **bot token**, set a **panel password** (at least 8 characters) and choose the bot language. The panel language is switched with the EN / RU buttons in the top-left corner.
3. Click **"Save and start the bot"**. The token is checked with Discord before saving. If Discord can't be reached (for example, it is unavailable at your provider), the data is still saved and the problem is shown in the panel.

> Complete the setup right after starting: until it is done, whoever opens the link first becomes the panel owner. The panel runs over HTTP, so use it only on a trusted network.

<h3 align="center">Panel sections</h3>

| Section | Contents |
|---|---|
| **Offenders** | Latest records as Discord-style messages: offender display name, username and ID, trigger text, channel link, images (identical ones stored once), action. Updates automatically |
| **Status** | Bot state, ping, uptime, control buttons, panel addresses on the network |
| **Servers** | The server list and per server (Telegram-style picker with smart search): punishment preset, steps, reasons, detection reset period, log channel, auto-detection thresholds |
| **Proxy** | Proxy and subscription list, state of each entry, time of the last check, entry editor |
| **Logs** | Console log across the whole page with export |
| **Settings** | Languages, administrator account link, token replacement, updates, removal of a user's data |

In the panel logs, offender fields, trigger text and channel names are cut to 69 characters so spam can't bloat the history. Videos are not saved. Records are kept for at most 30 days (and at most 300 records).

<h3 align="center">Administrator account link and password reset</h3>

The link is required to recover the password.

1. In the panel open **Settings → Moderator accounts → Generate code**. Up to 10 accounts can be linked by repeating the steps; accounts are unlinked in the same place.
2. Send the bot the command `/reg CODE` in **DIRECT** messages. The bot checks that you are an administrator (or the owner) of a server it works on and links your account by ID.

If the password is lost:

1. Click **"Forgot password?"** on the sign-in page.
2. Send the bot the command `/log` (no code) in **DIRECT** messages. The bot replies with a code to the linked account only.
3. Enter the code in the browser, then enter the new password twice.

Without a linked account the password can be recovered with **security questions**: in **Settings → Password recovery** choose up to 3 questions (ready-made or your own); answers are written in Latin letters without spaces (use `_`) and stored only as hashes. A hint shown under the password field after two wrong attempts is set there too. On the sign-in page the password field is cleared after a wrong password.

If neither a linked account nor questions exist, the recovery page shows the command that reinstalls the bot for your device (Termux or other). Reinstalling deletes all bot data.

<h3 align="center">Bot control</h3>

The bot status (online, paused, stopped) is always shown at the top of the panel. The **Status** tab has **Pause / Resume**, **Restart** and **Stop / Start** buttons. While paused, the bot does not react to image spam and manual commands still work; stopping disconnects the bot from Discord completely while the panel stays available. The chosen state is kept after a restart. The server list is in the **Servers** tab.

<h3 align="center">Proxy (if Discord is blocked)</h3>

In the **Proxy** tab you can add up to 100 entries: links, configs and subscription links go into one field.

- On every connection the bot checks **all** entries, connects to the fastest one and chooses again if it stops responding. If the selected entry's ping is above 1000 ms the bot looks for a faster one; if there is none, it stays on the fastest available.
- If no entry works, the bot connects **directly**.
- In the background, every 10 minutes all entries (including unused ones) are checked. If the bot is connected directly and some entry comes back, it switches to it by itself.
- An entry that does not respond for a total of one day is removed from the list automatically. The time is counted only while the device has internet: short network drops and phone sleep are not counted.

Accepted (one link per line, or one or several configs in a row):

| Format | Example |
|---|---|
| SOCKS5 | `socks5://user:pass@host:1080` |
| HTTP | `http://host:3128` |
| VLESS (link) | `vless://uuid@host:443?type=tcp&security=reality&pbk=…&sid=…&flow=xtls-rprx-vision#name` |
| Xray / V2Ray config (JSON) | a full config from an app, for example a v2rayNG export |
| VMess, Trojan, Shadowsocks | `vmess://…`, `trojan://…`, `ss://…` |
| Subscription | `https://provider/sub/…` (or `happ://add/…`, `v2raytun://import/…`, `clash://install-config?url=…`): the bot downloads the server list, the "Update" button re-reads it |

VLESS links support the `tcp`, `ws`, `grpc`, `httpupgrade` and `xhttp` transports and `none`, `tls`, `reality` security. For a JSON config the outbound proxy is taken (the one tagged `proxy`, or the first suitable one); other Xray protocols in such a config work too. Subscription entries of other types (hysteria, tuic, etc.) are skipped. A subscription is requested with several User-Agent headers in turn (Happ, v2rayN, a browser, curl), because providers answer different clients differently. Encrypted `happ://crypt5/…` links are decrypted locally with keys from a public list (github.com/cylaro/happ-decrypt, downloaded once into `data/cache`); the subscription itself is never sent anywhere. Older `crypt`, `crypt2`–`crypt4` are not supported. sing-box configs (the `outbounds` field), several configs in a row and `tg://socks` links are accepted as well. Telegram MTProto proxies (`tg://proxy`) cannot carry Discord traffic and are rejected. The list limit is 1000 entries. Each entry has an editor (pencil) and there is a form for adding without links.

For SOCKS5, VLESS and configs the bot uses the **Xray** core. It is downloaded automatically from GitHub on first use (with a checksum check) to `data/bin/xray`. If GitHub is unavailable, put the `xray` file into that folder manually. Entries and subscription links are stored in `data/proxies.json` in encrypted form.

**If the subscription can't be downloaded from the phone** (for example, the subscription server blocks your IP), run this on a computer (Windows, Linux or macOS, Python 3 required):

```bash
python tools/subscription.py "https://provider/sub/…" -o servers.txt
```

`servers.txt` contains the server links: open it and paste the content into the field in the Proxy tab.

<h3 align="center">Updating from the panel</h3>

1. Open **Settings → Updates** and click **"Check for updates"**.
2. If a new version is available, the list of changes is shown. Enter the panel password and click **"Update now"**.
3. The bot stops, downloads the update, checks dependencies and the new files, and starts again. Data and settings are kept. If anything fails, the previous version is restored. After the restart you need to sign in again.

<h3 align="center">Removing a user's data</h3>

In **Settings → Remove user data** enter the username (not the display name) or the ID. The panel shows the number of matching records. After confirmation, the display name, username and ID in those records are replaced with `null`, and the stored message text and images are removed; detection counters and console log lines mentioning the user are erased as well. A record with ID `null` is considered erased; a user whose name is literally "null" is not. The bot also deletes **its own** log messages about that user in the log channels of all servers (using the saved message references and by reading the channel history for 90 days); other messages are never touched. If the bot is offline, the Discord channels are not checked.

<h3 align="center">Punishments, presets and counters</h3>

In the **Servers** tab each server gets a preset:

| Preset | What it does |
|---|---|
| One action | timeout and message deletion with the configured values on every detection |
| 4 detections, then a ban | 1st detection: 5 min timeout and deletion for 1 h; 2nd: 1 day and 1 day; 3rd: 1 week and 1 day; 4th and later: ban and deletion for 1 day. The reason gets the detection number and a request to contact a moderator if it was a mistake |
| Ban at the first detection | ban and deletion of messages for 1 day |
| Custom | up to 8 steps: action (timeout or ban), length, deletion period and reason for each |

The detection counter is kept per user per server and resets after the configured number of days without violations (30 by default, 90 at most). Nothing is stored longer than 90 days. The reason is written to the audit log; sending it to the offender in a direct message is off by default and is enabled with a checkbox in the server settings. On a ban Discord deletes messages for the chosen period (7 days at most).

<h3 align="center">Settings transfer, console log, updates</h3>

- **Settings → Transfer settings**: "Import" on the left, "Export" on the right. Export asks for a password and saves a file with server settings, presets, reasons and counters; user IDs in the counters are encrypted with that password, offenders and logs are not included. Import opens a file picker, checks the file and asks for the password; records older than 90 days are dropped.
- The **Logs** tab (between "Proxy" and "Settings") shows the console log across the whole page, the last 300 lines with auto-refresh; export as txt, json or csv, for everything stored or since the last bot start. The file `data/console.log` keeps up to 2000 lines for 30 days.
- The version block at the top right of **Settings**: "Show changes" expands the latest commits (needs a git installation), "Check for update" runs the usual check.

---

<h2 align="center">Discord commands</h2>

| Command | Where | Permission | Purpose |
|---|---|---|---|
| `/mrbeast <user>` | server | Moderate Members | Manual timeout and message deletion |
| `/mrbeastlog <channel>` | server | Administrator | Set the log channel |
| `/mrbeastconfig` | server | Administrator | Reason, timeout (`1d`, `12h`, `30m`, `1d12h`, max `28d`) and delete period. Without arguments it shows current values |
| `/reg <code>` | direct messages | server administrator | Link the account |
| `/log` | direct messages | linked account | Password reset code |

All settings except the manual `/mrbeast` are also available in the web panel.

---

<h2 align="center">Data storage</h2>

Everything lives in the `data/` folder (excluded from git):

| File | Contents |
|---|---|
| `auth.json` | the bot token in encrypted form and a password hash (PBKDF2-SHA256); the password itself is never stored |
| `secret.key` | the encryption key |
| `settings.json` | per-server settings |
| `config.json` | languages and the linked administrator account |
| `proxies.json` | the proxy list in encrypted form |
| `bin/xray`, `xray/` | the Xray core and its temporary config (appear when a proxy is used) |
| `logs.json`, `images/` | logs (kept up to 30 days, max 300) and the image cache, both encrypted |

The token, logs and images are encrypted (Fernet) and the key sits in a separate file next to them, so the bot can start by itself after a restart. This protects against leaking a single file by accident, but not against someone who gets the whole `data/` folder. Do not publish it or share it. Details: [privacy policy](PRIVACY.md).

---

<h2 align="center">Termux recommendations</h2>

- Disable battery optimization for Termux, otherwise Android may suspend the process.
- `start.sh` enables `termux-wake-lock` so the device doesn't put the process to sleep. It is better not to dismiss the Termux notification.
- The phone and the device you open the panel from must be on the same network.

<h2 align="center">Troubleshooting</h2>

| Problem | Solution |
|---|---|
| The panel says Discord can't be reached | Discord may be blocked by your provider: add a proxy in the **Proxy** tab or turn on a VPN on the device. The bot keeps retrying |
| "Discord rejected this token" | The token was copied partially or has been reset. Get a new one in the Developer Portal and replace it in Settings |
| The panel mentions Intents | Enable **Server Members Intent** and **Message Content Intent**, then restart the bot |
| The bot is silent in direct messages | Pick `/reg` and `/log` from the list that appears after typing `/`; plain text is ignored and answered with a hint. If the list is empty, restart Discord |
| Slash commands are not visible | Wait a few minutes and restart Discord. The bot must be added with the `applications.commands` scope |
| The panel doesn't open from another device | The console prints all network addresses of the phone: use the one from your network (usually Wi-Fi). You can compare the phone's IP in the router. If it still fails, turn off "client isolation" (AP isolation) in the router and make sure both devices are on the same network |
| Timeout is not applied | The bot's role is below the user's role, or the user is an administrator |
| No report in the log channel | Check the bot's permissions there: View Channel, Send Messages, Embed Links |

---

<div align="center">

<b>BigFloppa9</b>

</div>
