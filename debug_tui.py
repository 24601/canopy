#!/usr/bin/env python3
"""
Debug TUI - Find the actual fucking issues
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 DEBUGGING TUI INITIALIZATION ISSUES...")

# Test basic imports first
print("📦 Testing imports...")

try:
    print("   1. Testing canopy_core.tui.themes...")
    from canopy_core.tui.themes import THEMES, ThemeManager

    print("      ✅ themes imported successfully")
except Exception as e:
    print(f"      ❌ themes import failed: {e}")
    traceback.print_exc()

try:
    print("   2. Testing canopy_core.types...")
    from canopy_core.types import AgentState, SystemState, VoteDistribution

    print("      ✅ types imported successfully")
except Exception as e:
    print(f"      ❌ types import failed: {e}")
    traceback.print_exc()

try:
    print("   3. Testing canopy_core.logging...")
    from canopy_core.logging import get_logger

    print("      ✅ logging imported successfully")
except Exception as e:
    print(f"      ❌ logging import failed: {e}")
    traceback.print_exc()

try:
    print("   4. Testing textual widgets...")
    from textual.widgets import Button, DataTable, Footer, Header, LoadingIndicator, ProgressBar, RichLog, Static

    print("      ✅ textual widgets imported successfully")
except Exception as e:
    print(f"      ❌ textual widgets import failed: {e}")
    traceback.print_exc()

# Now test the main TUI import
try:
    print("   5. Testing AdvancedCanopyTUI import...")
    from canopy_core.tui.advanced_app import AdvancedCanopyTUI

    print("      ✅ AdvancedCanopyTUI imported successfully")
except Exception as e:
    print(f"      ❌ AdvancedCanopyTUI import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test TUI instantiation
try:
    print("   6. Testing TUI instantiation...")
    app = AdvancedCanopyTUI(theme="dark")
    print("      ✅ TUI instantiated successfully")
except Exception as e:
    print(f"      ❌ TUI instantiation failed: {e}")
    traceback.print_exc()
    sys.exit(1)


# Test TUI startup
async def test_tui_startup():
    print("🚀 Testing TUI startup...")

    try:
        app = AdvancedCanopyTUI(theme="dark")
        print("   📱 Starting TUI in test mode...")

        async with app.run_test(size=(80, 24)) as pilot:
            print("   ✅ TUI started successfully!")

            # Test basic functionality
            print("   🔨 Testing basic key presses...")

            await pilot.press("tab")
            await asyncio.sleep(0.1)
            print("      ✅ Tab key works")

            await pilot.press("r")
            await asyncio.sleep(0.1)
            print("      ✅ Refresh key works")

            # Try to capture app state
            try:
                widgets = app.query("*")
                print(f"      📊 Found {len(widgets)} widgets")

                # List widget types
                widget_types = [w.__class__.__name__ for w in widgets]
                unique_types = list(set(widget_types))
                print(f"      🎯 Widget types: {', '.join(unique_types)}")

            except Exception as widget_error:
                print(f"      ⚠️  Widget query failed: {widget_error}")

            print("   🎯 TUI test completed successfully!")
            return True

    except Exception as e:
        print(f"   💥 TUI startup failed: {e}")
        traceback.print_exc()
        return False


async def main():
    success = await test_tui_startup()

    if success:
        print("\n🏆 TUI DEBUG PASSED - TUI is working!")
        return 0
    else:
        print("\n💥 TUI DEBUG FAILED - Issues found!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
