# Canopy TUI Interface

Canopy provides a single, advanced Terminal User Interface (TUI) with **EXTREME HIGH CONTRAST** for maximum visibility and accessibility.

## Features

- **Single TUI Implementation**: Only one TUI (`AdvancedCanopyTUI`) - all others have been removed
- **Extreme High Contrast**: Pure black background with bright white text and colorful accents
- **Real-time Updates**: Live streaming of agent status and system metrics
- **Bright Visual Elements**: Cyan borders, yellow accents, bright colored buttons
- **Advanced Data Tables**: With bright cyan headers and high contrast rows
- **Comprehensive Logging**: Built-in RichLog with white text on dark background
- **Responsive Controls**: Keyboard shortcuts with immediate visual feedback

## High Contrast Design

The TUI uses an extreme high contrast color scheme for maximum visibility:

- **Background**: Pure black (`#000000`)
- **Text**: Pure white (`#ffffff`)
- **Borders**: Bright cyan (`#00ffff`)
- **Accents**: Bright yellow (`#ffff00`)
- **Success**: Bright green (`#00ff00`)
- **Warning**: Bright orange (`#ff8000`)
- **Error**: Bright red (`#ff0000`)
- **Buttons**: High contrast with bright backgrounds and dark text

## Usage

Start the TUI with any model configuration:

```bash
# Single model
python cli.py --tui --models o4-mini

# Multiple models
python cli.py --tui --models o4-mini grok-4

# With configuration file
python cli.py --tui --config examples/production.yaml
```

## Keyboard Shortcuts

- `q` - Quit application
- `r` - Refresh display
- `p` - Pause/Resume session
- `s` - Start new session
- `Ctrl+T` - Toggle theme (currently disabled - using fixed high contrast)
- `Ctrl+S` - Save session
- `Ctrl+R` - Reset session
- `Tab` / `Shift+Tab` - Navigate between elements
- `Arrow Keys` - Navigate within elements
- `Enter` - Activate focused element
- `Escape` - Cancel/back

## Interface Layout

### System Status Panel
- **Location**: Top of screen
- **Display**: Bright cyan border with yellow title
- **Contents**: Phase, consensus status, debate rounds, active agents, duration
- **Colors**: White text on medium gray background for high contrast

### Agents Container
- **Location**: Main content area
- **Display**: Individual agent panels with bright borders
- **Contents**: Agent progress, model information, output logs
- **Colors**: Each agent has distinct colored borders (cyan, magenta, etc.)

### Information Panel
- **Location**: Right side
- **Contents**: Vote distribution, additional metrics
- **Display**: Bright orange borders for vote visualization

### Main Log
- **Location**: Lower portion
- **Display**: Bright green border
- **Contents**: System-wide logging with white text
- **Features**: Auto-scrolling, search functionality

### Controls
- **Location**: Bottom
- **Display**: Control buttons with high contrast colors
- **Buttons**: Start (cyan), Pause (gray), Reset (orange), Save (green)

## Technical Implementation

### Single TUI Architecture
- **File**: `canopy_core/tui/advanced_app.py`
- **CSS**: `canopy_core/tui/advanced_styles.css`
- **Class**: `AdvancedCanopyTUI`
- **Framework**: Textual 5 with modern reactive programming

### Removed Components
- Old `app.py` (CanopyApp) - DELETED
- Old `styles.css` - DELETED
- Widget system in `widgets/` - DELETED
- All test TUI implementations - KEPT ONLY FOR TESTING

### CSS Architecture
The TUI uses hardcoded high contrast values instead of theme variables:

```css
/* Pure black background, white text */
Screen {
    background: #000000;
    color: #ffffff;
}

/* Bright cyan borders */
.panel {
    border: solid #00ffff;
    border-title-color: #ffff00;
}

/* High contrast buttons */
Button.-primary {
    background: #00ffff;
    color: #000000;
}
```

## Accessibility Features

- **Maximum Contrast**: All text/background combinations exceed WCAG AAA standards
- **Bright Colors**: No subtle grays or low-contrast elements
- **Clear Borders**: All panels have bright, visible borders
- **Consistent Layout**: Predictable navigation and element placement
- **Keyboard Navigation**: Full keyboard support for all functions

## Development Notes

### Testing
- **Test Harness**: `tests/tui/test_harness.py` with multimodal AI testing
- **Screenshot Capture**: Real SVG-to-PNG conversion with Cairo
- **AI Validation**: Automated contrast and visibility checking

### Maintenance
- **Single Source**: Only `advanced_app.py` needs updates
- **No Theme System**: Colors are hardcoded for consistency
- **Direct CSS**: No variable substitution or complex theming

## Troubleshooting

### Common Issues

1. **TUI Not Starting**
   - Ensure all dependencies are installed: `pip install textual rich`
   - Check model configuration is valid

2. **Poor Visibility**
   - This should no longer occur with the extreme high contrast design
   - If issues persist, check terminal color support

3. **Keyboard Not Working**
   - Ensure terminal supports keyboard input
   - Try different terminal emulator if needed

### Performance

- **Optimized Rendering**: Efficient updates only when needed
- **Memory Management**: Proper cleanup of resources
- **Responsive Design**: Works well on various terminal sizes

## Migration from Old TUI

If you were using the old TUI system:

1. **No Code Changes**: The CLI automatically uses the new TUI
2. **Same Commands**: All `--tui` commands work identically
3. **Better Visibility**: Much improved contrast and readability
4. **Enhanced Features**: More robust with better error handling

The transition is seamless - just run your existing commands and enjoy the improved visibility!
