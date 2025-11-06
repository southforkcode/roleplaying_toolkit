# Design: Player Creation Template System (Issue #21)

## Overview

Implement a YAML-based template system for player character creation. Templates define interactive Q&A workflows that guide users through character creation with support for both direct input and dice rolling macros.

## Problem Statement

Currently, player creation is hardcoded to the D&D 6-ability system. We need:
1. **Template-based workflows**: Different RPG systems (D&D, Pathfinder, etc.) have different character creation processes
2. **Interactive prompts**: Flexible Q&A session that adapts based on user input
3. **Dice integration**: Users should be able to roll dice to generate values during creation
4. **File-based API**: YAML templates act as a declarative interface to define character creation flows

## Design Goals

- ✅ Support custom player creation workflows via YAML templates
- ✅ Provide dice rolling macros (e.g., `@roll-top 3 4d6`)
- ✅ Display template-specific context in prompts/responses
- ✅ Seamlessly integrate with existing player persistence
- ✅ Maintain backwards compatibility with direct character creation

## Architecture

### 1. Template Structure (YAML Format)

**File Location**: `templates/player_creation/<template_name>.yaml`

**Example**: `templates/player_creation/d20_standard.yaml`

```yaml
name: "D&D 5e Standard Character Creation"
version: "1.0"
description: "Standard D&D 5e character creation with 6 ability scores"

steps:
  - id: name
    prompt: "What is your character's name?"
    type: text
    field: name
    validation:
      min_length: 1
      max_length: 50

  - id: strength
    prompt: "Assign your Strength score"
    type: ability
    field: strength
    help: "You can enter a number directly or use macros like @roll-top 3 4d6 to roll dice"
    macros_enabled: true
    validation:
      min: 3
      max: 20
      parse_rolls: true

  - id: dexterity
    prompt: "Assign your Dexterity score"
    type: ability
    field: dexterity
    macros_enabled: true
    validation:
      min: 3
      max: 20
      parse_rolls: true

  # ... similar for con, int, wis, cha

  - id: confirm
    prompt: "Review your character. Save? (yes/no)"
    type: confirmation
    field: null
    on_confirm: save
    on_reject: review
```

**Template Field Types**:
- `text`: Free-form text input
- `ability`: Numeric score for character abilities
- `choice`: Multiple choice selection
- `confirmation`: Yes/no confirmation
- `review`: Display summary without input

### 2. Core Components

#### 2.1 Template Loader (`lib/template_loader.py`)

**Responsibilities**:
- Load YAML template files from `templates/` directory
- Validate template structure (schema validation)
- Parse and compile templates into Template objects
- Cache loaded templates for performance

**Key Methods**:
```python
class TemplateLoader:
    def load_template(name: str) -> Template
    def list_available_templates() -> List[str]
    def validate_template(template_dict) -> bool
    def reload_templates()  # For development
```

#### 2.2 Template Model (`lib/template.py`)

**Responsibilities**:
- Represent a complete template with validation
- Provide step iteration and state management
- Support template versioning and metadata

**Key Methods**:
```python
class Template:
    name: str
    version: str
    steps: List[TemplateStep]
    
    def get_step(index: int) -> TemplateStep
    def get_step_by_id(id: str) -> TemplateStep
    def validate_answer(step_id: str, answer: str) -> Tuple[bool, str]

class TemplateStep:
    id: str
    prompt: str
    type: str
    field: Optional[str]  # Which player field to populate
    macros_enabled: bool
    validation: Dict[str, Any]
    help: Optional[str]
```

#### 2.3 Macro System (`lib/template_macros.py`)

**Macros Supported**:
- `@roll-top N <dice_notation>`: Roll dice, keep top N
  - Example: `@roll-top 3 4d6` (roll 4d6, keep highest 3)
- `@roll <dice_notation>`: Simple dice roll
  - Example: `@roll d20`, `@roll 2d6+3`
- `@sum [values]`: Sum numeric values
  - Example: `@sum 14 2` (returns 16)

**Key Methods**:
```python
class MacroProcessor:
    def process_macro(macro_str: str) -> Tuple[bool, str | int]
    def parse_macro(input_str: str) -> Optional[MacroDefinition]
    def validate_macro(macro_def: MacroDefinition) -> Tuple[bool, str]
```

**Macro Processing Flow**:
1. User input: `@roll-top 3 4d6`
2. Parser: Extract macro type, parameters
3. Executor: Roll 4d6, calculate sum of top 3
4. Return: Result value and message

#### 2.4 Template-based Player Creation Handler (`lib/template_player_context.py`)

**Responsibilities**:
- Manage interactive workflow using a specific template
- Delegate to macro processor for dice rolling
- Validate user input against step requirements
- Collect answers and populate player object
- Handle branching (e.g., review → edit → save flow)

