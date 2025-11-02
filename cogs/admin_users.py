import discord
from discord.ext import commands
import sqlite3

OWNER_ID = USER_ID  # your Discord user ID
DB_PATH = "approved_users.db"

class UserAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS approved_users (
                        user_id INTEGER PRIMARY KEY
                    )""")
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Only respond to DMs from the owner
        if not isinstance(message.channel, discord.DMChannel):
            return
        if message.author.id != OWNER_ID:
            return

        parts = message.content.strip().split()
        if len(parts) < 2:
            return

        command, *args = parts
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if command.lower() == "adduser" and len(args) == 1:
            try:
                user_id = int(args[0])
                c.execute("INSERT OR IGNORE INTO approved_users (user_id) VALUES (?)", (user_id,))
                conn.commit()
                await message.channel.send(f"✅ User `{user_id}` has been added to the approved list.")
            except ValueError:
                await message.channel.send("❌ Invalid user ID.")
        
        elif command.lower() == "removeuser" and len(args) == 1:
            try:
                user_id = int(args[0])
                c.execute("DELETE FROM approved_users WHERE user_id = ?", (user_id,))
                conn.commit()
                await message.channel.send(f"🗑️ User `{user_id}` removed from the approved list.")
            except ValueError:
                await message.channel.send("❌ Invalid user ID.")
        
        elif command.lower() == "listusers":
            c.execute("SELECT user_id FROM approved_users")
            users = [str(row[0]) for row in c.fetchall()]
            if users:
                await message.channel.send("📜 Approved users:\n" + "\n".join(users))
            else:
                await message.channel.send("ℹ️ No users currently approved.")
        
        conn.close()

async def setup(bot):
    await bot.add_cog(UserAdmin(bot))
