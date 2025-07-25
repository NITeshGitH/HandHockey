# 🏒 Hand Hockey Discord Bot

A comprehensive Discord bot for managing Hand Hockey matches with turn-based gameplay, team management, and live commentary.

## ✨ Features

### 🎮 Match Management
- Create and manage matches with unique IDs
- Join existing matches with player limits
- Automatic match expiration and cleanup
- Detailed match information and player lists

### 👥 Team Setup
- Random player shuffling into teams
- Custom team naming
- Role assignments (Striker, Midfielder, Defender, Goalkeeper)
- Formation validation

### 🚀 Game Flow
- Coin toss system for match start
- Turn-based action system with DM notifications
- Timeout handling and warnings
- Action choice validation

### 🎭 Dynamic Commentary
- Real-time match commentary
- Event-specific messages (goals, saves, fouls, etc.)
- Randomized game events for demonstrations
- Rich embed formatting

### 📊 Statistics & Profiles
- Player profiles with match statistics
- Live scoreboards during matches
- Performance tracking
- Achievement system

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- pip (Python package manager)

### Quick Setup

1. **Clone or download the project files**
   ```bash
   # Navigate to your project directory
   cd "C:\Users\nverm\OneDrive\Desktop\HAND HOCKEY"
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure your bot token**
   - Edit the `.env` file created by the setup
   - Add your Discord bot token:
     ```
     DISCORD_TOKEN=your_bot_token_here
     ```

4. **Start the bot**
   ```bash
   python main.py
   ```

### Manual Installation

If you prefer manual setup:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file**
   ```bash
   copy .env.example .env
   ```

3. **Edit .env with your bot token**

4. **Run the bot**
   ```bash
   python main.py
   ```

## 🎯 Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token and paste it in your `.env` file
6. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent

## 🔗 Bot Permissions

Your bot needs the following permissions:
- Send Messages
- Embed Links
- Read Message History
- Use External Emojis

**Invite link template:**
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot
```

## 📋 Commands and UI/UX Design

### Match Management (`H` prefix)
- `Hcreate_match` - Create a new match with a UI prompt displaying match ID and host details. Player list and joining instructions are integrated within the embed, and match data is dynamically stored in the `matches` and `match_players` tables.
- `Hjoin_match <match_id>` - Join an existing match with interface feedback on success and player count. The command checks player limits via direct database queries.

### Team Setup
- `Hset_team_name <team> <name>` - Change team names with UI feedback confirming the name change. This updates the `matches` table to reflect team identities.
- `Hshuffle_players` - Distributes players and assigns roles automatically. Player assignments and roles are displayed in a formatted embed, and updates are made in the `match_players` table.

### Game Flow
- `Htoss` - Displays who wins the toss with action prompts to guide the next steps. Matches are updated to reflect the status in the database.
- `Hchoose_action <attack/defend>` - Allows a team to select an initial strategy with the chosen option displayed in an embed.
- `Hstart_match` - Uses direct messages to inform players about their turn actions. Updates match status to 'started' in the database.

### Dynamic Commentary
- `Hdemo_commentary` - Demonstrates commentary system with examples of each type.
- `Hrandom_event` - Generates random match events with associated commentary to enhance game immersion.

### Player Statistics
- `Hprofile [member]` - Generates a detailed player profile using rich embeds to showcase stats pulled from the `players` table.
- `Hscorecard` - Displays live match scoreboard using embed fields for real-time updates.

### Error Handling and Help System
- **Robust error handling** - Provides contextual embeds for common errors, informing users about possible resolution steps.
- **Comprehensive help system** - Offers detailed descriptions of commands and their usage with examples, simplifying user onboarding.

## 🗄️ Database Architecture & Synchronization

### PostgreSQL Integration (Neon Cloud)

The bot uses **PostgreSQL** hosted on **Neon.com**for persistent data storage, ensuring all match data, player statistics, and game events are preserved across bot restarts.

#### Core Database Tables:

