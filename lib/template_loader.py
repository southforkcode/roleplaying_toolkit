"""Template loading and management system."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from lib.template import Template


class TemplateLoader:
    """Loads and manages player creation templates."""

    def __init__(self, templates_dir: str):
        """Initialize template loader.

        Args:
            templates_dir: Directory containing template YAML files
        """
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Template] = {}
        self._load_all_templates()

    def _load_all_templates(self) -> None:
        """Load all templates from templates directory."""
        self.templates = {}

        if not self.templates_dir.exists():
            return

        # Look for YAML files in the templates directory
        for yaml_file in self.templates_dir.glob("*.yaml"):
            template_name = yaml_file.stem
            try:
                template = self._load_template_file(yaml_file)
                if template:
                    self.templates[template_name] = template
            except Exception as e:
                # Log error but continue loading other templates
                print(f"Warning: Failed to load template '{template_name}': {e}")

    def _load_template_file(self, file_path: Path) -> Optional[Template]:
        """Load a single template file.

        Args:
            file_path: Path to YAML template file

        Returns:
            Template instance or None if failed

        Raises:
            ValueError: If template structure is invalid
            yaml.YAMLError: If YAML parsing fails
        """
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"Template file {file_path} is empty")

        template = Template.from_dict(data)

        # Validate template
        is_valid, error_msg = template.validate()
        if not is_valid:
            raise ValueError(f"Template validation failed: {error_msg}")

        return template

    def load_template(self, name: str) -> Optional[Template]:
        """Load a template by name.

        Args:
            name: Template name (without .yaml extension)

        Returns:
            Template instance or None if not found
        """
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """List available template names.

        Returns:
            Sorted list of template names
        """
        return sorted(self.templates.keys())

    def get_template_info(self, name: str) -> Optional[Dict[str, str]]:
        """Get information about a template.

        Args:
            name: Template name

        Returns:
            Dictionary with template info or None if not found
        """
        template = self.load_template(name)
        if not template:
            return None

        return {
            "name": template.name,
            "version": template.version,
            "description": template.description,
            "steps": str(len(template.steps)),
        }

    def reload_templates(self) -> Tuple[bool, str]:
        """Reload all templates from disk.

        Returns:
            Tuple of (success, message)
        """
        try:
            self._load_all_templates()
            count = len(self.templates)
            return True, f"Reloaded {count} templates"
        except Exception as e:
            return False, f"Failed to reload templates: {e}"

    def validate_template_file(
        self, file_path: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate a template file without loading it.

        Args:
            file_path: Path to template YAML file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            if not data:
                return False, "Template file is empty"

            template = Template.from_dict(data)
            return template.validate()

        except yaml.YAMLError as e:
            return False, f"YAML parse error: {e}"
        except Exception as e:
            return False, str(e)

    def template_count(self) -> int:
        """Get number of loaded templates.

        Returns:
            Number of templates
        """
        return len(self.templates)
