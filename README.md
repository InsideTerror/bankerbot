
# 🏦 BankerBot — Global Economy Bridge for RP Servers

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Discord.py](https://img.shields.io/badge/Discord.py-2.4-blueviolet)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active-success)

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
Edit the constants in `main.py` and `cogs/economy_bridge.py`:

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

## 📜 License

This project is licensed under the MIT License.
Copyright 2025 Fritz Teufel (discord)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Invite
[Click here to invite BankerBot to your server!](https://discord.com/oauth2/authorize?client_id=1363180301693616313)

## 💬 Contact

For development, debugging, or partnership inquiries, contact:  
**@mr_fritz_teufel** on Discord
