# TouchDesigner Analysis

**Dump any TouchDesigner network to JSON. Feed it to AI.**

One Python script, zero dependencies. Run it inside TouchDesigner, get a complete JSON snapshot of your entire project — every operator, parameter, connection, script, table, and CHOP channel. Then ask Claude, ChatGPT, or Gemini to analyze it for you.

> Built by [tomorrow.lab](https://github.com/tomorrow-lab-open) — open tools for creative technologists.

---

## Why?

TouchDesigner projects are opaque. You can't `grep` a `.toe` file. You can't ask AI to review your network. You can't diff two versions.

This tool fixes that. One command turns your entire TD project into readable JSON that any AI can understand.

**Use cases:**
- Ask AI to explain someone else's project
- Debug signal flow and find broken connections
- Document your network architecture
- Find unused operators or dead paths
- Onboard collaborators who don't know your project
- Compare two versions of a project

---

## Quick Start

### 1. Download

Download [`td_dump.py`](https://raw.githubusercontent.com/tomorrow-lab-open/touchdesigner-analysis/main/td_dump.py) and save it somewhere (e.g. your Desktop).

### 2. Open TouchDesigner

Open the `.toe` file you want to analyze.

### 3. Run the script

Open the **Textport** (press `Alt+T`), then paste this one line:

```python
exec(open('C:/Users/yourname/Desktop/td_dump.py').read())
```

> Replace the path with wherever you saved `td_dump.py`. Use **forward slashes** `/` even on Windows.

### 4. Get your JSON

The script will print:

```
=== TD Network Dumper ===
Project:    my-project
Operators:  251
Output:     C:/Users/yourname/Desktop/td-dump-my-project.json

Now feed the JSON to your AI:
  "Analyze this TouchDesigner network. What does it do?"
=========================
```

The JSON file is on your Desktop, named `td-dump-{project-name}.json`.

### 5. Ask AI

Upload the JSON to any AI chat and ask your question. See [AI Prompts](#ai-prompts) below for ready-to-use prompts.

---

## What Gets Dumped

| Family | What's captured |
|--------|----------------|
| **All operators** | Name, path, type, family |
| **Parameters** | All non-default values + expressions |
| **Connections** | Every input/output wire between operators |
| **DATs** | Full script text + table contents |
| **CHOPs** | Channel names + current values |
| **TOPs** | Resolution (width × height) |
| **SOPs** | Point and primitive counts |
| **COMPs** | Recursive children (full tree) |

**Skipped:** TouchDesigner internal UI (`/ui`, `/local`, `/sys`, `/perform`).

---

## Configuration

Edit the top of `td_dump.py` if needed:

```python
ROOT_PATH = '/project1'     # Change to dump a specific container
MAX_DEPTH = 15               # Limit recursion depth
OUTPUT_DIR = None            # None = Desktop, or set a custom path
SKIP_PATHS = ['/ui', '/local', '/sys', '/perform']
```

---

## JSON Structure

```json
{
  "tool": "touchdesigner-analysis",
  "version": "2.1",
  "td_version": "2023.11880",
  "file": "my-project",
  "timestamp": "2026-02-27 03:15:00",
  "operator_count": 251,
  "network": {
    "name": "project1",
    "path": "/project1",
    "type": "baseCOMP",
    "family": "COMP",
    "children": [
      {
        "name": "constant1",
        "path": "/project1/constant1",
        "type": "constantCHOP",
        "family": "CHOP",
        "params": {
          "name0": "frequency",
          "value0": 0.5
        },
        "channels": [
          { "name": "frequency", "val": 0.5 }
        ],
        "outputs": [
          { "index": 0, "to": "/project1/math1", "to_input": 0 }
        ]
      }
    ]
  }
}
```

---

## AI Prompts

Copy-paste these when you upload your JSON to an AI. Pick the one that fits your situation.

### General Analysis
```
Analyze this TouchDesigner network JSON. Explain:
1. What does this project do? (high-level purpose)
2. What is the signal flow? (data path from input to output)
3. What are the main sections/modules?
4. Are there any potential issues? (disconnected operators, unusual parameter values)
```

### Debug Help
```
I'm having issues with this TouchDesigner project. Here's the full network dump as JSON.

Look for:
- Disconnected or orphaned operators (no inputs AND no outputs)
- Broken signal chains (missing connections)
- Parameter expressions that reference non-existent paths
- Script errors or suspicious code in DAT text content
- CHOP channels with unexpected values (NaN, 0 when shouldn't be)
```

### Architecture Review
```
Review this TouchDesigner network architecture. Suggest improvements:
- Are there operators that could be consolidated?
- Is the signal flow clean or tangled?
- Are scripts well-organized or scattered?
- What would you refactor for better maintainability?
- Rate the overall organization from 1-10.
```

### Onboarding / Documentation
```
I need to understand this TouchDesigner project built by someone else.
Create documentation from this network dump:
1. Project overview (what it does)
2. Module breakdown (main sections and their purposes)
3. Signal flow diagram (describe as text: A → B → C)
4. Key parameters to tweak (what an operator would adjust)
5. External dependencies (OSC, MIDI, files, network connections)
```

### Performance Audit
```
Analyze this TouchDesigner network for performance:
- How many operators total? Is this a heavy project?
- Are there unnecessary cook-chains?
- TOP resolutions — anything unnecessarily high?
- SOP point counts — anything heavy?
- Are scripts running every frame that don't need to?
- Suggest specific optimizations.
```

### Compare Two Dumps
```
I have two JSON dumps of the same TouchDesigner project at different stages.
Compare them and tell me:
1. What operators were added/removed?
2. What parameters changed?
3. What connections changed?
4. Summarize the changes in plain language.

[Paste both JSONs]
```

---

## Tips

- **Large projects**: If the JSON is too big for your AI's context window, set `ROOT_PATH` to a specific container (e.g., `/project1/scene1`) to dump only that section.
- **Sensitive data**: The dump includes all DAT script text and table contents. Review before sharing if your project contains API keys or credentials.
- **Version tracking**: Run the dump before and after changes, then use the "Compare Two Dumps" prompt to see what changed.
- **Multiple roots**: Run the script multiple times with different `ROOT_PATH` values to dump specific sections separately.

---

## Requirements

- TouchDesigner 2022+ (any edition, including Non-Commercial)
- That's it. No pip install, no external libraries. It uses only TD's built-in Python.

---

## License

MIT — use it however you want.

---

*Made with care by [tomorrow.lab](https://github.com/tomorrow-lab-open) in Chiang Mai.*