1. **`players` Table**
   - Stores user profiles, match statistics, ratings
   - Fields: `user_id`, `username`, `display_name`, `matches_played`, `matches_won`, `goals`, `assists`, `saves`, `rating`
   - **UI/UX Integration**: Powers the `Hprofile` command with rich embeds displaying comprehensive player statistics
   - **Auto-sync**: Player records are created/updated automatically when joining matches

2. **`matches` Table**
   - Contains match metadata, team names, scores, and status
   - Fields: `match_id`, `host_id`, `status`, `team_a_name`, `team_b_name`, `team_a_score`, `team_b_score`
   - **UI/UX Integration**: Enables real-time scorecard updates and match information displays
   - **Status Management**: Tracks match progression from 'waiting' → 'ongoing' → 'finished'

3. **`match_players` Table**
   - Many-to-many relationship between matches and players
   - Fields: `match_id`, `user_id`, `team`, `role`, `is_captain`
   - **UI/UX Integration**: Powers team lineup displays and role assignments in formatted embeds
   - **Dynamic Updates**: Real-time synchronization when shuffling teams or assigning roles

4. **`match_events` Table**
   - Records game events for commentary and statistics
   - Fields: `match_id`, `event_type`, `player1_id`, `description`, `minute`
   - **UI/UX Integration**: Feeds the dynamic commentary system with contextual match events

### Database Synchronization Features:

#### Real-Time UI Updates
- **Match Creation**: Instantly creates database entries and displays formatted embed with joining instructions
- **Player Joining**: Updates `match_players` table and refreshes UI with current player count
- **Team Shuffling**: Bulk updates player assignments and immediately reflects changes in team lineup embeds
- **Live Scoring**: Real-time score updates synchronized between database and Discord embeds

#### Data Consistency & Error Handling
- **Connection Pooling**: Maintains 1-10 database connections for optimal performance
- **Retry Logic**: Automatic reconnection with exponential backoff for network issues
- **Transaction Safety**: Ensures data integrity during complex operations like team shuffling
- **Graceful Degradation**: Fallback UI messages when database is temporarily unavailable

#### Performance Optimizations
- **Indexed Queries**: Optimized database indexes for fast match and player lookups
- **Batch Operations**: Efficient bulk updates during team assignments
- **Connection Management**: Proper cleanup and resource management
- **Query Optimization**: Minimized database calls through strategic data caching

### UI/UX Database Integration Examples:

#### Match Creation Flow:
```
1. User: Hcreate_match
2. Database: CREATE match record + INSERT host as player
3. UI: Display rich embed with match ID, joining instructions
4. Database: Index match for quick retrieval
5. UI: Auto-cleanup expired matches from display
```

#### Team Assignment Flow:
```
1. User: Hshuffle_players
2. Database: SELECT all match players
3. Logic: Balance teams and assign roles
4. Database: BULK UPDATE player assignments
5. UI: Display formatted team lineups with roles and captains
6. Database: COMMIT transaction for data consistency
```

#### Live Statistics Flow:
```
1. User: Hprofile @player
2. Database: SELECT player stats with aggregations
3. UI: Generate rich embed with statistics, achievements
4. Database: Track profile view for analytics
5. UI: Display with proper formatting and emojis
```

## 🎨 UI/UX Design Patterns

### Discord Embed Design System

The bot uses a consistent design language across all commands with color-coded embeds and standardized formatting:

#### Color Scheme
- **🟢 Success (0x00ff00)**: Match creation, successful joins, completed actions
- **🔴 Error (0xff0000)**: Validation errors, failed operations, access denied
- **🟡 Warning (0xffaa00)**: Timeouts, missing requirements, potential issues
- **🔵 Info (0x0099ff)**: General information, help messages, status updates
- **🟨 Gold (0xffd700)**: Special events, toss results, achievements
- **🟠 Orange (0xff6600)**: Commentary, match events, dynamic content

#### Embed Structure Patterns

**Match Creation Embeds:**
```
🏒 NEW MATCH CREATED!
┌─ Match ID: ABC123DE
├─ Host: @username
├─ 👥 Join Instructions
├─ ⚙️ Setup Commands  
├─ 🔧 Management Options
└─ ⏰ Expiry Information
```

