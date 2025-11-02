import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import aiohttp
import asyncio
from datetime import datetime, timezone

# =====================================================
# CONFIGURATION
# =====================================================
CENTRAL_BANK_SERVER_ID = SERVER_ID
APPROVAL_CHANNEL_ID = CHANNEL_ID
CENTRAL_BANK_ROLE_ID = ROLE_ID
UNB_API_KEY = "REPLACE_WITH_REAL_KEY"
UNB_BASE_URL = "https://unbelievaboat.com/api/v1"
DB_PATH = "global_market.db"
APPROVED_DB = "approved_users.db"

# Safeguards
MIN_RATE = 0.0001
MAX_RATE = 1000000.0
MAX_TRANSFER_USD = 1000000.0
MAX_TRANSFER_PERCENT = 0.8  # Max 80% of balance per transfer
API_DELAY = 0.25
# =====================================================


class EconomyBridge(commands.Cog):
    """Handles global economy linking, approvals, transfers, and audits."""

    def __init__(self, bot):
        self.bot = bot
        self.init_dbs()

    # =====================================================
    # DATABASE SETUP
    # =====================================================
    def init_dbs(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    guild_id TEXT PRIMARY KEY,
                    guild_name TEXT,
                    currency_name TEXT,
                    rate_usd REAL,
                    status TEXT,
                    requested_by TEXT,
                    requested_at TEXT,
                    note TEXT,
                    decided_by TEXT,
                    decided_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT,
                    actor_id TEXT,
                    actor_name TEXT,
                    target_guild_id TEXT,
                    target_guild_name TEXT,
                    note TEXT
                )
            """)
        with sqlite3.connect(APPROVED_DB) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS approved_users (user_id INTEGER PRIMARY KEY)""")

    def db(self, query, params=(), path=DB_PATH):
        with sqlite3.connect(path) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.fetchall()

    # =====================================================
    # LOGGING
    # =====================================================
    def log_audit(self, action, actor, target_guild, note=""):
        self.db("""
            INSERT INTO audits (timestamp, action, actor_id, actor_name, target_guild_id, target_guild_name, note)
            VALUES (?,?,?,?,?,?,?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            action,
            str(actor.id),
            actor.display_name,
            str(target_guild.id if hasattr(target_guild, "id") else target_guild),
            getattr(target_guild, "name", str(target_guild)),
            note
        ))

    # =====================================================
    # PERMISSIONS
    # =====================================================
    def is_approved(self, user_id: int) -> bool:
        result = self.db("SELECT 1 FROM approved_users WHERE user_id = ?", (user_id,), path=APPROVED_DB)
        return bool(result)

    def is_admin(self, member: discord.Member) -> bool:
        return member.guild_permissions.administrator

    # =====================================================
    # UTILITIES
    # =====================================================
    def find_guild_by_name(self, name: str):
        for g in self.bot.guilds:
            if g.name.lower() == name.lower():
                return g
        for g in self.bot.guilds:
            if name.lower() in g.name.lower():
                return g
        return None

    async def send_guild_message(self, guild_id, message):
        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return
        try:
            if guild.system_channel:
                await guild.system_channel.send(message)
            else:
                ch = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                if ch:
                    await ch.send(message)
        except:
            pass

    # =====================================================
    # UNBELIEVABOAT API
    # =====================================================
    async def get_balance(self, guild_id: int, user_id: int):
        """Get a user's balance from UnbelievaBoat API."""
        url = f"{UNB_BASE_URL}/guilds/{guild_id}/users/{user_id}"
        headers = {"Authorization": UNB_API_KEY}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    print(f"[Unb GET] {resp.status} for {user_id} in {guild_id}: {text}")
                    if resp.status == 200:
                        data = await resp.json()
                        return {"cash": data.get("cash", 0), "bank": data.get("bank", 0)}
                    elif resp.status == 404:
                        print("[Unb GET] ⚠️ User not found")
                    elif resp.status == 401:
                        print("[Unb GET] ❌ Unauthorized — check API key or permissions")
        except asyncio.TimeoutError:
            print(f"[Unb GET] ❌ Timeout while fetching {user_id} in {guild_id}")
        except Exception as e:
            print(f"[Unb GET] ❌ Exception for {user_id} in {guild_id}: {type(e).__name__} — {e}")

        return {"cash": 0, "bank": 0}


    async def update_balance(self, guild_id: int, user_id: int, cash_change: int = 0, bank_change: int = 0, reason: str = "Global transfer"):
        """Apply a change to a user's UnbelievaBoat balance."""
        url = f"{UNB_BASE_URL}/guilds/{guild_id}/users/{user_id}"
        headers = {
            "Authorization": UNB_API_KEY,
            "Content-Type": "application/json"
        }

        # Ensure integers — UnbelievaBoat rejects floats silently
        payload = {
            "cash": int(cash_change),
            "bank": int(bank_change),
            "reason": str(reason)
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.patch(url, headers=headers, json=payload) as resp:
                    text = await resp.text()
                    print(f"[Unb PATCH] {resp.status} for {guild_id}/{user_id}: {text} | payload={payload}")

                    # Accept 200 and 204 as success (some versions return no content)
                    return resp.status in (200, 204)
        except asyncio.TimeoutError:
            print(f"[Unb PATCH] ❌ Timeout while updating {guild_id}/{user_id}")
        except Exception as e:
            print(f"[Unb PATCH] ❌ Exception for {guild_id}/{user_id}: {type(e).__name__} — {e}")
        return False



    # =====================================================
    # EMBED UTILITY
    # =====================================================
    def update_embed_status(self, embed, approved):
        new_embed = embed.copy()
        new_embed.color = discord.Color.green() if approved else discord.Color.red()
        status = "✅ Approved" if approved else "⛔ Denied"
        new_embed.add_field(name="Status", value=status, inline=False)
        return new_embed

    # =====================================================
    # VIEW (APPROVE/DENY)
    # =====================================================
    class ApplicationView(discord.ui.View):
        def __init__(self, parent, guild_id):
            super().__init__(timeout=None)
            self.parent = parent
            self.guild_id = guild_id

        @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
        async def approve(self, interaction: discord.Interaction, _):
            if not self.parent.is_approved(interaction.user.id):
                await interaction.response.send_message("❌ You are not authorized.", ephemeral=False)
                return
            self.parent.db("UPDATE applications SET status='approved', decided_by=?, decided_at=? WHERE guild_id=?",
                           (str(interaction.user.id), datetime.now(timezone.utc).isoformat(), str(self.guild_id)))
            await interaction.message.edit(embed=self.parent.update_embed_status(interaction.message.embeds[0], True), view=None)
            await self.parent.send_guild_message(self.guild_id, "✅ Your economy has been **approved** by the Central Bank!")
            await interaction.response.send_message("Approved ✅", ephemeral=False)

        @discord.ui.button(label="⛔ Deny", style=discord.ButtonStyle.danger)
        async def deny(self, interaction: discord.Interaction, _):
            if not self.parent.is_approved(interaction.user.id):
                await interaction.response.send_message("❌ You are not authorized.", ephemeral=False)
                return
            self.parent.db("UPDATE applications SET status='denied', decided_by=?, decided_at=? WHERE guild_id=?",
                           (str(interaction.user.id), datetime.now(timezone.utc).isoformat(), str(self.guild_id)))
            await interaction.message.edit(embed=self.parent.update_embed_status(interaction.message.embeds[0], False), view=None)
            await self.parent.send_guild_message(self.guild_id, "⛔ Your economy application was **denied**.")
            await interaction.response.send_message("Denied ⛔", ephemeral=False)

    # =====================================================
    # COMMANDS
    # =====================================================
    economy = app_commands.Group(name="economy", description="Global market functions")

    # --- Apply to join global market ---
    @economy.command(name="optin", description="Submit your server to join the global market.")
    async def optin(self, interaction: discord.Interaction, currency: str, rate_usd: float, note: str = ""):
        g = interaction.guild
        if not g or not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permission.", ephemeral=False)
            return
        if rate_usd < MIN_RATE or rate_usd > MAX_RATE:
            await interaction.response.send_message("⚠️ Invalid rate.", ephemeral=False)
            return

        now = datetime.now(timezone.utc).isoformat()
        self.db("""
        INSERT INTO applications (guild_id,guild_name,currency_name,rate_usd,status,requested_by,requested_at,note)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(guild_id) DO UPDATE SET
            currency_name=excluded.currency_name,
            rate_usd=excluded.rate_usd,
            status='pending',
            requested_by=excluded.requested_by,
            requested_at=excluded.requested_at,
            note=excluded.note
        """, (str(g.id), g.name, currency, rate_usd, "pending", str(interaction.user.id), now, note))

        await interaction.response.send_message("✅ Application submitted to the Central Bank.", ephemeral=False)

        channel = self.bot.get_channel(APPROVAL_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🌍 New Market Application",
                description=f"**Guild:** {g.name}\n**Currency:** {currency}\n**Rate:** ${rate_usd:.4f}\n**Requested by:** {interaction.user.display_name}",
                color=discord.Color.gold(),
                timestamp=datetime.now(timezone.utc)
            )
            if note:
                embed.add_field(name="Note", value=note, inline=False)
            await channel.send(embed=embed, view=self.ApplicationView(self, g.id))

    async def update_balance(self, guild_id: int, user_id: int, cash_change: int = 0, bank_change: int = 0, reason: str = "Global transfer"):
        url = f"{UNB_BASE_URL}/guilds/{guild_id}/users/{user_id}"
        headers = {"Authorization": UNB_API_KEY}
        payload = {"cash": cash_change, "bank": bank_change, "reason": reason}

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=payload) as resp:
                text = await resp.text()
                print(f"[Unb PATCH] {resp.status} for {guild_id}/{user_id}: {text} | payload={payload}")
            return resp.status == 200


    # --- Withdraw server ---
    @economy.command(name="withdraw", description="Withdraw your server from the global market.")
    async def withdraw(self, interaction: discord.Interaction):
        g = interaction.guild
        if not g or not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only administrators can withdraw.", ephemeral=False)
            return
        self.db("DELETE FROM applications WHERE guild_id=?", (str(g.id),))
        await interaction.response.send_message(f"🏳️ {g.name} withdrawn from global market.", ephemeral=False)
        self.log_audit("withdraw", interaction.user, g)

    # --- List approved economies ---
    @economy.command(name="list", description="List all approved economies.")
    async def list(self, interaction: discord.Interaction):
        rows = self.db("SELECT guild_name,currency_name,rate_usd FROM applications WHERE status='approved'")
        if not rows:
            await interaction.response.send_message("No approved economies yet.", ephemeral=False)
            return
        msg = "\n".join(f"• **{r[0]}** — {r[1]} (${r[2]:.4f})" for r in rows)
        await interaction.response.send_message(msg, ephemeral=False)

    # --- Kick guild (approved officers only) ---
    @economy.command(name="kick", description="Remove a guild from the global market (approved users only).")
    async def kick(self, interaction: discord.Interaction, guild_name: str):
        if not self.is_approved(interaction.user.id):
            await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=False)
            self.log_audit("kick_attempt_unauthorized", interaction.user, guild_name, "Unauthorized attempt.")
            return

        g = self.find_guild_by_name(guild_name)
        if not g:
            await interaction.response.send_message("⚠️ Guild not found.", ephemeral=False)
            return
        self.db("DELETE FROM applications WHERE guild_id=?", (str(g.id),))
        await self.send_guild_message(g.id, "🚫 Your economy has been **removed** by the Central Bank.")
        await interaction.response.send_message(f"🚫 {g.name} removed from market.", ephemeral=False)
        self.log_audit("kick", interaction.user, g)

    # =====================================================
    # 🏦 TRANSFER FUNDS BETWEEN SERVERS (FIXED)
    # =====================================================
    @economy.command(name="transfer", description="Transfer funds between global market servers.")
    async def transfer(self, interaction: discord.Interaction, target_server: str, amount: float, mode: str = "cash"):
            """Transfer your funds between two approved economies, correctly formatted for UnbelievaBoat API."""
            try:
                await interaction.response.defer(thinking=True)

                user = interaction.user
                origin_guild = interaction.guild
                if origin_guild is None:
                    await interaction.followup.send("❌ Could not detect your server context.", ephemeral=False)
                    return

                # Find target guild
                target_guild = self.find_guild_by_name(target_server)
                if target_guild is None:
                    await interaction.followup.send("⚠️ Target server not found.", ephemeral=False)
                    return

                # Fetch currency info
                origin_row = self.db("SELECT currency_name, rate_usd FROM applications WHERE guild_id=? AND status='approved'",
                                    (str(origin_guild.id),))
                target_row = self.db("SELECT currency_name, rate_usd FROM applications WHERE guild_id=? AND status='approved'",
                                    (str(target_guild.id),))
                if not origin_row or not target_row:
                    await interaction.followup.send("❌ One or both servers are not in the approved global economy.", ephemeral=False)
                    return

                origin_currency, origin_rate = origin_row[0]
                target_currency, target_rate = target_row[0]

                # Calculate USD value then target amount
                usd_value = amount * origin_rate
                if usd_value > MAX_TRANSFER_USD:
                    await interaction.followup.send("⚠️ Transfer exceeds global limit.", ephemeral=False)
                    return

                target_amount = usd_value / target_rate

                # Fetch balances via API
                balances = await self.get_balance(origin_guild.id, user.id)
                cash_bal = balances.get("cash", 0)
                bank_bal = balances.get("bank", 0)

                # Choose mode
                if mode.lower() == "bank":
                    if bank_bal < amount:
                        await interaction.followup.send(f"❌ Insufficient bank balance: you have {bank_bal:.2f} {origin_currency}.", ephemeral=False)
                        return
                    cash_delta_origin = 0
                    bank_delta_origin = -int(amount)
                else:
                    if cash_bal < amount:
                        await interaction.followup.send(f"❌ Insufficient cash balance: you have {cash_bal:.2f} {origin_currency}.", ephemeral=False)
                        return
                    cash_delta_origin = -int(amount)
                    bank_delta_origin = 0

                # Target credit always as cash by default
                cash_delta_target = int(target_amount)
                bank_delta_target = 0

                # Perform origin deduction
                ok_origin = await self.update_balance(origin_guild.id, user.id,
                                                    cash_change=cash_delta_origin,
                                                    bank_change=bank_delta_origin,
                                                    reason=f"Global transfer to {target_guild.name}")
                if not ok_origin:
                    await interaction.followup.send("⚠️ Transfer failed when debiting your origin account.", ephemeral=False)
                    self.log_audit("transfer_failed", user, origin_guild, f"Debit failed: {amount} {origin_currency}")
                    return

                # Perform target credit
                ok_target = await self.update_balance(target_guild.id, user.id,
                                                    cash_change=cash_delta_target,
                                                    bank_change=bank_delta_target,
                                                    reason=f"Global transfer from {origin_guild.name}")
                if not ok_target:
                    await interaction.followup.send("⚠️ Transfer failed when crediting target account.", ephemeral=False)
                    self.log_audit("transfer_failed", user, target_guild, f"Credit failed: {target_amount:.2f} {target_currency}")
                    return

                # Log and inform success
                self.log_audit("transfer", user, target_guild,
                            f"{amount:.2f} {origin_currency} → {target_amount:.2f} {target_currency}")
                await interaction.followup.send(
                    f"💸 Successfully transferred **{amount:.2f} {origin_currency}** from **{origin_guild.name}** → **{target_amount:.2f} {target_currency}** in **{target_guild.name}**",
                    ephemeral=False
                )

            except Exception as e:
                import traceback
                traceback.print_exc()
                try:
                    await interaction.followup.send(f"❌ Internal error: {type(e).__name__} — {e}", ephemeral=False)
                except:
                    pass



async def setup(bot):
    await bot.add_cog(EconomyBridge(bot))
