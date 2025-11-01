
- `main.py`: Starts the bot, loads cogs asynchronously, syncs slash commands.
- `economy_bridge.py`: Contains all economic and approval logic.
- `global_market.db`: Stores applications and transfers.

---

## 🧠 Quality of Life Features

- Server name–based commands (no IDs).
- Natural language error messages and embeds.
- Auto sanity-check on exchange rates (warns if unusually high or low).
- Role check for approvers.
- Case-insensitive fuzzy guild matching.
- Uses ephemeral responses for user feedback.
- Compatible with Linux, Raspberry Pi, and SQLite persistence.

---

## 🔐 Configuration Variables
Inside `economy_bridge.py`:

| Variable | Description |
|-----------|-------------|
| `CENTRAL_BANK_SERVER_ID` | ID of the main review server |
| `APPROVAL_CHANNEL_ID` | Channel for new applications |
| `APPROVER_ROLE_NAME` | Role allowed to approve or deny |
| `UNB_API_KEY` | UnbelievaBoat API token |
| `DB_PATH` | SQLite file path |
| `MIN_RATE`, `MAX_RATE` | Rate limits |
| `MAX_TRANSFER_USD`, `MAX_TRANSFER_PERCENT` | Transfer safeguards |
| `API_DELAY` | API cooldown between PATCH requests |

---

## 🧾 Slash Commands Summary

| Command | Role | Description |
|----------|------|-------------|
| `/economy optin` | Guild admin | Submit your server for approval |
| `/economy approve` | World Bank Officer | Approve pending guilds |
| `/economy deny` | World Bank Officer | Deny pending guilds |
| `/economy list` | Public | Show approved guilds |
| `/economy transfer` | Public | Transfer currency between approved economies |

---

## 📈 Planned Upgrades
- Role-based automatic salaries  
- Global leaderboard  
- Trade treaties and embargoes  
- Global taxation  
- Audit exports and dashboards  

---

### 🪙 Summary
> BankerBot unifies roleplay servers under a shared financial system — linking cities, stabilizing exchange rates, and maintaining realism through the World Bank.

