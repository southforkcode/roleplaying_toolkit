from lib.states.game_state import GameState

import importlib
import pkgutil


class StateManager(object):
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def __init__(self, states=["*"]):
        assert StateManager.instance is None, "StateManager is a singleton!"
        self._states = []
        self._current_state = None
        self.load_states(states)

    def load_states(self, states):
        """Dynamically load states from the lib.states package."""
        if states == ["*"]:
            # Load all states from the lib.states package
            package = importlib.import_module("lib.states")
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                module = importlib.import_module(f"lib.states.{module_name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, GameState) and attr is not GameState:
                        self._states.append(attr())
        else:
            for state_name in states:
                module = importlib.import_module(f"lib.states.{state_name.lower()}")
                state_class = getattr(module, state_name)
                self._states.append(state_class())

        if self._states:
            self._current_state = self._states[0]
