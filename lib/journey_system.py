"""Journey system for tracking long trips and quests."""

from typing import List, Optional, Dict, Any


class Journey:
    """Represents a single journey with name, steps, difficulty, and progress."""

    def __init__(
        self, name: str, total_steps: int, difficulty: int, current_step: int = 0
    ):
        """Initialize a journey.

        Args:
            name: Journey name/description
            total_steps: Total number of steps to complete the journey
            difficulty: Difficulty level of the journey (0 or positive integer)
            current_step: Current progress (default 0)
        """
        if not name or not name.strip():
            raise ValueError("Journey name cannot be empty")
        if total_steps <= 0:
            raise ValueError("Total steps must be positive")
        if difficulty < 0:
            raise ValueError("Difficulty must be 0 or positive")
        if current_step < 0:
            raise ValueError("Current step cannot be negative")
        if current_step > total_steps:
            raise ValueError("Current step cannot exceed total steps")

        self.name = name.strip()
        self.total_steps = total_steps
        self.difficulty = difficulty
        self.progress = current_step

    def is_completed(self) -> bool:
        """Check if the journey is complete."""
        return self.progress >= self.total_steps

    def remaining_steps(self) -> int:
        """Get the number of remaining steps."""
        return max(0, self.total_steps - self.progress)

    def progress_percentage(self) -> float:
        """Get progress as a percentage."""
        return (self.progress / self.total_steps) * 100

    def make_progress(self, steps: int = 1) -> str:
        """Advance the journey by the specified number of steps.

        Args:
            steps: Number of steps to advance (default 1)

        Returns:
            String describing the progress made
        """
        if steps <= 0:
            raise ValueError("Progress must be positive")

        old_progress = self.progress
        self.progress = min(self.progress + steps, self.total_steps)

        if self.is_completed() and old_progress < self.total_steps:
            return (
                f"Journey '{self.name}' completed! ({self.progress}/{self.total_steps})"
            )
        else:
            return f"Progress on '{self.name}': {self.progress}/{self.total_steps}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert journey to dictionary for serialization."""
        return {
            "name": self.name,
            "total_steps": self.total_steps,
            "difficulty": self.difficulty,
            "progress": self.progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Journey":
        """Create journey from dictionary."""
        return cls(
            name=data["name"],
            total_steps=data["total_steps"],
            difficulty=data["difficulty"],
            current_step=data.get("progress", data.get("current_step", 0)),
        )

    def __str__(self) -> str:
        """String representation of the journey."""
        return f'"{self.name}" ({self.progress}/{self.total_steps} steps, difficulty {self.difficulty})'

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Journey(name='{self.name}', progress={self.progress}, total_steps={self.total_steps}, difficulty={self.difficulty})"


class JourneyManager:
    """Manages a stack of journeys with current journey tracking."""

    def __init__(self):
        """Initialize the journey manager."""
        self._journeys: List[Journey] = []

    @property
    def current_journey(self) -> Optional[Journey]:
        """Get the current (top of stack) journey."""
        return self._journeys[-1] if self._journeys else None

    @property
    def journey_count(self) -> int:
        """Get the total number of journeys."""
        return len(self._journeys)

    def has_active_journeys(self) -> bool:
        """Check if there are any active journeys."""
        return len(self._journeys) > 0

    def get_all_journeys(self) -> List[Journey]:
        """Get all journeys (current first, then deferred in reverse order)."""
        return list(reversed(self._journeys))

    def start_journey(self, name: str, total_steps: int, difficulty: int) -> Journey:
        """Start a new journey.

        Args:
            name: Journey name/description
            total_steps: Total number of steps
            difficulty: Difficulty level (0 or positive integer)

        Returns:
            The newly started journey
        """
        # Check for duplicate names
        for journey in self._journeys:
            if journey.name == name:
                raise ValueError(f"Journey with name '{name}' already exists")

        journey = Journey(name, total_steps, difficulty)
        self._journeys.append(journey)
        return journey

    def make_progress(self, steps: int = 1) -> str:
        """Progress the current journey.

        Args:
            steps: Number of steps to advance

        Returns:
            Message about the progress
        """
        if not self.current_journey:
            raise ValueError("No active journeys")

        journey = self.current_journey
        was_complete_before = journey.is_completed()
        result = journey.make_progress(steps)

        if journey.is_completed() and not was_complete_before:
            # Journey just completed, remove it from stack
            self._journeys.pop()

        return result

    def stop_current_journey(self) -> Journey:
        """Stop and remove the current journey.

        Returns:
            The stopped journey
        """
        if not self._journeys:
            raise ValueError("No active journeys")
        return self._journeys.pop()

    def stop_all_journeys(self) -> List[Journey]:
        """Stop and remove all journeys.

        Returns:
            List of all stopped journeys
        """
        stopped = list(reversed(self._journeys))
        self._journeys.clear()
        return stopped

    def stop_journey_by_name(self, name: str) -> Optional[Journey]:
        """Stop a specific journey by name.

        Args:
            name: Name of the journey to stop

        Returns:
            The stopped journey, or None if not found
        """
        name = name.strip()
        for i, journey in enumerate(self._journeys):
            if journey.name.lower() == name.lower():
                return self._journeys.pop(i)
        return None

    def get_status_summary(self) -> str:
        """Get a formatted status summary of all journeys."""
        if not self._journeys:
            return "No journeys in progress."

        lines = [f"Journeys in progress ({len(self._journeys)}):"]
        for i, journey in enumerate(reversed(self._journeys)):
            is_current = i == 0
            status_marker = "➤ " if is_current else "  "
            progress_bar = self._create_progress_bar(journey)
            lines.append(
                f"{status_marker}{journey.name}: {journey.progress}/{journey.total_steps} "
                f"steps {progress_bar} (difficulty {journey.difficulty})"
            )

        return "\n".join(lines)

    def _create_progress_bar(self, journey: Journey, width: int = 10) -> str:
        """Create a visual progress bar for a journey."""
        if journey.total_steps == 0:
            return "[##########]"

        filled = int((journey.progress / journey.total_steps) * width)
        empty = width - filled
        return f"[{'#' * filled}{'.' * empty}]"

    def to_dict(self) -> Dict[str, Any]:
        """Convert journey manager to dictionary for serialization."""
        return {"journeys": [journey.to_dict() for journey in reversed(self._journeys)]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JourneyManager":
        """Create journey manager from dictionary."""
        manager = cls()
        journey_list = data.get("journeys", [])
        # Reverse the list so current journey ends up on top of stack
        for journey_data in reversed(journey_list):
            journey = Journey.from_dict(journey_data)
            manager._journeys.append(journey)
        return manager
