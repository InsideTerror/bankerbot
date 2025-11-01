# 🏦 BankerBot — Global Economy Bridge for RP Servers

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Discord.py](https://img.shields.io/badge/Discord.py-2.4-blueviolet)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active-success)

> **BankerBot** is a Discord bot designed to act as a **global compatibility layer** between roleplay city servers — enabling cross-server economies, currency exchange, and global financial governance.

---

## 🌍 Overview

BankerBot connects multiple Discord servers using the [UnbelievaBoat API](https://unbelievaboat.com/api/docs), allowing each server to:
- Define its own currency and exchange rate against USD.
- Opt-in to a shared global economy managed by a **Central Bank server**.
- Transfer funds between approved servers with automatic conversion rates.
- Maintain fair governance and prevent abuse through a **World Bank Officer** system.

---

## ✨ Core Features

### 🏦 Global Market System
Each participating server can apply to join the global economy with its own:
- **Currency name**
- **Exchange rate (vs USD)**
- **Approval message** that appears in the Central Bank’s approval channel.

### 🌐 Cross-Server Transfers
Users can safely transfer their UnbelievaBoat balances between approved economies:
- Automatic conversion using stored exchange rates.  
- Supports both **cash** and **bank** balances.  
- Full API integration ensures data consistency.

### 🧾 Central Bank Oversight
The Central Bank manages:
- Server applications (approve/deny via interactive buttons).
- Forced removals from the market (`/economy kick`).
- Audit logs for all key actions.

### 👮 Role-Based Access Control
- Only **approved officers** (from a SQLite list) can manage the global market.  
- Server administrators can voluntarily withdraw their economy.

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/BankerBot.git
cd BankerBot
