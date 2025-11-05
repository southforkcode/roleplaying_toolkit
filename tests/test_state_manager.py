"""Tests for the state management system."""

import pytest
import tempfile
import shutil
from pathlib import Path

from lib.state_manager import StateManager
from lib.journey_system import JourneyManager


class TestStateManager:
    """Test cases for StateManager class."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for each test
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_save_empty_journey_manager(self):
        """Test saving an empty journey manager."""
        journey_manager = JourneyManager()
        result = self.state_manager.save_state(journey_manager, "empty_test")

        assert "empty_test" in result
        assert Path(self.temp_dir, "empty_test.yaml").exists()

    def test_save_with_journeys(self):
        """Test saving a journey manager with active journeys."""
        journey_manager = JourneyManager()
        journey_manager.start_journey("Test Journey", 5, 2)
        journey_manager.make_progress(2)
        journey_manager.start_journey("Second Journey", 3, 1)

        result = self.state_manager.save_state(journey_manager, "with_journeys")

        assert "with_journeys" in result
        save_path = Path(self.temp_dir, "with_journeys.yaml")
        assert save_path.exists()

        # Verify file content is valid YAML
        import yaml

        with open(save_path, "r") as f:
            data = yaml.safe_load(f)

        assert "version" in data
        assert "timestamp" in data
        assert "journey_manager" in data
        assert len(data["journey_manager"]["journeys"]) == 2

    def test_save_default_name(self):
        """Test saving with default name."""
        journey_manager = JourneyManager()
        result = self.state_manager.save_state(journey_manager)

        assert "quicksave" in result
        assert Path(self.temp_dir, "quicksave.yaml").exists()

    def test_save_invalid_name(self):
        """Test saving with invalid names."""
        journey_manager = JourneyManager()

        # Empty name
        with pytest.raises(ValueError, match="Save name cannot be empty"):
            self.state_manager.save_state(journey_manager, "")

        # Only whitespace
        with pytest.raises(ValueError, match="Save name cannot be empty"):
            self.state_manager.save_state(journey_manager, "   ")

        # Only invalid characters
        with pytest.raises(
            ValueError, match="Save name contains only invalid characters"
        ):
            self.state_manager.save_state(journey_manager, "///\\\\")

    def test_save_name_sanitization(self):
        """Test that save names are properly sanitized."""
        journey_manager = JourneyManager()
        result = self.state_manager.save_state(
            journey_manager, "test/save\\name:with|invalid<chars>"
        )

        # Should create a file with sanitized name (invalid chars removed)
        assert "testsavenamewithinvalidchars" in result.lower()

        # Check that a valid file was created
        saves = self.state_manager.list_saves()
        assert len(saves) == 1

    def test_load_nonexistent_file(self):
        """Test loading a non-existent save file."""
        with pytest.raises(
            FileNotFoundError, match="Save file 'nonexistent' not found"
        ):
            self.state_manager.load_state("nonexistent")

    def test_load_valid_save(self):
        """Test loading a valid save file."""
        # Create and save a journey manager
        original_manager = JourneyManager()
        original_manager.start_journey("Test Journey", 5, 2)
        original_manager.make_progress(2)
        original_manager.start_journey("Second Journey", 3, 1)
        original_manager.make_progress(1)

        self.state_manager.save_state(original_manager, "test_save")

        # Load it back
        loaded_manager = self.state_manager.load_state("test_save")

        # Verify the loaded state matches original
        assert loaded_manager.journey_count == original_manager.journey_count
        assert (
            loaded_manager.current_journey.name == original_manager.current_journey.name
        )
        assert (
            loaded_manager.current_journey.progress
            == original_manager.current_journey.progress
        )

        # Check all journeys match
        original_journeys = original_manager.get_all_journeys()
        loaded_journeys = loaded_manager.get_all_journeys()

        assert len(original_journeys) == len(loaded_journeys)
        for orig, loaded in zip(original_journeys, loaded_journeys):
            assert orig.name == loaded.name
            assert orig.total_steps == loaded.total_steps
            assert orig.difficulty == loaded.difficulty
            assert orig.progress == loaded.progress

    def test_load_corrupted_file(self):
        """Test loading a corrupted YAML file."""
        corrupted_path = Path(self.temp_dir, "corrupted.yaml")
        with open(corrupted_path, "w") as f:
            f.write("invalid: yaml: content: [unclosed")

        with pytest.raises(ValueError, match="Corrupted save file"):
            self.state_manager.load_state("corrupted")

    def test_load_invalid_format(self):
        """Test loading a file with invalid format."""
        invalid_path = Path(self.temp_dir, "invalid.yaml")
        with open(invalid_path, "w") as f:
            f.write("just a string")

        with pytest.raises(ValueError, match="Invalid save file format"):
            self.state_manager.load_state("invalid")

    def test_load_missing_version(self):
        """Test loading a file missing version information."""
        import yaml

        invalid_data = {"journey_manager": {"journeys": []}}
        invalid_path = Path(self.temp_dir, "no_version.yaml")

        with open(invalid_path, "w") as f:
            yaml.dump(invalid_data, f)

        with pytest.raises(ValueError, match="Save file missing version information"):
            self.state_manager.load_state("no_version")

    def test_load_incompatible_version(self):
        """Test loading a file with incompatible version."""
        import yaml

        incompatible_data = {"version": "2.0", "journey_manager": {"journeys": []}}
        incompatible_path = Path(self.temp_dir, "incompatible.yaml")

        with open(incompatible_path, "w") as f:
            yaml.dump(incompatible_data, f)

        with pytest.raises(ValueError, match="Incompatible save file version: 2.0"):
            self.state_manager.load_state("incompatible")

    def test_list_saves_empty(self):
        """Test listing saves when directory is empty."""
        saves = self.state_manager.list_saves()
        assert saves == []

    def test_list_saves_with_files(self):
        """Test listing saves with multiple files."""
        journey_manager = JourneyManager()

        # Create multiple saves
        self.state_manager.save_state(journey_manager, "save1")
        self.state_manager.save_state(journey_manager, "save2")
        self.state_manager.save_state(journey_manager, "another_save")

        saves = self.state_manager.list_saves()
        assert len(saves) == 3
        assert "save1" in saves
        assert "save2" in saves
        assert "another_save" in saves
        # Should be sorted
        assert saves == sorted(saves)

    def test_delete_save(self):
        """Test deleting a save file."""
        journey_manager = JourneyManager()
        self.state_manager.save_state(journey_manager, "to_delete")

        # Verify it exists
        assert "to_delete" in self.state_manager.list_saves()

        # Delete it
        result = self.state_manager.delete_save("to_delete")
        assert "Deleted save 'to_delete'" in result

        # Verify it's gone
        assert "to_delete" not in self.state_manager.list_saves()

    def test_delete_nonexistent_save(self):
        """Test deleting a non-existent save file."""
        with pytest.raises(
            FileNotFoundError, match="Save file 'nonexistent' not found"
        ):
            self.state_manager.delete_save("nonexistent")

    def test_get_save_info(self):
        """Test getting information about a save file."""
        journey_manager = JourneyManager()
        journey_manager.start_journey("Test Journey", 5, 2)
        journey_manager.start_journey("Another Journey", 3, 1)

        self.state_manager.save_state(journey_manager, "info_test")

        info = self.state_manager.get_save_info("info_test")

        assert info["name"] == "info_test"
        assert info["version"] == "1.0"
        assert "timestamp" in info
        assert info["journey_count"] == 2
        assert info["file_size"] > 0

    def test_get_save_info_nonexistent(self):
        """Test getting info for non-existent save."""
        with pytest.raises(
            FileNotFoundError, match="Save file 'nonexistent' not found"
        ):
            self.state_manager.get_save_info("nonexistent")

    def test_round_trip_complex_state(self):
        """Test saving and loading complex journey state."""
        # Create complex state
        original_manager = JourneyManager()

        # Add multiple journeys with different states
        original_manager.start_journey("Completed Journey", 3, 1)
        original_manager.make_progress(3)  # This should complete and remove

        original_manager.start_journey("Long Journey", 10, 5)
        original_manager.make_progress(7)

        original_manager.start_journey("Easy Journey", 2, 0)
        original_manager.make_progress(1)

        original_manager.start_journey("Current Journey", 4, 3)

        # Save the state
        self.state_manager.save_state(original_manager, "complex_state")

        # Load it back
        loaded_manager = self.state_manager.load_state("complex_state")

        # Verify complex state is preserved
        assert loaded_manager.journey_count == original_manager.journey_count

        original_journeys = original_manager.get_all_journeys()
        loaded_journeys = loaded_manager.get_all_journeys()

        assert len(original_journeys) == len(loaded_journeys)

        for orig, loaded in zip(original_journeys, loaded_journeys):
            assert orig.name == loaded.name
            assert orig.total_steps == loaded.total_steps
            assert orig.difficulty == loaded.difficulty
            assert orig.progress == loaded.progress
            assert orig.is_completed() == loaded.is_completed()
