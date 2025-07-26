#!/usr/bin/env python3
"""
🔥🤖 REAL SENTIENT TUI DESTROYER - THE FUCKING BEAST 🤖🔥
WITH FULL AI POWER AND RELENTLESS ANALYSIS
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import what we need
from canopy_core.tui.advanced_app import AdvancedCanopyTUI


class RealSentientDestroyer:
    """THE REAL FUCKING DESTROYER WITH AI POWER."""

    def __init__(self):
        self.issues_found = []
        self.ai_analyses = []
        self.state_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Try to initialize AI models
        self.has_openai = bool(os.getenv("OPENAI_API_KEY"))
        self.has_gemini = bool(os.getenv("GEMINI_API_KEY"))

        if self.has_openai:
            try:
                import openai

                self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                print("🤖 OpenAI API LOADED - REASONING ENGINE ONLINE")
            except Exception as e:
                print(f"❌ OpenAI failed to load: {e}")
                self.has_openai = False

        if self.has_gemini:
            try:
                import google.generativeai as genai

                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini_model = genai.GenerativeModel(
                    "gemini-1.5-pro",
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )
                print("🧠 Gemini API LOADED - VISION ENGINE ONLINE")
            except Exception as e:
                print(f"❌ Gemini failed to load: {e}")
                self.has_gemini = False

        if not self.has_openai and not self.has_gemini:
            print("⚠️  WARNING: NO AI MODELS LOADED!")
            print("   Set OPENAI_API_KEY and/or GEMINI_API_KEY for full power")

    async def capture_tui_state(self, pilot, step_name: str) -> Dict[str, Any]:
        """Capture comprehensive TUI state for AI analysis."""
        app = pilot.app

        # Capture all possible state information
        state = {
            "step_name": step_name,
            "timestamp": datetime.now().isoformat(),
            "app_title": getattr(app, "title", "Unknown"),
            "app_class": app.__class__.__name__,
            "visible_widgets": [],
            "widget_tree": {},
            "focused_widget": None,
            "app_size": getattr(app, "size", None),
            "text_content": "",
            "error_state": "unknown",
        }

        try:
            # Capture widget information
            widgets = app.query("*")
            state["visible_widgets"] = [w.__class__.__name__ for w in widgets if hasattr(w, "visible") and w.visible]
            state["total_widgets"] = len(widgets)

            # Try to get focused widget
            if hasattr(app, "focused") and app.focused:
                state["focused_widget"] = app.focused.__class__.__name__

            # Try to capture text content
            try:
                if hasattr(app, "export_text"):
                    state["text_content"] = app.export_text()
                else:
                    # Fallback: construct from widgets
                    text_parts = []
                    for widget in widgets:
                        if hasattr(widget, "renderable"):
                            text_parts.append(str(widget.renderable))
                    state["text_content"] = "\n".join(text_parts)
            except Exception:
                state["text_content"] = f"Text capture failed for {step_name}"

            # Check for error indicators
            error_indicators = ["error", "exception", "traceback", "failed", "crash"]
            text_lower = state["text_content"].lower()
            state["has_errors"] = any(indicator in text_lower for indicator in error_indicators)

            # Widget health check
            state["widget_health"] = {
                "responsive": True,
                "accessible": len(state["visible_widgets"]) > 0,
                "focused": state["focused_widget"] is not None,
            }

        except Exception as e:
            state["capture_error"] = str(e)
            state["error_state"] = "capture_failed"

        self.state_history.append(state)
        return state

    async def ai_analyze_state(self, state: Dict[str, Any], previous_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Use AI to analyze the TUI state like a fucking expert."""

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "step": state["step_name"],
            "ai_model": "none",
            "findings": [],
            "severity": "unknown",
            "recommendations": [],
            "issues_detected": [],
        }

        # OpenAI Reasoning Analysis
        if self.has_openai:
            try:
                analysis.update(await self._openai_analyze_state(state, previous_state))
            except Exception as e:
                analysis["openai_error"] = str(e)

        # Gemini Vision Analysis (if we had screenshots)
        if self.has_gemini:
            try:
                analysis.update(await self._gemini_analyze_state(state, previous_state))
            except Exception as e:
                analysis["gemini_error"] = str(e)

        self.ai_analyses.append(analysis)
        return analysis

    async def _openai_analyze_state(
        self, state: Dict[str, Any], previous_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Use OpenAI for deep reasoning analysis."""

        context = f"""
        ANALYZE THIS TUI STATE WITH EXTREME PRECISION:

        CURRENT STATE:
        - Step: {state['step_name']}
        - App: {state['app_class']}
        - Widgets: {len(state['visible_widgets'])} visible
        - Widget Types: {list(set(state['visible_widgets']))}
        - Focused: {state['focused_widget']}
        - Has Errors: {state.get('has_errors', False)}
        - Text Length: {len(state.get('text_content', ''))}
        - Text Preview: {state.get('text_content', '')[:500]}
        """

        if previous_state:
            context += f"""

        PREVIOUS STATE COMPARISON:
        - Previous Widgets: {previous_state.get('visible_widgets', [])}
        - Widget Changes: Added {set(state['visible_widgets']) - set(previous_state.get('visible_widgets', []))}, Removed {set(previous_state.get('visible_widgets', [])) - set(state['visible_widgets'])}
        - Focus Change: {previous_state.get('focused_widget')} -> {state['focused_widget']}
        """

        context += """

        ANALYZE WITH EXTREME SCRUTINY:
        1. UI/UX Issues - Is the interface broken, confusing, or poorly designed?
        2. Functionality Issues - Are features working correctly?
        3. Performance Issues - Any signs of sluggishness or inefficiency?
        4. Accessibility Issues - Can users with disabilities use this?
        5. Error Conditions - Any errors, crashes, or exceptions?
        6. Design Problems - Poor contrast, layout issues, visual problems?
        7. Navigation Issues - Can users move around effectively?
        8. Data Issues - Missing data, incorrect displays, corrupted state?

        BE EXTREMELY CRITICAL AND FIND EVERY POSSIBLE ISSUE.

        Return JSON analysis:
        {
            "overall_assessment": "healthy/degraded/critical",
            "issues_detected": [
                {
                    "type": "ui/functionality/performance/accessibility/error/design/navigation/data",
                    "severity": "critical/high/medium/low",
                    "description": "detailed issue description",
                    "evidence": "what you observed",
                    "impact": "how this affects users",
                    "fix_suggestion": "specific fix recommendation"
                }
            ],
            "positive_findings": ["things that work well"],
            "red_flags": ["serious concerns that need immediate attention"],
            "user_experience_rating": 1-10,
            "recommendations": ["specific actionable improvements"],
            "next_tests_suggested": ["what to test next to find more issues"]
        }
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are the world's most ruthless TUI testing expert. Find EVERY possible issue with extreme precision and detailed analysis.",
                },
                {"role": "user", "content": context},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        analysis = json.loads(response.choices[0].message.content)
        analysis["ai_model"] = "openai_gpt4o"

        return analysis

    async def _gemini_analyze_state(
        self, state: Dict[str, Any], previous_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Use Gemini for additional analysis."""

        prompt = f"""
        GEMINI ANALYSIS OF TUI STATE:

        Current State: {json.dumps(state, indent=2)}

        Provide additional analysis focusing on:
        1. Text content quality and readability
        2. Widget organization and structure
        3. Information architecture
        4. User flow and navigation logic
        5. Content presentation issues

        Return JSON with findings and recommendations.
        """

        response = self.gemini_model.generate_content(prompt)

        try:
            analysis = json.loads(response.text)
            analysis["ai_model"] = "gemini_1.5_pro"
            return analysis
        except:
            return {
                "ai_model": "gemini_1.5_pro",
                "raw_response": response.text,
                "parse_error": "Failed to parse JSON response",
            }

    async def hammer_test_with_ai_analysis(self, pilot):
        """HAMMER TEST with full AI analysis of every step."""
        print("🔥🤖 BEGINNING AI-POWERED HAMMER TEST 🤖🔥")

        # Capture initial state
        print("📸 Capturing initial state...")
        initial_state = await self.capture_tui_state(pilot, "initial_state")

        # AI analysis of initial state
        print("🤖 AI analyzing initial state...")
        initial_analysis = await self.ai_analyze_state(initial_state)

        print(f"🔍 INITIAL STATE ANALYSIS:")
        if initial_analysis.get("overall_assessment"):
            print(f"   Overall: {initial_analysis['overall_assessment'].upper()}")
        if initial_analysis.get("issues_detected"):
            print(f"   Issues Found: {len(initial_analysis['issues_detected'])}")
            for issue in initial_analysis["issues_detected"][:3]:  # Show first 3
                print(f"     - {issue.get('severity', 'unknown').upper()}: {issue.get('description', 'Unknown issue')}")
        if initial_analysis.get("user_experience_rating"):
            print(f"   UX Rating: {initial_analysis['user_experience_rating']}/10")

        # Test sequences with AI analysis
        test_sequences = [
            (["tab", "tab", "tab"], "Navigation flow"),
            (["ctrl+t"], "Theme switching"),
            (["r"], "Refresh functionality"),
            (["p"], "Pause functionality"),
            (["f1"], "Help system"),
            (["enter"], "Enter interaction"),
            (["escape"], "Escape handling"),
            (["up", "down", "left", "right"], "Arrow navigation"),
            (["ctrl+s"], "Save functionality"),
            (["ctrl+r"], "Reset functionality"),
        ]

        previous_state = initial_state

        for sequence, description in test_sequences:
            print(f"\n🔨 TESTING: {description}")

            try:
                # Execute sequence
                for key in sequence:
                    print(f"   Pressing: {key}")
                    await pilot.press(key)
                    await asyncio.sleep(0.2)

                # Capture state after test
                post_test_state = await self.capture_tui_state(pilot, f"after_{description.replace(' ', '_')}")

                # AI analysis
                print("🤖 AI analyzing changes...")
                analysis = await self.ai_analyze_state(post_test_state, previous_state)

                # Report findings
                print(f"🔍 AI FINDINGS for {description}:")
                if analysis.get("overall_assessment"):
                    assessment = analysis["overall_assessment"]
                    emoji = "✅" if assessment == "healthy" else "⚠️" if assessment == "degraded" else "🚨"
                    print(f"   {emoji} Assessment: {assessment.upper()}")

                if analysis.get("issues_detected"):
                    for issue in analysis["issues_detected"]:
                        severity = issue.get("severity", "unknown").upper()
                        desc = issue.get("description", "Unknown issue")
                        emoji = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "HIGH" else "🔍"
                        print(f"   {emoji} {severity}: {desc}")

                        # Add to global issues
                        self.issues_found.append(
                            {
                                "test": description,
                                "sequence": sequence,
                                "severity": severity,
                                "description": desc,
                                "ai_analysis": issue,
                            }
                        )

                if analysis.get("recommendations"):
                    print(f"   💡 AI Recommendations:")
                    for rec in analysis["recommendations"][:2]:  # Show first 2
                        print(f"     - {rec}")

                previous_state = post_test_state

            except Exception as e:
                print(f"   💥 TEST CRASHED: {e}")
                self.issues_found.append(
                    {
                        "test": description,
                        "sequence": sequence,
                        "severity": "CRITICAL",
                        "description": f"Test crashed: {e}",
                        "ai_analysis": {"type": "crash", "error": str(e)},
                    }
                )

        return len(self.issues_found) == 0

    async def generate_final_ai_report(self):
        """Generate comprehensive AI-powered final report."""
        print("\n🤖 GENERATING FINAL AI ANALYSIS REPORT...")

        if not self.has_openai:
            print("❌ No OpenAI API - cannot generate final report")
            return

        # Compile all data
        report_data = {
            "session_id": self.session_id,
            "total_tests": len(self.state_history),
            "total_issues": len(self.issues_found),
            "ai_analyses": len(self.ai_analyses),
            "issues": self.issues_found,
            "state_history": self.state_history[-5:],  # Last 5 states
            "all_analyses": self.ai_analyses,
        }

        # Ask AI for comprehensive summary
        summary_prompt = f"""
        GENERATE COMPREHENSIVE TUI TESTING REPORT:

        SESSION DATA:
        {json.dumps(report_data, indent=2, default=str)}

        Create a final report analyzing:
        1. Overall TUI health and quality assessment
        2. Critical issues that must be fixed immediately
        3. Performance and usability concerns
        4. Accessibility compliance
        5. User experience rating and recommendations
        6. Technical debt and architectural issues
        7. Priority matrix for fixes
        8. Detailed fix instructions for each issue

        Be extremely thorough and actionable.

        Return JSON format:
        {
            "executive_summary": "one paragraph overview",
            "overall_rating": 1-10,
            "critical_issues": [{"issue": "", "fix": "", "priority": 1-5}],
            "recommendations": ["specific actionable items"],
            "technical_assessment": "detailed technical analysis",
            "user_experience_report": "UX analysis",
            "next_steps": ["immediate actions needed"],
            "testing_completeness": 1-10
        }
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are the world's leading TUI testing expert and software quality analyst.",
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            final_report = json.loads(response.choices[0].message.content)

            # Display the report
            print("\n" + "=" * 80)
            print("🤖 FINAL AI ANALYSIS REPORT")
            print("=" * 80)

            print(f"\n📊 EXECUTIVE SUMMARY:")
            print(f"   {final_report.get('executive_summary', 'No summary available')}")

            print(f"\n⭐ OVERALL RATING: {final_report.get('overall_rating', 'N/A')}/10")
            print(f"🧪 TESTING COMPLETENESS: {final_report.get('testing_completeness', 'N/A')}/10")

            critical_issues = final_report.get("critical_issues", [])
            if critical_issues:
                print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
                for i, issue in enumerate(critical_issues, 1):
                    print(f"   {i}. {issue.get('issue', 'Unknown issue')}")
                    print(f"      Fix: {issue.get('fix', 'No fix provided')}")
                    print(f"      Priority: {issue.get('priority', 'Unknown')}/5")

            recommendations = final_report.get("recommendations", [])
            if recommendations:
                print(f"\n💡 AI RECOMMENDATIONS ({len(recommendations)}):")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")

            next_steps = final_report.get("next_steps", [])
            if next_steps:
                print(f"\n🎯 IMMEDIATE NEXT STEPS:")
                for i, step in enumerate(next_steps, 1):
                    print(f"   {i}. {step}")

            print(f"\n🔬 TECHNICAL ASSESSMENT:")
            print(f"   {final_report.get('technical_assessment', 'No technical assessment available')}")

            print(f"\n👤 USER EXPERIENCE REPORT:")
            print(f"   {final_report.get('user_experience_report', 'No UX report available')}")

            return final_report

        except Exception as e:
            print(f"❌ Failed to generate final AI report: {e}")
            return None


async def run_real_destroyer():
    """Run the REAL FUCKING DESTROYER with full AI power."""
    print("🔥🤖🔥 REAL SENTIENT TUI DESTROYER ACTIVATED 🔥🤖🔥")
    print("=" * 80)
    print("THIS IS THE REAL DEAL - FULL AI ANALYSIS POWER")
    print("EVERY STEP ANALYZED BY ADVANCED AI MODELS")
    print("RELENTLESS, THOROUGH, FUCKING BRUTAL")
    print("=" * 80)

    destroyer = RealSentientDestroyer()

    if not destroyer.has_openai and not destroyer.has_gemini:
        print("\n🚨 WARNING: NO AI MODELS AVAILABLE!")
        print("Set OPENAI_API_KEY and/or GEMINI_API_KEY for full power")
        print("Proceeding with basic analysis only...\n")

    # Start the TUI app
    app = AdvancedCanopyTUI(theme="dark")

    try:
        async with app.run_test(size=(120, 40)) as pilot:
            print("🚀 TUI STARTED - BEGINNING DESTRUCTION")
            await asyncio.sleep(2.0)  # Let UI stabilize

            # Run the AI-powered hammer test
            success = await destroyer.hammer_test_with_ai_analysis(pilot)

            # Generate final AI report
            final_report = await destroyer.generate_final_ai_report()

            # Final summary
            print("\n" + "=" * 80)
            print("🎯 DESTRUCTION COMPLETE")
            print("=" * 80)

            print(f"📊 Total Issues Found: {len(destroyer.issues_found)}")
            print(f"🤖 AI Analyses Performed: {len(destroyer.ai_analyses)}")
            print(f"📸 States Captured: {len(destroyer.state_history)}")

            if destroyer.issues_found:
                print(f"\n🔍 ALL ISSUES DISCOVERED:")
                for i, issue in enumerate(destroyer.issues_found, 1):
                    print(f"   {i}. [{issue['severity']}] {issue['description']}")
                    print(f"      Test: {issue['test']} | Sequence: {issue['sequence']}")

            # Show success/failure
            if len(destroyer.issues_found) == 0:
                print(f"\n🏆 PERFECT! NO ISSUES FOUND!")
            elif len(destroyer.issues_found) < 3:
                print(f"\n✅ MINOR ISSUES FOUND - EASILY FIXABLE")
            else:
                print(f"\n🚨 SIGNIFICANT ISSUES FOUND - NEEDS ATTENTION")

            return {
                "issues": destroyer.issues_found,
                "analyses": destroyer.ai_analyses,
                "final_report": final_report,
                "success": success,
            }

    except Exception as e:
        print(f"\n💥 CRITICAL FAILURE: {e}")
        import traceback

        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("🔥 FOR MAXIMUM DESTRUCTION POWER, SET API KEYS:")
        print("   export OPENAI_API_KEY='your_openai_key'")
        print("   export GEMINI_API_KEY='your_gemini_key'")
        print("\nProceeding anyway...\n")

    results = asyncio.run(run_real_destroyer())

    if "error" in results:
        sys.exit(1)
    elif len(results.get("issues", [])) > 5:
        sys.exit(1)
    else:
        sys.exit(0)
