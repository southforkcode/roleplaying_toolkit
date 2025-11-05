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
- `new` - Reset session (requires double confirmation)

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

#### Save/Load System

- `save [name]` - Save current game state (defaults to 'quicksave')
- `load <name>` - Load saved game state
- `saves` - List all available save files

## Feature Details

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

Persistent game state with multiple save slots:

- **YAML Format**: Human-readable save files
- **Named Saves**: Create multiple save slots for different scenarios
- **Full State Restoration**: Complete journey stack and progress preserved
- **Session Persistence**: Load games across application restarts

**Example Save/Load Usage:**

```text
> save before_boss
Game saved as 'before_boss' at saves/before_boss.yaml

> saves
Available saves:
  before_boss - 2025-11-05 06:00:08 (2 journeys)
  quicksave - 2025-11-05 05:57:00 (0 journeys)

> load before_boss
Game loaded from 'before_boss'
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

### Session Management

Safe session reset with confirmation:

- **Double Confirmation**: Type `new` twice to reset all journeys
- **Cancellation**: Any other command after first `new` cancels the reset
- **State Preservation**: Accidentally typing `new` won't immediately clear your progress

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
