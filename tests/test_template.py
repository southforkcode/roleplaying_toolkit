"""Tests for template system."""

import pytest
import tempfile
from pathlib import Path

import yaml

from lib.template import Template, TemplateStep, ValidationRules
from lib.template_loader import TemplateLoader


class TestValidationRules:
    """Test validation rules."""

    def test_string_min_length(self):
        """Test minimum string length validation."""
        rules = ValidationRules(min_length=3)
        valid, msg = rules.validate("abc")
        assert valid is True

        valid, msg = rules.validate("ab")
        assert valid is False
        assert "Minimum length" in msg

    def test_string_max_length(self):
        """Test maximum string length validation."""
        rules = ValidationRules(max_length=5)
        valid, msg = rules.validate("abcde")
        assert valid is True

        valid, msg = rules.validate("abcdef")
        assert valid is False
        assert "Maximum length" in msg

    def test_numeric_min(self):
        """Test minimum numeric validation."""
        rules = ValidationRules(min=3)
        valid, msg = rules.validate(3)
        assert valid is True

        valid, msg = rules.validate(2)
        assert valid is False
        assert "Minimum value" in msg

    def test_numeric_max(self):
        """Test maximum numeric validation."""
        rules = ValidationRules(max=20)
        valid, msg = rules.validate(20)
        assert valid is True

        valid, msg = rules.validate(21)
        assert valid is False
        assert "Maximum value" in msg

    def test_choices(self):
        """Test choice validation."""
        rules = ValidationRules(choices=["red", "green", "blue"])
        valid, msg = rules.validate("red")
        assert valid is True

        valid, msg = rules.validate("yellow")
        assert valid is False
        assert "one of" in msg


class TestTemplateStep:
    """Test template step model."""

    def test_step_creation(self):
        """Test creating a template step."""
        step = TemplateStep(
            id="name",
            prompt="What is your name?",
            type="text",
            field="name",
        )
        assert step.id == "name"
        assert step.prompt == "What is your name?"
        assert step.type == "text"
        assert step.field == "name"

    def test_step_from_dict(self):
        """Test creating step from dictionary."""
        data = {
            "id": "strength",
            "prompt": "Set your Strength",
            "type": "ability",
            "field": "strength",
            "macros_enabled": True,
            "validation": {"min": 3, "max": 20},
        }
        step = TemplateStep.from_dict(data)
        assert step.id == "strength"
        assert step.type == "ability"
        assert step.macros_enabled is True
        assert step.validation.min == 3
        assert step.validation.max == 20

    def test_step_to_dict(self):
        """Test converting step to dictionary."""
        step = TemplateStep(
            id="name",
            prompt="What is your name?",
            type="text",
            field="name",
            macros_enabled=False,
        )
        data = step.to_dict()
        assert data["id"] == "name"
        assert data["prompt"] == "What is your name?"
        assert data["type"] == "text"
        assert data["field"] == "name"


