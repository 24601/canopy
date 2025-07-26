#!/usr/bin/env python3
"""
Debug Agent Registration Issue
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from canopy_core.tui.advanced_app import AdvancedCanopyTUI, AgentProgressWidget


async def debug_agent_registration():
    """Debug the agent registration process."""
    print("🔍 DEBUGGING AGENT REGISTRATION ISSUE")
    print("=" * 60)

    try:
        app = AdvancedCanopyTUI(theme="dark")

        async with app.run_test(size=(120, 40)) as pilot:
            print("✅ TUI started successfully")

            # Check initial state
            agents_before = app.query("AgentProgressWidget")
            print(f"📊 Agents before registration: {len(agents_before)}")

            # Check if agents container exists
            try:
                container = app.query_one("#agents-container")
                print(f"✅ Agents container found: {container}")

                # Check container children
                children = list(container.children)
                print(f"📋 Container children before: {len(children)}")
                for i, child in enumerate(children):
                    print(f"   {i+1}. {child.__class__.__name__} (id: {getattr(child, 'id', None)})")

            except Exception as e:
                print(f"❌ Agents container not found: {e}")
                return

            # Try to add an agent
            print(f"\n🤖 Adding agent...")
            try:
                await app.add_agent(1, "Debug-Agent")
                print("✅ add_agent() called successfully")

                # Small delay to allow UI updates
                await asyncio.sleep(0.2)

            except Exception as e:
                print(f"❌ add_agent() failed: {e}")
                import traceback

                traceback.print_exc()
                return

            # Check state after adding agent
            agents_after = app.query("AgentProgressWidget")
            print(f"📊 Agents after registration: {len(agents_after)}")

            # Check container children again
            try:
                container = app.query_one("#agents-container")
                children = list(container.children)
                print(f"📋 Container children after: {len(children)}")
                for i, child in enumerate(children):
                    print(f"   {i+1}. {child.__class__.__name__} (id: {getattr(child, 'id', None)})")

            except Exception as e:
                print(f"❌ Container check failed: {e}")

            # Try to find the specific agent widget
            try:
                agent_widget = app.query_one("#agent-1")
                print(f"✅ Agent widget found: {agent_widget}")
            except Exception as e:
                print(f"❌ Agent widget not found: {e}")

            # Check if placeholder was removed
            try:
                placeholder = app.query_one("#agents-placeholder")
                print(f"⚠️  Placeholder still exists: {placeholder}")
            except Exception as e:
                print(f"✅ Placeholder was removed (as expected)")

            # Final summary
            if len(agents_after) > len(agents_before):
                print(f"\n🎉 SUCCESS: Agent registration worked!")
                print(f"   Before: {len(agents_before)} agents")
                print(f"   After: {len(agents_after)} agents")
            else:
                print(f"\n❌ FAILURE: Agent registration did not work")
                print(f"   Before: {len(agents_before)} agents")
                print(f"   After: {len(agents_after)} agents")

                # Let's try to manually create the widget to see if that works
                print(f"\n🧪 Testing manual widget creation...")
                try:
                    manual_widget = AgentProgressWidget(agent_id=999, model_name="Manual-Test")
                    print(f"✅ Manual widget created: {manual_widget}")

                    # Try to mount it manually
                    await container.mount(manual_widget)
                    print(f"✅ Manual widget mounted successfully")

                    # Check again
                    agents_manual = app.query("AgentProgressWidget")
                    print(f"📊 Agents after manual mount: {len(agents_manual)}")

                except Exception as manual_error:
                    print(f"❌ Manual widget creation failed: {manual_error}")
                    import traceback

                    traceback.print_exc()

    except Exception as e:
        print(f"💥 Debug session failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_agent_registration())