**Team Lineup Embeds:**
```
🔀 PLAYERS SHUFFLED & ASSIGNED!
┌─ 🔵 Team A (4 players)
│   ├─ 👑 Player1 (GK)
│   ├─ Player2 (DEF)
│   ├─ Player3 (MF)
│   └─ Player4 (ST)
├─ 🔴 Team B (4 players)
│   ├─ 👑 Player5 (GK)
│   ├─ Player6 (DEF)
│   ├─ Player7 (MF)
│   └─ Player8 (ST)
└─ ⚽ Role Distribution Info
```

**Live Scorecard Embeds:**
```
📊 LIVE SCORECARD
┌─ Match: ABC123DE | Status: Ongoing
├─ 🔵 Team Warriors: 2 goals, 8 shots, 3 saves
├─ 🔴 Team Champions: 1 goal, 6 shots, 5 saves
└─ 🔥 Match in progress!
```

### Interactive Command Flow Design

#### Progressive Disclosure Pattern
Commands reveal information and next steps progressively:

1. **Initial Command**: Shows primary result with immediate context
2. **Action Prompts**: Clear next-step instructions with exact command syntax
3. **Status Updates**: Real-time feedback on command execution
4. **Error Recovery**: Specific resolution steps when commands fail

#### Contextual Help Integration
- **Inline Examples**: Command usage shown directly in error messages
- **Related Commands**: Cross-references to relevant commands in each embed
- **Status-Aware Prompts**: Different UI based on match/player state
- **Progressive Onboarding**: Guided experience for new users

### User Experience Flows

#### Match Creation & Setup Flow
```
Hcreate_match → Rich embed with:
├─ Unique match ID prominently displayed
├─ Copy-paste join command for easy sharing
├─ Next-step setup commands clearly listed
├─ Management options for host
└─ Automatic expiry warning

Players join → Dynamic updates:
├─ Player count updates in real-time
├─ Team balance suggestions when appropriate
├─ Setup completion status indicators
└─ Ready-to-start notifications
```

#### Team Assignment & Role Management
```
Hshuffle_players → Intelligent distribution:
├─ Balanced team sizes automatically
├─ Role assignments with emoji indicators
├─ Captain assignments clearly marked
├─ Team names and customization options
└─ Formation validation feedback
```

#### Live Game Experience
```
Game Start → Multi-channel communication:
├─ Public announcements in main channel
├─ Private DMs for individual player actions
├─ Real-time scorecard updates
├─ Dynamic commentary generation
└─ Progress tracking and statistics
```

### Accessibility & Usability Features

#### Error Prevention
- **Input Validation**: Real-time validation with helpful error messages
- **Duplicate Prevention**: Checks for existing matches, duplicate joins
- **Permission Verification**: Clear messages when users lack required permissions
- **State Validation**: Prevents invalid actions based on current match state

#### Error Recovery
- **Specific Error Messages**: Detailed explanations of what went wrong
- **Resolution Steps**: Exact commands to fix common issues
- **Alternative Actions**: Suggestions for alternative approaches
- **Graceful Degradation**: Fallback options when features are unavailable

#### Responsive Design
- **Mobile-Friendly**: Embeds optimized for mobile Discord clients
- **Concise Information**: Key details prioritized in limited screen space
- **Clear Hierarchy**: Important information emphasized with formatting
- **Quick Actions**: Essential commands easily accessible

### Database-UI Synchronization Patterns

#### Optimistic UI Updates
```
User Action → Immediate UI Feedback → Database Sync → Confirmation

Example: Team shuffle
1. Show "Shuffling..." status immediately
2. Display tentative team assignments
3. Commit to database in background
4. Confirm with final formatted results
5. Handle any sync errors gracefully
```

#### Real-Time State Management
- **Live Updates**: Scorecard reflects database changes instantly
- **Conflict Resolution**: Handle simultaneous user actions gracefully
- **Data Consistency**: Ensure UI always reflects true database state
- **Cache Invalidation**: Smart cache updates for optimal performance