class TestTemplate:
    """Test template model."""

    def test_template_creation(self):
        """Test creating a template."""
        step = TemplateStep(
            id="name", prompt="What is your name?", type="text", field="name"
        )
        template = Template(
            name="test_template",
            version="1.0",
            description="Test template",
            steps=[step],
        )
        assert template.name == "test_template"
        assert template.version == "1.0"
        assert len(template.steps) == 1

    def test_template_from_dict(self):
        """Test creating template from dictionary."""
        data = {
            "name": "D&D Test",
            "version": "1.0",
            "description": "Test template",
            "steps": [
                {
                    "id": "name",
                    "prompt": "Name?",
                    "type": "text",
                    "field": "name",
                },
                {
                    "id": "strength",
                    "prompt": "Strength?",
                    "type": "ability",
                    "field": "strength",
                    "validation": {"min": 3, "max": 20},
                },
            ],
        }
        template = Template.from_dict(data)
        assert template.name == "D&D Test"
        assert len(template.steps) == 2

    def test_template_from_dict_missing_name(self):
        """Test template validation - missing name."""
        data = {
            "version": "1.0",
            "steps": [{"id": "name", "prompt": "Name?", "type": "text"}],
        }
        with pytest.raises(ValueError, match="'name' field"):
            Template.from_dict(data)

    def test_template_from_dict_missing_version(self):
        """Test template validation - missing version."""
        data = {
            "name": "Test",
            "steps": [{"id": "name", "prompt": "Name?", "type": "text"}],
        }
        with pytest.raises(ValueError, match="'version' field"):
            Template.from_dict(data)

    def test_template_from_dict_no_steps(self):
        """Test template validation - no steps."""
        data = {"name": "Test", "version": "1.0", "steps": []}
        with pytest.raises(ValueError, match="at least one step"):
            Template.from_dict(data)

    def test_template_from_dict_duplicate_step_ids(self):
        """Test template validation - duplicate step IDs."""
        data = {
            "name": "Test",
            "version": "1.0",
            "steps": [
                {"id": "name", "prompt": "Name?", "type": "text"},
                {"id": "name", "prompt": "Name again?", "type": "text"},
            ],
        }
        with pytest.raises(ValueError, match="unique IDs"):
            Template.from_dict(data)

    def test_template_validate(self):
        """Test template validation."""
        data = {
            "name": "Valid Template",
            "version": "1.0",
            "steps": [{"id": "name", "prompt": "Name?", "type": "text"}],
        }
        template = Template.from_dict(data)
        is_valid, error = template.validate()
        assert is_valid is True
        assert error is None

    def test_template_validate_invalid_step_type(self):
        """Test template validation - invalid step type."""
        template = Template(
            name="Test",
            version="1.0",
            description="",
            steps=[
                TemplateStep(
                    id="test", prompt="Test?", type="invalid_type", field=None
                )
            ],
        )
        is_valid, error = template.validate()
        assert is_valid is False
        assert "invalid type" in error

    def test_get_step(self):
        """Test getting step by index."""
        step1 = TemplateStep(id="step1", prompt="First?", type="text")
        step2 = TemplateStep(id="step2", prompt="Second?", type="text")
        template = Template(
            name="Test",
            version="1.0",
            description="",
            steps=[step1, step2],
        )

        assert template.get_step(0) == step1
        assert template.get_step(1) == step2
        assert template.get_step(2) is None
        assert template.get_step(-1) is None

    def test_get_step_by_id(self):
        """Test getting step by ID."""
        step1 = TemplateStep(id="strength", prompt="Strength?", type="ability")
        step2 = TemplateStep(id="dexterity", prompt="Dexterity?", type="ability")
        template = Template(
            name="Test",
            version="1.0",
            description="",
            steps=[step1, step2],
        )

        assert template.get_step_by_id("strength") == step1
        assert template.get_step_by_id("dexterity") == step2
        assert template.get_step_by_id("unknown") is None

    def test_step_count(self):
        """Test step count."""
        template = Template(
            name="Test",
            version="1.0",
            description="",
            steps=[
                TemplateStep(id="step1", prompt="1?", type="text"),
                TemplateStep(id="step2", prompt="2?", type="text"),
            ],
        )
        assert template.step_count() == 2


