"""
TUI Integration Bridge for Canopy

This module provides a compatibility layer between the old streaming_display.py
ANSI-based system and the new state-of-the-art Textual TUI implementation.

It allows existing code to continue working while gradually migrating to the
modern Textual interface with all its advanced features.
"""

import asyncio
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .logging import get_logger
from .tui.modern_app import ErrorSeverity, ModernCanopyTUI, create_modern_canopy_tui
from .types import AgentState, SystemState, VoteDistribution

logger = get_logger(__name__)


class ModernDisplayOrchestrator:
    """
    Modern replacement for StreamingOrchestrator using state-of-the-art Textual TUI.

    Provides API compatibility with the old streaming display while using
    the new modern TUI implementation underneath.
    """

    def __init__(
        self,
        display_enabled: bool = True,
        stream_callback: Optional[Callable] = None,
        max_lines: int = 10,
        save_logs: bool = True,
        answers_dir: Optional[str] = None,
        theme: str = "dark",
        web_mode: bool = False,
    ):
        """Initialize the modern display orchestrator.

        Args:
            display_enabled: Whether to show the TUI
            stream_callback: Optional callback for streaming events
            max_lines: Maximum lines to display (for compatibility)
            save_logs: Whether to save logs to files
            answers_dir: Directory for answer files
            theme: UI theme name
            web_mode: Enable web deployment features
        """
        self.display_enabled = display_enabled
        self.stream_callback = stream_callback
        self.save_logs = save_logs
        self.answers_dir = answers_dir

        # Modern TUI instance
        self.tui_app: Optional[ModernCanopyTUI] = None
        self.tui_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Configuration
        self.theme = theme
        self.web_mode = web_mode

        # State tracking for compatibility
        self.agent_states: Dict[str, AgentState] = {}
        self.system_state = SystemState()
        self.vote_distribution = VoteDistribution()

        # Thread safety
        self._lock = asyncio.Lock()

        if display_enabled:
            self._start_modern_tui()

    def _start_modern_tui(self) -> None:
        """Start the modern Textual TUI in the background with robust error handling."""
        try:
            # Validate configuration before starting
            if not isinstance(self.theme, str):
                logger.warning(f"Invalid theme type: {type(self.theme)}, using default")
                self.theme = "dark"

            if not isinstance(self.web_mode, bool):
                logger.warning(f"Invalid web_mode type: {type(self.web_mode)}, using default")
                self.web_mode = False

            # Create the modern TUI app with validation
            self.tui_app = create_modern_canopy_tui(theme=self.theme, web_mode=self.web_mode)

            if not self.tui_app:
                raise RuntimeError("Failed to create TUI app instance")

            # Start TUI in background thread to avoid blocking
            def run_tui():
                try:
                    # Use asyncio.run to start the TUI
                    asyncio.run(self.tui_app.run_async())
                except KeyboardInterrupt:
                    logger.info("TUI stopped by user")
                except Exception as e:
                    logger.error(f"TUI runtime error: {e}")
                    # Try to handle error through the TUI's error handler if available
                    if hasattr(self.tui_app, "error_handler"):
                        asyncio.run(self.tui_app.error_handler.handle_error(e, "TUI runtime", ErrorSeverity.CRITICAL))
                finally:
                    self.is_running = False
                    logger.info("TUI thread terminated")

            # Create and start thread with proper error handling
            tui_thread = threading.Thread(target=run_tui, daemon=True, name="CanopyTUI")
            tui_thread.start()

            # Verify thread started successfully
            import time

            time.sleep(0.1)  # Brief wait to check if thread started
            if not tui_thread.is_alive():
                raise RuntimeError("TUI thread failed to start")

            self.is_running = True
            logger.info("🚀 Modern Canopy TUI started successfully")

        except Exception as e:
            logger.error(f"Failed to start modern TUI: {e}")
            self.display_enabled = False
            self.is_running = False

            # Ensure tui_app is None if startup failed
            self.tui_app = None

    async def stream_output(self, agent_id: int, content: str) -> None:
        """Stream output content to the modern TUI with robust error handling."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            # Input validation
            if not isinstance(agent_id, int):
                raise ValueError(f"agent_id must be int, got {type(agent_id)}")
            if not isinstance(content, str):
                content = str(content) if content is not None else ""
            if not content.strip():
                return  # Skip empty content

            async with self._lock:
                # Convert agent_id to string for consistency
                agent_str = str(agent_id)

                # Update agent state if it exists
                if agent_str in self.agent_states:
                    try:
                        state = self.agent_states[agent_str]
                        await self.tui_app.update_agent(agent_str, state)
                    except Exception as update_error:
                        # Handle agent update error through TUI error handler
                        if hasattr(self.tui_app, "error_handler"):
                            await self.tui_app.error_handler.handle_error(
                                update_error,
                                f"Updating agent {agent_str} during stream",
                                ErrorSeverity.WARNING,
                                show_notification=False,
                            )
                        else:
                            logger.warning(f"Agent update error: {update_error}")

                # Log the output as an agent message
                try:
                    await self.tui_app.log_message(content, level="agent", agent_id=agent_str)
                except Exception as log_error:
                    # Fallback logging if TUI logging fails
                    logger.warning(f"TUI logging failed, using fallback: {log_error}")
                    logger.info(f"Agent {agent_id}: {content}")

                # Call legacy callback if provided
                if self.stream_callback:
                    try:
                        # Validate callback is callable
                        if not callable(self.stream_callback):
                            logger.error(f"Stream callback is not callable: {type(self.stream_callback)}")
                        else:
                            self.stream_callback(agent_id, content)
                    except Exception as callback_error:
                        logger.warning(f"Stream callback error: {callback_error}")
                        # Don't let callback errors break the stream

        except Exception as e:
            logger.error(f"Error streaming output for agent {agent_id}: {e}")
            # Try to report error through TUI error handler if available
            if self.tui_app and hasattr(self.tui_app, "error_handler"):
                try:
                    await self.tui_app.error_handler.handle_error(
                        e, f"Streaming output for agent {agent_id}", ErrorSeverity.ERROR
                    )
                except:
                    pass  # Prevent recursive errors

    async def set_agent_model(self, agent_id: int, model_name: str) -> None:
        """Set agent model with immediate TUI update."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            async with self._lock:
                agent_str = str(agent_id)

                # Create or update agent state
                if agent_str not in self.agent_states:
                    self.agent_states[agent_str] = AgentState(
                        agent_id=agent_id, model_name=model_name, status="unknown"
                    )
                else:
                    self.agent_states[agent_str].model_name = model_name

                # Update TUI
                await self.tui_app.update_agent(agent_str, self.agent_states[agent_str])
                await self.tui_app.log_message(f"Agent {agent_id} initialized with model: {model_name}", level="info")

        except Exception as e:
            logger.error(f"Error setting agent model: {e}")

    async def update_agent_status(self, agent_id: int, status: str) -> None:
        """Update agent status with immediate TUI update."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            async with self._lock:
                agent_str = str(agent_id)

                # Update agent state
                if agent_str not in self.agent_states:
                    self.agent_states[agent_str] = AgentState(agent_id=agent_id, status=status)
                else:
                    old_status = self.agent_states[agent_str].status
                    self.agent_states[agent_str].status = status

                    # Log status change
                    if old_status != status:
                        await self.tui_app.log_message(
                            f"Agent {agent_id} status: {old_status} → {status}", level="info"
                        )

                # Update TUI with enhanced status information
                await self.tui_app.update_agent_status(agent_id, status, state=self.agent_states[agent_str])

        except Exception as e:
            logger.error(f"Error updating agent status: {e}")

    async def update_phase(self, old_phase: str, new_phase: str) -> None:
        """Update system phase with TUI notification."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            self.system_state.phase = new_phase

            # Update TUI system state
            await self.tui_app.update_system_state(self.system_state)
            await self.tui_app.log_message(f"Phase transition: {old_phase} → {new_phase}", level="success")

        except Exception as e:
            logger.error(f"Error updating phase: {e}")

    async def update_vote_distribution(self, vote_dist: Dict[int, int]) -> None:
        """Update vote distribution with enhanced visualization."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            # Convert to VoteDistribution object
            vote_distribution = VoteDistribution()
            for agent_id, count in vote_dist.items():
                for _ in range(count):
                    vote_distribution.add_vote(agent_id)

            self.vote_distribution = vote_distribution

            # Update system state
            self.system_state.vote_distribution = vote_distribution
            await self.tui_app.update_system_state(self.system_state)

            # Log vote update
            total_votes = sum(vote_dist.values())
            await self.tui_app.log_message(f"Vote distribution updated: {total_votes} total votes", level="info")

        except Exception as e:
            logger.error(f"Error updating vote distribution: {e}")

    async def update_consensus_status(self, representative_id: int, vote_dist: Dict[int, int]) -> None:
        """Update consensus status with celebration notification."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            # Update vote distribution first
            await self.update_vote_distribution(vote_dist)

            # Update system state
            self.system_state.consensus_reached = True
            self.system_state.representative_agent_id = representative_id

            await self.tui_app.update_system_state(self.system_state)
            await self.tui_app.log_message(
                f"🎉 CONSENSUS REACHED! Agent {representative_id} selected as representative", level="success"
            )

        except Exception as e:
            logger.error(f"Error updating consensus status: {e}")

    async def reset_consensus(self) -> None:
        """Reset consensus state."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            self.system_state.consensus_reached = False
            self.system_state.representative_agent_id = None
            self.vote_distribution = VoteDistribution()

            await self.tui_app.update_system_state(self.system_state)
            await self.tui_app.log_message("Consensus state reset", level="info")

        except Exception as e:
            logger.error(f"Error resetting consensus: {e}")

    async def add_system_message(self, message: str) -> None:
        """Add system message with enhanced logging."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            await self.tui_app.log_message(message, level="info")

        except Exception as e:
            logger.error(f"Error adding system message: {e}")

    # Additional methods for enhanced functionality
    async def update_agent_vote_target(self, agent_id: int, target_id: Optional[int]) -> None:
        """Update agent vote target."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            async with self._lock:
                agent_str = str(agent_id)

                if agent_str in self.agent_states:
                    self.agent_states[agent_str].vote_target = target_id
                    await self.tui_app.update_agent(agent_str, self.agent_states[agent_str])

                    target_msg = f"Agent {target_id}" if target_id else "None"
                    await self.tui_app.log_message(f"Agent {agent_id} vote target: {target_msg}", level="info")

        except Exception as e:
            logger.error(f"Error updating vote target: {e}")

    async def update_agent_chat_round(self, agent_id: int, round_num: int) -> None:
        """Update agent chat round."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            async with self._lock:
                agent_str = str(agent_id)

                if agent_str in self.agent_states:
                    self.agent_states[agent_str].chat_round = round_num
                    await self.tui_app.update_agent(agent_str, self.agent_states[agent_str])

        except Exception as e:
            logger.error(f"Error updating chat round: {e}")

    async def update_agent_update_count(self, agent_id: int, count: int) -> None:
        """Update agent update count."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            async with self._lock:
                agent_str = str(agent_id)

                if agent_str in self.agent_states:
                    self.agent_states[agent_str].update_count = count
                    await self.tui_app.update_agent(agent_str, self.agent_states[agent_str])

        except Exception as e:
            logger.error(f"Error updating update count: {e}")

    async def update_agent_votes_cast(self, agent_id: int, votes_cast: int) -> None:
        """Update agent votes cast count."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            async with self._lock:
                agent_str = str(agent_id)

                if agent_str in self.agent_states:
                    self.agent_states[agent_str].votes_cast = votes_cast
                    await self.tui_app.update_agent(agent_str, self.agent_states[agent_str])

        except Exception as e:
            logger.error(f"Error updating votes cast: {e}")

    async def update_debate_rounds(self, rounds: int) -> None:
        """Update debate rounds count."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            self.system_state.debate_rounds = rounds
            await self.tui_app.update_system_state(self.system_state)

        except Exception as e:
            logger.error(f"Error updating debate rounds: {e}")

    async def update_algorithm_name(self, algorithm_name: str) -> None:
        """Update algorithm name."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            self.system_state.algorithm_name = algorithm_name
            await self.tui_app.update_system_state(self.system_state)
            await self.tui_app.log_message(f"Algorithm set to: {algorithm_name}", level="info")

        except Exception as e:
            logger.error(f"Error updating algorithm name: {e}")

    def format_agent_notification(self, agent_id: int, notification_type: str, content: str) -> None:
        """Format agent notifications (async wrapper for compatibility)."""
        asyncio.create_task(self._format_agent_notification(agent_id, notification_type, content))

    async def _format_agent_notification(self, agent_id: int, notification_type: str, content: str) -> None:
        """Format agent notifications for display."""
        if not self.display_enabled or not self.tui_app:
            return

        try:
            notification_icons = {
                "update": "📢",
                "debate": "🗣️",
                "presentation": "🎯",
                "prompt": "💡",
            }

            icon = notification_icons.get(notification_type, "📨")
            message = f"{icon} Agent {agent_id} {notification_type}: {content}"

            await self.tui_app.log_message(message, level="info", agent_id=str(agent_id))

        except Exception as e:
            logger.error(f"Error formatting notification: {e}")

    def get_agent_log_path(self, agent_id: int) -> str:
        """Get agent log path (compatibility method)."""
        # In the modern TUI, logs are handled differently
        # This returns a placeholder for compatibility
        return f"logs/agent_{agent_id}.log"

    def get_agent_answer_path(self, agent_id: int) -> str:
        """Get agent answer path (compatibility method)."""
        if self.answers_dir:
            return f"{self.answers_dir}/agent_{agent_id}.txt"
        return f"answers/agent_{agent_id}.txt"

    def get_system_log_path(self) -> str:
        """Get system log path (compatibility method)."""
        return "logs/system.log"

    def cleanup(self) -> None:
        """Clean up resources when orchestrator is no longer needed."""
        try:
            self.is_running = False

            if self.tui_app:
                # The TUI app will handle its own cleanup
                pass

            logger.info("Modern display orchestrator cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Factory function for easy migration
def create_streaming_display(
    display_enabled: bool = True,
    stream_callback: Optional[Callable] = None,
    max_lines: int = 10,
    save_logs: bool = True,
    answers_dir: Optional[str] = None,
    theme: str = "dark",
    web_mode: bool = False,
) -> ModernDisplayOrchestrator:
    """
    Create a modern streaming display orchestrator.

    This replaces the old create_streaming_display function with a modern
    implementation that uses the state-of-the-art Textual TUI.

    Args:
        display_enabled: Whether to show the TUI
        stream_callback: Optional callback for streaming events
        max_lines: Maximum lines (compatibility parameter)
        save_logs: Whether to save logs
        answers_dir: Directory for answer files
        theme: UI theme name
        web_mode: Enable web deployment features

    Returns:
        ModernDisplayOrchestrator instance with full API compatibility
    """
    return ModernDisplayOrchestrator(
        display_enabled=display_enabled,
        stream_callback=stream_callback,
        max_lines=max_lines,
        save_logs=save_logs,
        answers_dir=answers_dir,
        theme=theme,
        web_mode=web_mode,
    )


# Legacy compatibility exports
StreamingOrchestrator = ModernDisplayOrchestrator
MultiRegionDisplay = ModernDisplayOrchestrator

__all__ = [
    "ModernDisplayOrchestrator",
    "create_streaming_display",
    "StreamingOrchestrator",  # Legacy compatibility
    "MultiRegionDisplay",  # Legacy compatibility
]
