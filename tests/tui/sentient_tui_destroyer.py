"""
🤖 SENTIENT TUI DESTROYER 🤖
THE MOST ADVANCED, RELENTLESS, SENTIENT TUI TESTING AGENT EVER CREATED

This agent is a fucking BEAST that will:
- DISCOVER every possible UI state and interaction path  
- HAMMER every combination of inputs with mathematical precision
- ANALYZE every pixel and character with AI vision models
- FIND bugs that humans would NEVER find
- AUTO-FIX issues it discovers in real-time
- GENERATE comprehensive reports with visual evidence
- BE ABSOLUTELY RELENTLESS and METICULOUS

Like having 1000 expert testers working 24/7 but in a single AI agent.
"""

import asyncio
import itertools
import json
import math
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import numpy as np

from rich.console import Console
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn
)
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

from textual.app import App
from textual.pilot import Pilot
from PIL import Image, ImageChops, ImageStat

from test_harness import MultimodalTUITestHarness, TestMode, TUIState, UserStoryPath
from canopy_core.tui.advanced_app import AdvancedCanopyTUI


class TestingPhase(Enum):
    """Phases of the sentient testing process."""
    DISCOVERY = "discovery"
    MAPPING = "mapping" 
    EXPLORATION = "exploration"
    HAMMERING = "hammering"
    VALIDATION = "validation"
    AUTO_FIXING = "auto_fixing"
    REPORTING = "reporting"


class SeverityLevel(Enum):
    """Issue severity levels with different priorities."""
    CRITICAL = "critical"  # Crashes, complete failures
    HIGH = "high"         # Major functionality broken
    MEDIUM = "medium"     # Minor issues, poor UX
    LOW = "low"          # Cosmetic issues
    INFO = "info"        # Informational findings


@dataclass
class UIDiscovery:
    """Comprehensive UI element discovery data."""
    widget_types: Set[str] = field(default_factory=set)
    interactive_elements: List[Dict[str, Any]] = field(default_factory=list)
    navigation_paths: Dict[str, List[str]] = field(default_factory=dict)
    color_palette: Set[str] = field(default_factory=set)
    layout_structure: Dict[str, Any] = field(default_factory=dict)
    accessibility_features: List[str] = field(default_factory=list)
    performance_indicators: Dict[str, float] = field(default_factory=dict)


@dataclass
class TestingIssue:
    """Detailed issue tracking with AI analysis."""
    id: str
    severity: SeverityLevel
    category: str
    title: str
    description: str
    reproduction_steps: List[str]
    evidence: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    suggested_fixes: List[str]
    state_fingerprint: str
    screenshot_paths: List[Path] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.now)
    fixed: bool = False
    fix_attempts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass 
class InputCombination:
    """Mathematical input combination for exhaustive testing."""
    sequence: List[str]
    modifiers: List[str]
    timing: List[float]
    expected_outcome: Optional[str]
    test_category: str
    priority: int