**Key Methods**:
```python
class TemplatePlayerCreationHandler:
    def __init__(template: Template, game_manager, main_handler)
    def handle(input: str) -> str
    def get_current_step() -> TemplateStep
    def validate_and_advance(input: str) -> Tuple[bool, str]
    def save_player() -> Tuple[bool, str]
```

### 3. Integration Points

#### 3.1 Main Event Loop (`roleplaying_toolkit.py`)

When user invokes: `create_player <template_name>`

```python
# In custom_commands.py
def _create_player_command_with_template(command, game_manager, handler):
    """Handle: create_player [template_name]"""
    if no template specified:
        return player_creation_default()  # Existing behavior
    
    template = TemplateLoader.load_template(template_name)
    if not template:
        return error_response(f"Template '{template_name}' not found")
    
    player_handler = TemplatePlayerCreationHandler(
        template, game_manager, handler
    )
    
    return {
        "success": True,
        "message": player_handler.get_welcome_message(),
        "context": player_handler,
        "mode": "template_player_creation"
    }
```

#### 3.2 Context Display

**Prompt Format**:
```
create_player:<template_name> :: [Step prompt]
create_player:<template_name> >
```

**Response Format**:
```
create_player:<template_name> :: [Response message]
```

#### 3.3 Template Directory Structure

```
templates/
  player_creation/
    d20_standard.yaml      # D&D 5e standard
    d20_variant.yaml       # D&D 5e with variants
    pathfinder.yaml        # Pathfinder system
    custom_template.yaml   # User-defined template
```

### 4. Command Integration

#### 4.1 Enhanced create_player Command

```
Usage: create_player [template_name]

Examples:
  create_player                    # Use default D&D creation (existing)
  create_player d20_standard       # Use D&D 5e template
  create_player pathfinder         # Use Pathfinder template

Special Commands:
  help                    # Show template-specific help
  show                    # Show current step details
  back                    # Go to previous step (if allowed)
  cancel                  # Exit without saving
```

#### 4.2 Template Management Commands

```
list_templates          # Show available player creation templates
show_template <name>    # Display template structure/steps
create_template <name>  # Wizard to create custom template (future)
```

### 5. Error Handling & Validation

**Template Validation**:
- Schema validation against expected structure
- Required fields check (name, version, steps)
- Step ID uniqueness
- Field references validity

**User Input Validation**:
- Step-specific validation rules
- Type checking (text, numeric, choice)
- Range validation (min/max for scores)
- Macro validation and execution errors

**Error Messages**:
```
Invalid input: expected numeric value between 3-20
Usage: @roll-top N <dice_notation> (e.g., @roll-top 3 4d6)
Template 'unknown' not found. Available: d20_standard, pathfinder
```

### 6. Implementation Phases

**Phase 1: Core Infrastructure**
- [ ] Template model and loader
- [ ] Basic YAML template parser
- [ ] Template validation
- [ ] Template-based context handler (simple steps)

**Phase 2: Macro System**
- [ ] Macro parser and processor
- [ ] @roll, @roll-top macro implementations
- [ ] Macro error handling and validation
- [ ] Integration with context handler

**Phase 3: Command Integration**
- [ ] Enhance create_player command
- [ ] Context display with template name
- [ ] Integration tests

**Phase 4: Template Library & Polish**
- [ ] Create built-in templates (d20_standard, etc.)
- [ ] Documentation and examples
- [ ] Template management commands
- [ ] Performance optimization

### 7. Backwards Compatibility

- Existing `create_player` (no args) continues to work with default D&D workflow
- Default workflow can be represented as internal template (not requiring YAML file)
- No breaking changes to Player model or persistence

### 8. Testing Strategy

**Unit Tests**:
- Template loading and validation
- Macro parsing and execution
- Step validation and progression
- Input parsing and error handling

**Integration Tests**:
- Full template-based creation workflow
- Macro execution in context
- Player persistence after template creation
- Context display and transitions

**Test Coverage**:
- Happy path: Complete character creation with template
- Edge cases: Invalid input, macro errors, cancellation
- Backwards compatibility: Default creation still works

## Questions for User

1. **Template Location**: Should templates be:
   - Bundled with the project in `templates/` directory?
   - User-configurable via config file?
   - Both (built-in + user custom)?

2. **Macro Syntax**: The `@` prefix for macros - does this feel right, or prefer different syntax?

3. **Step Types**: Beyond `text`, `ability`, `choice`, `confirmation` - any other types needed?

4. **Branching Logic**: Should templates support conditional steps based on previous answers?

5. **Template Wizard**: Should we implement a command to interactively create templates, or just hand-written YAML?

## Success Criteria

- ✅ Load and validate YAML templates
- ✅ Execute interactive template-based workflows
- ✅ Process dice rolling macros
- ✅ Create and persist players from template workflows
- ✅ Maintain backwards compatibility
- ✅ Comprehensive test coverage (>90%)
- ✅ Clear error messages for users
- ✅ Documentation with examples

