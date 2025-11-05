"""Tests for the journey system."""
import pytest
from lib.journey_system import Journey, JourneyManager


class TestJourney:
    """Test cases for Journey class."""

    def test_journey_creation(self):
        """Test creating a new journey."""
        journey = Journey("Find treasure", 5, "medium")
        assert journey.name == "Find treasure"
        assert journey.total_steps == 5
        assert journey.difficulty == "medium"
        assert journey.progress == 0
        assert not journey.is_completed()

    def test_journey_progress(self):
        """Test making progress on a journey."""
        journey = Journey("Test Quest", 3, "easy")
        
        # Make partial progress
        result = journey.make_progress(1)
        assert journey.progress == 1
        assert not journey.is_completed()
        assert "Test Quest" in result
        assert "1/3" in result
        
        # Complete the journey
        result = journey.make_progress(2)
        assert journey.progress == 3
        assert journey.is_completed()
        assert "completed" in result.lower()

    def test_journey_progress_overflow(self):
        """Test making more progress than remaining steps."""
        journey = Journey("Short Quest", 2, "easy")
        
        # Make more progress than remaining
        result = journey.make_progress(5)
        assert journey.progress == 2  # Should cap at total_steps
        assert journey.is_completed()
        assert "completed" in result.lower()

    def test_journey_zero_progress(self):
        """Test making zero progress."""
        journey = Journey("No Progress", 3, "easy")
        
        with pytest.raises(ValueError, match="Progress must be positive"):
            journey.make_progress(0)

    def test_journey_negative_progress(self):
        """Test making negative progress."""
        journey = Journey("Negative Test", 3, "easy")
        
        with pytest.raises(ValueError, match="Progress must be positive"):
            journey.make_progress(-1)

    def test_journey_serialization(self):
        """Test journey serialization to dictionary."""
        journey = Journey("Serialize Test", 4, "hard")
        journey.make_progress(2)
        
        data = journey.to_dict()
        
        expected = {
            "name": "Serialize Test",
            "total_steps": 4,
            "difficulty": "hard",
            "progress": 2
        }
        assert data == expected

    def test_journey_deserialization(self):
        """Test journey deserialization from dictionary."""
        data = {
            "name": "Deserialize Test",
            "total_steps": 6,
            "difficulty": "medium",
            "progress": 3
        }
        
        journey = Journey.from_dict(data)
        
        assert journey.name == "Deserialize Test"
        assert journey.total_steps == 6
        assert journey.difficulty == "medium"
        assert journey.progress == 3


