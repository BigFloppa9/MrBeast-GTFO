# MrBeast GTFO: information for the Discord review team

Source code: https://github.com/BigFloppa9/MrBeast-GTFO
Privacy policy: https://github.com/BigFloppa9/MrBeast-GTFO/blob/main/PRIVACY.md

## Purpose

MrBeast GTFO is an open-source anti-scam moderation bot. It targets one specific, widespread attack: hijacked accounts that post fake "MrBeast" giveaway / cheat-download images (usually 4+ images, often with the text "bro") across many channels within seconds. The scam leads to more account takeovers and spreads from server to server.

## What the bot does

1. Auto-detection. If one user posts at least N images in at least M different channels within K seconds (default 4 / 2 / 10, adjustable per server), the bot treats the account as hijacked.
2. Action. It applies a timeout (default 1 day, max 28 days) with a reason shown in the audit log that tells the victim to change passwords, revoke sessions and enable 2FA. It then deletes that user's recent messages across channels where the bot has Read Message History and Manage Messages.
3. Reporting. It posts an embed report to a log channel chosen by the server admin: offender, trigger text, channel, timeout and number of deleted messages.
4. Manual use. Moderators with Moderate Members can use /mrbeast <user> to apply the same action.
5. Configuration. Server admins use /mrbeastlog and /mrbeastconfig, or a password-protected web control panel hosted by the bot operator (logs, status, per-server settings).

The bot only reacts to the image-spam pattern. It does not moderate normal conversation, does not read DMs (the only DM commands are /reg and /log, used to link and recover the control-panel account), and never acts on users who do not trigger the rule.

## Permissions (minimum)

View Channels, Read Message History, Manage Messages, Moderate Members, Send Messages, Embed Links. No Administrator.

## Privileged intents

- Message Content Intent: detection relies on attachments and embeds of messages, which Discord does not deliver without this intent. The message text is only used for a short snippet in the moderation report.
- Server Members Intent: when the rule fires, the bot looks up the author as a guild Member from the member cache to call the timeout endpoint. Without the intent the lookup fails.
- Presence Intent: not requested.

## Data handling

Messages of non-offending users are never stored. When a user is punished, an incident record is kept on the operator's own device: user ID, display name, username, the first 69 characters of the trigger text, the channel, up to 8 distinct images from the offending messages (no video) and the action taken. Records and images are encrypted at rest, kept at most 30 days (and at most 300 records), never shared, sold, or used for ML training. See the privacy policy for details.

## Note on demo material

The privileged intents of the production application are currently disabled, so a live demonstration (screenshots or video) cannot be produced right now. The full source code is public: any question about how the application works can be answered by reviewing it directly or with an automated / AI-assisted code review. The sections below point to the relevant places.

## Where to verify this in the code

- mrbeast/bot.py, `Guard.on_message`: detection (uses attachments/embeds, needs Message Content).
- mrbeast/bot.py, `Guard.run_auto` and `apply_timeout`: member lookup and timeout (needs Server Members).
- mrbeast/bot.py, `purge_messages`: deletion of the offender's messages.
- mrbeast/bot.py, `build_embed` and `record_log`: exactly what is reported and logged.
- mrbeast/logstore.py: retention (30 days / 300 records), image storage and encryption at rest.
- The bot makes no network requests except to the Discord API and the Discord CDN (to save images of offending messages).

## How to test

Add the bot to a test server with the permissions above, set a log channel with /mrbeastlog, then post 4 images from a regular test account into 2 different channels within 10 seconds. The bot times the account out, deletes its messages and posts a report.
