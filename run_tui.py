#!/usr/bin/env python3
"""
Run the Advanced Canopy TUI
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from canopy_core.tui.advanced_app import AdvancedCanopyTUI
from canopy_core.types import SystemState, VoteDistribution


async def run_demo():
    """Run a demo of the TUI with mock data."""
    app = AdvancedCanopyTUI(theme="dark")

    # Set up a demo task to simulate agent activity
    async def demo_task():
        await asyncio.sleep(1)
        await app.log_message("🚀 Demo mode: Adding mock agents...", "info")

        # Add some demo agents
        await app.add_agent(1, "GPT-4o")
        await app.add_agent(2, "Claude-3.5-Sonnet")
        await app.add_agent(3, "Gemini-2.0-Pro")

        await asyncio.sleep(1)
        await app.log_message("⚡ Starting mock debate session...", "info")

        # Simulate agent activity
        for i in range(5):
            await asyncio.sleep(2)
            await app.update_agent_status(1, "thinking", f"Analyzing problem... step {i+1}")
            await app.update_agent_status(2, "working", f"Generating response {i+1}")
            await app.update_agent_status(3, "voting", f"Casting vote {i+1}")

            # Mock system state updates
            state = SystemState()
            state.phase = "debate"
            state.debate_rounds = i + 1
            state.consensus_reached = i >= 4
            state.vote_distribution = VoteDistribution()
            state.vote_distribution.votes = {1: i + 1, 2: i, 3: i + 2}

            await app.update_system_state(state)
            await app.log_message(f"📊 Debate round {i+1} completed", "success")

        await app.log_message("🏆 Demo completed! TUI is fully functional.", "success")

    # Start the demo task
    app.set_timer(0.5, demo_task)

    await app.run_async()


def main():
    """Main entry point."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
