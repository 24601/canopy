#!/usr/bin/env python3
"""
Demo script for the new Textual-based MassGen TUI.

This script demonstrates the new TUI using Textual v5.0.1 with:
- Modern reactive widgets
- Real-time data streaming using DataTable
- Agent panels with status updates
- System status monitoring
- Vote distribution visualization
- Trace monitoring (if enabled)
- Log viewing capabilities
"""

import asyncio
import random
import time

from canopy_core.tui.app import CanopyApp
from canopy_core.types import AgentState, SystemState, VoteDistribution


async def demo_streaming_data():
    """Demonstrate streaming data to the TUI."""

    # Create and run the TUI app
    app = CanopyApp()

    # Create some demo agents
    agent_configs = [
        {"id": 0, "model": "gpt-4o", "status": "working"},
        {"id": 1, "model": "claude-3.5-sonnet", "status": "working"},
        {"id": 2, "model": "gemini-pro", "status": "working"},
    ]

    # Initialize agent states
    for config in agent_configs:
        state = AgentState(
            agent_id=config["id"],
            model_name=config["model"],
            status=config["status"],
            chat_round=0,
            update_count=0,
            votes_cast=0,
        )
        await app.update_agent(config["id"], state)

    # Initialize system state
    system_state = SystemState(
        phase="collaboration",
        consensus_reached=False,
        debate_rounds=0,
        algorithm_name="massgen",
        representative_agent_id=None,
    )
    await app.update_system_state(system_state)

    # Start background task to simulate streaming updates
    async def simulate_agent_work():
        """Simulate agent work with streaming output."""
        round_num = 1

        while True:
            for agent_id in range(3):
                # Simulate streaming output
                messages = [
                    f"🤖 Agent {agent_id} starting round {round_num}...",
                    "📊 Analyzing problem space...",
                    "💡 Generating solution approach...",
                    f"⚡ Processing with {agent_configs[agent_id]['model']}...",
                    f"✅ Completed analysis for round {round_num}",
                ]

                for msg in messages:
                    await app.update_agent(
                        agent_id,
                        AgentState(
                            agent_id=agent_id,
                            model_name=agent_configs[agent_id]["model"],
                            status="working",
                            chat_round=round_num,
                            update_count=round_num * 5,
                            votes_cast=max(0, round_num - 1),
                        ),
                    )

                    # Stream the message
                    agent_panel = app.agent_panels.get(agent_id)
                    if agent_panel:
                        agent_panel.stream_output(f"{msg}\n")

                    await asyncio.sleep(0.5)

                # Random status updates
                if random.random() < 0.3:  # 30% chance
                    status = random.choice(["working", "voted", "failed"])
                    await app.update_agent(
                        agent_id,
                        AgentState(
                            agent_id=agent_id,
                            model_name=agent_configs[agent_id]["model"],
                            status=status,
                            chat_round=round_num,
                            update_count=round_num * 5,
                            votes_cast=max(0, round_num - 1),
                        ),
                    )

            # Update system state
            if round_num > 2:
                # Simulate voting phase
                vote_dist = VoteDistribution()
                for _ in range(random.randint(3, 8)):
                    vote_dist.add_vote(random.randint(0, 2))

                system_state.phase = "consensus" if round_num > 4 else "collaboration"
                system_state.debate_rounds = round_num
                system_state.vote_distribution = vote_dist

                if round_num > 5:
                    system_state.consensus_reached = True
                    system_state.representative_agent_id = vote_dist.leader_agent_id

                await app.update_system_state(system_state)
                await app.update_vote_distribution(vote_dist)

            # Add system messages
            messages = [
                f"🔄 Starting collaboration round {round_num}",
                f"📈 {len(app.agent_panels)} agents participating",
                f"⏱️ Round {round_num} in progress...",
            ]

            for msg in messages:
                await app.add_log_entry(None, msg)
                await asyncio.sleep(0.2)

            round_num += 1
            await asyncio.sleep(3)  # Wait between rounds

    # Start the simulation
    asyncio.create_task(simulate_agent_work())

    # Run the app
    await app.run_async()


def main():
    """Main entry point for the demo."""
    print("🚀 Starting MassGen Textual TUI Demo...")
    print("📋 Features demonstrated:")
    print("  • Real-time agent status updates")
    print("  • Streaming agent output")
    print("  • System state monitoring")
    print("  • Vote distribution visualization")
    print("  • Modern Textual v5.0.1 widgets")
    print("\n⌨️  Controls:")
    print("  • q: Quit")
    print("  • l: Toggle logs")
    print("  • t: Toggle traces")
    print("  • r: Refresh")
    print("\n🎯 Starting in 3 seconds...")
    time.sleep(3)

    try:
        asyncio.run(demo_streaming_data())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
