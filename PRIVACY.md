# Privacy Policy / Политика конфиденциальности

**MrBeast GTFO** is an open-source Discord moderation bot ([source code](https://github.com/BigFloppa9/MrBeast-GTFO)). This policy describes what the bot processes and stores.

## 1. What the bot processes

The bot receives message events (including attachments, embeds and text) from servers it has been added to. It only reads them to check whether one user posts several images in several different channels within a short time window (by default 4 images in 2 channels within 10 seconds, adjustable by the server administrator).

Messages of users who do not trigger this rule are **not stored**. For the length of the time window (seconds) the bot keeps references to the recent image messages of each user in memory only, and drops them afterwards.

## 2. What the bot stores

Only when a user is punished (automatically or with the `/mrbeast` command) the bot saves an incident record:

- the Discord user ID, display name and username of the offender;
- for automatic detection: the first 69 characters of the triggering message text, the name of the channel and a link to it;
- for automatic detection: copies of up to 8 distinct images from the offending messages (images only, up to 8 MB each, no video), identical images are stored once;
- the moderator's display name, username and ID for manual actions;
- the applied action (timeout length, number of deleted messages) and the time.

Only the latest 300 incident records are kept; older records and their images are deleted automatically.

The bot also stores per-server settings (timeout reason and length, delete period, log channel ID, detection thresholds), the chosen languages and, optionally, the ID and name of the Discord account linked as the control-panel moderator.

The bot token is stored encrypted and the control-panel password only as a salted hash.

## 3. Where the data is stored

The bot is self-hosted: all stored data lives in the `data/` folder on the device or server of the person who runs the bot. It is not sent to the developer or to any third party and is not sold, shared, or used for advertising, profiling or training of machine-learning models.

## 4. Information posted to Discord

If a server administrator selects a log channel, the bot posts a report there with the offender's mention and ID, the triggering message text (shortened) and the action taken. Access to that report is governed by the permissions of that channel.

## 5. Retention and deletion

Incident records are kept until they are rotated out (see section 2) or until the operator deletes the `data/` folder. To request removal of data about you, open an issue at https://github.com/BigFloppa9/MrBeast-GTFO/issues or contact the person who runs the bot on your server. Removing the bot from a server stops all processing for that server.

## 6. Changes

This policy may be updated together with the source code; the current version is always in the repository.

---

## Кратко по-русски

Бот читает сообщения только чтобы заметить, что один пользователь за несколько секунд разослал картинки по нескольким каналам. Сообщения обычных пользователей не сохраняются. При срабатывании сохраняется запись об инциденте: ID, имя и юзернейм нарушителя, первые 69 символов сообщения, канал, до 8 картинок (без видео) и применённое действие. Хранятся последние 300 записей. Все данные лежат в папке `data/` на устройстве того, кто запустил бота, никуда не передаются и не продаются. Удаление данных: через issue в репозитории или у владельца бота; удаление бота с сервера прекращает обработку.