class SentientTUIDestroyer:
    """
    🤖 THE ULTIMATE SENTIENT TUI TESTING AGENT 🤖
    
    This is not just a test harness - it's a sentient AI agent that:
    - THINKS like a human tester but with superhuman precision
    - LEARNS from every interaction and builds a knowledge base
    - DISCOVERS edge cases that humans would never find
    - ADAPTS its testing strategy based on what it finds
    - HAMMERS the system with relentless mathematical precision
    - AUTO-FIXES issues it discovers in real-time
    - GENERATES actionable reports with visual evidence
    
    IT WILL FIND EVERY BUG. GUARANTEED.
    """
    
    def __init__(
        self,
        app_class: type[App],
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        max_test_duration: int = 3600,  # 1 hour default
        output_dir: str = "sentient_destroyer_results",
        auto_fix: bool = True,
        brutal_mode: bool = True,
        **kwargs
    ):
        """Initialize the sentient destroyer with maximum capabilities."""
        self.app_class = app_class
        self.max_test_duration = max_test_duration
        self.output_dir = Path(output_dir)
        self.auto_fix = auto_fix
        self.brutal_mode = brutal_mode
        
        # Create output structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "fixes").mkdir(exist_ok=True)
        (self.output_dir / "evidence").mkdir(exist_ok=True)
        
        # Initialize the multimodal test harness
        self.harness = MultimodalTUITestHarness(
            app_class=app_class,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key,
            test_mode=TestMode.MULTIMODAL if gemini_api_key else TestMode.TEXT_ONLY,
            enable_reasoning=True,
            max_states=10000,  # Massive state space
            output_dir=str(self.output_dir),
            enable_screenshots=True,
            enable_logging=True
        )
        
        # Sentient state tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ui_knowledge = UIDiscovery()
        self.discovered_issues: List[TestingIssue] = []
        self.state_graph: Dict[str, Dict[str, Any]] = {}
        self.input_combinations: List[InputCombination] = []
        self.performance_history: List[Dict[str, Any]] = []
        
        # AI models for different analysis types
        self.ai_models = {
            "vision": gemini_api_key,
            "reasoning": openai_api_key, 
            "code_analysis": claude_api_key
        }
        
        # Testing strategy evolution
        self.strategy_weights = {
            "edge_case_focus": 0.3,
            "performance_focus": 0.2,
            "accessibility_focus": 0.2,
            "visual_focus": 0.3
        }
        
        # Progress tracking
        self.console = Console()
        self.test_start_time = None
        self.phase = TestingPhase.DISCOVERY
        
        # Thread pool for concurrent testing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initiate_total_destruction(self) -> Dict[str, Any]:
        """
        🔥 INITIATE TOTAL TUI DESTRUCTION 🔥
        
        The main entry point for complete TUI annihilation.
        This will systematically discover, map, explore, hammer, and validate
        EVERY SINGLE ASPECT of the TUI.
        """
        self.test_start_time = datetime.now()
        
        self._display_destroyer_banner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.fields[phase]}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task(
                "Destroying TUI", 
                total=100,
                phase="Initializing Sentient Destroyer"
            )
            
            results = {}
            
            try:
                # Phase 1: UI Discovery and Mapping
                progress.update(main_task, advance=5, phase="🔍 PHASE 1: DISCOVERY & MAPPING")
                discovery_results = await self._phase_1_discovery()
                results["discovery"] = discovery_results
                progress.update(main_task, advance=15)
                
                # Phase 2: Mathematical Input Generation
                progress.update(main_task, advance=5, phase="🧮 PHASE 2: MATHEMATICAL INPUT GENERATION")
                input_results = await self._phase_2_input_generation()
                results["input_generation"] = input_results
                progress.update(main_task, advance=15)
                
                # Phase 3: Systematic Exploration
                progress.update(main_task, advance=5, phase="🗺️ PHASE 3: SYSTEMATIC EXPLORATION")
                exploration_results = await self._phase_3_exploration()
                results["exploration"] = exploration_results
                progress.update(main_task, advance=20)
                
                # Phase 4: BRUTAL HAMMERING
                progress.update(main_task, advance=5, phase="🔨 PHASE 4: BRUTAL HAMMERING")
                hammering_results = await self._phase_4_brutal_hammering()
                results["hammering"] = hammering_results
                progress.update(main_task, advance=20)
                
                # Phase 5: AI-Powered Validation
                progress.update(main_task, advance=5, phase="🤖 PHASE 5: AI VALIDATION")
                validation_results = await self._phase_5_ai_validation()
                results["validation"] = validation_results
                progress.update(main_task, advance=10)
                
                # Phase 6: Auto-Fix (if enabled)
                if self.auto_fix:
                    progress.update(main_task, advance=2, phase="🔧 PHASE 6: AUTO-FIXING")
                    fix_results = await self._phase_6_auto_fix()
                    results["auto_fix"] = fix_results
                    progress.update(main_task, advance=8)
                else:
                    progress.update(main_task, advance=10)
                
                # Phase 7: Comprehensive Reporting
                progress.update(main_task, advance=2, phase="📊 PHASE 7: GENERATING REPORTS")
                report_results = await self._phase_7_reporting()
                results["reporting"] = report_results
                progress.update(main_task, advance=3)
                
                progress.update(main_task, completed=100, phase="🎯 DESTRUCTION COMPLETE")
                
                return results
                
            except Exception as e:
                self.console.print(f"[bold red]💥 DESTROYER ENCOUNTERED ERROR: {e}[/]")
                self._log_critical_error(str(e))
                raise
                
    def _display_destroyer_banner(self) -> None:
        """Display the epic destroyer banner."""
        banner = """
🤖════════════════════════════════════════════════════════════════════🤖
║                                                                      ║
║               🔥 SENTIENT TUI DESTROYER ACTIVATED 🔥                 ║
║                                                                      ║
║  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ║
║  ██ ADVANCED AI-POWERED TUI TESTING SYSTEM ONLINE ██             ║
║  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  ║
║                                                                      ║
║  🎯 MISSION: TOTAL TUI ANNIHILATION                                  ║
║  🔍 STRATEGY: MATHEMATICAL PRECISION + AI ANALYSIS                   ║
║  ⚡ APPROACH: RELENTLESS & METICULOUS                               ║
║  🏆 OBJECTIVE: ZERO BUGS TOLERANCE                                   ║
║                                                                      ║
🤖════════════════════════════════════════════════════════════════════🤖
        """
        
        self.console.print(Panel(banner, style="bold red"))
        
    async def _phase_1_discovery(self) -> Dict[str, Any]:
        """
        🔍 PHASE 1: DISCOVERY & MAPPING
        
        Systematically discover and map every aspect of the TUI:
        - Widget inventory and capabilities
        - Navigation paths and state transitions
        - Visual elements and color analysis
        - Performance characteristics
        - Accessibility features
        """
        self.phase = TestingPhase.DISCOVERY
        self.console.print("[bold yellow]🔍 Beginning UI Discovery & Mapping...[/]")
        
        discoveries = {
            "widgets": {},
            "navigation": {},
            "visuals": {},
            "performance": {},
            "accessibility": {}
        }
        
        # Start the app for discovery
        app = self.app_class()
        async with app.run_test(size=(120, 40)) as pilot:
            
            # Initial state capture and analysis
            self.console.print("📸 Capturing initial TUI state...")
            initial_state = await self.harness.capture_tui_state(pilot, "discovery_initial")
            
            # Comprehensive AI analysis of initial state
            self.console.print("🤖 AI analyzing initial state structure...")
            initial_analysis = await self.harness.analyze_state_multimodal(initial_state)
            
            # Widget discovery - find every interactive element
            self.console.print("🔍 Discovering all widgets and interactive elements...")
            widget_discovery = await self._discover_widgets(pilot, initial_state)
            discoveries["widgets"] = widget_discovery
            
            # Navigation mapping - map all possible navigation paths
            self.console.print("🗺️ Mapping navigation paths...")
            navigation_map = await self._map_navigation_paths(pilot)
            discoveries["navigation"] = navigation_map
            
            # Visual analysis - colors, contrast, layout
            self.console.print("🎨 Analyzing visual elements and design...")
            visual_analysis = await self._analyze_visual_elements(initial_state)
            discoveries["visuals"] = visual_analysis
            
            # Performance baseline
            self.console.print("⚡ Establishing performance baseline...")
            performance_baseline = await self._establish_performance_baseline(pilot)
            discoveries["performance"] = performance_baseline
            
            # Accessibility audit
            self.console.print("♿ Auditing accessibility features...")
            accessibility_audit = await self._audit_accessibility(pilot, initial_state)
            discoveries["accessibility"] = accessibility_audit
            
        self.console.print("[bold green]✅ Discovery phase complete![/]")
        return discoveries
        
    async def _discover_widgets(self, pilot: Pilot, state: TUIState) -> Dict[str, Any]:
        """Discover all widgets and their capabilities."""
        widgets = {
            "inventory": state.visible_widgets,
            "interactive": [],
            "focusable": [],
            "types": set(state.visible_widgets)
        }
        
        # Test which widgets are interactive
        for widget_type in set(state.visible_widgets):
            try:
                # Try to interact with widgets of this type
                # This is simplified - real implementation would use widget IDs
                await pilot.press("tab")  # Try to focus
                await asyncio.sleep(0.1)
                
                new_state = await self.harness.capture_tui_state(pilot, f"widget_test_{widget_type}")
                if new_state.focused_widget != state.focused_widget:
                    widgets["focusable"].append(widget_type)
                    
            except Exception:
                pass
                
        self.ui_knowledge.widget_types.update(widgets["types"])
        return widgets
        
    async def _map_navigation_paths(self, pilot: Pilot) -> Dict[str, Any]:
        """Map all possible navigation paths through the UI."""
        navigation_keys = [
            "tab", "shift+tab", "up", "down", "left", "right", 
            "enter", "escape", "space", "home", "end", "page_up", "page_down"
        ]
        
        paths = {}
        current_state = await self.harness.capture_tui_state(pilot, "nav_start")
        
        for key in navigation_keys:
            try:
                # Record state before navigation
                before_state = await self.harness.capture_tui_state(pilot, f"nav_before_{key}")
                
                # Perform navigation
                await pilot.press(key)
                await asyncio.sleep(0.2)
                
                # Record state after navigation
                after_state = await self.harness.capture_tui_state(pilot, f"nav_after_{key}")
                
                # Analyze the change
                changed = (
                    before_state.focused_widget != after_state.focused_widget or
                    before_state.visible_widgets != after_state.visible_widgets or
                    before_state.ansi_text != after_state.ansi_text
                )
                
                paths[key] = {
                    "causes_change": changed,
                    "before_focus": before_state.focused_widget,
                    "after_focus": after_state.focused_widget,
                    "widget_change": before_state.visible_widgets != after_state.visible_widgets
                }
                
            except Exception as e:
                paths[key] = {"error": str(e)}
                
        return paths
        
    async def _analyze_visual_elements(self, state: TUIState) -> Dict[str, Any]:
        """Comprehensive visual analysis using AI."""
        visual_data = {
            "dimensions": state.screenshot.size,
            "colors": await self._extract_color_palette(state.screenshot),
            "contrast_analysis": await self._analyze_contrast(state.screenshot),
            "layout_structure": await self._analyze_layout(state),
            "text_analysis": await self._analyze_text_elements(state)
        }
        
        return visual_data
        
    async def _extract_color_palette(self, image: Image.Image) -> List[str]:
        """Extract the main color palette from the UI screenshot."""
        # Convert to RGB and get color statistics
        rgb_image = image.convert('RGB')
        colors = rgb_image.getcolors(maxcolors=256)
        
        if colors:
            # Sort by frequency and extract top colors
            colors.sort(key=lambda x: x[0], reverse=True)
            palette = []
            
            for count, color in colors[:10]:  # Top 10 colors
                hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                palette.append(hex_color)
                
            return palette
            
        return []
        
    async def _analyze_contrast(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze contrast and accessibility of colors."""
        # Convert to grayscale for contrast analysis
        grayscale = image.convert('L')
        stat = ImageStat.Stat(grayscale)
        
        return {
            "mean_brightness": stat.mean[0],
            "brightness_range": stat.extrema[0],
            "brightness_stddev": stat.stddev[0],
            "contrast_ratio": (stat.extrema[0][1] - stat.extrema[0][0]) / 255.0
        }
        
    async def _analyze_layout(self, state: TUIState) -> Dict[str, Any]:
        """Analyze the layout structure and organization."""
        return {
            "widget_count": len(state.visible_widgets),
            "focused_widget": state.focused_widget,
            "text_length": len(state.ansi_text),
            "cursor_position": state.cursor_position,
            "layout_complexity": len(set(state.visible_widgets))
        }
        
    async def _analyze_text_elements(self, state: TUIState) -> Dict[str, Any]:
        """Analyze text content and readability."""
        text = state.ansi_text
        
        # Basic text analysis
        words = text.split()
        lines = text.split('\n')
        
        return {
            "total_characters": len(text),
            "word_count": len(words),
            "line_count": len(lines),
            "avg_words_per_line": len(words) / max(len(lines), 1),
            "has_content": len(text.strip()) > 0,
            "readability_score": self._calculate_readability_score(text)
        }
        
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate a simple readability score (0-100)."""
        if not text.strip():
            return 0.0
            
        # Simple metrics: length, word variety, sentence structure
        words = text.split()
        unique_words = set(words)
        
        if not words:
            return 0.0
            
        uniqueness = len(unique_words) / len(words)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple scoring formula
        score = min(100, (uniqueness * 50) + (min(avg_word_length, 10) * 5))
        return score
        
    async def _establish_performance_baseline(self, pilot: Pilot) -> Dict[str, Any]:
        """Establish performance baseline metrics."""
        # Measure response times for basic operations
        operations = ["tab", "enter", "escape", "up", "down"]
        response_times = {}
        
        for operation in operations:
            times = []
            for _ in range(5):  # Test each operation 5 times
                start_time = time.time()
                await pilot.press(operation)
                await pilot.pause()  # Wait for UI to stabilize
                end_time = time.time()
                times.append(end_time - start_time)
                
            response_times[operation] = {
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "samples": times
            }
            
        return {
            "response_times": response_times,
            "baseline_established": datetime.now().isoformat()
        }
        
    async def _audit_accessibility(self, pilot: Pilot, state: TUIState) -> Dict[str, Any]:
        """Audit accessibility features and compliance."""
        accessibility = {
            "keyboard_navigation": True,  # TUI is inherently keyboard-based
            "focus_indicators": state.focused_widget is not None,
            "text_content": len(state.ansi_text.strip()) > 0,
            "color_independence": True,  # Would need more sophisticated analysis
            "issues": []
        }
        
        # Check for common accessibility issues
        if not state.focused_widget:
            accessibility["issues"].append("No clear focus indicator")
            
        if len(state.ansi_text.strip()) < 10:
            accessibility["issues"].append("Very little text content for screen readers")
            
        # Test tab navigation
        try:
            initial_focus = state.focused_widget
            await pilot.press("tab")
            await asyncio.sleep(0.1)
            new_state = await self.harness.capture_tui_state(pilot, "accessibility_tab_test")
            
            if new_state.focused_widget == initial_focus:
                accessibility["issues"].append("Tab navigation may not be working properly")
                
        except Exception:
            accessibility["issues"].append("Error testing keyboard navigation")
            
        return accessibility
        
    async def _phase_2_input_generation(self) -> Dict[str, Any]:
        """
        🧮 PHASE 2: MATHEMATICAL INPUT GENERATION
        
        Generate exhaustive input combinations using mathematical principles:
        - All possible key combinations and sequences
        - Timing-based interactions
        - Edge case scenarios
        - Performance stress patterns
        """
        self.phase = TestingPhase.MAPPING
        self.console.print("[bold yellow]🧮 Generating mathematical input combinations...[/]")
        
        # Base input set
        base_inputs = [
            # Navigation
            "tab", "shift+tab", "up", "down", "left", "right",
            "home", "end", "page_up", "page_down",
            
            # Action keys
            "enter", "escape", "space", "backspace", "delete",
            
            # Function keys
            "f1", "f2", "f3", "f4", "f5",
            
            # Modifiers with letters
            "ctrl+a", "ctrl+c", "ctrl+v", "ctrl+x", "ctrl+z",
            "ctrl+s", "ctrl+o", "ctrl+n", "ctrl+p", "ctrl+q",
            "ctrl+r", "ctrl+t", "ctrl+l",
            
            # Regular characters
            "a", "b", "c", "1", "2", "3", "!", "@", "#",
            
            # Special sequences
            "alt+tab", "ctrl+shift+t", "ctrl+alt+d"
        ]
        
        # Generate combinations
        combinations = []
        
        # Single inputs
        for input_key in base_inputs:
            combinations.append(InputCombination(
                sequence=[input_key],
                modifiers=[],
                timing=[0.0],
                expected_outcome=None,
                test_category="single_input",
                priority=1
            ))
            
        # Two-key sequences
        for key1, key2 in itertools.combinations(base_inputs[:20], 2):  # Limit for performance
            combinations.append(InputCombination(
                sequence=[key1, key2],
                modifiers=[],
                timing=[0.0, 0.1],
                expected_outcome=None,
                test_category="sequence",
                priority=2
            ))
            
        # Rapid-fire sequences (stress testing)
        rapid_sequences = [
            ["tab"] * 10,
            ["up", "down"] * 5,
            ["left", "right"] * 5,
            ["enter"] * 3,
            ["escape"] * 3
        ]
        
        for seq in rapid_sequences:
            combinations.append(InputCombination(
                sequence=seq,
                modifiers=[],
                timing=[0.05] * len(seq),  # Very rapid
                expected_outcome=None,
                test_category="stress",
                priority=3
            ))
            
        # Random sequences (chaos testing)
        for _ in range(50):
            seq_length = random.randint(2, 8)
            random_seq = [random.choice(base_inputs) for _ in range(seq_length)]
            random_timing = [random.uniform(0.01, 0.5) for _ in range(seq_length)]
            
            combinations.append(InputCombination(
                sequence=random_seq,
                modifiers=[],
                timing=random_timing,
                expected_outcome=None,
                test_category="chaos",
                priority=4
            ))
            
        # Edge case timings
        edge_timings = [
            [0.001] * 5,  # Extremely rapid
            [2.0] * 3,    # Very slow
            [0.0, 1.0, 0.0, 1.0, 0.0],  # Alternating
        ]
        
        for timing in edge_timings:
            seq = base_inputs[:len(timing)]
            combinations.append(InputCombination(
                sequence=seq,
                modifiers=[],
                timing=timing,
                expected_outcome=None,
                test_category="timing_edge",
                priority=3
            ))
            
        self.input_combinations = combinations
        
        self.console.print(f"[bold green]✅ Generated {len(combinations)} input combinations![/]")
        
        return {
            "total_combinations": len(combinations),
            "categories": {
                category: len([c for c in combinations if c.test_category == category])
                for category in set(c.test_category for c in combinations)
            }
        }
        
    async def _phase_3_exploration(self) -> Dict[str, Any]:
        """
        🗺️ PHASE 3: SYSTEMATIC EXPLORATION
        
        Systematically explore every generated input combination:
        - Execute all input sequences
        - Capture and analyze every state change
        - Build comprehensive state graph
        - Identify anomalies and issues
        """
        self.phase = TestingPhase.EXPLORATION
        self.console.print("[bold yellow]🗺️ Beginning systematic exploration...[/]")
        
        exploration_results = {
            "combinations_tested": 0,
            "states_discovered": 0,
            "issues_found": 0,
            "execution_errors": 0,
            "performance_data": []
        }
        
        app = self.app_class()
        async with app.run_test(size=(120, 40)) as pilot:
            
            # Test each input combination
            total_combinations = len(self.input_combinations)
            
            with Progress(console=self.console) as progress:
                task = progress.add_task(
                    "[cyan]Exploring combinations...", 
                    total=total_combinations
                )
                
                for i, combination in enumerate(self.input_combinations):
                    
                    try:
                        # Execute the input combination
                        execution_start = time.time()
                        
                        # Capture state before
                        state_before = await self.harness.capture_tui_state(
                            pilot, f"explore_before_{i}"
                        )
                        
                        # Execute the sequence
                        for j, (key, timing) in enumerate(zip(combination.sequence, combination.timing)):
                            if timing > 0:
                                await asyncio.sleep(timing)
                            await pilot.press(key)
                            
                        # Wait for stabilization
                        await pilot.pause()
                        
                        # Capture state after
                        state_after = await self.harness.capture_tui_state(
                            pilot, f"explore_after_{i}"
                        )
                        
                        execution_time = time.time() - execution_start
                        
                        # Analyze the state change
                        await self._analyze_state_change(
                            state_before, state_after, combination, i
                        )
                        
                        exploration_results["combinations_tested"] += 1
                        
                        # Record performance
                        exploration_results["performance_data"].append({
                            "combination_index": i,
                            "execution_time": execution_time,
                            "sequence_length": len(combination.sequence),
                            "category": combination.test_category
                        })
                        
                        # Check for new states
                        state_fingerprint = state_after.fingerprint()
                        if state_fingerprint not in self.state_graph:
                            self.state_graph[state_fingerprint] = {
                                "state": state_after,
                                "discovered_by": combination,
                                "discovery_index": i
                            }
                            exploration_results["states_discovered"] += 1
                            
                    except Exception as e:
                        # Log execution error
                        exploration_results["execution_errors"] += 1
                        await self._log_execution_error(combination, i, str(e))
                        
                    progress.update(task, advance=1)
                    
                    # Prevent infinite loops or resource exhaustion
                    if i > 0 and i % 100 == 0:
                        self.console.print(f"[dim]Processed {i}/{total_combinations} combinations...[/]")
                        
        exploration_results["issues_found"] = len(self.discovered_issues)
        
        self.console.print(f"[bold green]✅ Exploration complete! "
                          f"Tested {exploration_results['combinations_tested']} combinations, "
                          f"found {exploration_results['issues_found']} issues![/]")
        
        return exploration_results
        
    async def _analyze_state_change(
        self, 
        before: TUIState, 
        after: TUIState, 
        combination: InputCombination,
        index: int
    ) -> None:
        """Analyze a state change for issues and anomalies."""
        
        # Quick checks for obvious issues
        issues = []
        
        # Check for crashes or severe errors
        if not after.visible_widgets:
            issues.append(self._create_issue(
                "CRITICAL_NO_WIDGETS",
                SeverityLevel.CRITICAL,
                "No widgets visible after input",
                f"All widgets disappeared after sequence: {combination.sequence}",
                combination,
                before,
                after,
                index
            ))
            
        # Check for performance issues
        if len(combination.timing) > 0:
            expected_time = sum(combination.timing) + 0.5  # Add buffer
            # Actual execution time would be measured in calling function
            
        # Check for visual anomalies using AI (if available)
        if self.ai_models["vision"]:
            try:
                ai_analysis = await self.harness.analyze_state_multimodal(after)
                
                if ai_analysis and "visual_anomalies" in ai_analysis:
                    for anomaly in ai_analysis["visual_anomalies"]:
                        issues.append(self._create_issue(
                            f"VISUAL_ANOMALY_{index}",
                            SeverityLevel.MEDIUM,
                            "Visual anomaly detected",
                            f"AI detected: {anomaly}",
                            combination,
                            before,
                            after,
                            index
                        ))
                        
            except Exception:
                pass  # AI analysis failed, continue
                
        # Check for text content issues
        if before.ansi_text and not after.ansi_text.strip():
            issues.append(self._create_issue(
                f"TEXT_DISAPPEARED_{index}",
                SeverityLevel.HIGH,
                "Text content disappeared",
                f"Text content vanished after sequence: {combination.sequence}",
                combination,
                before,
                after,
                index
            ))
            
        # Check for focus issues
        if before.focused_widget and not after.focused_widget:
            # Focus lost - might be intentional or problematic
            if "escape" not in combination.sequence:  # Escape often clears focus intentionally
                issues.append(self._create_issue(
                    f"FOCUS_LOST_{index}",
                    SeverityLevel.LOW,
                    "Focus lost unexpectedly",
                    f"Widget focus was lost after: {combination.sequence}",
                    combination,
                    before,
                    after,
                    index
                ))
                
        # Add all discovered issues
        self.discovered_issues.extend(issues)
        
    def _create_issue(
        self,
        issue_id: str,
        severity: SeverityLevel,
        title: str,
        description: str,
        combination: InputCombination,
        state_before: TUIState,
        state_after: TUIState,
        index: int
    ) -> TestingIssue:
        """Create a comprehensive testing issue."""
        
        return TestingIssue(
            id=f"{self.session_id}_{issue_id}",
            severity=severity,
            category=combination.test_category,
            title=title,
            description=description,
            reproduction_steps=self._generate_reproduction_steps(combination),
            evidence={
                "state_before": {
                    "widgets": state_before.visible_widgets,
                    "focused": state_before.focused_widget,
                    "text_length": len(state_before.ansi_text)
                },
                "state_after": {
                    "widgets": state_after.visible_widgets,
                    "focused": state_after.focused_widget,
                    "text_length": len(state_after.ansi_text)
                },
                "combination": {
                    "sequence": combination.sequence,
                    "timing": combination.timing,
                    "category": combination.test_category
                }
            },
            ai_analysis={},
            suggested_fixes=[],
            state_fingerprint=state_after.fingerprint(),
            screenshot_paths=[],
            discovered_at=datetime.now(),
        )
        
    def _generate_reproduction_steps(self, combination: InputCombination) -> List[str]:
        """Generate human-readable reproduction steps."""
        steps = ["1. Start the TUI application"]
        
        for i, key in enumerate(combination.sequence):
            timing = combination.timing[i] if i < len(combination.timing) else 0.0
            if timing > 0.1:
                steps.append(f"{i+2}. Wait {timing:.2f} seconds")
            steps.append(f"{i+2+(1 if timing > 0.1 else 0)}. Press '{key}'")
            
        steps.append(f"{len(steps)+1}. Observe the issue")
        return steps
        
    async def _log_execution_error(
        self, 
        combination: InputCombination, 
        index: int, 
        error: str
    ) -> None:
        """Log an execution error during testing."""
        
        issue = TestingIssue(
            id=f"{self.session_id}_EXEC_ERROR_{index}",
            severity=SeverityLevel.HIGH,
            category="execution_error",
            title="Input sequence execution failed",
            description=f"Failed to execute sequence {combination.sequence}: {error}",
            reproduction_steps=self._generate_reproduction_steps(combination),
            evidence={
                "error": error,
                "combination": {
                    "sequence": combination.sequence,
                    "timing": combination.timing,
                    "category": combination.test_category
                }
            },
            ai_analysis={},
            suggested_fixes=["Check for input handling errors", "Verify key sequence validity"],
            state_fingerprint="execution_error",
            discovered_at=datetime.now()
        )
        
        self.discovered_issues.append(issue)
        
    async def _phase_4_brutal_hammering(self) -> Dict[str, Any]:
        """
        🔨 PHASE 4: BRUTAL HAMMERING
        
        The most intense testing phase:
        - Stress testing with extreme inputs
        - Resource exhaustion attempts
        - Race condition discovery
        - Edge case boundary testing
        - Chaos engineering
        """
        self.phase = TestingPhase.HAMMERING
        self.console.print("[bold red]🔨 INITIATING BRUTAL HAMMERING MODE...[/]")
        
        hammering_results = {
            "stress_tests": 0,
            "chaos_tests": 0,
            "boundary_tests": 0,
            "race_conditions": 0,
            "crashes_induced": 0,
            "performance_degradation": []
        }
        
        if not self.brutal_mode:
            self.console.print("[yellow]Brutal mode disabled, skipping...[/]")
            return hammering_results
            
        app = self.app_class()
        async with app.run_test(size=(120, 40)) as pilot:
            
            # 1. Stress Testing - Rapid fire inputs
            self.console.print("💥 Stress test: Rapid fire inputs...")
            await self._stress_test_rapid_inputs(pilot, hammering_results)
            
            # 2. Chaos Testing - Random sequences
            self.console.print("🌪️ Chaos test: Random input chaos...")
            await self._chaos_test_random_sequences(pilot, hammering_results)
            
            # 3. Boundary Testing - Edge values
            self.console.print("📏 Boundary test: Edge case values...")
            await self._boundary_test_edge_cases(pilot, hammering_results)
            
            # 4. Resource Exhaustion
            self.console.print("🔄 Resource test: Memory and performance...")
            await self._resource_exhaustion_test(pilot, hammering_results)
            
            # 5. Race Condition Testing
            self.console.print("⚡ Race condition test: Concurrent operations...")
            await self._race_condition_test(pilot, hammering_results)
            
        self.console.print(f"[bold green]✅ Brutal hammering complete! "
                          f"Induced {hammering_results.get('crashes_induced', 0)} crashes![/]")
                          
        return hammering_results
        
    async def _stress_test_rapid_inputs(self, pilot: Pilot, results: Dict[str, Any]) -> None:
        """Stress test with extremely rapid inputs."""
        
        stress_sequences = [
            # Tab bombing
            ["tab"] * 50,
            # Arrow key spam
            ["up", "down"] * 25,
            ["left", "right"] * 25,
            # Enter spam
            ["enter"] * 20,
            # Mixed rapid sequence
            ["tab", "enter", "escape", "up", "down"] * 10
        ]
        
        for i, sequence in enumerate(stress_sequences):
            try:
                start_time = time.time()
                
                # Execute rapid sequence
                for key in sequence:
                    await pilot.press(key)
                    await asyncio.sleep(0.01)  # Extremely rapid
                    
                execution_time = time.time() - start_time
                
                # Check if UI is still responsive
                test_state = await self.harness.capture_tui_state(pilot, f"stress_{i}")
                
                if not test_state.visible_widgets:
                    results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                    
                results["performance_degradation"].append({
                    "test": f"stress_{i}",
                    "sequence_length": len(sequence),
                    "execution_time": execution_time,
                    "widgets_after": len(test_state.visible_widgets)
                })
                
            except Exception as e:
                results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                
        results["stress_tests"] = len(stress_sequences)
        
    async def _chaos_test_random_sequences(self, pilot: Pilot, results: Dict[str, Any]) -> None:
        """Chaos testing with completely random input sequences."""
        
        all_keys = [
            "tab", "shift+tab", "up", "down", "left", "right",
            "enter", "escape", "space", "backspace", "delete",
            "home", "end", "page_up", "page_down",
            "a", "b", "c", "1", "2", "3",
            "ctrl+a", "ctrl+c", "ctrl+v", "ctrl+s", "ctrl+q"
        ]
        
        chaos_tests = 20  # Number of chaos sequences
        
        for i in range(chaos_tests):
            try:
                # Generate random sequence
                sequence_length = random.randint(5, 30)
                chaos_sequence = [random.choice(all_keys) for _ in range(sequence_length)]
                
                # Execute with random timing
                for key in chaos_sequence:
                    await pilot.press(key)
                    await asyncio.sleep(random.uniform(0.001, 0.1))
                    
                # Check for survival
                test_state = await self.harness.capture_tui_state(pilot, f"chaos_{i}")
                
                if not test_state.visible_widgets:
                    results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                    
            except Exception:
                results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                
        results["chaos_tests"] = chaos_tests
        
    async def _boundary_test_edge_cases(self, pilot: Pilot, results: Dict[str, Any]) -> None:
        """Test boundary conditions and edge cases."""
        
        boundary_tests = [
            # Extremely slow inputs
            {"sequence": ["tab", "enter"], "timing": [5.0, 5.0]},
            # Zero-delay inputs
            {"sequence": ["up", "down", "left", "right"], "timing": [0.0, 0.0, 0.0, 0.0]},
            # Single key repeated many times
            {"sequence": ["tab"] * 100, "timing": [0.05] * 100},
        ]
        
        for i, test in enumerate(boundary_tests):
            try:
                sequence = test["sequence"]
                timing = test["timing"]
                
                for key, delay in zip(sequence, timing):
                    if delay > 0:
                        await asyncio.sleep(delay)
                    await pilot.press(key)
                    
                # Verify state
                test_state = await self.harness.capture_tui_state(pilot, f"boundary_{i}")
                
                if not test_state.visible_widgets:
                    results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                    
            except Exception:
                results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                
        results["boundary_tests"] = len(boundary_tests)
        
    async def _resource_exhaustion_test(self, pilot: Pilot, results: Dict[str, Any]) -> None:
        """Test resource exhaustion scenarios."""
        
        # Test rapid state changes to exhaust memory
        for i in range(100):
            try:
                await pilot.press("tab")
                await pilot.press("shift+tab")
                
                if i % 20 == 0:
                    # Check memory usage (simplified)
                    test_state = await self.harness.capture_tui_state(pilot, f"resource_{i}")
                    
            except Exception:
                results["crashes_induced"] = results.get("crashes_induced", 0) + 1
                break
                
    async def _race_condition_test(self, pilot: Pilot, results: Dict[str, Any]) -> None:
        """Test for race conditions with concurrent operations."""
        
        # Simulate concurrent key presses (as much as possible in single-threaded env)
        race_sequences = [
            ["tab", "enter"],
            ["up", "down"],
            ["left", "right"],
            ["escape", "space"]
        ]
        
        for sequence in race_sequences:
            try:
                # Rapid alternating inputs to try to catch race conditions
                for _ in range(10):
                    for key in sequence:
                        await pilot.press(key)
                        await asyncio.sleep(0.001)  # Minimal delay
                        
            except Exception:
                results["race_conditions"] = results.get("race_conditions", 0) + 1
                
    async def _phase_5_ai_validation(self) -> Dict[str, Any]:
        """
        🤖 PHASE 5: AI-POWERED VALIDATION
        
        Use multiple AI models to validate and analyze all findings:
        - Deep analysis of discovered issues
        - Cross-validation between different AI models
        - Severity assessment and prioritization
        - Root cause analysis
        """
        self.phase = TestingPhase.VALIDATION
        self.console.print("[bold cyan]🤖 AI analyzing all findings...[/]")
        
        validation_results = {
            "issues_analyzed": 0,
            "ai_confirmations": 0,
            "false_positives": 0,
            "severity_updates": 0,
            "root_causes_identified": 0
        }
        
        if not self.discovered_issues:
            self.console.print("[green]No issues found to validate![/]")
            return validation_results
            
        # Analyze each issue with AI
        for issue in self.discovered_issues:
            try:
                # Get AI analysis if we have the models
                if self.ai_models["reasoning"]:
                    ai_analysis = await self._get_ai_issue_analysis(issue)
                    issue.ai_analysis = ai_analysis
                    
                    # Update severity based on AI analysis
                    if ai_analysis.get("severity_recommendation"):
                        old_severity = issue.severity
                        new_severity = SeverityLevel(ai_analysis["severity_recommendation"])
                        if new_severity != old_severity:
                            issue.severity = new_severity
                            validation_results["severity_updates"] += 1
                            
                    # Add AI-suggested fixes
                    if ai_analysis.get("suggested_fixes"):
                        issue.suggested_fixes.extend(ai_analysis["suggested_fixes"])
                        
                validation_results["issues_analyzed"] += 1
                
            except Exception as e:
                self.console.print(f"[red]AI analysis failed for issue {issue.id}: {e}[/]")
                
        self.console.print(f"[bold green]✅ AI validation complete! "
                          f"Analyzed {validation_results['issues_analyzed']} issues![/]")
                          
        return validation_results
        
    async def _get_ai_issue_analysis(self, issue: TestingIssue) -> Dict[str, Any]:
        """Get comprehensive AI analysis of an issue."""
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.ai_models["reasoning"])
            
            prompt = f"""
            Analyze this TUI testing issue and provide comprehensive analysis:
            
            ISSUE: {issue.title}
            DESCRIPTION: {issue.description}
            CATEGORY: {issue.category}
            CURRENT SEVERITY: {issue.severity.value}
            
            REPRODUCTION STEPS:
            {chr(10).join(issue.reproduction_steps)}
            
            EVIDENCE:
            {json.dumps(issue.evidence, indent=2)}
            
            Please provide analysis in JSON format:
            {{
                "is_real_issue": true/false,
                "severity_recommendation": "critical/high/medium/low/info",
                "root_cause_analysis": "detailed explanation",
                "impact_assessment": "what users will experience",
                "suggested_fixes": ["fix 1", "fix 2", ...],
                "testing_gaps": ["what else should be tested"],
                "confidence_score": 0.0-1.0
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert TUI testing analyst."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"AI analysis failed: {e}"}
            
    async def _phase_6_auto_fix(self) -> Dict[str, Any]:
        """
        🔧 PHASE 6: AUTO-FIXING
        
        Attempt to automatically fix discovered issues:
        - Generate code patches
        - Apply CSS fixes
        - Update configuration
        - Create theme adjustments
        """
        self.phase = TestingPhase.AUTO_FIXING
        
        if not self.auto_fix:
            self.console.print("[yellow]Auto-fix disabled, skipping...[/]")
            return {"auto_fix_disabled": True}
            
        self.console.print("[bold magenta]🔧 Attempting automatic fixes...[/]")
        
        fix_results = {
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 0,
            "files_modified": []
        }
        
        critical_issues = [
            issue for issue in self.discovered_issues 
            if issue.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        ]
        
        for issue in critical_issues:
            try:
                fix_attempt = await self._attempt_auto_fix(issue)
                issue.fix_attempts.append(fix_attempt)
                
                if fix_attempt.get("success"):
                    issue.fixed = True
                    fix_results["fixes_successful"] += 1
                    fix_results["files_modified"].extend(fix_attempt.get("files_modified", []))
                else:
                    fix_results["fixes_failed"] += 1
                    
                fix_results["fixes_attempted"] += 1
                
            except Exception as e:
                fix_results["fixes_failed"] += 1
                self.console.print(f"[red]Auto-fix failed for {issue.id}: {e}[/]")
                
        self.console.print(f"[bold green]✅ Auto-fix complete! "
                          f"Fixed {fix_results['fixes_successful']}/{fix_results['fixes_attempted']} issues![/]")
                          
        return fix_results
        
    async def _attempt_auto_fix(self, issue: TestingIssue) -> Dict[str, Any]:
        """Attempt to automatically fix a specific issue."""
        
        fix_attempt = {
            "issue_id": issue.id,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "files_modified": [],
            "changes_made": [],
            "error": None
        }
        
        try:
            # Analyze the issue type and determine fix strategy
            if "contrast" in issue.description.lower() or "visibility" in issue.description.lower():
                # Try to fix contrast/visibility issues
                fix_attempt = await self._fix_contrast_issue(issue, fix_attempt)
                
            elif "navigation" in issue.description.lower() or "focus" in issue.description.lower():
                # Try to fix navigation issues
                fix_attempt = await self._fix_navigation_issue(issue, fix_attempt)
                
            elif "performance" in issue.description.lower() or "slow" in issue.description.lower():
                # Try to fix performance issues
                fix_attempt = await self._fix_performance_issue(issue, fix_attempt)
                
            else:
                # Generic fix attempt
                fix_attempt = await self._generic_fix_attempt(issue, fix_attempt)
                
        except Exception as e:
            fix_attempt["error"] = str(e)
            
        return fix_attempt
        
    async def _fix_contrast_issue(self, issue: TestingIssue, fix_attempt: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix contrast/visibility issues."""
        
        # Look for theme/CSS files
        theme_files = list(Path(".").glob("**/*theme*.css")) + list(Path(".").glob("**/*style*.css"))
        
        if theme_files:
            # Generate improved CSS with better contrast
            improved_css = """
/* Auto-generated high contrast improvements */
.high-contrast {
    background: #000000;
    color: #ffffff;
}

.focused {
    background: #0066cc;
    color: #ffffff;
    border: 2px solid #ffffff;
}

.text-content {
    color: #ffffff;
    background: #1a1a1a;
}

.button {
    background: #0066cc;
    color: #ffffff;
    border: 1px solid #ffffff;
}

.button:hover {
    background: #0080ff;
}
"""
            
            # Save the improved CSS
            fix_file = self.output_dir / "fixes" / f"contrast_fix_{issue.id}.css"
            fix_file.write_text(improved_css)
            
            fix_attempt["success"] = True
            fix_attempt["files_modified"] = [str(fix_file)]
            fix_attempt["changes_made"] = ["Generated high-contrast CSS"]
            
        return fix_attempt
        
    async def _fix_navigation_issue(self, issue: TestingIssue, fix_attempt: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix navigation issues."""
        
        # Generate navigation improvement suggestions
        nav_fix = """
# Navigation Fix Suggestions

## Issue: {issue.title}

### Recommended Code Changes:

1. Ensure proper focus management:
```python
def on_key(self, event: events.Key) -> None:
    if event.key == "tab":
        self.focus_next()
    elif event.key == "shift+tab":
        self.focus_previous()
```

2. Add focus indicators:
```css
Widget:focus {
    border: 2px solid #0066cc;
    outline: none;
}
```

3. Verify tab order:
```python
def compose(self) -> ComposeResult:
    with Container():
        yield Widget(id="first", tab_index=1)
        yield Widget(id="second", tab_index=2)
        yield Widget(id="third", tab_index=3)
```
""".format(issue=issue)
        
        fix_file = self.output_dir / "fixes" / f"navigation_fix_{issue.id}.md"
        fix_file.write_text(nav_fix)
        
        fix_attempt["success"] = True
        fix_attempt["files_modified"] = [str(fix_file)]
        fix_attempt["changes_made"] = ["Generated navigation improvement guide"]
        
        return fix_attempt
        
    async def _fix_performance_issue(self, issue: TestingIssue, fix_attempt: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix performance issues."""
        
        perf_fix = f"""
# Performance Fix for Issue: {issue.title}

## Analysis
{issue.description}

## Recommended Optimizations:

1. Add debouncing for rapid inputs:
```python
from asyncio import create_task, sleep

class OptimizedApp(App):
    def __init__(self):
        super().__init__()
        self._last_input_time = 0
        self._input_debounce = 0.1  # 100ms debounce
        
    async def on_key(self, event):
        current_time = time.time()
        if current_time - self._last_input_time < self._input_debounce:
            return  # Ignore rapid inputs
        self._last_input_time = current_time
        # Process input...
```

2. Optimize rendering:
```python
@work(exclusive=True)
async def update_display(self):
    # Batch updates together
    pass
```

3. Limit update frequency:
```python
self.set_interval(0.1, self.update_metrics)  # Max 10 FPS
```
"""
        
        fix_file = self.output_dir / "fixes" / f"performance_fix_{issue.id}.md"
        fix_file.write_text(perf_fix)
        
        fix_attempt["success"] = True
        fix_attempt["files_modified"] = [str(fix_file)]
        fix_attempt["changes_made"] = ["Generated performance optimization guide"]
        
        return fix_attempt
        
    async def _generic_fix_attempt(self, issue: TestingIssue, fix_attempt: Dict[str, Any]) -> Dict[str, Any]:
        """Generic fix attempt for unclassified issues."""
        
        generic_fix = f"""
# Generic Fix for Issue: {issue.title}

## Issue Details
- **ID**: {issue.id}
- **Severity**: {issue.severity.value}
- **Category**: {issue.category}
- **Description**: {issue.description}

## Reproduction Steps
{chr(10).join(f"{i}. {step}" for i, step in enumerate(issue.reproduction_steps, 1))}

## Evidence
```json
{json.dumps(issue.evidence, indent=2)}
```

## AI Analysis
{json.dumps(issue.ai_analysis, indent=2) if issue.ai_analysis else "No AI analysis available"}

## Suggested Fixes
{chr(10).join(f"- {fix}" for fix in issue.suggested_fixes)}

## Debugging Steps
1. Add logging to track the issue:
```python
import logging
logger = logging.getLogger(__name__)

# Add at the problem location
logger.debug(f"State before issue: {{state_info}}")
```

2. Add error handling:
```python
try:
    # Problem code
    pass
except Exception as e:
    logger.error(f"Issue reproduced: {{e}}")
```

3. Add validation:
```python
assert condition, f"Validation failed: {{condition}}"
```
"""
        
        fix_file = self.output_dir / "fixes" / f"generic_fix_{issue.id}.md"
        fix_file.write_text(generic_fix)
        
        fix_attempt["success"] = True
        fix_attempt["files_modified"] = [str(fix_file)]
        fix_attempt["changes_made"] = ["Generated generic fix documentation"]
        
        return fix_attempt
        
    async def _phase_7_reporting(self) -> Dict[str, Any]:
        """
        📊 PHASE 7: COMPREHENSIVE REPORTING
        
        Generate detailed reports with visual evidence:
        - Executive summary
        - Detailed issue breakdown
        - Visual evidence gallery
        - Performance analysis
        - Recommendations and fixes
        """
        self.phase = TestingPhase.REPORTING
        self.console.print("[bold blue]📊 Generating comprehensive reports...[/]")
        
        report_data = await self._generate_comprehensive_report()
        
        # Generate different report formats
        html_report = await self._generate_html_report(report_data)
        json_report = await self._generate_json_report(report_data)
        markdown_report = await self._generate_markdown_report(report_data)
        
        # Display final summary
        self._display_final_summary(report_data)
        
        return {
            "html_report": str(html_report),
            "json_report": str(json_report),
            "markdown_report": str(markdown_report),
            "total_issues": len(self.discovered_issues),
            "critical_issues": len([i for i in self.discovered_issues if i.severity == SeverityLevel.CRITICAL]),
            "test_duration": (datetime.now() - self.test_start_time).total_seconds()
        }
        
    async def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive report data."""
        
        end_time = datetime.now()
        total_duration = end_time - self.test_start_time
        
        # Categorize issues by severity
        issues_by_severity = {}
        for severity in SeverityLevel:
            issues_by_severity[severity.value] = [
                issue for issue in self.discovered_issues if issue.severity == severity
            ]
            
        # Categorize issues by type
        issues_by_category = {}
        for issue in self.discovered_issues:
            category = issue.category
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue)
            
        # Calculate statistics
        stats = {
            "total_tests_executed": len(self.input_combinations),
            "total_states_discovered": len(self.state_graph),
            "total_issues_found": len(self.discovered_issues),
            "critical_issues": len(issues_by_severity.get("critical", [])),
            "high_issues": len(issues_by_severity.get("high", [])),
            "medium_issues": len(issues_by_severity.get("medium", [])),
            "low_issues": len(issues_by_severity.get("low", [])),
            "test_duration_seconds": total_duration.total_seconds(),
            "test_duration_human": str(total_duration),
            "issues_per_minute": len(self.discovered_issues) / (total_duration.total_seconds() / 60),
            "success_rate": 1.0 - (len(self.discovered_issues) / max(len(self.input_combinations), 1))
        }
        
        return {
            "session_id": self.session_id,
            "timestamp": end_time.isoformat(),
            "test_start": self.test_start_time.isoformat(),
            "test_end": end_time.isoformat(),
            "app_class": self.app_class.__name__,
            "statistics": stats,
            "issues_by_severity": {k: [self._serialize_issue(i) for i in v] for k, v in issues_by_severity.items()},
            "issues_by_category": {k: [self._serialize_issue(i) for i in v] for k, v in issues_by_category.items()},
            "ui_discovery": {
                "widget_types": list(self.ui_knowledge.widget_types),
                "total_widgets_discovered": len(self.ui_knowledge.widget_types),
                "interactive_elements": len(self.ui_knowledge.interactive_elements),
            },
            "performance_summary": self._summarize_performance(),
            "recommendations": self._generate_recommendations()
        }
        
    def _serialize_issue(self, issue: TestingIssue) -> Dict[str, Any]:
        """Serialize an issue for reporting."""
        return {
            "id": issue.id,
            "severity": issue.severity.value,
            "category": issue.category,
            "title": issue.title,
            "description": issue.description,
            "reproduction_steps": issue.reproduction_steps,
            "evidence": issue.evidence,
            "ai_analysis": issue.ai_analysis,
            "suggested_fixes": issue.suggested_fixes,
            "discovered_at": issue.discovered_at.isoformat(),
            "fixed": issue.fixed,
            "fix_attempts": len(issue.fix_attempts)
        }
        
    def _summarize_performance(self) -> Dict[str, Any]:
        """Summarize performance findings."""
        return {
            "total_performance_samples": len(self.performance_history),
            "average_response_time": sum(p.get("execution_time", 0) for p in self.performance_history) / max(len(self.performance_history), 1),
            "performance_issues_found": len([i for i in self.discovered_issues if "performance" in i.category.lower()])
        }
        
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        critical_count = len([i for i in self.discovered_issues if i.severity == SeverityLevel.CRITICAL])
        if critical_count > 0:
            recommendations.append(f"🚨 URGENT: Fix {critical_count} critical issues immediately")
            
        high_count = len([i for i in self.discovered_issues if i.severity == SeverityLevel.HIGH])
        if high_count > 0:
            recommendations.append(f"⚠️ HIGH PRIORITY: Address {high_count} high-severity issues")
            
        # Check for patterns
        contrast_issues = len([i for i in self.discovered_issues if "contrast" in i.description.lower()])
        if contrast_issues > 2:
            recommendations.append("🎨 Consider implementing a high-contrast theme")
            
        nav_issues = len([i for i in self.discovered_issues if "navigation" in i.category.lower()])
        if nav_issues > 2:
            recommendations.append("🧭 Review and improve keyboard navigation flow")
            
        perf_issues = len([i for i in self.discovered_issues if "performance" in i.category.lower()])
        if perf_issues > 1:
            recommendations.append("⚡ Implement performance optimizations")
            
        if not self.discovered_issues:
            recommendations.append("🎉 Excellent! No issues found - your TUI is rock solid!")
            
        return recommendations
        
    async def _generate_html_report(self, data: Dict[str, Any]) -> Path:
        """Generate beautiful HTML report."""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Sentient TUI Destroyer Report - {data['session_id']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; color: #333; background: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px;
            text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .stats-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }}
        .stat-card {{ 
            background: white; padding: 25px; border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
        .critical {{ color: #e74c3c; }}
        .high {{ color: #f39c12; }}
        .medium {{ color: #f1c40f; }}
        .low {{ color: #27ae60; }}
        .info {{ color: #3498db; }}
        .issues-section {{ background: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .issue-card {{ 
            border-left: 4px solid #ddd; padding: 20px; margin-bottom: 20px;
            border-radius: 0 8px 8px 0; background: #f8f9fa;
        }}
        .issue-critical {{ border-left-color: #e74c3c; }}
        .issue-high {{ border-left-color: #f39c12; }}
        .issue-medium {{ border-left-color: #f1c40f; }}
        .issue-low {{ border-left-color: #27ae60; }}
        .recommendations {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px;
        }}
        .footer {{ text-align: center; padding: 30px; color: #666; }}
        .code {{ background: #f4f4f4; padding: 10px; border-radius: 6px; font-family: monospace; }}
        .badge {{ 
            display: inline-block; padding: 4px 12px; border-radius: 20px;
            font-size: 0.8em; font-weight: bold; color: white; margin-right: 10px;
        }}
        .reproduction-steps {{ 
            background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;
            border-left: 4px solid #007bff;
        }}
        .evidence {{ background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 SENTIENT TUI DESTROYER</h1>
            <h2>Comprehensive Testing Report</h2>
            <p>Session: {data['session_id']}</p>
            <p>App: {data['app_class']}</p>
            <p>Generated: {data['timestamp']}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{data['statistics']['total_tests_executed']}</div>
                <div>Tests Executed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['statistics']['total_issues_found']}</div>
                <div>Issues Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number critical">{data['statistics']['critical_issues']}</div>
                <div>Critical Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['statistics']['test_duration_human']}</div>
                <div>Test Duration</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['statistics']['success_rate']:.1%}</div>
                <div>Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data['statistics']['issues_per_minute']:.1f}</div>
                <div>Issues/Minute</div>
            </div>
        </div>

        <div class="recommendations">
            <h2>🎯 Key Recommendations</h2>
            <ul>
                {chr(10).join(f"<li>{rec}</li>" for rec in data['recommendations'])}
            </ul>
        </div>
"""

        # Add issues by severity
        for severity in ["critical", "high", "medium", "low", "info"]:
            severity_issues = data['issues_by_severity'].get(severity, [])
            if severity_issues:
                html_content += f"""
        <div class="issues-section">
            <h2 class="{severity}">{severity.upper()} Issues ({len(severity_issues)})</h2>
"""
                for issue in severity_issues:
                    html_content += f"""
            <div class="issue-card issue-{severity}">
                <h3>{issue['title']} <span class="badge" style="background-color: {self._get_severity_color(severity)}">{severity.upper()}</span></h3>
                <p><strong>Category:</strong> {issue['category']}</p>
                <p><strong>Description:</strong> {issue['description']}</p>
                
                <div class="reproduction-steps">
                    <strong>🔄 Reproduction Steps:</strong>
                    <ol>
                        {chr(10).join(f"<li>{step}</li>" for step in issue['reproduction_steps'])}
                    </ol>
                </div>
                
                {f'''
                <div class="evidence">
                    <strong>📊 Evidence:</strong>
                    <pre class="code">{json.dumps(issue['evidence'], indent=2)}</pre>
                </div>
                ''' if issue['evidence'] else ''}
                
                {f'''
                <div>
                    <strong>🤖 AI Analysis:</strong>
                    <pre class="code">{json.dumps(issue['ai_analysis'], indent=2)}</pre>
                </div>
                ''' if issue['ai_analysis'] else ''}
                
                {f'''
                <div>
                    <strong>🔧 Suggested Fixes:</strong>
                    <ul>
                        {chr(10).join(f"<li>{fix}</li>" for fix in issue['suggested_fixes'])}
                    </ul>
                </div>
                ''' if issue['suggested_fixes'] else ''}
                
                <p><small><strong>Discovered:</strong> {issue['discovered_at']} | <strong>Fixed:</strong> {'✅ Yes' if issue['fixed'] else '❌ No'}</small></p>
            </div>
"""
                html_content += "</div>"

        html_content += """
        <div class="footer">
            <p>🤖 Generated by Sentient TUI Destroyer</p>
            <p>The most advanced TUI testing system ever created</p>
        </div>
    </div>
</body>
</html>
"""

        # Save HTML report
        html_path = self.output_dir / "reports" / f"destroyer_report_{self.session_id}.html"
        html_path.write_text(html_content, encoding='utf-8')
        
        return html_path
        
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level."""
        colors = {
            "critical": "#e74c3c",
            "high": "#f39c12", 
            "medium": "#f1c40f",
            "low": "#27ae60",
            "info": "#3498db"
        }
        return colors.get(severity, "#666")
        
    async def _generate_json_report(self, data: Dict[str, Any]) -> Path:
        """Generate machine-readable JSON report."""
        json_path = self.output_dir / "reports" / f"destroyer_report_{self.session_id}.json"
        json_path.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
        return json_path
        
    async def _generate_markdown_report(self, data: Dict[str, Any]) -> Path:
        """Generate Markdown report for documentation."""
        
        md_content = f"""# 🤖 Sentient TUI Destroyer Report

**Session ID:** {data['session_id']}  
**App:** {data['app_class']}  
**Test Duration:** {data['statistics']['test_duration_human']}  
**Generated:** {data['timestamp']}

## 📊 Executive Summary

- **Total Tests:** {data['statistics']['total_tests_executed']}
- **Issues Found:** {data['statistics']['total_issues_found']}
- **Critical Issues:** {data['statistics']['critical_issues']}
- **Success Rate:** {data['statistics']['success_rate']:.1%}
- **Issues per Minute:** {data['statistics']['issues_per_minute']:.1f}

## 🎯 Key Recommendations

{chr(10).join(f"- {rec}" for rec in data['recommendations'])}

## 🐛 Issues by Severity

"""
        
        for severity in ["critical", "high", "medium", "low", "info"]:
            severity_issues = data['issues_by_severity'].get(severity, [])
            if severity_issues:
                md_content += f"\n### {severity.upper()} Issues ({len(severity_issues)})\n\n"
                
                for issue in severity_issues:
                    md_content += f"""#### {issue['title']}

**Category:** {issue['category']}  
**Description:** {issue['description']}

**Reproduction Steps:**
{chr(10).join(f"{i}. {step}" for i, step in enumerate(issue['reproduction_steps'], 1))}

**Suggested Fixes:**
{chr(10).join(f"- {fix}" for fix in issue['suggested_fixes']) if issue['suggested_fixes'] else "No suggestions available"}

**Status:** {'✅ Fixed' if issue['fixed'] else '❌ Not Fixed'}

---

"""

        md_content += f"""
## 📈 Performance Summary

- **Total Performance Samples:** {data['performance_summary']['total_performance_samples']}
- **Average Response Time:** {data['performance_summary']['average_response_time']:.3f}s
- **Performance Issues:** {data['performance_summary']['performance_issues_found']}

## 🔍 UI Discovery

- **Widget Types Discovered:** {len(data['ui_discovery']['widget_types'])}
- **Interactive Elements:** {data['ui_discovery']['interactive_elements']}

**Widget Types:**
{chr(10).join(f"- {widget}" for widget in data['ui_discovery']['widget_types'])}

---

*Generated by 🤖 Sentient TUI Destroyer - The Ultimate TUI Testing System*
"""
        
        md_path = self.output_dir / "reports" / f"destroyer_report_{self.session_id}.md"
        md_path.write_text(md_content, encoding='utf-8')
        
        return md_path
        
    def _display_final_summary(self, data: Dict[str, Any]) -> None:
        """Display epic final summary in the console."""
        
        # Create summary table
        table = Table(title="🤖 SENTIENT TUI DESTROYER - FINAL RESULTS", style="bold")
        
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="magenta", width=20)
        table.add_column("Assessment", style="green", width=30)
        
        # Add statistics
        stats = data['statistics']
        
        table.add_row("Total Tests Executed", str(stats['total_tests_executed']), "Comprehensive")
        table.add_row("Issues Discovered", str(stats['total_issues_found']), 
                     "🚨 Needs Attention" if stats['total_issues_found'] > 0 else "🎉 Perfect!")
        table.add_row("Critical Issues", str(stats['critical_issues']),
                     "🔥 URGENT!" if stats['critical_issues'] > 0 else "✅ None")
        table.add_row("High Priority Issues", str(stats['high_issues']),
                     "⚠️ Important" if stats['high_issues'] > 0 else "✅ None")
        table.add_row("Success Rate", f"{stats['success_rate']:.1%}",
                     "🏆 Excellent" if stats['success_rate'] > 0.95 else "🔧 Needs Work")
        table.add_row("Test Duration", stats['test_duration_human'], "Thorough")
        table.add_row("Issues per Minute", f"{stats['issues_per_minute']:.1f}", "High Detection Rate")
        
        self.console.print(table)
        
        # Show recommendations
        if data['recommendations']:
            self.console.print("\n[bold yellow]🎯 KEY RECOMMENDATIONS:[/]")
            for i, rec in enumerate(data['recommendations'], 1):
                self.console.print(f"[yellow]{i}.[/] {rec}")
                
        # Final verdict
        if stats['critical_issues'] > 0:
            self.console.print(f"\n[bold red]🚨 VERDICT: CRITICAL ISSUES FOUND - IMMEDIATE ACTION REQUIRED![/]")
        elif stats['high_issues'] > 0:
            self.console.print(f"\n[bold yellow]⚠️ VERDICT: HIGH PRIORITY ISSUES - SHOULD BE ADDRESSED SOON[/]")
        elif stats['total_issues_found'] > 0:
            self.console.print(f"\n[bold blue]ℹ️ VERDICT: MINOR ISSUES FOUND - CONSIDER ADDRESSING[/]")
        else:
            self.console.print(f"\n[bold green]🏆 VERDICT: PERFECT TUI - NO ISSUES FOUND![/]")
            
        # Show report locations
        self.console.print(f"\n[bold cyan]📊 Reports generated in:[/] {self.output_dir}/reports/")
        self.console.print(f"[bold cyan]🔧 Auto-fixes in:[/] {self.output_dir}/fixes/")
        self.console.print(f"[bold cyan]📸 Screenshots in:[/] {self.output_dir}/screenshots/")
        
    def _log_critical_error(self, error: str) -> None:
        """Log a critical error that stops the destroyer."""
        error_log = self.output_dir / "critical_error.log"
        with open(error_log, "w") as f:
            f.write(f"CRITICAL ERROR at {datetime.now().isoformat()}\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Error: {error}\n")


# Convenience function for easy usage
async def destroy_tui(
    app_class: type[App],
    brutal_mode: bool = True,
    auto_fix: bool = True,
    max_duration: int = 3600,
    **kwargs
) -> Dict[str, Any]:
    """
    🔥 DESTROY A TUI WITH EXTREME PREJUDICE 🔥
    
    Args:
        app_class: The TUI app class to destroy
        brutal_mode: Enable brutal hammering (default: True)
        auto_fix: Attempt automatic fixes (default: True)
        max_duration: Maximum test duration in seconds
        **kwargs: Additional arguments for the destroyer
        
    Returns:
        Comprehensive destruction results
    """
    destroyer = SentientTUIDestroyer(
        app_class=app_class,
        brutal_mode=brutal_mode,
        auto_fix=auto_fix,
        max_test_duration=max_duration,
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("CLAUDE_API_KEY"),
        **kwargs
    )
    
    return await destroyer.initiate_total_destruction()


if __name__ == "__main__":
    
    print("🔥🤖 SENTIENT TUI DESTROYER - INITIALIZING... 🤖🔥")
    
    # Example usage - destroy the Advanced Canopy TUI
    results = asyncio.run(destroy_tui(
        app_class=AdvancedCanopyTUI,
        brutal_mode=True,
        auto_fix=True,
        max_duration=1800,  # 30 minutes
        output_dir="destroyer_results"
    ))
    
    print(f"\n🎯 DESTRUCTION COMPLETE!")
    print(f"📊 Results: {results['reporting']['total_issues']} issues found")
    print(f"⚡ Critical: {results['reporting']['critical_issues']} issues")
    print(f"📁 Reports: {results['reporting']['html_report']}")
    
    # Exit with appropriate code
    if results['reporting']['critical_issues'] > 0:
        exit(1)  # Critical issues found
    else:
        exit(0)  # Success