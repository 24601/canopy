#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canopy (Multi-Agent Scaling System) - Command Line Interface

This provides a clean command-line interface for the Canopy system.

Usage examples:
    # Use YAML configuration file
    python cli.py "What is 2+2?" --config examples/production.yaml

    # Use model names directly (single or multiple agents)
    python cli.py "What is 2+2?" --models gpt-4o gemini-2.5-flash
    python cli.py "What is 2+2?" --models gpt-4o  # Single agent mode

    # Interactive mode (no question provided)
    python cli.py --models gpt-4o grok-4
"""

import argparse
import sys
from pathlib import Path

from canopy_core import ConfigurationError, create_config_from_models, load_config_from_yaml, run_mass_with_config

# Add path if needed for imports
sys.path.insert(0, str(Path(__file__).parent))

# Color constants for beautiful terminal output
BRIGHT_CYAN = "\033[96m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_RED = "\033[91m"
BRIGHT_WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


def display_vote_distribution(vote_distribution):
    """Display the vote distribution in a more readable format."""
    # sort the keys
    sorted_keys = sorted(vote_distribution.keys())
    for agent_id in sorted_keys:
        print(f"      {BRIGHT_CYAN}Agent {agent_id}{RESET}: {BRIGHT_GREEN}{vote_distribution[agent_id]}{RESET} votes")


def run_interactive_mode(config):
    """Run Canopy in interactive mode, asking for questions repeatedly."""

    print("\n🤖 Canopy Interactive Mode")
    print("=" * 60)

    # Display current configuration
    print("📋 Current Configuration:")
    print("-" * 30)

    # Show models/agents
    if hasattr(config, "agents") and config.agents:
        print(f"🤖 Agents ({len(config.agents)}):")
        for i, agent in enumerate(config.agents, 1):
            model_name = (
                getattr(agent.model_config, "model", "Unknown") if hasattr(agent, "model_config") else "Unknown"
            )
            agent_type = getattr(agent, "agent_type", "Unknown")
            tools = getattr(agent.model_config, "tools", []) if hasattr(agent, "model_config") else []
            tools_str = ", ".join(tools) if tools else "None"
            print(f"   {i}. {model_name} ({agent_type})")
            print(f"      Tools: {tools_str}")
    else:
        print("🤖 Single Agent Mode")

    # Show orchestrator settings
    if hasattr(config, "orchestrator"):
        orch = config.orchestrator
        print("⚙️  Orchestrator:")
        print(f"   • Algorithm: {getattr(orch, 'algorithm', 'massgen')}")
        print(f"   • Duration: {getattr(orch, 'max_duration', 'Default')}s")
        print(f"   • Consensus: {getattr(orch, 'consensus_threshold', 'Default')}")
        print(f"   • Max Debate Rounds: {getattr(orch, 'max_debate_rounds', 'Default')}")

    # Show model parameters (from first agent as representative)
    if hasattr(config, "agents") and config.agents and hasattr(config.agents[0], "model_config"):
        model_config = config.agents[0].model_config
        print("🔧 Model Config:")
        temp = getattr(model_config, "temperature", "Default")
        timeout = getattr(model_config, "inference_timeout", "Default")
        max_rounds = getattr(model_config, "max_rounds", "Default")
        print(f"   • Temperature: {temp}")
        print(f"   • Timeout: {timeout}s")
        print(f"   • Max Debate Rounds: {max_rounds}")

    # Show display settings
    if hasattr(config, "streaming_display"):
        display = config.streaming_display
        display_status = "✅ Enabled" if getattr(display, "display_enabled", True) else "❌ Disabled"
        logs_status = "✅ Enabled" if getattr(display, "save_logs", True) else "❌ Disabled"
        print(f"📺 Display: {display_status}")
        print(f"📁 Logs: {logs_status}")

    print("-" * 30)
    print("💬 Type your questions below. Type 'quit', 'exit', or press Ctrl+C to stop.")
    print("=" * 60)

    chat_history = ""
    try:
        while True:
            try:
                question = input("\n👤 User: ").strip()
                chat_history += f"User: {question}\n"

                if question.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if not question:
                    print("Please enter a question or type 'quit' to exit.")
                    continue

                print("\n🔄 Processing your question...")

                # Run Canopy
                result = run_mass_with_config(chat_history, config)

                response = result["answer"]
                chat_history += f"Assistant: {response}\n"

                # Display complete conversation exchange
                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")
                print(f"{BOLD}{BRIGHT_WHITE}💬 CONVERSATION EXCHANGE{RESET}")
                print(f"{BRIGHT_CYAN}{'='*80}{RESET}")

                # User input section with simple indentation
                print(f"\n{BRIGHT_BLUE}👤 User:{RESET}")
                print(f"    {BRIGHT_WHITE}{question}{RESET}")

                # Assistant response section
                print(f"\n{BRIGHT_GREEN}🤖 Assistant:{RESET}")

                agents = {f"Agent {agent.agent_id}": agent.model_config.model for agent in config.agents}

                # Show metadata with clean indentation
                if result.get("single_agent_mode", False):
                    print(f"    {BRIGHT_YELLOW}📋 Mode:{RESET} Single Agent")
                    print(f"    {BRIGHT_MAGENTA}🤖 Agents:{RESET} {agents}")
                    print(f"    {BRIGHT_CYAN}🎯 Representative:{RESET} {result['representative_agent_id']}")
                    print(f"    {BRIGHT_GREEN}🔧 Model:{RESET} {result.get('model_used', 'Unknown')}")
                    print(f"    {BRIGHT_BLUE}⏱️  Duration:{RESET} {result['session_duration']:.1f}s")
                    if result.get("citations"):
                        print(f"    {BRIGHT_WHITE}📚 Citations:{RESET} {len(result['citations'])}")
                    if result.get("code"):
                        print(f"    {BRIGHT_WHITE}💻 Code blocks:{RESET} {len(result['code'])}")
                else:
                    print(f"    {BRIGHT_YELLOW}📋 Mode:{RESET} Multi-Agent")
                    print(f"    {BRIGHT_MAGENTA}🤖 Agents:{RESET} {agents}")
                    print(f"    {BRIGHT_CYAN}🎯 Representative:{RESET} {result['representative_agent_id']}")
                    print(f"    {BRIGHT_GREEN}✅ Consensus:{RESET} {result['consensus_reached']}")
                    print(f"    {BRIGHT_BLUE}⏱️  Duration:{RESET} {result['session_duration']:.1f}s")
                    print(f"    {BRIGHT_YELLOW}📊 Vote Distribution:{RESET}")
                    display_vote_distribution(result["summary"]["final_vote_distribution"])

                # Print the response with simple indentation
                print(f"\n    {BRIGHT_RED}💡 Response:{RESET}")
                # Indent the response content
                for line in response.split("\n"):
                    print(f"        {line}")

                print(f"\n{BRIGHT_CYAN}{'='*80}{RESET}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                print("Please try again or type 'quit' to exit.")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


def main():
    """Clean CLI interface for Canopy."""
    parser = argparse.ArgumentParser(
        description="Canopy (Multi-Agent Scaling System) - Clean CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use YAML configuration
  python cli.py "What is the capital of France?" --config examples/production.yaml

  # Use model names directly (single or multiple agents)
  python cli.py "What is 2+2?" --models gpt-4o gemini-2.5-flash
  python cli.py "What is 2+2?" --models gpt-4o  # Single agent mode

  # Interactive mode (no question provided)
  python cli.py --models gpt-4o grok-4

  # Override parameters
  python cli.py "Question" --models gpt-4o gemini-2.5-flash --max-duration 1200 --consensus 0.8

  # Use TreeQuest algorithm
  python cli.py "Question" --models gpt-4o gemini-2.5-flash --algorithm treequest
        """,
    )

    # Task input (now optional for interactive mode)
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to solve (optional - if not provided, enters interactive mode)",
    )

    # Special actions
    parser.add_argument("--list-profiles", action="store_true", help="List available algorithm profiles")
    parser.add_argument("--serve", action="store_true", help="Start OpenAI-compatible API server")
    parser.add_argument("--port", type=int, default=8000, help="API server port (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API server host (default: 0.0.0.0)")

    # Configuration options (mutually exclusive)
    config_group = parser.add_mutually_exclusive_group(required=False)
    config_group.add_argument("--config", type=str, help="Path to YAML configuration file")
    config_group.add_argument("--models", nargs="+", help="Model names (e.g., gpt-4o gemini-2.5-flash)")

    # Configuration overrides
    parser.add_argument("--max-duration", type=int, default=None, help="Max duration in seconds")
    parser.add_argument("--consensus", type=float, default=None, help="Consensus threshold (0.0-1.0)")
    parser.add_argument("--max-debates", type=int, default=None, help="Maximum debate rounds")
    parser.add_argument(
        "--algorithm",
        type=str,
        default=None,
        choices=["massgen", "treequest"],
        help="Orchestration algorithm to use (default: massgen)",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="Algorithm profile name (e.g., treequest-sakana, massgen-diverse)",
    )
    parser.add_argument("--no-display", action="store_true", help="Disable streaming display")
    parser.add_argument("--no-logs", action="store_true", help="Disable file logging")
    parser.add_argument("--tui", action="store_true", help="Use advanced Textual TUI interface")
    parser.add_argument(
        "--tui-theme", type=str, default="dark", choices=["dark", "light"], help="TUI theme (default: dark)"
    )

    args = parser.parse_args()

    # Handle --list-profiles
    if args.list_profiles:
        from canopy_core.algorithms.profiles import describe_profile, list_profiles

        profiles = list_profiles()
        print("\n📋 Available Algorithm Profiles:")
        print("=" * 60)
        for profile_name in sorted(profiles):
            print(f"\n{describe_profile(profile_name)}")
            print("-" * 60)
        return

    # Handle --tui (Advanced TUI mode)
    if args.tui:
        import asyncio

        from canopy_core.tui.advanced_app import AdvancedCanopyTUI

        print(f"\n{BRIGHT_CYAN}🚀 Starting Advanced Canopy TUI{RESET}")
        print(f"{BRIGHT_YELLOW}📡 Theme: {args.tui_theme}{RESET}")
        print(f"{BRIGHT_GREEN}💡 Press 'q' to quit, 'r' to refresh, 'p' to pause{RESET}")
        print(f"\n{DIM}Starting TUI in 2 seconds...{RESET}\n")

        import time

        time.sleep(2)

        try:
            # Load configuration
            if not args.config and not args.models:
                print("❌ Error: Either --config or --models is required for TUI mode")
                sys.exit(1)

            if args.config:
                config = load_config_from_yaml(args.config)
            else:
                config = create_config_from_models(args.models)

            # Apply overrides
            if args.max_duration is not None:
                config.orchestrator.max_duration = args.max_duration
            if args.consensus is not None:
                config.orchestrator.consensus_threshold = args.consensus
            if args.max_debates is not None:
                config.orchestrator.max_debate_rounds = args.max_debates
            if args.algorithm is not None:
                config.orchestrator.algorithm = args.algorithm
            if args.no_display:
                config.streaming_display.display_enabled = False
            if args.no_logs:
                config.streaming_display.save_logs = False

            config.validate()

            # Start TUI
            app = AdvancedCanopyTUI(theme=args.tui_theme)

            # If question provided, we'll handle it in TUI mode
            if args.question:
                # TODO: Integrate question handling into TUI
                pass

            app.run()

        except KeyboardInterrupt:
            print(f"\n{BRIGHT_YELLOW}👋 TUI stopped by user{RESET}")
        except Exception as e:
            print(f"\n{BRIGHT_RED}❌ TUI error: {e}{RESET}")
            import traceback

            traceback.print_exc()
        return

    # Handle --serve (API server mode)
    if args.serve:
        import uvicorn

        from canopy_core.api_server import app

        print(f"\n{BRIGHT_CYAN}🚀 Starting Canopy API Server{RESET}")
        print(f"{BRIGHT_YELLOW}📡 Host: {args.host}:{args.port}{RESET}")
        print(
            f"{BRIGHT_GREEN}📚 Docs: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/docs{RESET}"
        )
        print(
            f"{BRIGHT_BLUE}🔗 OpenAPI: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}/openapi.json{RESET}"
        )
        print(f"\n{BRIGHT_WHITE}Available endpoints:{RESET}")
        print("  • POST /v1/chat/completions    - OpenAI Chat API compatible")
        print("  • POST /v1/completions         - OpenAI Completions API compatible")
        print("  • GET  /v1/models              - List available models")
        print("  • GET  /health                 - Health check")
        print(f"\n{DIM}Press CTRL+C to stop the server{RESET}\n")

        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return

    # Load configuration
    try:
        # Check if we need a configuration
        if not args.config and not args.models:
            print("❌ Error: Either --config or --models is required")
            parser.print_help()
            sys.exit(1)

        if args.config:
            config = load_config_from_yaml(args.config)
        else:  # args.models
            config = create_config_from_models(args.models)

        # Apply command-line overrides
        if args.max_duration is not None:
            config.orchestrator.max_duration = args.max_duration
        if args.consensus is not None:
            config.orchestrator.consensus_threshold = args.consensus
        if args.max_debates is not None:
            config.orchestrator.max_debate_rounds = args.max_debates
        if args.algorithm is not None:
            config.orchestrator.algorithm = args.algorithm
        if args.profile is not None:
            config.orchestrator.algorithm_profile = args.profile
            # If using a profile, we might need to adjust the agents
            from canopy_core.algorithms.profiles import get_profile

            profile = get_profile(args.profile)
            if profile and not args.config:  # Only override agents if not using a config file
                # Create agent configs from profile
                from canopy_core.types import AgentConfig, ModelConfig

                config.agents = []
                for i, model_config in enumerate(profile.models, 1):
                    agent_config = AgentConfig(
                        agent_id=i,
                        agent_type=model_config["agent_type"],
                        model_config=ModelConfig(**{k: v for k, v in model_config.items() if k != "agent_type"}),
                    )
                    config.agents.append(agent_config)
        if args.no_display:
            config.streaming_display.display_enabled = False
        if args.no_logs:
            config.streaming_display.save_logs = False

        # Validate final configuration
        config.validate()

        # The used models
        agents = {f"Agent {agent.agent_id}": agent.model_config.model for agent in config.agents}

        # Check if question was provided
        if args.question:
            # Single question mode
            result = run_mass_with_config(args.question, config)

            # Display results
            print("\n" + "=" * 60)
            print(f"🎯 FINAL ANSWER (Agent {result['representative_agent_id']}):")
            print("=" * 60)
            print(result["answer"])
            print("\n" + "=" * 60)

            # Show different metadata based on single vs multi-agent mode
            if result.get("single_agent_mode", False):
                print("🤖 Single Agent Mode")
                print(f"🤖 Agents: {agents}")
                print(f"⏱️  Duration: {result['session_duration']:.1f}s")
                if result.get("citations"):
                    print(f"📚 Citations: {len(result['citations'])}")
                if result.get("code"):
                    print(f"💻 Code blocks: {len(result['code'])}")
            else:
                print(f"🤖 Agents: {agents}")
                print(f"🎯 Representative Agent: {result['representative_agent_id']}")
                print(f"✅ Consensus: {result['consensus_reached']}")
                print(f"⏱️  Duration: {result['session_duration']:.1f}s")
                print("📊 Votes:")
                display_vote_distribution(result["summary"]["final_vote_distribution"])
        else:
            # Interactive mode
            run_interactive_mode(config)

    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
