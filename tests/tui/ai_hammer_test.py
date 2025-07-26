"""
AI-POWERED HAMMER TEST for the REAL Canopy TUI
This will test EVERY DAMN THING using AI vision and reasoning.
LIKE A REAL HUMAN - but RELENTLESS!
"""

import asyncio
import os
import time

from test_harness import MultimodalTUITestHarness, TestMode, UserStoryPath

from canopy_core.tui.advanced_app import AdvancedCanopyTUI


class AIHammerTester:
    """AI-powered testing that HAMMERS every aspect of the TUI."""

    def __init__(self):
        self.harness = MultimodalTUITestHarness(
            app_class=AdvancedCanopyTUI,
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            test_mode=TestMode.MULTIMODAL if os.getenv("GEMINI_API_KEY") else TestMode.TEXT_ONLY,
            enable_reasoning=True,
            max_states=100,  # Allow for extensive testing
            output_dir="ai_hammer_results",
            enable_screenshots=True,
            enable_logging=True,
        )
        self.issues_found = []
        self.fixes_applied = []

    async def hammer_test_contrast_visibility(self, pilot):
        """HAMMER TEST: Contrast and visibility issues."""
        print("🔨 HAMMERING: Contrast and visibility...")

        issues = []

        # Capture initial state
        state = await self.harness.capture_tui_state(pilot, "contrast_test")

        # AI analysis of contrast
        analysis = await self.harness.analyze_state_multimodal(state)

        # Check for contrast problems
        if "visual_anomalies" in analysis:
            for anomaly in analysis["visual_anomalies"]:
                if any(
                    word in anomaly.lower() for word in ["dark", "gray", "dim", "contrast", "invisible", "hard to read"]
                ):
                    issues.append(f"CONTRAST ISSUE: {anomaly}")
                    print(f"❌ FOUND CONTRAST PROBLEM: {anomaly}")

        # Check text visibility
        if "text_content_summary" in analysis:
            summary = analysis["text_content_summary"]
            if any(word in summary.lower() for word in ["empty", "blank", "no text", "invisible"]):
                issues.append("TEXT VISIBILITY: Text appears empty or invisible")
                print("❌ FOUND TEXT VISIBILITY PROBLEM")

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_interactions(self, pilot):
        """HAMMER TEST: Every possible interaction."""
        print("🔨 HAMMERING: All possible interactions...")

        interactions = [
            {"action": "key", "value": "r"},  # Refresh
            {"action": "key", "value": "p"},  # Pause
            {"action": "key", "value": "s"},  # Start
            {"action": "key", "value": "ctrl+t"},  # Toggle theme
            {"action": "key", "value": "ctrl+s"},  # Save
            {"action": "key", "value": "ctrl+r"},  # Reset
            {"action": "key", "value": "tab"},  # Navigation
            {"action": "key", "value": "shift+tab"},  # Reverse navigation
            {"action": "key", "value": "up"},  # Up arrow
            {"action": "key", "value": "down"},  # Down arrow
            {"action": "key", "value": "left"},  # Left arrow
            {"action": "key", "value": "right"},  # Right arrow
            {"action": "key", "value": "enter"},  # Enter
            {"action": "key", "value": "escape"},  # Escape
        ]

        issues = []

        for i, interaction in enumerate(interactions):
            print(f"🔨 Testing interaction {i+1}/{len(interactions)}: {interaction}")

            try:
                # Capture state before
                state_before = await self.harness.capture_tui_state(pilot, f"before_{i}")

                # Perform interaction
                if interaction["action"] == "key":
                    await pilot.press(interaction["value"])
                elif interaction["action"] == "click":
                    # We'll add click tests later when we identify clickable elements
                    pass

                await asyncio.sleep(0.3)  # Let UI update

                # Capture state after
                state_after = await self.harness.capture_tui_state(pilot, f"after_{i}")

                # AI analysis of the change
                analysis = await self.harness.analyze_state_multimodal(state_after)

                # Check for errors or problems
                if "visual_anomalies" in analysis:
                    for anomaly in analysis["visual_anomalies"]:
                        if any(word in anomaly.lower() for word in ["error", "crash", "broken", "missing"]):
                            issues.append(f"INTERACTION ERROR ({interaction}): {anomaly}")
                            print(f"❌ INTERACTION PROBLEM: {anomaly}")

                # Check if UI responded appropriately
                if state_before.ansi_text == state_after.ansi_text:
                    # UI didn't change - might be okay for some interactions
                    pass
                else:
                    print(f"✅ UI responded to {interaction}")

            except Exception as e:
                issues.append(f"INTERACTION CRASH ({interaction}): {str(e)}")
                print(f"💥 INTERACTION CRASHED: {interaction} - {e}")

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_theme_switching(self, pilot):
        """HAMMER TEST: Theme switching and contrast."""
        print("🔨 HAMMERING: Theme switching...")

        issues = []

        # Test theme switching multiple times
        for i in range(3):
            print(f"🔨 Theme switch test {i+1}/3")

            # Capture before theme switch
            state_before = await self.harness.capture_tui_state(pilot, f"theme_before_{i}")

            # Switch theme
            await pilot.press("ctrl+t")
            await asyncio.sleep(1.0)  # Give time for theme to apply

            # Capture after theme switch
            state_after = await self.harness.capture_tui_state(pilot, f"theme_after_{i}")

            # AI analysis of theme change
            analysis = await self.harness.analyze_state_multimodal(state_after)

            # Check if theme actually changed
            if state_before.ansi_text == state_after.ansi_text:
                issues.append(f"THEME SWITCHING: Theme doesn't appear to change (iteration {i+1})")
                print(f"❌ THEME NOT CHANGING")
            else:
                print(f"✅ Theme changed successfully")

            # Check contrast after theme change
            if "visual_anomalies" in analysis:
                for anomaly in analysis["visual_anomalies"]:
                    if any(word in anomaly.lower() for word in ["contrast", "invisible", "hard to read"]):
                        issues.append(f"THEME CONTRAST: {anomaly} (iteration {i+1})")
                        print(f"❌ THEME CONTRAST PROBLEM: {anomaly}")

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_ui_elements(self, pilot):
        """HAMMER TEST: Every UI element visibility and functionality."""
        print("🔨 HAMMERING: UI elements...")

        issues = []

        # Capture current state
        state = await self.harness.capture_tui_state(pilot, "ui_elements_test")
        analysis = await self.harness.analyze_state_multimodal(state)

        # Check for essential UI elements
        required_elements = ["system status", "agents", "log", "vote", "button", "panel", "border"]

        ui_summary = analysis.get("text_content_summary", "").lower()
        ui_elements = analysis.get("ui_elements", [])

        for element in required_elements:
            if element not in ui_summary and not any(element in str(ui_el).lower() for ui_el in ui_elements):
                issues.append(f"MISSING UI ELEMENT: {element} not found or not visible")
                print(f"❌ MISSING: {element}")
            else:
                print(f"✅ FOUND: {element}")

        # Check for readable text
        if len(state.ansi_text.strip()) < 50:
            issues.append("UI CONTENT: Very little text content visible")
            print("❌ MINIMAL CONTENT")

        # Check widget visibility
        if len(state.visible_widgets) < 5:
            issues.append(f"WIDGET COUNT: Only {len(state.visible_widgets)} widgets visible (seems low)")
            print(f"❌ LOW WIDGET COUNT: {len(state.visible_widgets)}")
        else:
            print(f"✅ WIDGET COUNT: {len(state.visible_widgets)} widgets")

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def hammer_test_responsiveness(self, pilot):
        """HAMMER TEST: UI responsiveness and performance."""
        print("🔨 HAMMERING: Responsiveness...")

        issues = []

        # Rapid input test
        rapid_inputs = ["r", "p", "s", "r", "p", "s", "r"]

        start_time = time.time()
        for input_key in rapid_inputs:
            await pilot.press(input_key)
            await asyncio.sleep(0.1)  # Very rapid

        end_time = time.time()
        response_time = end_time - start_time

        if response_time > 5.0:  # Should handle rapid input in under 5 seconds
            issues.append(f"RESPONSIVENESS: Slow response to rapid input ({response_time:.2f}s)")
            print(f"❌ SLOW RESPONSE: {response_time:.2f}s")
        else:
            print(f"✅ RESPONSIVE: {response_time:.2f}s")

        # Check if UI is still functional after rapid input
        state = await self.harness.capture_tui_state(pilot, "responsiveness_test")
        analysis = await self.harness.analyze_state_multimodal(state)

        if "visual_anomalies" in analysis:
            for anomaly in analysis["visual_anomalies"]:
                if any(word in anomaly.lower() for word in ["frozen", "crashed", "unresponsive"]):
                    issues.append(f"RESPONSIVENESS: {anomaly}")
                    print(f"❌ RESPONSIVENESS ISSUE: {anomaly}")

        self.issues_found.extend(issues)
        return len(issues) == 0

    async def generate_ai_recommendations(self):
        """Use AI to generate recommendations for fixing found issues."""
        print("🤖 AI GENERATING RECOMMENDATIONS...")

        if not self.issues_found:
            print("✅ NO ISSUES FOUND - TUI is working perfectly!")
            return

        print(f"🔍 FOUND {len(self.issues_found)} ISSUES:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")

        # Use AI reasoning to suggest fixes
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                prompt = f"""
                Analyze these TUI issues and provide specific code fixes:

                ISSUES FOUND:
                {chr(10).join(f"- {issue}" for issue in self.issues_found)}

                The TUI is built with Textual and uses a theme system.
                Provide specific recommendations for:
                1. CSS fixes for contrast/visibility issues
                2. Python code fixes for functionality issues
                3. Theme color adjustments
                4. UI structure improvements

                Be very specific with exact color codes, CSS selectors, and code changes.
                """

                response = client.chat.completions.create(
                    model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=2000
                )

                recommendations = response.choices[0].message.content
                print(f"🤖 AI RECOMMENDATIONS:\n{recommendations}")

                return recommendations

            except Exception as e:
                print(f"❌ AI recommendation failed: {e}")

        return None


