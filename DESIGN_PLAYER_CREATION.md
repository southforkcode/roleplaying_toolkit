# Issue #20: Player Character Creation - Design & Implementation Plan

## Overview
Add functionality to create and manage player characters (PCs) within a game. Players will have ability scores that can be set via dice rolls or direct assignment. Each game will have its own set of players, isolated in the game's folder.

## Requirements Analysis

### User Stories
1. **Create Player**: User can initiate player creation with `create_player` command
2. **Get Player Name**: System prompts for player name (must be unique within game)
3. **Roll Ability Scores**: User can roll dice in player creation context
4. **Set Ability Stats**: User can assign stat values (e.g., `set strength to 14`)
5. **View Player Status**: User can see current player creation status
6. **Save Player**: User can save player and return to game context
7. **Exit Without Saving**: User can exit with `exit` or `quit` without saving
8. **Game Status**: Game `status` shows all PCs with abbreviated stats
9. **Player Persistence**: Players saved with game in `saves/game_<name>/players/`

### Key Constraints
- (a) No duplicate player names per game
- (b) Players stored per-game in isolated folders
- (c) Can exit without saving changes
- (d) Help command available in player creation context
- (e) Player data integrated into game context after save
- (f) Flexible stat assignment
- (g) Roll command works in player creation context
- (h) Root status shows all players with abbreviated stats

## Architecture Design

### 1. Player Data Model
```python
class Player:
    """Represents a player character with stats."""
    - name: str
    - stats: Dict[str, int]  # ability scores
    - race: Optional[str]
    - class_type: Optional[str]
    - to_dict() -> dict
    - from_dict(data) -> Player
```

### 2. PlayerManager Class
**File**: `lib/player_manager.py`

Responsibilities:
- Create new players
- Load/save players from YAML
- Validate player names (uniqueness)
- Get all players for a game
- Update player stats

Methods:
```python
class PlayerManager:
    def __init__(self, game_path: str)
    def create_player(name: str) -> Player
    def save_player(player: Player) -> bool
    def load_players() -> List[Player]
    def get_player(name: str) -> Optional[Player]
    def player_exists(name: str) -> bool
    def get_all_players() -> List[Player]
    def delete_player(name: str) -> bool
    def update_player(player: Player) -> bool
```

### 3. Player Creation Context Handler
**File**: `lib/player_context.py`

A separate context that:
- Intercepts commands differently than game context
- Available commands: `roll`, `set`, `status`, `save`, `exit`, `quit`, `help`
- Returns to game context on `save` or `exit`
- Manages temporary player object during creation

Methods:
```python
class PlayerCreationHandler:
    def __init__(command_handler, player_manager, game_name)
    def handle_command(command: Command) -> Result
    def exit_context() -> bool  # True if saved, False if discarded
```

### 4. Command Handler Integration
**File**: `lib/custom_commands.py`

New command:
- `create_player`: Initiates player creation, switches context

Modified commands:
- `status`: If in game context, shows players in abbreviated format

### 5. Ability Score System
**File**: `lib/ability_scores.py`

Standard D&D ability scores:
- Strength (STR)
- Dexterity (DEX)
- Constitution (CON)
- Intelligence (INT)
- Wisdom (WIS)
- Charisma (CHA)

Ranges: 3-20 (typical D&D)
```python
ABILITIES = {
    "strength": {"min": 3, "max": 20, "short": "str"},
    "dexterity": {"min": 3, "max": 20, "short": "dex"},
    "constitution": {"min": 3, "max": 20, "short": "con"},
    "intelligence": {"min": 3, "max": 20, "short": "int"},
    "wisdom": {"min": 3, "max": 20, "short": "wis"},
    "charisma": {"min": 3, "max": 20, "short": "cha"},
}
```

## File Structure
```
saves/
└── game_<name>/
    ├── game.yaml
    ├── journal.yaml
    ├── state.yaml
    ├── saves/
    └── players/              (NEW)
        ├── Jackbar.yaml
        ├── Elara.yaml
        └── ...
```

## Data Format (players/<name>.yaml)
```yaml
name: Jackbar
race: null
class: null
stats:
  strength: 14
  dexterity: 12
  constitution: 13
  intelligence: 10
  wisdom: 11
  charisma: 9
created_at: 2025-11-05T10:30:00
updated_at: 2025-11-05T10:30:00
```

## User Interaction Flow

### Creating a Player
```
> create_player
Starting new player creation...
Name?
>> Jackbar
Created player Jackbar.
>> set strength to 14
Set Jackbar strength to 14.
>> roll 4d6
Rolled 4d6: [4, 5, 1, 5] = 15
>> set dexterity to 15
Set Jackbar dexterity to 15.
>> status
Jackbar (no race) (no class)
strength: 14
dexterity: 15
constitution: 0
intelligence: 0
wisdom: 0
charisma: 0
>> save
Saved player Jackbar.
> status
PCs:
Jackbar -/- str:14 dex:15 con:0 int:0 wis:0 cha:0
```

### Game Status with Players
```
> status
Current Game: DndCampaign
Players (2):
  1. Jackbar -/- str:14 dex:15
  2. Elara ranger str:12 dex:16
Active Journeys: 0
```

## Testing Strategy (TDD)

### 1. Player Model Tests
- Create player with name
- Serialize/deserialize to/from dict
- Validate ability scores

### 2. PlayerManager Tests
- Create player with unique name
- Prevent duplicate names
- Save/load players
- Update player stats
- Delete player
- Get all players

### 3. Player Creation Context Tests
- Start creation context
- Handle name command
- Handle set stat commands
- Handle roll command
- Handle status command
- Save player and return to game context
- Exit without saving

### 4. Integration Tests
- Create multiple players
- Each player isolated to game
- Status shows all players
- Can switch between games and see different players

## Implementation Phases

### Phase 1: Data Model & Persistence
- [x] Create `lib/ability_scores.py` with ability definitions
- [x] Create `lib/player.py` with Player class
- [x] Create `lib/player_manager.py` with persistence logic
- [x] Write comprehensive tests for both

### Phase 2: Context Handler
- [x] Create `lib/player_context.py` with context handler
- [x] Implement commands: set, roll, status, save, exit, help
- [x] Write tests for context switching
- [x] Write tests for command handling

### Phase 3: Integration
- [x] Add `create_player` command to main handler
- [x] Integrate PlayerManager with game context
- [x] Update game `status` to show players
- [x] Write integration tests

### Phase 4: Polish
- [x] Run linting and fix style
- [x] Update documentation
- [x] Verify all tests pass

## Refactoring Opportunities

1. **Context Management**: Extract a generic context switching mechanism for reuse
2. **Command Parsing**: Enhance to support `set <stat> to <value>` syntax
3. **Game Manager Integration**: Add player-related methods
4. **Status Formatting**: Create utilities for consistent formatting

## Success Criteria

✅ All tests passing (TDD approach)
✅ Player creation workflow working
✅ Players persist to YAML files
✅ Each game has isolated players
✅ No duplicate player names allowed
✅ Context switching works smoothly
✅ Code passes linting
✅ Documentation updated

## Branch Strategy
- Feature branch: `feature/player-creation`
- No merge until all criteria met
- Incremental commits with clear messages
