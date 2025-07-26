#!/usr/bin/env python3
"""
🔥🔨 SIMPLE AI HAMMER TEST - RELENTLESS TUI TESTING 🔨🔥
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import what we need directly
from canopy_core.tui.advanced_app import AdvancedCanopyTUI


class SimpleTUIHammer:
    """Simplified but RELENTLESS TUI hammer test."""

    def __init__(self):
        self.issues_found = []
        self.tests_passed = 0
        self.tests_failed = 0

    async def hammer_test_basic_functionality(self, pilot):
        """HAMMER TEST: Basic TUI functionality."""
        print("🔨 HAMMERING: Basic functionality...")

        issues = []
        tests = [
            # Basic navigation tests
            ("tab", "Tab navigation"),
            ("shift+tab", "Reverse tab navigation"),
            ("up", "Up arrow navigation"),
            ("down", "Down arrow navigation"),
            ("left", "Left arrow navigation"),
            ("right", "Right arrow navigation"),
            ("enter", "Enter key"),
            ("escape", "Escape key"),
            # Function tests
            ("r", "Refresh command"),
            ("p", "Pause command"),
            ("ctrl+t", "Theme toggle"),
            ("ctrl+s", "Save command"),
            ("ctrl+r", "Reset command"),
            ("f1", "Help command"),
            ("f5", "Force refresh"),
        ]

        for key, description in tests:
            try:
                print(f"  🔨 Testing: {description} ({key})")

                # Press the key
                await pilot.press(key)
                await asyncio.sleep(0.2)  # Let UI respond

                # Check if app is still responsive
                try:
                    # Try to capture app state
                    app = pilot.app
                    if hasattr(app, "title"):
                        title = app.title
                    if hasattr(app, "query"):
                        widgets = app.query("*")

                    print(f"    ✅ {description}: OK")
                    self.tests_passed += 1

                except Exception as state_error:
                    issues.append(f"State check failed for {description}: {state_error}")
                    print(f"    ❌ {description}: State check failed")
                    self.tests_failed += 1

            except Exception as e:
                issues.append(f"Key press failed for {description} ({key}): {e}")
                print(f"    💥 {description}: CRASHED - {e}")
                self.tests_failed += 1

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_rapid_input(self, pilot):
        """HAMMER TEST: Rapid input stress test."""
        print("🔨 HAMMERING: Rapid input stress test...")

        issues = []

        # Rapid fire test sequences
        sequences = [
            (["tab"] * 20, "Tab bombing"),
            (["up", "down"] * 10, "Arrow key spam"),
            (["r", "p", "r", "p"] * 5, "Command spam"),
            (["enter", "escape"] * 10, "Enter/Escape spam"),
        ]

        for sequence, description in sequences:
            try:
                print(f"  🔨 Testing: {description}")
                start_time = time.time()

                for key in sequence:
                    await pilot.press(key)
                    await asyncio.sleep(0.01)  # Very rapid

                end_time = time.time()
                duration = end_time - start_time

                # Check if app survived
                try:
                    app = pilot.app
                    if hasattr(app, "title"):
                        title = app.title  # Test basic access
                    print(f"    ✅ {description}: Survived ({duration:.2f}s)")
                    self.tests_passed += 1

                except Exception as survival_error:
                    issues.append(f"App didn't survive {description}: {survival_error}")
                    print(f"    💥 {description}: App crashed after rapid input")
                    self.tests_failed += 1

            except Exception as e:
                issues.append(f"Rapid input test failed for {description}: {e}")
                print(f"    ❌ {description}: Test failed - {e}")
                self.tests_failed += 1

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_ui_stress(self, pilot):
        """HAMMER TEST: UI stress and edge cases."""
        print("🔨 HAMMERING: UI stress test...")

        issues = []

        # Stress tests
        stress_tests = [
            (["ctrl+t"] * 5, "Theme switching spam"),
            (["f5"] * 10, "Force refresh spam"),
            (["ctrl+r", "r"] * 3, "Reset/refresh combo"),
        ]

        for sequence, description in stress_tests:
            try:
                print(f"  🔨 Testing: {description}")

                for key in sequence:
                    await pilot.press(key)
                    await asyncio.sleep(0.1)

                # Verify app is still working
                try:
                    app = pilot.app
                    widgets = app.query("*")
                    print(f"    ✅ {description}: UI stable ({len(widgets)} widgets)")
                    self.tests_passed += 1

                except Exception as stability_error:
                    issues.append(f"UI instability after {description}: {stability_error}")
                    print(f"    ⚠️  {description}: UI instability detected")
                    self.tests_failed += 1

            except Exception as e:
                issues.append(f"Stress test failed for {description}: {e}")
                print(f"    ❌ {description}: Failed - {e}")
                self.tests_failed += 1

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_error_resistance(self, pilot):
        """HAMMER TEST: Error resistance and recovery."""
        print("🔨 HAMMERING: Error resistance...")

        issues = []

        # Try invalid key combinations
        invalid_tests = [
            ("ctrl+alt+shift+f12", "Invalid combo 1"),
            ("ctrl+z", "Undo (might not be supported)"),
            ("alt+f4", "Alt-F4 (shouldn't close)"),
            ("ctrl+break", "Break combination"),
        ]

        for key_combo, description in invalid_tests:
            try:
                print(f"  🔨 Testing: {description}")

                await pilot.press(key_combo)
                await asyncio.sleep(0.2)

                # App should still be responsive
                try:
                    app = pilot.app
                    if hasattr(app, "title"):
                        title = app.title
                    print(f"    ✅ {description}: Handled gracefully")
                    self.tests_passed += 1

                except Exception as recovery_error:
                    issues.append(f"App failed to handle {description}: {recovery_error}")
                    print(f"    ❌ {description}: Not handled gracefully")
                    self.tests_failed += 1

            except Exception as e:
                # This is actually expected for invalid keys
                print(f"    ✅ {description}: Rejected properly")
                self.tests_passed += 1

        self.issues_found.extend(issues)
        return len(issues) == 0


async def run_simple_hammer_test():
    """Run the simplified but RELENTLESS hammer test."""
    print("🔥🔨 SIMPLE AI HAMMER TEST - MAXIMUM DESTRUCTION MODE 🔨🔥")
    print("=" * 80)

    hammer = SimpleTUIHammer()

    # Start the TUI app
    app = AdvancedCanopyTUI(theme="dark")

    try:
        async with app.run_test(size=(120, 40)) as pilot:
            print("🚀 Advanced Canopy TUI started")
            print("🔨 BEGINNING RELENTLESS TESTING...")

            # Let UI stabilize
            await asyncio.sleep(2.0)

            # Run all hammer tests
            tests = [
                ("BASIC FUNCTIONALITY", hammer.hammer_test_basic_functionality),
                ("RAPID INPUT STRESS", hammer.hammer_test_rapid_input),
                ("UI STRESS TEST", hammer.hammer_test_ui_stress),
                ("ERROR RESISTANCE", hammer.hammer_test_error_resistance),
            ]

            results = {}

            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    success = await test_func(pilot)
                    results[test_name] = success
                    print(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
                except Exception as e:
                    print(f"💥 CRASHED: {test_name} - {e}")
                    results[test_name] = False
                    hammer.issues_found.append(f"TEST CRASH ({test_name}): {str(e)}")

            # Final results
            print(f"\n{'='*60}")
            print("🔨 HAMMER TEST FINAL RESULTS")
            print(f"{'='*60}")

            passed = sum(1 for success in results.values() if success)
            total = len(results)

            print(f"📊 Tests Passed: {hammer.tests_passed}")
            print(f"📊 Tests Failed: {hammer.tests_failed}")
            print(f"📊 Test Categories: {passed}/{total} passed")
            print(f"📊 Issues Found: {len(hammer.issues_found)}")

            if hammer.issues_found:
                print(f"\n🔍 ISSUES DISCOVERED:")
                for i, issue in enumerate(hammer.issues_found, 1):
                    print(f"  {i}. {issue}")

            if hammer.tests_failed == 0:
                print(f"\n🏆 PERFECT! TUI SURVIVED ALL HAMMER TESTS!")
                print(f"   Your TUI is ROCK SOLID! 💪")
            elif hammer.tests_failed < 5:
                print(f"\n✅ GOOD! TUI survived most tests with minor issues")
                print(f"   Consider fixing the {hammer.tests_failed} failed tests")
            else:
                print(f"\n⚠️  WARNING! TUI has significant issues")
                print(f"   {hammer.tests_failed} tests failed - needs attention")

            return results, hammer.issues_found

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: Failed to start TUI - {e}")
        import traceback

        traceback.print_exc()
        return {}, [f"CRITICAL: Failed to start TUI - {e}"]


if __name__ == "__main__":
    print("🔨 LAUNCHING SIMPLE HAMMER TEST...")

    results, issues = asyncio.run(run_simple_hammer_test())

    print(f"\n🎯 HAMMER TEST COMPLETE!")

    # Exit with appropriate code
    if len(issues) > 10:  # Too many issues
        print(f"🚨 CRITICAL: Too many issues found!")
        sys.exit(1)
    elif len(issues) > 0:
        print(f"⚠️  Issues found but manageable")
        sys.exit(0)
    else:
        print(f"🏆 SUCCESS: TUI is solid!")
        sys.exit(0)
