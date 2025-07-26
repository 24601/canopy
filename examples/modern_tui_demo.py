#!/usr/bin/env python3
"""
🚀 State-of-the-Art Canopy TUI Demo

This script demonstrates the modern Textual-based TUI with latest v5+ features:

✨ FEATURES SHOWCASED:
- Command Palette with fuzzy search (Ctrl+P)
- DataTable with reactive updates and rich cell styling
- Advanced Grid layouts with responsive design
- Sparklines for real-time performance visualization
- TabbedContent for organized multi-view interface
- Web deployment ready (textual-serve compatible)
- Advanced reactive patterns with data binding
- Performance optimizations with partial updates
- Modern theming with CSS variable injection

🎮 CONTROLS:
- Ctrl+P: Open command palette
- Tab/Shift+Tab: Navigate between tabs
- Q: Quit
- R: Refresh
- P: Pause/Resume
- Ctrl+T: Cycle themes
- F1: Help

🌐 WEB MODE:
Run with --web to enable web deployment mode
"""

import asyncio
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from canopy_core.tui_bridge import create_streaming_display
from canopy_core.types import AgentState, SystemState, VoteDistribution


class ModernTUIDemo:
    """Advanced demo showcasing state-of-the-art TUI features."""
    
    def __init__(self, web_mode: bool = False, theme: str = "dark"):
        """Initialize the demo.
        
        Args:
            web_mode: Enable web deployment features
            theme: UI theme name
        """
        self.web_mode = web_mode
        self.theme = theme
        self.orchestrator = None
        self.demo_agents: List[Dict] = [
            {"id": 0, "model": "gpt-4o", "name": "Strategist"},
            {"id": 1, "model": "claude-3.5-sonnet", "name": "Analyst"},
            {"id": 2, "model": "gemini-2.0-flash-exp", "name": "Synthesizer"},
            {"id": 3, "model": "o1-preview", "name": "Reasoner"},
        ]
        self.is_running = True
        self.current_round = 1
        
    async def run_demo(self):
        """Run the comprehensive TUI demo."""
        print("🚀 Starting State-of-the-Art Canopy TUI Demo...")
        print("\n✨ FEATURES DEMONSTRATED:")
        print("  • Command Palette with fuzzy search (Ctrl+P)")
        print("  • DataTable with reactive cell updates")
        print("  • Advanced Grid layouts with layers")
        print("  • Sparklines for real-time metrics")
        print("  • TabbedContent interface")
        print("  • Performance optimizations")
        print("  • Modern reactive patterns")
        print("  • Dynamic theming support")
        
        if self.web_mode:
            print("  • 🌐 Web deployment mode enabled")
        
        print("\n🎮 CONTROLS:")
        print("  • Ctrl+P: Command palette")
        print("  • Tab: Switch tabs")
        print("  • Q: Quit")
        print("  • P: Pause/Resume")
        print("  • Ctrl+T: Cycle themes")
        print("  • F1: Help")
        
        print("\n⏳ Starting in 3 seconds...")
        await asyncio.sleep(3)
        
        # Create the modern streaming display
        self.orchestrator = create_streaming_display(
            display_enabled=True,
            save_logs=True,
            theme=self.theme,
            web_mode=self.web_mode
        )
        
        # Initialize system state
        await self._initialize_demo()
        
        # Start concurrent demo tasks
        tasks = [
            asyncio.create_task(self._agent_lifecycle_demo()),
            asyncio.create_task(self._system_metrics_demo()),
            asyncio.create_task(self._voting_consensus_demo()),
            asyncio.create_task(self._real_time_updates_demo()),
        ]
        
        try:
            # Run all demo tasks concurrently
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        finally:
            await self._cleanup_demo()

    async def _initialize_demo(self):
        """Initialize the demo with system state and agents."""
        # Set up initial system state
        system_state = SystemState(
            phase="initialization",
            consensus_reached=False,
            debate_rounds=0,
            algorithm_name="canopy",
            representative_agent_id=None,
        )
        
        await self.orchestrator.update_phase("startup", "initialization")
        await self.orchestrator.add_system_message("🚀 Canopy Multi-Agent System initializing...")
        
        # Initialize agents with staggered timing for visual effect
        for i, agent_config in enumerate(self.demo_agents):
            await asyncio.sleep(1)  # Stagger agent creation
            
            # Set agent model
            await self.orchestrator.set_agent_model(
                agent_config["id"], 
                agent_config["model"]
            )
            
            # Update agent status
            await self.orchestrator.update_agent_status(
                agent_config["id"], 
                "initializing"
            )
            
            await self.orchestrator.add_system_message(
                f"🤖 {agent_config['name']} ({agent_config['model']}) joined the system"
            )
        
        await self.orchestrator.update_phase("initialization", "collaboration")
        await self.orchestrator.add_system_message("✅ All agents initialized - starting collaboration")

    async def _agent_lifecycle_demo(self):
        """Demonstrate comprehensive agent lifecycle with realistic scenarios."""
        await asyncio.sleep(2)  # Let initialization finish
        
        scenarios = [
            "Analyzing problem constraints and requirements",
            "Researching relevant background information", 
            "Generating initial solution approaches",
            "Evaluating feasibility and trade-offs",
            "Refining solutions based on feedback",
            "Preparing final recommendations",
        ]
        
        while self.is_running:
            for round_num in range(1, 6):
                if not self.is_running:
                    break
                
                self.current_round = round_num
                
                # Update all agents for this round
                for agent_config in self.demo_agents:
                    if not self.is_running:
                        break
                    
                    agent_id = agent_config["id"]
                    
                    # Update round information
                    await self.orchestrator.update_agent_chat_round(agent_id, round_num)
                    await self.orchestrator.update_agent_update_count(agent_id, round_num * 3)
                    
                    # Simulate agent working
                    await self.orchestrator.update_agent_status(agent_id, "working")
                    
                    # Stream realistic agent output
                    scenario = random.choice(scenarios)
                    await self.orchestrator.stream_output(
                        agent_id, 
                        f"\n🔍 Round {round_num}: {scenario}\n"
                    )
                    
                    # Simulate processing time with multiple status updates
                    for step in range(3):
                        await asyncio.sleep(1)
                        if not self.is_running:
                            break
                        
                        step_messages = [
                            "Gathering data and context...",
                            "Processing information...",
                            "Generating insights...",
                            "Validating approach...",
                            "Preparing output...",
                        ]
                        
                        await self.orchestrator.stream_output(
                            agent_id,
                            f"  • {random.choice(step_messages)}\n"
                        )
                    
                    # Simulate completion
                    await self.orchestrator.update_agent_status(agent_id, "completed")
                    await self.orchestrator.stream_output(
                        agent_id,
                        f"✅ Round {round_num} analysis complete\n"
                    )
                    
                    await asyncio.sleep(0.5)
                
                # Round summary
                await self.orchestrator.add_system_message(
                    f"🔄 Round {round_num} completed - all agents finished analysis"
                )
                
                await asyncio.sleep(2)
            
            # Brief pause before next cycle
            await asyncio.sleep(5)

    async def _system_metrics_demo(self):
        """Demonstrate real-time system metrics and performance monitoring."""
        await asyncio.sleep(3)
        
        while self.is_running:
            # Simulate system load variations
            cpu_load = random.uniform(20, 80)
            memory_usage = random.uniform(30, 70)
            network_activity = random.uniform(10, 90)
            
            # Update debate rounds
            await self.orchestrator.update_debate_rounds(self.current_round)
            
            # Add performance metrics to logs
            if random.random() < 0.3:  # 30% chance
                metrics_msg = (
                    f"📊 System Metrics - "
                    f"CPU: {cpu_load:.1f}% | "
                    f"Memory: {memory_usage:.1f}% | "
                    f"Network: {network_activity:.1f}%"
                )
                await self.orchestrator.add_system_message(metrics_msg)
            
            await asyncio.sleep(2)

    async def _voting_consensus_demo(self):
        """Demonstrate voting and consensus mechanisms."""
        await asyncio.sleep(10)  # Let other systems establish
        
        voting_cycle = 0
        
        while self.is_running:
            voting_cycle += 1
            
            # Start voting phase
            await self.orchestrator.update_phase("collaboration", "voting")
            await self.orchestrator.add_system_message(
                f"🗳️ Starting voting cycle {voting_cycle}"
            )
            
            # Simulate agents casting votes
            vote_distribution = {}
            
            for agent_config in self.demo_agents:
                if not self.is_running:
                    break
                
                agent_id = agent_config["id"]
                
                # Update agent status to voting
                await self.orchestrator.update_agent_status(agent_id, "voting")
                
                # Simulate vote decision time
                await asyncio.sleep(1)
                
                # Cast vote (agents tend to vote for others, sometimes themselves)
                if random.random() < 0.8:  # 80% vote for others
                    vote_target = random.choice([
                        aid for aid in range(len(self.demo_agents)) 
                        if aid != agent_id
                    ])
                else:
                    vote_target = agent_id
                
                # Update vote target
                await self.orchestrator.update_agent_vote_target(agent_id, vote_target)
                
                # Record vote
                if vote_target not in vote_distribution:
                    vote_distribution[vote_target] = 0
                vote_distribution[vote_target] += 1
                
                # Update votes cast count
                current_votes = voting_cycle
                await self.orchestrator.update_agent_votes_cast(agent_id, current_votes)
                
                await self.orchestrator.stream_output(
                    agent_id,
                    f"🗳️ Vote cast for Agent {vote_target}\n"
                )
                
                await self.orchestrator.update_agent_status(agent_id, "voted")
                
                await asyncio.sleep(0.5)
            
            # Update vote distribution
            await self.orchestrator.update_vote_distribution(vote_distribution)
            
            # Check for consensus (simple majority)
            max_votes = max(vote_distribution.values()) if vote_distribution else 0
            total_votes = sum(vote_distribution.values())
            
            if max_votes > total_votes / 2:
                # Consensus reached
                representative_id = max(vote_distribution.items(), key=lambda x: x[1])[0]
                
                await self.orchestrator.update_consensus_status(
                    representative_id, vote_distribution
                )
                
                await self.orchestrator.update_phase("voting", "consensus")
                
                # Celebrate consensus
                await asyncio.sleep(3)
                
                # Reset for next cycle
                await self.orchestrator.reset_consensus()
                await self.orchestrator.update_phase("consensus", "collaboration")
                
                await asyncio.sleep(5)
            else:
                # No consensus, continue
                await self.orchestrator.add_system_message(
                    "❌ No consensus reached - continuing discussion"
                )
                await self.orchestrator.update_phase("voting", "collaboration")
                await asyncio.sleep(3)
            
            # Wait before next voting cycle
            await asyncio.sleep(15)

    async def _real_time_updates_demo(self):
        """Demonstrate real-time updates and streaming capabilities."""
        await asyncio.sleep(5)
        
        update_counter = 0
        
        while self.is_running:
            update_counter += 1
            
            # Simulate various types of real-time events
            event_types = [
                ("info", "🔍 Processing new data batch"),
                ("success", "✅ Model checkpoint saved"),
                ("warning", "⚠️ High memory usage detected"),
                ("info", "📊 Performance metrics updated"),
                ("success", "🎯 Target accuracy achieved"),
                ("info", "🔄 Background optimization running"),
            ]
            
            if random.random() < 0.6:  # 60% chance of system event
                level, message = random.choice(event_types)
                await self.orchestrator.add_system_message(
                    f"[{update_counter:04d}] {message}"
                )
            
            # Occasional agent-specific updates
            if random.random() < 0.4:  # 40% chance of agent event
                agent_config = random.choice(self.demo_agents)
                agent_id = agent_config["id"]
                
                agent_events = [
                    "💡 New insight discovered",
                    "🔍 Exploring alternative approach",
                    "📈 Confidence score updated",
                    "🛠️ Adjusting parameters",
                    "📝 Documenting findings",
                ]
                
                event = random.choice(agent_events)
                await self.orchestrator.stream_output(
                    agent_id,
                    f"  → {event}\n"
                )
            
            # Dynamic status changes
            if random.random() < 0.2:  # 20% chance of status change
                agent_config = random.choice(self.demo_agents)
                agent_id = agent_config["id"]
                
                new_status = random.choice(["thinking", "working", "completed"])
                await self.orchestrator.update_agent_status(agent_id, new_status)
            
            await asyncio.sleep(1.5)

    async def _cleanup_demo(self):
        """Clean up demo resources."""
        self.is_running = False
        
        if self.orchestrator:
            await self.orchestrator.add_system_message("🛑 Demo shutting down...")
            
            # Update all agents to completed status
            for agent_config in self.demo_agents:
                await self.orchestrator.update_agent_status(
                    agent_config["id"], "completed"
                )
            
            await self.orchestrator.add_system_message("👋 Demo completed successfully")
            
            # Give time for final updates
            await asyncio.sleep(2)
            
            # Cleanup orchestrator
            self.orchestrator.cleanup()


async def main():
    """Main entry point for the demo."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🚀 State-of-the-Art Canopy TUI Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python modern_tui_demo.py                    # Run with default settings
  python modern_tui_demo.py --web              # Enable web deployment mode
  python modern_tui_demo.py --theme light      # Use light theme
  python modern_tui_demo.py --web --theme dark # Web mode with dark theme

WEB MODE:
  When --web is enabled, the TUI will be ready for deployment with textual-serve:
  textual serve modern_tui_demo.py:app --host 0.0.0.0 --port 8080
        """
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Enable web deployment mode (textual-serve compatible)"
    )
    
    parser.add_argument(
        "--theme",
        choices=["dark", "light"],
        default="dark",
        help="UI theme (default: dark)"
    )
    
    args = parser.parse_args()
    
    # Create and run demo
    demo = ModernTUIDemo(web_mode=args.web, theme=args.theme)
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


# For textual-serve deployment
def create_app():
    """Create app instance for textual-serve deployment."""
    from canopy_core.tui.modern_app import create_modern_canopy_tui
    return create_modern_canopy_tui(web_mode=True)


if __name__ == "__main__":
    print("🚀 Canopy State-of-the-Art TUI Demo")
    print("=" * 50)
    asyncio.run(main())