async def run_ai_hammer_test():
    """Run the complete AI hammer test suite."""
    print("🔥🔨 STARTING AI HAMMER TEST - WILL TEST EVERYTHING! 🔨🔥")
    print("=" * 80)

    tester = AIHammerTester()

    # Start the REAL advanced TUI app
    app = AdvancedCanopyTUI(theme="dark")  # Use our improved high-contrast theme

    async with app.run_test(size=(120, 40)) as pilot:
        print("🚀 REAL Advanced Canopy TUI started")
        print("🔨 BEGINNING RELENTLESS AI TESTING...")

        # Let UI stabilize
        await asyncio.sleep(2.0)

        # Run all hammer tests
        tests = [
            ("CONTRAST & VISIBILITY", tester.hammer_test_contrast_visibility),
            ("ALL INTERACTIONS", tester.hammer_test_interactions),
            ("THEME SWITCHING", tester.hammer_test_theme_switching),
            ("UI ELEMENTS", tester.hammer_test_ui_elements),
            ("RESPONSIVENESS", tester.hammer_test_responsiveness),
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
                tester.issues_found.append(f"TEST CRASH ({test_name}): {str(e)}")

        # Final summary
        print(f"\n{'='*50}")
        print("🔨 HAMMER TEST RESULTS:")
        print(f"{'='*50}")

        passed = sum(1 for success in results.values() if success)
        total = len(results)

        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {status}: {test_name}")

        print(f"\nOVERALL: {passed}/{total} tests passed")
        print(f"ISSUES FOUND: {len(tester.issues_found)}")

        # Generate AI recommendations
        await tester.generate_ai_recommendations()

        # Show test artifacts
        if tester.harness.enable_screenshots:
            screenshots_dir = tester.harness.screenshot_manager.screenshots_dir
            screenshot_count = len(list(screenshots_dir.glob("*.png")))
            print(f"\n📸 Generated {screenshot_count} screenshots in {screenshots_dir}")

        print(f"\n🎯 AI HAMMER TEST COMPLETE!")
        print(f"{'🎉 ALL TESTS PASSED!' if passed == total else '🔧 ISSUES NEED FIXING!'}")

    return results, tester.issues_found


if __name__ == "__main__":
    print("🔨 LAUNCHING AI HAMMER TEST...")
    results, issues = asyncio.run(run_ai_hammer_test())

    if issues:
        print(f"\n🚨 CRITICAL: {len(issues)} issues must be fixed!")
        exit(1)
    else:
        print("\n🏆 SUCCESS: TUI passed all AI hammer tests!")
        exit(0)
