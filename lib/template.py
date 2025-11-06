"""Template system for player character creation workflows."""

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ValidationRules:
    """Validation rules for a template step."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None
    pattern: Optional[str] = None
    choices: Optional[List[str]] = None
    parse_rolls: bool = False

    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate a value against these rules.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Handle string validation
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                return False, f"Minimum length is {self.min_length}"
            if self.max_length is not None and len(value) > self.max_length:
                return False, f"Maximum length is {self.max_length}"
            if self.choices is not None and value not in self.choices:
                return False, f"Must be one of: {', '.join(self.choices)}"
            return True, None

        # Handle numeric validation
        if isinstance(value, (int, float)):
            if self.min is not None and value < self.min:
                return False, f"Minimum value is {self.min}"
            if self.max is not None and value > self.max:
                return False, f"Maximum value is {self.max}"
            return True, None

        return True, None


@dataclass
class TemplateStep:
    """Represents a single step in a player creation template."""

    id: str
    prompt: str
    type: str  # text, ability, choice, confirmation, review
    field: Optional[str] = None  # Player field to populate (None for meta-steps)
    help: Optional[str] = None
    macros_enabled: bool = False
    validation: ValidationRules = dataclass_field(default_factory=ValidationRules)
    choices: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateStep":
        """Create TemplateStep from dictionary.

        Args:
            data: Dictionary with step definition

        Returns:
            TemplateStep instance
        """
        validation_data = data.get("validation", {})
        validation = ValidationRules(
            min_length=validation_data.get("min_length"),
            max_length=validation_data.get("max_length"),
            min=validation_data.get("min"),
            max=validation_data.get("max"),
            pattern=validation_data.get("pattern"),
            choices=validation_data.get("choices"),
            parse_rolls=validation_data.get("parse_rolls", False),
        )

        return cls(
            id=data.get("id", ""),
            prompt=data.get("prompt", ""),
            type=data.get("type", "text"),
            field=data.get("field"),
            help=data.get("help"),
            macros_enabled=data.get("macros_enabled", False),
            validation=validation,
            choices=data.get("choices"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of step
        """
        return {
            "id": self.id,
            "prompt": self.prompt,
            "type": self.type,
            "field": self.field,
            "help": self.help,
            "macros_enabled": self.macros_enabled,
            "validation": {
                "min_length": self.validation.min_length,
                "max_length": self.validation.max_length,
                "min": self.validation.min,
                "max": self.validation.max,
                "pattern": self.validation.pattern,
                "choices": self.validation.choices,
                "parse_rolls": self.validation.parse_rolls,
            },
            "choices": self.choices,
        }


@dataclass
class Template:
    """Represents a complete player creation template."""

    name: str
    version: str
    description: str
    steps: List[TemplateStep]
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Create Template from dictionary.

        Args:
            data: Dictionary with template definition

        Returns:
            Template instance

        Raises:
            ValueError: If template structure is invalid
        """
        if "name" not in data:
            raise ValueError("Template must have 'name' field")
        if "version" not in data:
            raise ValueError("Template must have 'version' field")
        if "steps" not in data or not data["steps"]:
            raise ValueError("Template must have at least one step")

        steps = [TemplateStep.from_dict(step_data) for step_data in data["steps"]]

        # Validate step IDs are unique
        step_ids = [step.id for step in steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Template steps must have unique IDs")

        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            steps=steps,
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of template
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
        }

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate template structure.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.name:
            return False, "Template name cannot be empty"
        if not self.version:
            return False, "Template version cannot be empty"
        if not self.steps:
            return False, "Template must have at least one step"

        # Validate each step
        for step in self.steps:
            if not step.id:
                return False, "All steps must have unique IDs"
            if not step.prompt:
                return False, f"Step '{step.id}' must have a prompt"
            if step.type not in ["text", "ability", "choice", "confirmation", "review"]:
                return False, f"Step '{step.id}' has invalid type '{step.type}'"

        return True, None

    def get_step(self, index: int) -> Optional[TemplateStep]:
        """Get step by index.

        Args:
            index: Step index

        Returns:
            TemplateStep or None if index out of bounds
        """
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None

    def get_step_by_id(self, step_id: str) -> Optional[TemplateStep]:
        """Get step by ID.

        Args:
            step_id: Step ID

        Returns:
            TemplateStep or None if not found
        """
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def step_count(self) -> int:
        """Get total number of steps.

        Returns:
            Number of steps
        """
        return len(self.steps)
