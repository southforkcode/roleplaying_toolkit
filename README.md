# Roleplaying Toolkit

A command-line toolkit for roleplaying games with journey tracking, dice rolling, and save/load functionality.

## Features

- **Journey System**: Track long-term quests and adventures with progress monitoring
- **Dice Rolling**: Full D&D-style dice rolling with advantage/disadvantage support
- **Save/Load System**: Persistent game state with named save slots
- **Session Management**: Reset and manage game sessions safely
- **Interactive Interface**: User-friendly command-line interface

## Usage

Run the main application:

```bash
python roleplaying_toolkit.py
```

### Available Commands

#### Basic Commands

- `help` - Show available commands
- `quit` / `exit` - Exit the application
- `status` - Show current game status

#### Game Management

- `new <game_name>` - Create a new game or load an existing one
  - Example: `new dnd_friends_of_the_obelisk`
  - If creating a new game with unsaved changes, you'll be prompted for confirmation
- `list` - List all available games with session counts
- `select <game_name>` - Switch to a different game
  - Example: `select campaign_module_1`
- `session` - Display current game info and session status

#### Journey System

- `journey "name" <steps> <difficulty>` - Start a new journey
  - Example: `journey "Find the Lost Temple" 10 3`
- `progress [amount]` - Make progress on current journey (defaults to 1 step)
  - Example: `progress 2`
- `stop` - Complete and remove the current journey

#### Dice Rolling

- `roll <dice> [advantage|disadvantage]` - Roll dice with optional advantage/disadvantage
  - Basic: `roll d20`, `roll 2d6`
  - Advantage: `roll d20 advantage`, `roll 2d6 adv`, `roll d12 a`
  - Disadvantage: `roll d20 disadvantage`, `roll 3d6 disadv`, `roll d8 d`

#### Fate Checking

- `fate <option1>,<option2>[,<option3>...]` - Make a random decision between options
  - Rolls d100 to select one option with equal probability
  - Example: `fate safe,encounter` → select between two outcomes
  - Example: `fate success,partial,failure` → select between three outcomes

#### Journal System

- `journal [limit]` - View the last N journal entries (default 10)
  - Example: `journal` → shows last 10 entries
  - Example: `journal 20` → shows last 20 entries
  - Automatically logs journey starts, progress, and completions

#### Save/Load System

- `save [name]` - Save current game state (defaults to 'quicksave')
- `load <name>` - Load saved game state
- `saves` - List all available save files

## Feature Details

### Multi-Game System

Organize your games into separate named spaces, each with their own journeys, saves, and journal:

- **Multiple Games**: Create and manage multiple independent game campaigns
- **Game Switching**: Easily switch between different games without losing progress
- **Unsaved Confirmation**: Get prompted when switching games with unsaved changes
- **Game Metadata**: Track total sessions and modification dates for each game
- **Automatic Game Restoration**: The last played game is automatically restored on app startup

