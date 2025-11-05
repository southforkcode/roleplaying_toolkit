"""Journal management system for tracking PC actions and game events."""

import os
from datetime import datetime
from pathlib import Path
import yaml


class JournalManager:
    """Manages persistent journal of game events with YAML storage."""

    def __init__(self, journal_path: str = "saves/journal.yaml"):
        """Initialize the journal manager.

        Args:
            journal_path: Path to the journal YAML file
        """
        self.journal_path = journal_path
        self._ensure_directory_exists()
        self._load_journal()

    def _ensure_directory_exists(self):
        """Ensure the saves directory exists."""
        Path(self.journal_path).parent.mkdir(parents=True, exist_ok=True)

    def _load_journal(self):
        """Load journal from YAML file or create if doesn't exist."""
        if os.path.exists(self.journal_path):
            try:
                with open(self.journal_path, "r") as f:
                    data = yaml.safe_load(f)
                    self.entries = data.get("entries", []) if data else []
            except (yaml.YAMLError, IOError):
                self.entries = []
        else:
            self.entries = []

    def _save_journal(self):
        """Save journal to YAML file."""
        data = {"entries": self.entries}
        with open(self.journal_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add_entry(
        self, event_type: str, description: str, metadata: dict = None
    ) -> None:
        """Add a new entry to the journal.

        Args:
            event_type: Type of event (e.g., 'journey_start', 'progress')
            description: Human-readable description of the event
            metadata: Optional dictionary with additional event data
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "description": description,
            "metadata": metadata or {},
        }
        self.entries.append(entry)
        self._save_journal()

    def get_entries(self, limit: int = 10) -> list:
        """Get the last N entries from the journal.

        Args:
            limit: Number of entries to return (default 10)

        Returns:
            List of entries, most recent last
        """
        return self.entries[-limit:] if self.entries else []

    def get_all_entries(self) -> list:
        """Get all entries from the journal.

        Returns:
            List of all entries
        """
        return self.entries.copy()

    def clear_journal(self) -> None:
        """Clear all entries from the journal.

        WARNING: This action is not reversible.
        """
        self.entries = []
        self._save_journal()

    def get_entry_count(self) -> int:
        """Get the total number of entries in the journal.

        Returns:
            Total entry count
        """
        return len(self.entries)
