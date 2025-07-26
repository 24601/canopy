#!/usr/bin/env python3
"""
🔥🤖 SENTIENT TUI DESTROYER LAUNCHER 🤖🔥
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from canopy_core.tui.advanced_app import AdvancedCanopyTUI

# Now import the destroyer
from tests.tui.sentient_tui_destroyer import destroy_tui


async def main():
    """Launch the Sentient TUI Destroyer with maximum power."""

    print("🔥🤖 SENTIENT TUI DESTROYER - PREPARING FOR LAUNCH 🤖🔥")
    print("=" * 80)

    # Check for API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not gemini_key and not openai_key:
        print("⚠️  WARNING: No AI API keys found!")
        print("   Set GEMINI_API_KEY and/or OPENAI_API_KEY for full AI power")
        print("   Proceeding with basic testing only...")
    else:
        print(f"✅ AI Power Detected:")
        if gemini_key:
            print(f"   🧠 Gemini API: Ready for vision analysis")
        if openai_key:
            print(f"   🤖 OpenAI API: Ready for reasoning")

    print("\n🚀 LAUNCHING DESTROYER IN 3 SECONDS...")
    await asyncio.sleep(1)
    print("3...")
    await asyncio.sleep(1)
    print("2...")
    await asyncio.sleep(1)
    print("1...")
    await asyncio.sleep(1)
    print("\n💥 DESTROYER ACTIVATED! 💥")

    try:
        # UNLEASH THE DESTROYER
        results = await destroy_tui(
            app_class=AdvancedCanopyTUI,
            brutal_mode=True,  # MAXIMUM BRUTALITY
            auto_fix=True,  # AUTO-GENERATE FIXES
            max_duration=900,  # 15 minutes of destruction
            output_dir="destroyer_results_" + str(int(asyncio.get_event_loop().time())),
        )

        # Display epic results
        print("\n" + "=" * 80)
        print("🎯 DESTRUCTION RESULTS:")
        print("=" * 80)

        total_issues = results.get("reporting", {}).get("total_issues", 0)
        critical_issues = results.get("reporting", {}).get("critical_issues", 0)

        print(f"📊 Total Issues Found: {total_issues}")
        print(f"🚨 Critical Issues: {critical_issues}")

        if critical_issues > 0:
            print(f"\n🚨 CRITICAL ISSUES DETECTED - IMMEDIATE ACTION REQUIRED!")
            print(f"   Check the generated reports for detailed fixes")
        elif total_issues > 0:
            print(f"\n⚠️  Issues found but none critical")
            print(f"   Review the reports for improvements")
        else:
            print(f"\n🏆 PERFECT! NO ISSUES FOUND!")
            print(f"   Your TUI is rock solid!")

        # Show report location
        if "reporting" in results:
            html_report = results["reporting"].get("html_report")
            if html_report:
                print(f"\n📊 Full Report: {html_report}")

        return results

    except Exception as e:
        print(f"\n💥 DESTROYER ENCOUNTERED CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Set some default environment for testing if not present
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("📝 Note: For full AI power, set environment variables:")
        print("   export GEMINI_API_KEY='your_key'")
        print("   export OPENAI_API_KEY='your_key'")

    results = asyncio.run(main())

    # Exit with appropriate code
    if results and results.get("reporting", {}).get("critical_issues", 0) > 0:
        sys.exit(1)  # Critical issues found
    else:
        sys.exit(0)  # Success or manageable issues
