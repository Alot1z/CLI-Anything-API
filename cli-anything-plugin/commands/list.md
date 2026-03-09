# cli-anything:list Command

List all available CLI-Anything tools (installed and generated).

## Usage

```bash
/cli-anything:list [--path <directory>] [--json]
```

## Options

- `--path <directory>` - Directory to search for generated CLIs (default: current directory)
- `--json` - Output in JSON format for machine parsing

## What This Command Does

Displays all CLI-Anything tools available in the system:

### 1. Installed CLIs

Uses `importlib.metadata` to find installed `cli-anything-*` packages:
- Pattern: package name starts with `cli-anything-`
- Extracts: software name, version, entry point

```python
from importlib.metadata import distributions

installed = {}
for dist in distributions():
    name = dist.metadata.get("Name", "")
    if name.startswith("cli-anything-"):
        software = name.replace("cli-anything-", "")
        version = dist.version
        # Find executable via entry points or shutil.which
        executable = shutil.which(f"cli-anything-{software}")
        installed[software] = {
            "status": "installed",
            "version": version,
            "executable": executable
        }
```

### 2. Generated CLIs

Uses `glob` to find local CLI directories:
- Pattern: `**/agent-harness/cli_anything/*/__init__.py`
- Extracts: software name, source path
- Status: `generated`

```python
from pathlib import Path
import glob

search_path = args.get("path", ".")
generated = {}

pattern = str(Path(search_path) / "**" / "agent-harness" / "cli_anything" / "*" / "__init__.py")
for init_file in glob.glob(pattern, recursive=True):
    parts = Path(init_file).parts
    # Find cli_anything/<software> pattern
    for i, p in enumerate(parts):
        if p == "cli_anything" and i + 1 < len(parts):
            software = parts[i + 1]
            # Get agent-harness directory as source
            agent_harness_idx = parts.index("agent-harness") if "agent-harness" in parts else i - 1
            source = str(Path(*parts[:agent_harness_idx + 2]))  # up to agent-harness
            generated[software] = {
                "status": "generated",
                "version": None,
                "executable": None,
                "source": source
            }
            break
```

### 3. Merge Results

- Deduplicate by software name
- If both installed and generated: show `installed` status with both paths
- The `source` field shows where the generated code is (even for installed)

## Output Formats

### Table Format (default)

```
CLI-Anything Tools (found 5)

Name            Status      Version   Source
──────────────────────────────────────────────────────────────
gimp            installed   1.0.0     ./gimp/agent-harness
blender         installed   1.0.0     ./blender/agent-harness
inkscape        generated   -         ./inkscape/agent-harness
audacity        generated   -         ./audacity/agent-harness
libreoffice     generated   -         ./libreoffice/agent-harness
```

### JSON Format (--json)

```json
{
  "tools": [
    {
      "name": "gimp",
      "status": "installed",
      "version": "1.0.0",
      "executable": "/usr/local/bin/cli-anything-gimp",
      "source": "./gimp/agent-harness"
    },
    {
      "name": "inkscape",
      "status": "generated",
      "version": null,
      "executable": null,
      "source": "./inkscape/agent-harness"
    }
  ],
  "total": 2,
  "installed": 1,
  "generated_only": 1
}
```

## Error Handling

| Scenario | Action |
|----------|--------|
| No CLIs found | Show "No CLI-Anything tools found" message |
| Invalid --path | Show error: "Path not found: <path>" |
| Permission denied | Skip directory, continue scanning, show warning |

## Implementation Steps

When this command is invoked, the agent should:

1. **Parse arguments**
   - Extract `--path` value (default: `.`)
   - Extract `--json` flag (default: false)

2. **Validate path exists**
   - If `--path` specified and doesn't exist, show error and exit

3. **Scan installed CLIs**
   - Use `importlib.metadata.distributions()` to find all packages
   - Filter for packages starting with `cli-anything-`
   - Extract name, version, find executable path

4. **Scan generated CLIs**
   - Use `glob.glob(pattern, recursive=True)` with depth limit
   - Parse directory structure to extract software name
   - Calculate relative path from current directory

5. **Merge results**
   - Create dict keyed by software name
   - Prefer installed data when both exist
   - Keep source path from generated if available

6. **Format output**
   - If `--json`: output JSON to stdout
   - Otherwise: format as table with proper alignment

7. **Print results**
   - Show summary line with count
   - Show table or JSON

## Examples

```bash
# List all tools in current directory
/cli-anything:list

# List tools with JSON output
/cli-anything:list --json

# Search a specific directory
/cli-anything:list --path /projects/my-tools

# Combined
/cli-anything:list --path ./output --json
```

## Notes

- Search depth is limited by glob pattern structure (about 5 levels)
- Relative paths are preferred for readability
- The command should work without any external dependencies beyond Python stdlib
