"""State management system for saving and loading game state."""

import yaml
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from lib.journey_system import JourneyManager


class StateManager:
    """Manages saving and loading of game state to/from YAML files."""

    def __init__(self, saves_directory: str = "saves"):
        """Initialize the state manager.

        Args:
            saves_directory: Directory to store save files (default: "saves")
        """
        self.saves_directory = Path(saves_directory)
        self.saves_directory.mkdir(exist_ok=True)

    def save_state(
        self, journey_manager: JourneyManager, save_name: str = "quicksave"
    ) -> str:
        """Save current game state to a YAML file.

        Args:
            journey_manager: The journey manager containing current state
            save_name: Name of the save file (without extension)

        Returns:
            Success message with save location

        Raises:
            ValueError: If save_name contains invalid characters
            OSError: If unable to write to save file
        """
        # Validate save name
        if not save_name or not save_name.strip():
            raise ValueError("Save name cannot be empty")

        # Remove invalid filename characters
        safe_name = "".join(
            c for c in save_name if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        if not safe_name:
            raise ValueError("Save name contains only invalid characters")

        # Create state dictionary
        state = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "journey_manager": journey_manager.to_dict(),
        }

        # Write to YAML file
        save_path = self.saves_directory / f"{safe_name}.yaml"
        try:
            with open(save_path, "w") as f:
                yaml.dump(state, f, default_flow_style=False, sort_keys=False)
            return f"Game saved as '{safe_name}' at {save_path}"
        except OSError as e:
            raise OSError(f"Failed to save game state: {e}")

    def load_state(self, save_name: str) -> JourneyManager:
        """Load game state from a YAML file.

        Args:
            save_name: Name of the save file (without extension)

        Returns:
            JourneyManager with loaded state

        Raises:
            FileNotFoundError: If save file doesn't exist
            ValueError: If save file is corrupted or incompatible
            OSError: If unable to read save file
        """
        if not save_name or not save_name.strip():
            raise ValueError("Save name cannot be empty")

        # Remove invalid filename characters (same as save)
        safe_name = "".join(
            c for c in save_name if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        if not safe_name:
            raise ValueError("Save name contains only invalid characters")

        save_path = self.saves_directory / f"{safe_name}.yaml"

        if not save_path.exists():
            raise FileNotFoundError(f"Save file '{safe_name}' not found")

        try:
            with open(save_path, "r") as f:
                state = yaml.safe_load(f)
        except OSError as e:
            raise OSError(f"Failed to read save file: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Corrupted save file: {e}")

        # Validate state structure
        if not isinstance(state, dict):
            raise ValueError("Invalid save file format")

        if "version" not in state:
            raise ValueError("Save file missing version information")

        if "journey_manager" not in state:
            raise ValueError("Save file missing journey manager data")

        # Check version compatibility
        version = state["version"]
        if version != "1.0":
            raise ValueError(f"Incompatible save file version: {version}")

        # Load journey manager
        try:
            journey_manager = JourneyManager.from_dict(state["journey_manager"])
            return journey_manager
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Failed to load journey data: {e}")

    def list_saves(self) -> list[str]:
        """List all available save files.

        Returns:
            List of save names (without .yaml extension)
        """
        saves = []
        for save_file in self.saves_directory.glob("*.yaml"):
            saves.append(save_file.stem)
        return sorted(saves)

    def delete_save(self, save_name: str) -> str:
        """Delete a save file.

        Args:
            save_name: Name of the save file to delete

        Returns:
            Success message

        Raises:
            FileNotFoundError: If save file doesn't exist
            OSError: If unable to delete file
        """
        if not save_name or not save_name.strip():
            raise ValueError("Save name cannot be empty")

        safe_name = "".join(
            c for c in save_name if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        if not safe_name:
            raise ValueError("Save name contains only invalid characters")

        save_path = self.saves_directory / f"{safe_name}.yaml"

        if not save_path.exists():
            raise FileNotFoundError(f"Save file '{safe_name}' not found")

        try:
            save_path.unlink()
            return f"Deleted save '{safe_name}'"
        except OSError as e:
            raise OSError(f"Failed to delete save file: {e}")

    def get_save_info(self, save_name: str) -> Dict[str, Any]:
        """Get information about a save file.

        Args:
            save_name: Name of the save file

        Returns:
            Dictionary with save information (version, timestamp, etc.)

        Raises:
            FileNotFoundError: If save file doesn't exist
            ValueError: If save file is corrupted
        """
        if not save_name or not save_name.strip():
            raise ValueError("Save name cannot be empty")

        safe_name = "".join(
            c for c in save_name if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        save_path = self.saves_directory / f"{safe_name}.yaml"

        if not save_path.exists():
            raise FileNotFoundError(f"Save file '{safe_name}' not found")

        try:
            with open(save_path, "r") as f:
                state = yaml.safe_load(f)

            # Extract basic info
            info = {
                "name": safe_name,
                "version": state.get("version", "unknown"),
                "timestamp": state.get("timestamp", "unknown"),
                "file_size": save_path.stat().st_size,
            }

            # Add journey count if available
            journey_data = state.get("journey_manager", {})
            journeys = journey_data.get("journeys", [])
            info["journey_count"] = len(journeys)

            return info

        except (OSError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to read save file info: {e}")
