# 🏦 BankerBot — Global Economy Bridge for RP Servers

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Discord.py](https://img.shields.io/badge/Discord.py-2.4-blueviolet)
![!License CC BY-NC 4.0](https://img.shields.io/badge/License-CC_20BY_NC_204.0-green)
![Static Badge](https://img.shields.io/badge/Unbelievaboat_API_Version-v1-yellow)
![Static Badge](https://img.shields.io/badge/Bot_Status-Active-Green)
![Static Badge](https://img.shields.io/badge/Bot_version-2.4-red)
![Static Badge](https://img.shields.io/badge/SQLite_Version-3.50.-white)
![Static Badge](https://img.shields.io/badge/Async_IO_Version-4.0.0-orange)






> **BankerBot** is a Discord bot designed to act as a **global compatibility layer** between roleplay city servers — enabling cross-server economies, currency exchange, and centralized market regulation.

---

## 🌍 Overview

BankerBot connects multiple Discord servers using the [UnbelievaBoat API](https://unbelievaboat.com/api/docs), allowing each server to:

- Define its own currency and exchange rate against USD.  
- Opt-in to a shared **global market** managed by a Central Bank.  
- Transfer funds between servers with automatic conversion rates.  
- Maintain fair governance through a **World Bank Officer** system.

---

## ✨ Core Features

### 🏦 Global Market System
Each participating server can apply to join the global economy with its own:
- **Currency name**
- **Exchange rate (vs USD)**
- **Application message** sent to the Central Bank for approval.

### 🌐 Cross-Server Transfers
Users can transfer their UnbelievaBoat balances between approved economies:
- Automatic conversion using exchange rates.  
- Supports both **cash** and **bank** balances.  
- Uses UnbelievaBoat API for data integrity.

### 🧾 Central Bank Oversight
The Central Bank manages:
- Server applications (approve/deny via interactive buttons).  
- Forced removals from the market (`/economy kick`).  
- Automatic audit logging of all key actions.

### 👮 Role-Based Access Control
- Only **approved officers** (from a database list) can manage the market.  
- Server administrators can withdraw their economy voluntarily.

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/InsideTerror/bankerbot.git
cd BankerBot
```
### 2. Set up a Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
>💡 **If you’re on a Raspberry Pi or system with “externally-managed environment” errors:**
>`python3 -m venv bankerbot`
` source bankerbot/bin/activate`
 `pip install -r requirements.txt`
### 3. Configure your bot
Edit the constants in `bot.py` and `cogs/economy_bridge.py`:

-   `DISCORD_TOKEN`
    
-   `CENTRAL_BANK_SERVER_ID`
    
-   `APPROVAL_CHANNEL_ID`
    
-   `UNB_API_KEY`
    
-   `CENTRAL_BANK_ROLE_ID`
### 4. Start the bot
`python3 bot.py`

## 🧩 File Structure
```bash
BankerBot/
│
├── main.py                  # Bot entry point and cog loader
├── cogs/
│   ├── economy_bridge.py    # Global economy logic
│   └── admin_bridge.py      # Approved user management
│
├── global_market.db         # Stores server data and audit logs
├── approved_users.db        # Stores IDs of authorized officers
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```
## 🧠 Commands Summary
Command | Description| Permissions

`/economy optin` | Submit your server to join the global economy. | Manage Server
`/economy withdraw` | Withdraw your server from the market. | Administrator
`/economy list` | View all approved servers. | Any
`/economy kick` | Remove a server (Central Bank only). | Approved Officer
`/economy transfer` | Transfer funds between servers with automatic conversion. | Any

## 🛡️ Security & Safeguards

-   Rate-limited to prevent API overload (`API_DELAY`).
    
-   Min/max limits for exchange rates and transfer amounts.
    
-   Role-based access for all sensitive commands.
    
-   Full audit trail of every action with timestamps.

## 🪙 Example Workflow

1.  A server runs:
 
    `/economy optin currency=Mark rate_usd=88.0` 
    
3.  The Central Bank receives a pending application message.
    
4.  A World Bank Officer clicks **Approve ✅** or **Deny ⛔**.
    
5.  Once approved, the server joins the global market.
    
6.  Users can transfer funds between approved servers:
    
    `/economy transfer target_server:"Supreme Court" amount:100 source_type:bank`

## License
see license.md

## Invite
[Click here to invite BankerBot to your server!](https://discord.com/oauth2/authorize?client_id=1363180301693616313)
[Approve Access to your server for the bot to work!!](https://unbelievaboat.com/applications/authorize?app_id=1433860813692734564)

## 💬 Contact

For development, debugging, or partnership inquiries, contact:  
**@mr_fritz_teufel** on Discord
