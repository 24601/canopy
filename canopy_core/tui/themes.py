"""Theme system for MassGen TUI with multiple color schemes."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Represents a complete theme for the TUI."""

    name: str
    description: str
    primary: str
    secondary: str
    background: str
    surface: str
    panel: str
    accent: str
    success: str
    warning: str
    error: str
    text: str
    text_muted: str
    text_disabled: str
    border: str
    border_focused: str

    def to_css_variables(self) -> str:
        """Convert theme to CSS variables."""
        return f"""
        $primary: {self.primary};
        $secondary: {self.secondary};
        $background: {self.background};
        $surface: {self.surface};
        $panel: {self.panel};
        $accent: {self.accent};
        $success: {self.success};
        $warning: {self.warning};
        $error: {self.error};
        $text: {self.text};
        $text-muted: {self.text_muted};
        $text-disabled: {self.text_disabled};
        $border: {self.border};
        $border-focused: {self.border_focused};
        """


# Predefined themes
THEMES: Dict[str, Theme] = {
    "dark": Theme(
        name="dark",
        description="EXTREME HIGH CONTRAST dark theme - MAXIMUM VISIBILITY",
        primary="#00ffff",  # Bright cyan - very visible
        secondary="#ff0080",  # Bright magenta
        background="#000000",  # Pure black for maximum contrast
        surface="#505050",  # Very light gray surface for maximum contrast
        panel="#707070",  # Even lighter panel - easily distinguishable
        accent="#ffff00",  # Bright yellow accent
        success="#00ff00",  # Bright green
        warning="#ff8000",  # Bright orange
        error="#ff0000",  # Bright red
        text="#ffffff",  # Pure white text
        text_muted="#f0f0f0",  # Almost white for muted text - NO MORE DARK GRAY!
        text_disabled="#c0c0c0",  # Very visible disabled text
        border="#a0a0a0",  # Very light gray borders - extremely visible
        border_focused="#00ffff",
    ),
    "light": Theme(
        name="light",
        description="Clean light theme for bright environments",
        primary="#0ea5e9",
        secondary="#ec4899",
        background="#ffffff",
        surface="#f8fafc",
        panel="#f1f5f9",
        accent="#8b5cf6",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        text="#0f172a",
        text_muted="#64748b",
        text_disabled="#cbd5e1",
        border="#e2e8f0",
        border_focused="#0ea5e9",
    ),
    "monokai": Theme(
        name="monokai",
        description="Popular Monokai color scheme",
        primary="#66d9ef",
        secondary="#f92672",
        background="#272822",
        surface="#3e3d32",
        panel="#3e3d32",
        accent="#a6e22e",
        success="#a6e22e",
        warning="#fd971f",
        error="#f92672",
        text="#f8f8f2",
        text_muted="#75715e",
        text_disabled="#49483e",
        border="#49483e",
        border_focused="#66d9ef",
    ),
    "dracula": Theme(
        name="dracula",
        description="Popular Dracula theme",
        primary="#bd93f9",
        secondary="#ff79c6",
        background="#282a36",
        surface="#383a59",
        panel="#44475a",
        accent="#50fa7b",
        success="#50fa7b",
        warning="#ffb86c",
        error="#ff5555",
        text="#f8f8f2",
        text_muted="#6272a4",
        text_disabled="#44475a",
        border="#44475a",
        border_focused="#bd93f9",
    ),
    "solarized_dark": Theme(
        name="solarized_dark",
        description="Solarized dark theme",
        primary="#268bd2",
        secondary="#2aa198",
        background="#002b36",
        surface="#073642",
        panel="#073642",
        accent="#b58900",
        success="#859900",
        warning="#cb4b16",
        error="#dc322f",
        text="#839496",
        text_muted="#586e75",
        text_disabled="#073642",
        border="#073642",
        border_focused="#268bd2",
    ),
    "tokyo_night": Theme(
        name="tokyo_night",
        description="Tokyo Night theme",
        primary="#7aa2f7",
        secondary="#bb9af7",
        background="#1a1b26",
        surface="#24283b",
        panel="#24283b",
        accent="#7dcfff",
        success="#9ece6a",
        warning="#e0af68",
        error="#f7768e",
        text="#c0caf5",
        text_muted="#565f89",
        text_disabled="#414868",
        border="#414868",
        border_focused="#7aa2f7",
    ),
    "gruvbox": Theme(
        name="gruvbox",
        description="Gruvbox dark theme",
        primary="#83a598",
        secondary="#fb4934",
        background="#282828",
        surface="#3c3836",
        panel="#3c3836",
        accent="#fabd2f",
        success="#b8bb26",
        warning="#fe8019",
        error="#fb4934",
        text="#ebdbb2",
        text_muted="#a89984",
        text_disabled="#504945",
        border="#504945",
        border_focused="#83a598",
    ),
    "nord": Theme(
        name="nord",
        description="Nord theme",
        primary="#88c0d0",
        secondary="#81a1c1",
        background="#2e3440",
        surface="#3b4252",
        panel="#434c5e",
        accent="#5e81ac",
        success="#a3be8c",
        warning="#ebcb8b",
        error="#bf616a",
        text="#eceff4",
        text_muted="#d8dee9",
        text_disabled="#4c566a",
        border="#4c566a",
        border_focused="#88c0d0",
    ),
    "catppuccin": Theme(
        name="catppuccin",
        description="Catppuccin Mocha theme",
        primary="#89b4fa",
        secondary="#f5c2e7",
        background="#1e1e2e",
        surface="#313244",
        panel="#313244",
        accent="#cba6f7",
        success="#a6e3a1",
        warning="#f9e2af",
        error="#f38ba8",
        text="#cdd6f4",
        text_muted="#a6adc8",
        text_disabled="#45475a",
        border="#45475a",
        border_focused="#89b4fa",
    ),
    "cyberpunk": Theme(
        name="cyberpunk",
        description="Neon cyberpunk theme",
        primary="#00ffff",
        secondary="#ff00ff",
        background="#0a0a0a",
        surface="#1a0a1a",
        panel="#2a1a2a",
        accent="#ffff00",
        success="#00ff00",
        warning="#ff8800",
        error="#ff0066",
        text="#ffffff",
        text_muted="#cc00cc",
        text_disabled="#660066",
        border="#ff00ff",
        border_focused="#00ffff",
    ),
}


