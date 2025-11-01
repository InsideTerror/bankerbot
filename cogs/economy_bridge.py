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
CENTRAL_BANK_SERVER_ID = 1431340709356638341   # Server where approvals happen
APPROVAL_CHANNEL_ID = 1433861882158256263      # Channel to post pending apps
APPROVER_ROLE_NAME = "World Bank Officer"     # Role that can approve/deny
UNB_API_KEY = "GET YOUR OWN"
UNB_BASE_URL = "https://unbelievaboat.com/api/v1"
DB_PATH = "global_market.db"

# Safeguards
MIN_RATE = 0.0001
MAX_RATE = 10000.0
MAX_TRANSFER_USD = 10000.0
MAX_TRANSFER_PERCENT = 0.5
API_DELAY = 0.25
# =====================================================


class EconomyBridge(commands.Cog):
    """Handles all global economy linking, approvals, and transfers."""

    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    # Database Setup
    def init_db(self):
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
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_id TEXT,
                    from_guild TEXT,
                    to_guild TEXT,
                    amount REAL,
                    usd_value REAL,
                    amount_converted REAL,
                    kind TEXT,
                    status TEXT
                )
            """)

    def db(self, query, params=()):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.fetchall()

    # Permission check
    async def is_approver(self, user: discord.User) -> bool:
        guild = self.bot.get_guild(CENTRAL_BANK_SERVER_ID)
        if not guild:
            return False
        member = guild.get_member(user.id)
        if not member:
            return False
        if member.guild_permissions.administrator:
            return True
        role = discord.utils.get(guild.roles, name=APPROVER_ROLE_NAME)
        return role in member.roles

    # UnbelievaBoat API calls
    async def unb_get_user(self, session, guild_id, user_id):
        headers = {"Authorization": UNB_API_KEY}
        async with session.get(f"{UNB_BASE_URL}/guilds/{guild_id}/users/{user_id}", headers=headers) as r:
            return await r.json() if r.status == 200 else None

    async def unb_patch_user(self, session, guild_id, user_id, cash=None, bank=None):
        headers = {"Authorization": UNB_API_KEY, "Content-Type": "application/json"}
        data = {}
        if cash is not None:
            data["cash"] = cash
        if bank is not None:
            data["bank"] = bank
        async with session.patch(f"{UNB_BASE_URL}/guilds/{guild_id}/users/{user_id}", headers=headers, json=data) as r:
            return r.status

    async def send_application_embed(self, guild, user, currency, rate_usd, note=""):
        channel = self.bot.get_channel(APPROVAL_CHANNEL_ID)
        if not channel:
            return
        role = discord.utils.get(channel.guild.roles, name=APPROVER_ROLE_NAME)
        mention = role.mention if role else ""

        embed = discord.Embed(
            title="🌍 New Market Application",
            description=(
                f"**Guild:** {guild.name}\n"
                f"**Currency:** {currency}\n"
                f"**Rate:** ${rate_usd:.4f}\n"
                f"**Requested by:** {user.mention}"
            ),
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        if note:
            embed.add_field(name="Note", value=note, inline=False)

        await channel.send(content=mention, embed=embed)

    # Slash Command Group
    economy = app_commands.Group(name="economy", description="Global economy management")

    # /economy optin
    @economy.command(name="optin", description="Submit this server to join the global market.")
    @app_commands.describe(currency="Currency name", rate_usd="Value of 1 unit in USD", note="Optional note")
    async def optin(self, interaction: discord.Interaction, currency: str, rate_usd: float, note: str = ""):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permission.", ephemeral=True)
            return
        g = interaction.guild
        if not g:
            await interaction.response.send_message("❌ Must be run inside a server.", ephemeral=True)
            return

        if rate_usd < MIN_RATE or rate_usd > MAX_RATE:
            await interaction.response.send_message("⚠️ Invalid rate value.", ephemeral=True)
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

        await interaction.response.send_message("✅ Application submitted for Central Bank review.", ephemeral=True)
        await self.send_application_embed(g, interaction.user, currency, rate_usd, note)

    # /economy approve
    @economy.command(name="approve", description="Approve a pending economy (Central Bank only).")
    async def approve(self, interaction: discord.Interaction, guild_id: str):
        if not await self.is_approver(interaction.user):
            await interaction.response.send_message("❌ You are not authorized.", ephemeral=True)
            return

        self.db("UPDATE applications SET status='approved', decided_by=?, decided_at=? WHERE guild_id=?",
                (str(interaction.user.id), datetime.now(timezone.utc).isoformat(), guild_id))
        await interaction.response.send_message(f"✅ Approved server `{guild_id}`.", ephemeral=True)

    # /economy deny
    @economy.command(name="deny", description="Deny a pending economy (Central Bank only).")
    async def deny(self, interaction: discord.Interaction, guild_id: str):
        if not await self.is_approver(interaction.user):
            await interaction.response.send_message("❌ You are not authorized.", ephemeral=True)
            return

        self.db("UPDATE applications SET status='denied', decided_by=?, decided_at=? WHERE guild_id=?",
                (str(interaction.user.id), datetime.now(timezone.utc).isoformat(), guild_id))
        await interaction.response.send_message(f"⛔ Denied server `{guild_id}`.", ephemeral=True)

    # /economy list
    @economy.command(name="list", description="View all approved economies.")
    async def list(self, interaction: discord.Interaction):
        rows = self.db("SELECT guild_name,currency_name,rate_usd FROM applications WHERE status='approved'")
        if not rows:
            await interaction.response.send_message("No approved economies yet.", ephemeral=True)
            return
        msg = "\n".join([f"• **{r[0]}** — {r[1]} (${r[2]:.4f})" for r in rows])
        await interaction.response.send_message(msg, ephemeral=True)

    # /economy transfer
    @economy.command(name="transfer", description="Transfer funds between two approved economies.")
    @app_commands.describe(target_guild_id="Destination guild ID", amount="Amount or % (e.g. 1000 or 25%)", kind="cash or bank")
    async def transfer(self, interaction: discord.Interaction, target_guild_id: str, amount: str, kind: str = "cash"):
        g = interaction.guild
        if not g:
            await interaction.response.send_message("❌ Run this inside a server.", ephemeral=True)
            return

        src = self.db("SELECT * FROM applications WHERE guild_id=?", (g.id,))
        dst = self.db("SELECT * FROM applications WHERE guild_id=?", (target_guild_id,))
        if not src or not dst or src[0][4] != "approved" or dst[0][4] != "approved":
            await interaction.response.send_message("❌ Both servers must be approved.", ephemeral=True)
            return

        src_rate, dst_rate = float(src[0][3]), float(dst[0][3])
        percent_mode = amount.endswith("%")
        amount_val = float(amount[:-1]) / 100 if percent_mode else float(amount)

        async with aiohttp.ClientSession() as s:
            data = await self.unb_get_user(s, g.id, interaction.user.id)
            if not data:
                await interaction.response.send_message("⚠️ Could not read UnbelievaBoat data.", ephemeral=True)
                return

            cash, bank = float(data.get("cash", 0)), float(data.get("bank", 0))
            total = cash + bank
            if percent_mode:
                amount_val = total * amount_val

            if kind == "cash" and cash < amount_val:
                await interaction.response.send_message("⚠️ Not enough cash.", ephemeral=True)
                return
            if kind == "bank" and bank < amount_val:
                await interaction.response.send_message("⚠️ Not enough bank balance.", ephemeral=True)
                return

            usd_value = amount_val * src_rate
            if usd_value > MAX_TRANSFER_USD:
                await interaction.response.send_message("⚠️ Transfer exceeds limit.", ephemeral=True)
                return
            if amount_val > total * MAX_TRANSFER_PERCENT:
                await interaction.response.send_message("⚠️ Too large a portion of your funds.", ephemeral=True)
                return

            # Deduct and deposit
            if kind == "cash":
                await self.unb_patch_user(s, g.id, interaction.user.id, cash=cash - amount_val)
            else:
                await self.unb_patch_user(s, g.id, interaction.user.id, bank=bank - amount_val)
            await asyncio.sleep(API_DELAY)

            dest_amount = usd_value / dst_rate
            dst_data = await self.unb_get_user(s, target_guild_id, interaction.user.id)
            if not dst_data:
                await interaction.response.send_message("⚠️ You must be in the destination server.", ephemeral=True)
                return
            if kind == "cash":
                await self.unb_patch_user(s, target_guild_id, interaction.user.id, cash=dst_data["cash"] + dest_amount)
            else:
                await self.unb_patch_user(s, target_guild_id, interaction.user.id, bank=dst_data["bank"] + dest_amount)

        self.db("""
            INSERT INTO transfers (timestamp,user_id,from_guild,to_guild,amount,usd_value,amount_converted,kind,status)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (datetime.now(timezone.utc).isoformat(), str(interaction.user.id), str(g.id),
              target_guild_id, amount_val, usd_value, dest_amount, kind, "success"))

        await interaction.response.send_message(
            f"✅ Transferred **{amount_val:.2f}** {src[0][2]} to {dst[0][2]}.\n"
            f"💵 Converted ${usd_value:,.2f} → **{dest_amount:.2f}** received.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(EconomyBridge(bot))