class TestTemplateLoader:
    """Test template loader."""

    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary templates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_dir = Path(tmpdir) / "player"
            templates_dir.mkdir()
            yield templates_dir

    def test_loader_initialization_empty_dir(self, temp_templates_dir):
        """Test loader with empty directory."""
        loader = TemplateLoader(str(temp_templates_dir))
        assert loader.template_count() == 0
        assert loader.list_templates() == []

    def test_loader_load_single_template(self, temp_templates_dir):
        """Test loading a single template."""
        template_data = {
            "name": "Test Template",
            "version": "1.0",
            "description": "Test",
            "steps": [
                {
                    "id": "name",
                    "prompt": "Name?",
                    "type": "text",
                    "field": "name",
                }
            ],
        }

        template_file = temp_templates_dir / "test.yaml"
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        loader = TemplateLoader(str(temp_templates_dir))
        assert loader.template_count() == 1
        assert "test" in loader.list_templates()

        template = loader.load_template("test")
        assert template is not None
        assert template.name == "Test Template"

    def test_loader_load_multiple_templates(self, temp_templates_dir):
        """Test loading multiple templates."""
        for name in ["d20", "pathfinder", "custom"]:
            template_data = {
                "name": f"{name.upper()} Template",
                "version": "1.0",
                "description": f"{name} template",
                "steps": [
                    {
                        "id": "name",
                        "prompt": "Name?",
                        "type": "text",
                        "field": "name",
                    }
                ],
            }

            template_file = temp_templates_dir / f"{name}.yaml"
            with open(template_file, "w") as f:
                yaml.dump(template_data, f)

        loader = TemplateLoader(str(temp_templates_dir))
        assert loader.template_count() == 3
        templates = loader.list_templates()
        assert "d20" in templates
        assert "pathfinder" in templates
        assert "custom" in templates

    def test_loader_list_templates_sorted(self, temp_templates_dir):
        """Test that templates are listed in sorted order."""
        for name in ["zebra", "apple", "banana"]:
            template_data = {
                "name": name,
                "version": "1.0",
                "steps": [
                    {"id": "test", "prompt": "Test?", "type": "text"}
                ],
            }
            template_file = temp_templates_dir / f"{name}.yaml"
            with open(template_file, "w") as f:
                yaml.dump(template_data, f)

        loader = TemplateLoader(str(temp_templates_dir))
        templates = loader.list_templates()
        assert templates == ["apple", "banana", "zebra"]

    def test_loader_template_not_found(self, temp_templates_dir):
        """Test loading non-existent template."""
        loader = TemplateLoader(str(temp_templates_dir))
        template = loader.load_template("nonexistent")
        assert template is None

    def test_loader_get_template_info(self, temp_templates_dir):
        """Test getting template info."""
        template_data = {
            "name": "Test Template",
            "version": "2.5",
            "description": "A test template",
            "steps": [
                {"id": "step1", "prompt": "Step 1?", "type": "text"},
                {"id": "step2", "prompt": "Step 2?", "type": "text"},
            ],
        }

        template_file = temp_templates_dir / "test.yaml"
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        loader = TemplateLoader(str(temp_templates_dir))
        info = loader.get_template_info("test")

        assert info is not None
        assert info["name"] == "Test Template"
        assert info["version"] == "2.5"
        assert info["description"] == "A test template"
        assert info["steps"] == "2"

    def test_loader_reload_templates(self, temp_templates_dir):
        """Test reloading templates."""
        loader = TemplateLoader(str(temp_templates_dir))
        assert loader.template_count() == 0

        # Add a template file
        template_data = {
            "name": "New Template",
            "version": "1.0",
            "steps": [{"id": "test", "prompt": "Test?", "type": "text"}],
        }
        template_file = temp_templates_dir / "new.yaml"
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        # Reload should pick it up
        success, message = loader.reload_templates()
        assert success is True
        assert loader.template_count() == 1
        assert "1 templates" in message

    def test_loader_validate_template_file(self, temp_templates_dir):
        """Test validating a template file."""
        template_data = {
            "name": "Valid Template",
            "version": "1.0",
            "steps": [{"id": "test", "prompt": "Test?", "type": "text"}],
        }
        template_file = temp_templates_dir / "valid.yaml"
        with open(template_file, "w") as f:
            yaml.dump(template_data, f)

        loader = TemplateLoader(str(temp_templates_dir))
        is_valid, error = loader.validate_template_file(str(template_file))
        assert is_valid is True
        assert error is None

    def test_loader_validate_invalid_template_file(self, temp_templates_dir):
        """Test validating an invalid template file."""
        template_file = temp_templates_dir / "invalid.yaml"
        with open(template_file, "w") as f:
            f.write("name: Test\nversion: 1.0")  # Missing steps

        loader = TemplateLoader(str(temp_templates_dir))
        is_valid, error = loader.validate_template_file(str(template_file))
        assert is_valid is False
        assert error is not None

    def test_loader_nonexistent_directory(self):
        """Test loader with non-existent directory."""
        loader = TemplateLoader("/nonexistent/path/templates")
        assert loader.template_count() == 0
        assert loader.list_templates() == []