class ThemeManager:
    """Manages theme switching and application."""

    def __init__(self, default_theme: str = "dark"):
        """Initialize with a default theme."""
        self.current_theme_name = default_theme
        self.current_theme = THEMES.get(default_theme, THEMES["dark"])

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme by name."""
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.current_theme = THEMES[theme_name]
            return True
        return False

    def get_theme(self) -> Theme:
        """Get the current theme."""
        return self.current_theme

    def get_theme_names(self) -> list[str]:
        """Get list of available theme names."""
        return list(THEMES.keys())

    def get_theme_css(self) -> str:
        """Generate CSS for the current theme."""
        theme = self.current_theme
        return f"""
        /* Theme: {theme.name} */
        {theme.to_css_variables()}

        /* Global theme application */
        Screen {{
            background: $background;
            color: $text;
        }}

        /* Panel styling */
        .panel {{
            background: $panel;
            border: tall $border;
        }}

        .panel:focus {{
            border: tall $border-focused;
        }}

        /* Agent panels */
        AgentPanel {{
            background: $surface;
            border: tall $border;
            color: $text;
        }}

        AgentPanel:focus {{
            border: tall $border-focused;
        }}

        AgentPanel.working {{
            border: tall $primary;
            background: $primary 15%;
        }}

        AgentPanel.voting {{
            border: tall $accent;
            background: $accent 15%;
        }}

        AgentPanel.error {{
            border: tall $error;
            background: $error 20%;
        }}

        /* System status panel */
        SystemStatusPanel {{
            background: $surface;
            border: tall $border;
            color: $text;
        }}

        SystemStatusPanel .status-active {{
            color: $success;
        }}

        SystemStatusPanel .status-paused {{
            color: $warning;
        }}

        SystemStatusPanel .status-error {{
            color: $error;
        }}

        /* Vote distribution */
        VoteDistribution {{
            background: $surface;
            border: tall $border;
        }}

        VoteDistribution .vote-bar {{
            background: $primary;
        }}

        VoteDistribution .consensus-reached {{
            color: $success;
        }}

        /* Trace panel */
        TracePanel {{
            background: $surface;
            border: tall $border;
        }}

        TracePanel .trace-info {{
            color: $text-muted;
        }}

        TracePanel .trace-warning {{
            color: $warning;
        }}

        TracePanel .trace-error {{
            color: $error;
        }}

        /* Buttons */
        Button {{
            background: $surface;
            color: $text;
            border: tall $border;
        }}

        Button:hover {{
            background: $panel;
            border: tall $primary;
        }}

        Button:focus {{
            background: $panel;
            border: tall $border-focused;
        }}

        Button.primary {{
            background: $primary;
            color: $background;
        }}

        Button.success {{
            background: $success;
            color: $background;
        }}

        Button.warning {{
            background: $warning;
            color: $background;
        }}

        Button.error {{
            background: $error;
            color: $background;
        }}

        /* Input fields */
        Input {{
            background: $surface;
            border: tall $border;
            color: $text;
        }}

        Input:focus {{
            border: tall $border-focused;
        }}

        /* Labels and text */
        Label {{
            color: $text;
        }}

        Label.muted {{
            color: $text-muted;
        }}

        Label.disabled {{
            color: $text-disabled;
        }}

        /* Scrollbars */
        ScrollBar {{
            background: $surface;
        }}

        ScrollBarThumb {{
            background: $border;
        }}

        ScrollBarThumb:hover {{
            background: $primary;
        }}

        /* Modal dialogs */
        ModalScreen {{
            background: $background 90%;
        }}

        .dialog {{
            background: $surface;
            border: thick $border;
            padding: 1 2;
        }}

        /* DataTable */
        DataTable {{
            background: $surface;
            color: $text;
        }}

        DataTable > .datatable--header {{
            background: $panel;
            color: $text;
            text-style: bold;
        }}

        DataTable > .datatable--cursor {{
            background: $primary 20%;
        }}

        DataTable > .datatable--hover {{
            background: $primary 10%;
        }}

        /* Tree view */
        Tree {{
            background: $surface;
            color: $text;
        }}

        Tree > .tree--cursor {{
            background: $primary 20%;
        }}

        /* Footer */
        Footer {{
            background: $panel;
            color: $text-muted;
        }}

        Footer > .footer--key {{
            background: $surface;
            color: $text;
        }}

        Footer > .footer--description {{
            color: $text-muted;
        }}
        """

    def cycle_theme(self) -> str:
        """Cycle to the next theme."""
        theme_names = self.get_theme_names()
        current_index = theme_names.index(self.current_theme_name)
        next_index = (current_index + 1) % len(theme_names)
        next_theme = theme_names[next_index]
        self.set_theme(next_theme)
        return next_theme