class TestJourneyManager:
    """Test cases for JourneyManager class."""

    def test_empty_manager(self):
        """Test empty journey manager."""
        manager = JourneyManager()
        assert not manager.has_active_journeys()
        assert manager.get_all_journeys() == []
        
        with pytest.raises(ValueError, match="No active journeys"):
            manager.make_progress(1)
            
        with pytest.raises(ValueError, match="No active journeys"):
            manager.stop_current_journey()

    def test_start_single_journey(self):
        """Test starting a single journey."""
        manager = JourneyManager()
        manager.start_journey("First Quest", 5, "easy")
        
        assert manager.has_active_journeys()
        journeys = manager.get_all_journeys()
        assert len(journeys) == 1
        assert journeys[0].name == "First Quest"

    def test_start_multiple_journeys(self):
        """Test starting multiple journeys (stacking)."""
        manager = JourneyManager()
        manager.start_journey("Quest 1", 3, "easy")
        manager.start_journey("Quest 2", 4, "medium")
        manager.start_journey("Quest 3", 2, "hard")
        
        assert manager.has_active_journeys()
        journeys = manager.get_all_journeys()
        assert len(journeys) == 3
        
        # Most recent journey should be first (stack behavior)
        assert journeys[0].name == "Quest 3"
        assert journeys[1].name == "Quest 2"
        assert journeys[2].name == "Quest 1"

    def test_duplicate_journey_names(self):
        """Test that duplicate journey names are not allowed."""
        manager = JourneyManager()
        manager.start_journey("Duplicate", 5, "easy")
        
        with pytest.raises(ValueError, match="already exists"):
            manager.start_journey("Duplicate", 3, "medium")

    def test_progress_current_journey(self):
        """Test making progress on the current (top) journey."""
        manager = JourneyManager()
        manager.start_journey("Bottom Quest", 5, "easy")
        manager.start_journey("Top Quest", 3, "medium")
        
        # Progress should be made on the top journey
        result = manager.make_progress(1)
        
        journeys = manager.get_all_journeys()
        assert journeys[0].progress == 1  # Top journey
        assert journeys[1].progress == 0  # Bottom journey
        assert "Top Quest" in result

    def test_journey_completion_removes_from_stack(self):
        """Test that completing a journey removes it from the stack."""
        manager = JourneyManager()
        manager.start_journey("Bottom Quest", 5, "easy")
        manager.start_journey("Top Quest", 2, "medium")
        
        # Complete the top journey
        result = manager.make_progress(2)
        
        # Top journey should be removed, bottom becomes current
        journeys = manager.get_all_journeys()
        assert len(journeys) == 1
        assert journeys[0].name == "Bottom Quest"
        assert "completed" in result.lower()

    def test_stop_current_journey(self):
        """Test stopping the current journey."""
        manager = JourneyManager()
        manager.start_journey("Bottom Quest", 5, "easy")
        manager.start_journey("Top Quest", 3, "medium")
        
        # Make some progress on top journey
        manager.make_progress(1)
        
        # Stop the top journey
        stopped = manager.stop_current_journey()
        
        assert stopped.name == "Top Quest"
        assert stopped.progress == 1
        
        # Bottom journey should now be current
        journeys = manager.get_all_journeys()
        assert len(journeys) == 1
        assert journeys[0].name == "Bottom Quest"

    def test_stop_all_journeys(self):
        """Test stopping all journeys leaves manager empty."""
        manager = JourneyManager()
        manager.start_journey("Quest 1", 3, "easy")
        manager.start_journey("Quest 2", 4, "medium")
        
        # Stop both journeys
        manager.stop_current_journey()
        manager.stop_current_journey()
        
        assert not manager.has_active_journeys()
        assert manager.get_all_journeys() == []

    def test_manager_serialization(self):
        """Test journey manager serialization."""
        manager = JourneyManager()
        manager.start_journey("Quest 1", 5, "easy")
        manager.start_journey("Quest 2", 3, "medium")
        manager.make_progress(1)  # Progress on Quest 2
        
        data = manager.to_dict()
        
        assert "journeys" in data
        assert len(data["journeys"]) == 2
        assert data["journeys"][0]["name"] == "Quest 2"
        assert data["journeys"][0]["progress"] == 1
        assert data["journeys"][1]["name"] == "Quest 1"
        assert data["journeys"][1]["progress"] == 0

    def test_manager_deserialization(self):
        """Test journey manager deserialization."""
        data = {
            "journeys": [
                {"name": "Quest A", "total_steps": 4, "difficulty": "hard", "progress": 2},
                {"name": "Quest B", "total_steps": 6, "difficulty": "easy", "progress": 0}
            ]
        }
        
        manager = JourneyManager.from_dict(data)
        
        assert manager.has_active_journeys()
        journeys = manager.get_all_journeys()
        assert len(journeys) == 2
        assert journeys[0].name == "Quest A"
        assert journeys[0].progress == 2
        assert journeys[1].name == "Quest B"
        assert journeys[1].progress == 0

    def test_empty_manager_serialization(self):
        """Test serialization of empty manager."""
        manager = JourneyManager()
        data = manager.to_dict()
        
        assert data == {"journeys": []}
        
        # Test round-trip
        new_manager = JourneyManager.from_dict(data)
        assert not new_manager.has_active_journeys()

    def test_invalid_journey_parameters(self):
        """Test invalid journey parameters."""
        manager = JourneyManager()
        
        # Test invalid steps
        with pytest.raises(ValueError):
            manager.start_journey("Bad Steps", 0, "easy")
        
        with pytest.raises(ValueError):
            manager.start_journey("Negative Steps", -1, "easy")
        
        # Test invalid difficulty
        with pytest.raises(ValueError):
            manager.start_journey("Bad Difficulty", 5, "impossible")

    def test_empty_journey_name(self):
        """Test empty journey name."""
        manager = JourneyManager()
        
        with pytest.raises(ValueError):
            manager.start_journey("", 5, "easy")
        
        with pytest.raises(ValueError):
            manager.start_journey("   ", 5, "easy")  # Whitespace only