#### Offline Resilience
- **Queued Actions**: Store user actions when database is temporarily unavailable
- **Status Indicators**: Clear feedback when systems are offline
- **Recovery Procedures**: Automatic sync when connectivity returns
- **Data Integrity**: Prevent data loss during network issues

## 🏗️ Project Structure

```
HAND HOCKEY/
├── main.py                    # Main bot entry point
├── config.py                  # Configuration management
├── utils.py                   # Utility functions and error handling
├── game_logic.py             # Core game mechanics
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .env                     # Environment variables (create this)
├── setup.py                 # Installation script
├── README.md                # This file
└── cogs/                    # Command modules
    ├── __init__.py
    ├── match_management.py   # Match creation, joining, deletion
    ├── team_setup.py        # Team and role management
    ├── game_flow.py         # Game flow and turn management
    ├── commentary.py        # Dynamic game commentary
    └── player_stats.py      # Player profiles and statistics
```

## ⚙️ Configuration

The bot uses environment variables for configuration. Edit your `.env` file:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here
COMMAND_PREFIX=H

# Game Settings
MAX_PLAYERS_PER_MATCH=10
MATCH_TIMEOUT_MINUTES=10
TURN_TIMEOUT_SECONDS=15
```

## 🎮 Game Mechanics

### Player Roles
- **ST (Striker)** - Primary attackers, good at scoring
- **MF (Midfielder)** - Versatile players, good at passing
- **DEF (Defender)** - Defensive specialists, good at blocking
- **GK (Goalkeeper)** - Goal protection, specialized saves

### Action System
Players choose actions from ranges (1-6 depending on situation):
- **1-3**: Conservative to Aggressive general actions
- **4-6**: Special situations (corner kicks, long shots)

### Game Flow
1. **Match Creation** - Host creates match with unique ID
2. **Player Joining** - Players join using match ID
3. **Team Setup** - Random shuffle or manual team assignment
4. **Role Assignment** - Assign positions to players
5. **Match Start** - Coin toss determines first action
6. **Turn-based Gameplay** - Players receive DMs for actions
7. **Commentary** - Real-time match updates
8. **Match End** - Statistics and results

## 🔧 Error Handling

The bot includes comprehensive error handling:
- **Validation Errors** - Invalid inputs and parameters
- **Match Errors** - Match-specific issues (expired, not found, etc.)
- **Player Errors** - Player-related problems
- **Discord Errors** - API and permission issues
- **Logging** - Detailed logs saved to `hand_hockey_bot.log`

## 🚀 Advanced Features

### Match Expiry
- Matches automatically expire after 10 minutes (configurable)
- Regular cleanup prevents memory issues
- Expired matches are removed from active list

### DM System
- Players receive private messages for turn actions
- Timeout warnings sent via DM
- Graceful handling of DM failures

### Logging
- Comprehensive command usage logging
- Error tracking and debugging
- Performance monitoring

## 🧪 Testing Commands

Use these commands to test bot functionality:

```bash
# Test basic functionality
Hhelp
Hcreate_match
Hlist_matches

# Test commentary system
Hdemo_commentary
Hrandom_event

# Test player features
Hprofile
Hscorecard
```

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Check bot token in `.env` file
- Verify bot has necessary permissions
- Check bot is online in Discord

**Import errors:**
- Run `python setup.py` to install dependencies
- Ensure all files are in correct directories
- Check Python version (3.8+ required)

**Command errors:**
- Check command prefix is correct (`H` by default)
- Verify bot has message permissions
- Check logs in `hand_hockey_bot.log`

### Debug Mode
Enable debug logging by editing `utils.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Development

### Adding New Commands
1. Create new command in appropriate cog file
2. Add error handling with `try/except`
3. Use utility functions for consistent formatting
4. Update help command if needed

### Adding New Features
1. Plan the feature in `game_logic.py` if game-related
2. Implement in appropriate cog
3. Add configuration options in `config.py`
4. Update documentation

## 📄 License

This project is provided as-is for educational and entertainment purposes.

## 🤝 Contributing

Feel free to submit issues, feature requests, or improvements!

---

**Made with ❤️ for Discord gaming communities**
