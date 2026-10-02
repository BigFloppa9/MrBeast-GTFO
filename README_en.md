# 🦁 MrBeast GTFO

**A test custom Discord moderation bot against the fraudulent "Mr. Beast" scam messages**

The bot spots an account that blasts the same images across several channels within seconds, puts it in timeout, deletes its messages and posts a report. The project was built for **Termux** from the start: the bot and its web control panel run right on your phone.

🌍 **Language / Язык:** [Русский](README.md) · English

---

## ✨ Features

- 🚨 Auto-detection: N images in M channels within K seconds (defaults 4 / 2 / 10)
- ⏱️ Timeout for the offender with a clear audit-log reason
- 🗑️ Deletes the offender's messages across all channels for a chosen period
- 📋 Reports in a log channel and in the web panel
- 🖥️ Dark Discord-style web panel: logs, status, per-server settings, languages
- 🔐 Password login; the token and password are stored on the device in protected form
- 🔑 Password reset through Discord (linked moderator account)
- 🌐 English and Russian: bot language and panel language are separate settings

---

## 📲 Install on Termux

> Install Termux from **F-Droid** or **GitHub**; the Google Play version is outdated.

```bash
pkg update -y && pkg install -y git
git clone https://github.com/BigFloppa9/MrBeast-GTFO
cd MrBeast-GTFO
bash install.sh
```

The script detects where it runs (Termux, Docker or a regular Linux server) and installs everything needed.

Start:

```bash
bash start.sh
```

The console prints two links:

```
http://192.168.x.x:8080   ← from any device on your Wi-Fi network
http://localhost:8080     ← from the phone itself
```

Open either one and finish the first-time setup. If port 8080 is busy, the next free port is used; the current address is always printed in the console.

**Phone died or Termux was closed?** Open Termux and run:

```bash
cd MrBeast-GTFO && bash start.sh
```

**Update:**

```bash
cd MrBeast-GTFO && git pull
```

Then restart the bot (`Ctrl+C`, then `bash start.sh` again).

### Docker and other servers

Run `install.sh` inside the container or on the server the same way as in Termux. In Docker, publish the panel port with `-p 8080:8080`. Port, address and data folder can be set with environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `MRBEAST_PORT` | `8080` | First port for the panel (the next one is used if busy) |
| `MRBEAST_HOST` | `0.0.0.0` | Listen address (`127.0.0.1` keeps the panel reachable from the device only) |
| `MRBEAST_DATA_DIR` | `./data` | Folder for settings, logs and keys |

---

## 🤖 Creating the bot in Discord

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2. **Bot** tab → **Reset Token** → copy the token. You need it during the panel's first setup. Never share it.
3. On the same page, under **Privileged Gateway Intents**, enable:
   - **Server Members Intent**
   - **Message Content Intent**
4. **OAuth2 → URL Generator** tab:
   - **Scopes:** `bot` and `applications.commands`
   - **Bot Permissions** (the minimum, **required**):

   | Permission | Why |
   |---|---|
   | View Channels | see channels |
   | Read Message History | find the offender's messages |
   | Manage Messages | delete the offender's messages |
   | Moderate Members | apply timeouts |
   | Send Messages | post reports in the log channel |
   | Embed Links | reports are sent as embeds |

5. Open the generated URL at the bottom of the page and add the bot to your server.

⚠️ **The bot's role must sit above the roles of the people it will punish** (Server Settings → Roles). Discord does not allow timeouts for administrators or the server owner.

If you want the bot to grant itself access to the log channel, also give it **Manage Channels** (optional). Without it, just allow the bot to post in the log channel manually.

---

## 🖥️ First panel launch

1. Open the link from the console.
2. Paste the **bot token**, choose a **panel password** (at least 8 characters), pick the panel and bot languages.
3. Click **Save and start the bot**. The token is checked with Discord before it is saved.

> Finish the setup right after starting: until it is done, whoever opens the link first becomes the panel owner. The panel runs over HTTP, so use it only on a trusted network.

### Panel sections

| Section | What's inside |
|---|---|
| **Logs** | The last 300 actions as Discord-style messages: offender display name, username and ID, trigger text, channel link, images (identical ones stored once), action. Updates live |
| **Status** | Bot state, ping, uptime, server list |
| **Servers** | Per server: timeout reason, duration, delete period, log channel, auto-detection thresholds |
| **Settings** | Panel and bot language, token replacement, moderator account link |

In the panel logs, offender fields, trigger text and channel names are cut to 69 characters so spam can't bloat the history. Videos are not saved.

### Moderator account and password reset

Needed so the password can be recovered.

1. In the panel: **Settings → Moderator account → Generate code**.
2. Send the bot the command `/reg CODE` in **DIRECT** messages. The account is linked.

If you forget the password:

1. Click **Forgot password?** on the sign-in page.
2. Send the bot the command `/log` in **DIRECT** messages. The bot replies with a code to the linked account only.
3. Enter the code in the panel, then the new password twice.

If no account was linked, stop the panel, delete `data/auth.json` and start it again: the setup runs from scratch.

---

## ⌨️ Discord commands

| Command | Where | Permission | What it does |
|---|---|---|---|
| `/mrbeast <user>` | server | Moderate Members | Manual timeout and message deletion |
| `/mrbeastlog <channel>` | server | Administrator | Set the log channel |
| `/mrbeastconfig` | server | Administrator | Reason, timeout (`1d`, `12h`, `30m`, `1d12h`, max `28d`) and delete period. Without arguments it shows current values |
| `/reg <code>` | direct messages | anyone | Link the moderator account |
| `/log` | direct messages | linked account | Password reset code |

Everything except `/mrbeast`, `/reg` and `/log` can also be done in the web panel.

---

## 🔐 What is stored where

Everything lives in the `data/` folder (excluded from git):

| File | Contents |
|---|---|
| `auth.json` | the bot token in encrypted form and a password hash (PBKDF2-SHA256); the password itself is never stored |
| `secret.key` | the key used to encrypt the token |
| `settings.json` | per-server settings |
| `config.json` | languages and the linked moderator account |
| `logs.json`, `images/` | logs (kept up to 30 days, max 300) and the image cache, both encrypted |

The token, logs and images are encrypted (Fernet) and the key sits in a separate file next to it, so the bot can start by itself after a restart. This protects against leaking a single file by accident, but not against someone who gets the whole `data/` folder. Do not publish or share it.

---

## 📱 Termux tips

- Disable battery optimization for Termux, otherwise Android may put the process to sleep.
- `start.sh` enables `termux-wake-lock` so the phone doesn't put the process to sleep. Better not to dismiss the Termux notification.
- The phone and the device you open the panel from must be on the same network.

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| "Discord rejected this token" | The token was copied partially or has been reset. Get a new one in the Developer Portal |
| Panel mentions Intents | Enable **Server Members Intent** and **Message Content Intent**, then restart the bot |
| Slash commands not visible | Wait a couple of minutes and restart Discord. The bot must be added with the `applications.commands` scope |
| Timeout is not applied | The bot's role is below the user's role, or the user is an administrator |
| No report in the log channel | Check the bot's permissions there: View Channel, Send Messages, Embed Links |

---

Made by **BigFloppa9** with Claude