**Startup Behavior (Issue #16):**

The application automatically tracks the current game in `saves/current_game.yaml`:

1. **No saved games**: Application prompts you to create a new game
2. **Games exist, but no metadata**: Application prompts you to create a new game  
3. **Valid current_game.yaml exists**: Application restores the last played game
4. **Game deleted**: Application treats as case 2 (prompts for new game)

**Example Game Management Workflow:**

```text
> list
No games found. Create one with: new <game_name>

> new dnd_lost_temple
Game 'dnd_lost_temple' created. Ready to play!

> journey "Find the Entrance" 5 2
Started journey: 'Find the Entrance' (5 steps, 2 difficulty)

> new module_3_expanded
You might have unsaved changes to the current game. Continue? (yes/no)
> yes
Game 'module_3_expanded' created. Ready to play!

> list
Available games:
  1. dnd_lost_temple - 0 sessions
  2. module_3_expanded - 0 sessions (current)

> select dnd_lost_temple
Switched to game 'dnd_lost_temple'

> status
Current Status: ... (shows the state of dnd_lost_temple, not module_3_expanded)
```

**File Structure:**

Each game is stored in its own folder with metadata automatically tracked:

```yaml
saves/
  current_game.yaml           # Tracks current game and last access time
  game_dnd_lost_temple/
    game.yaml                 # Game metadata
    journal.yaml              # Game-specific journal entries
    state.yaml                # Game state and journey stack
  game_module_3_expanded/
    game.yaml
    journal.yaml
    state.yaml
```

### Journey Tracking Details

Track long-term quests and adventures with the journey system:

- **Stack-based Management**: Start multiple journeys, with the most recent being "current"
- **Progress Tracking**: Make incremental progress toward journey completion
- **Automatic Completion**: Journeys are removed when completed
- **Persistent State**: Journey progress is saved with your game state

**Example Journey Workflow:**

```text
> journey "Find the Lost Temple" 10 3
Started journey: 'Find the Lost Temple' (10 steps, 3 difficulty)

> progress 2
Progress on 'Find the Lost Temple': 2/10

> journey "Escort the Merchant" 5 1
Started journey: 'Escort the Merchant' (5 steps, 1 difficulty)

> status
Current Status:
  Health: 100/100
  Mana: 50/50
  Level: 1
  Location: Starting Town

Active Journeys:
  1. Escort the Merchant (0/5) - 1
  2. Find the Lost Temple (2/10) - 3
```

### Persistent State Management

Persistent game state with multiple save slots per game:

- **YAML Format**: Human-readable save files
- **Per-Game Saves**: Each game maintains its own save slots
- **Named Saves**: Create multiple save slots for different scenarios within a game
- **Full State Restoration**: Complete journey stack and progress preserved
- **Session Persistence**: Load games across application restarts

**Example Save/Load Usage:**

```text
> new dnd_campaign
Game 'dnd_campaign' created. Ready to play!

> journey "Battle the Dragon" 8 5
Started journey: 'Battle the Dragon' (8 steps, 5 difficulty)

> save before_boss
Game saved as 'before_boss'

> saves
Available saves:
  before_boss (1 journeys)
  quicksave (0 journeys)

> load before_boss
Game loaded from 'before_boss'
```

**File Organization:**

Each game stores its data in an isolated folder:

```text
saves/
  game_dnd_campaign/
    game.yaml           # Game metadata
    journal.yaml        # Session journal entries
    state.yaml          # Current game state
    before_boss.yaml    # Named save point
    quicksave.yaml      # Auto-save slot
  game_module_3/
    game.yaml
    journal.yaml
    ...
```

### Dice Rolling with Advantage/Disadvantage

D&D-style dice rolling with advantage and disadvantage mechanics:

**Advantage Rolling:**

- Roll two sets of dice and take the higher total
- Aliases: `advantage`, `adv`, `a`
- Single die: `roll d20 advantage` → `Rolled d20 (advantage): 18, 7 => 18`
- Multiple dice: `roll 3d6 adv` → `Rolled 3d6 (advantage): [1, 2, 3] = 6, [4, 5, 6] = 15 => 15`

**Disadvantage Rolling:**

- Roll two sets of dice and take the lower total  
- Aliases: `disadvantage`, `disadv`, `d`
- Single die: `roll d20 disadvantage` → `Rolled d20 (disadvantage): 7, 18 => 7`
- Multiple dice: `roll 2d6 d` → `Rolled 2d6 (disadvantage): [1, 2] = 3, [5, 6] = 11 => 3`

### On-the-Fly Decision Making with Fate

The fate system lets you make random decisions between multiple options, useful for:

- Determining random encounters while traveling
- Deciding NPC actions and reactions
- Creating narrative branching points
- Resolving uncertain outcomes

**How Fate Works:**

- Specify 2 or more options separated by commas
- Each option has equal probability of selection
- A d100 roll determines which option is selected
- All options and the final selection are clearly shown

**Example Usage:**

```text
> fate safe,encounter
Fate checked: safe (50%), encounter (50%) => d100 => 75 => encounter

> fate success,partial_success,failure
Fate checked: success (33%), partial_success (33%), failure (33%) => d100 => 42 => partial_success
```

### Session Documentation with Journal

The journal system automatically documents your actions throughout a session, creating a persistent record you can review at any time.

**Automatic Logging:**

Events are automatically logged when you:

- Start a journey (logs journey name, steps, difficulty)
- Make progress (logs amount of progress on current journey)
- Complete a journey (logs completion with final progress)

**Viewing Your Journal:**

- `journal` - View the last 10 entries
- `journal 20` - View the last 20 entries
- Each entry shows timestamp and what happened

**Example Journal Output:**

```text
> journal
Journal Entries:

1. [2025-11-05 14:30:22] Started journey: 'Find the Lost Temple'
2. [2025-11-05 14:31:15] Made 2 step(s) on 'Find the Lost Temple'
3. [2025-11-05 14:32:40] Made 1 step(s) on 'Find the Lost Temple'
4. [2025-11-05 14:35:00] Completed journey: 'Find the Lost Temple'
5. [2025-11-05 14:35:15] Started journey: 'Escort the Merchant'
```

**Persistent Recording:**

- Journal entries are saved in YAML format in `saves/journal.yaml`
- Entries are never lost - even after closing and reopening the application
- Future versions will support named sessions and advanced filtering

## Getting Started

1. **Installation**: Clone the repository and run the application

   ```bash
   git clone https://github.com/southforkcode/roleplaying_toolkit.git
   cd roleplaying_toolkit
   python roleplaying_toolkit.py
   ```

2. **First Steps**: Try these commands to get familiar with the system

   ```text
   > help
   > journey "My First Quest" 5 1
   > progress 2
   > status
   > save tutorial
   ```

3. **Advanced Usage**: Explore dice rolling and save management

   ```text
   > roll d20 advantage
   > saves
   > new
   ```

## Development

For developers interested in contributing or extending the toolkit, see [DEVELOPER.md](DEVELOPER.md) for comprehensive development guidelines, architecture details, and testing procedures.
