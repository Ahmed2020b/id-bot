import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required for member-related operations
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store number assignments
number_assignments = {}

# File to store assignments
ASSIGNMENTS_FILE = 'assignments.json'

# File to store allowed roles
ROLES_FILE = 'allowed_roles.json'

def load_assignments():
    global number_assignments
    try:
        with open(ASSIGNMENTS_FILE, 'r') as f:
            number_assignments = json.load(f)
    except FileNotFoundError:
        number_assignments = {}

def save_assignments():
    with open(ASSIGNMENTS_FILE, 'w') as f:
        json.dump(number_assignments, f)

def load_allowed_roles():
    try:
        with open(ROLES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_allowed_roles(roles):
    with open(ROLES_FILE, 'w') as f:
        json.dump(roles, f)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    load_assignments()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.event
async def on_member_remove(member):
    user_id = str(member.id)
    assigned_number = None
    
    for num, uid in number_assignments.items():
        if uid == user_id:
            assigned_number = num
            break

    if assigned_number:
        del number_assignments[assigned_number]
        save_assignments()
        print(f"Number {assigned_number} has been automatically unassigned from {member.name} (ID: {member.id}) who left the server.")

def has_allowed_role(interaction: discord.Interaction) -> bool:
    allowed_roles = load_allowed_roles()
    user_roles = [role.id for role in interaction.user.roles]
    return any(role_id in user_roles for role_id in allowed_roles)

@bot.tree.command(name="addrole", description="Add a role that can assign numbers to others")
@app_commands.describe(role="The role to add")
async def add_role(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return

    allowed_roles = load_allowed_roles()
    if role.id not in allowed_roles:
        allowed_roles.append(role.id)
        save_allowed_roles(allowed_roles)
        await interaction.response.send_message(f"Role {role.name} can now assign numbers to others.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Role {role.name} is already allowed to assign numbers.", ephemeral=True)

@bot.tree.command(name="removerole", description="Remove a role's ability to assign numbers to others")
@app_commands.describe(role="The role to remove")
async def remove_role(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return

    allowed_roles = load_allowed_roles()
    if role.id in allowed_roles:
        allowed_roles.remove(role.id)
        save_allowed_roles(allowed_roles)
        await interaction.response.send_message(f"Role {role.name} can no longer assign numbers to others.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Role {role.name} wasn't allowed to assign numbers.", ephemeral=True)

@bot.tree.command(name="assign_to", description="Assign a number to another user")
@app_commands.describe(number="The number to assign (1-2000)", user="The user to assign the number to")
async def assign_to(interaction: discord.Interaction, number: int, user: discord.Member):
    if not has_allowed_role(interaction):
        await interaction.response.send_message("You don't have permission to assign numbers to others.", ephemeral=True)
        return

    if number < 1 or number > 2000:
        await interaction.response.send_message("Please choose a number between 1 and 2000.", ephemeral=True)
        return

    if str(number) in number_assignments:
        await interaction.response.send_message(f"Number {number} is already assigned to someone else.", ephemeral=True)
        return

    # Check if user already has a number assigned
    for num, user_id in number_assignments.items():
        if str(user_id) == str(user.id):
            await interaction.response.send_message(f"{user.name} already has number {num} assigned. Please unassign it first.", ephemeral=True)
            return

    number_assignments[str(number)] = str(user.id)
    save_assignments()
    await interaction.response.send_message(f"Number {number} has been assigned to {user.name}!", ephemeral=True)

@bot.tree.command(name="unassign", description="Unassign your number")
async def unassign(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    assigned_number = None
    
    for num, uid in number_assignments.items():
        if uid == user_id:
            assigned_number = num
            break

    if assigned_number:
        del number_assignments[assigned_number]
        save_assignments()
        await interaction.response.send_message(f"Number {assigned_number} has been unassigned from you.", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have any numbers assigned.", ephemeral=True)

@bot.tree.command(name="unassign_from", description="Unassign a number from another user")
@app_commands.describe(user="The user to unassign the number from")
async def unassign_from(interaction: discord.Interaction, user: discord.Member):
    if not has_allowed_role(interaction):
        await interaction.response.send_message("You don't have permission to unassign numbers from others.", ephemeral=True)
        return

    user_id = str(user.id)
    assigned_number = None
    
    for num, uid in number_assignments.items():
        if uid == user_id:
            assigned_number = num
            break

    if assigned_number:
        del number_assignments[assigned_number]
        save_assignments()
        await interaction.response.send_message(f"Number {assigned_number} has been unassigned from {user.name}.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{user.name} doesn't have any numbers assigned.", ephemeral=True)

@bot.tree.command(name="list", description="List all assigned numbers")
async def list_numbers(interaction: discord.Interaction):
    if not number_assignments:
        await interaction.response.send_message("No numbers are currently assigned.", ephemeral=True)
        return

    # Create a formatted list of assignments
    assignments_list = []
    for number, user_id in number_assignments.items():
        user = await bot.fetch_user(int(user_id))
        assignments_list.append(f"Number {number}: {user.name}")

    # Split the list into chunks to avoid message length limits
    chunk_size = 20
    chunks = [assignments_list[i:i + chunk_size] for i in range(0, len(assignments_list), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        message = "**Assigned Numbers:**\n" + "\n".join(chunk)
        if i == 0:
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN')) 