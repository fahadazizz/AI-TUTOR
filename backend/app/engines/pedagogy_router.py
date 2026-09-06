"""
AI Tutor — Pedagogy Router.

Routes pedagogical decisions to the correct subject-specific plugin based
on the concept's pedagogy_type.
"""

from typing import Dict
from app.engines.plugins.base_plugin import PedagogyPlugin
from app.logging import get_logger

logger = get_logger(__name__)


class PedagogyRouter:
    """Routes to the correct pedagogy plugin for a concept."""

    def __init__(self):
        self._plugins: Dict[str, PedagogyPlugin] = {}

    def register_plugin(self, pedagogy_type: str, plugin: PedagogyPlugin) -> None:
        """Register a pedagogy plugin for a specific pedagogy type."""
        self._plugins[pedagogy_type] = plugin
        logger.info("pedagogy_plugin_registered", pedagogy_type=pedagogy_type)

    def get_plugin(self, pedagogy_type: str) -> PedagogyPlugin:
        """Retrieve the pedagogy plugin for the given pedagogy type."""
        plugin = self._plugins.get(pedagogy_type)
        if not plugin:
            # Fallback to a default if the specific one is missing, 
            # though in a strict system we might want to raise an error.
            # We will raise an error here to enforce the generalization gate.
            raise ValueError(f"No PedagogyPlugin registered for pedagogy_type: {pedagogy_type}")
        return plugin
