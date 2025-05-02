# Discord Number Assignment Bot

A Discord bot that manages number assignments from 1 to 2000.

## Features

- Assign numbers to users
- Unassign numbers
- List all currently assigned numbers
- Persistent storage of assignments
- Role-based permissions for assigning numbers to others
- Automatic number unassignment when users leave the server

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the same directory as `bot.py` with your Discord bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

3. Run the bot:
```bash
python bot.py
```

## Commands

### Basic Commands
- `/assign <number>` - Assign a number to yourself (1-2000)
- `/unassign` - Remove your assigned number
- `/list` - View all currently assigned numbers

### Role Management Commands (Admin Only)
- `/addrole <role>` - Add a role that can assign numbers to others
- `/removerole <role>` - Remove a role's ability to assign numbers to others

### Role-Based Commands
- `/assign_to <number> <user>` - Assign a number to another user (requires allowed role)
- `/unassign_from <user>` - Unassign a number from another user (requires allowed role)

## Notes

- Each user can only have one number assigned at a time
- Numbers must be between 1 and 2000
- All commands are ephemeral (only visible to the user who ran the command)
- Only users with administrator permissions can manage which roles can assign numbers to others
- Users with allowed roles can assign and unassign numbers for other users
- Numbers are automatically unassigned when users leave the server 