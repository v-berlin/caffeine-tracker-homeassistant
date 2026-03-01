# caffeine-tracker-homeassistant

A pure-YAML caffeine tracking system for **Home Assistant** (Docker, latest).  
No custom integration, no HACS, no external database – just three config files and a JSON log.

---

## Features

| Feature | Details |
|---|---|
| **Exponential decay** | `remaining = dose × 0.5^(elapsed_h / half_life_h)` |
| **Multiple doses** | Every dose is tracked individually and summed |
| **Presets** | Espresso 80 mg · Coffee 120 mg · Energy 200 mg · Cola 35 mg |
| **Custom dose** | Any mg value via `script.caffeine_add_custom` |
| **Daily goal** | Configurable 50–1000 mg, status sensor tracks it |
| **Peak tracking** | Highest level seen today stored persistently |
| **Time-to-zero** | Estimates hours until level drops below 1 mg |
| **Warnings** | Persistent notifications when goal or 400 mg is exceeded |
| **Midnight reset** | Log cleared automatically at 00:00 |
| **Minutely refresh** | Sensors recalculate every 60 seconds |
| **Full persistence** | Data survives HA restarts via `/config/caffeine_log.json` |
| **CSV export** | One-call export to `/config/caffeine_export.csv` |

---

## File Overview

```
/config/
├── packages/
│   ├── package_caffeine.yaml      ← helpers, sensors, shell commands
│   ├── scripts_caffeine.yaml      ← scripts (add dose, reset, export)
│   └── automations_caffeine.yaml  ← automations (minutely, midnight, alerts)
├── caffeine_log.json              ← runtime data (auto-created)
├── caffeine_halflife.txt          ← synced half-life value (auto-created)
└── caffeine_export.csv            ← CSV export (created on demand)
```

---

## Installation

### 1 – Enable packages in `configuration.yaml`

```yaml
homeassistant:
  packages: !include_dir_named packages
```

> If you already use a `packages/` directory, just drop the three files there.

### 2 – Create the packages directory

```bash
mkdir -p /config/packages
```

### 3 – Copy the three YAML files

```
/config/packages/package_caffeine.yaml
/config/packages/scripts_caffeine.yaml
/config/packages/automations_caffeine.yaml
```

### 4 – Restart Home Assistant

Go to **Settings → System → Restart** (or run `ha core restart`).

### 5 – Verify

After restart you should see these entities:

| Type | Entity ID |
|---|---|
| Sensor | `sensor.caffeine_current_level_mg` |
| Sensor | `sensor.caffeine_time_until_zero` |
| Sensor | `sensor.caffeine_remaining_to_goal` |
| Sensor | `sensor.caffeine_status` |
| Input Number | `input_number.caffeine_half_life_hours` |
| Input Number | `input_number.caffeine_daily_goal` |
| Input Number | `input_number.caffeine_peak_today` |
| Script | `script.caffeine_add_custom` |
| Script | `script.caffeine_add_preset` |
| Script | `script.caffeine_reset_day` |
| Script | `script.caffeine_export_csv` |

---

## Usage

### Add a dose via preset

Call the script from **Developer Tools → Services** or any automation/dashboard button:

```yaml
service: script.caffeine_add_preset
data:
  preset_name: espresso   # espresso | coffee | energy | cola
  quantity: 1             # optional multiplier, default 1
```

**Preset reference**

| `preset_name` | mg per unit |
|---|---|
| `espresso` | 80 mg |
| `coffee` | 120 mg |
| `energy` | 200 mg |
| `cola` | 35 mg |

### Add a custom dose

```yaml
service: script.caffeine_add_custom
data:
  amount: 95   # any mg value > 0
```

### Manual day reset

```yaml
service: script.caffeine_reset_day
```

### Export to CSV

```yaml
service: script.caffeine_export_csv
```

Output: `/config/caffeine_export.csv`

```
timestamp,amount
2026-03-01T08:00:00,80
2026-03-01T10:30:00,120
```

---

## Configuration

| Entity | Default | Range | Description |
|---|---|---|---|
| `input_number.caffeine_half_life_hours` | 5 h | 1–24 h | Caffeine half-life (population average ~5 h) |
| `input_number.caffeine_daily_goal` | 400 mg | 50–1000 mg | Daily intake target |

Changes take effect at the next minutely sensor refresh (≤ 60 s).

---

## Mathematics

### Exponential decay per dose

```
remaining_mg = dose_mg × 0.5 ^ (elapsed_hours / half_life_hours)
```

### Total current level

```
current = Σ  dose_i × 0.5 ^ (elapsed_i / half_life)
```

All doses in `/config/caffeine_log.json` contribute independently.  
The result is floored at 0 and rounded to one decimal place.

### Time until < 1 mg

Solving `current × 0.5^(t/hl) = 1`:

```
t = half_life × log₂(current)   [hours from now]
```

Returns 0 when the current level is already below 1 mg.

---

## Data Format

`/config/caffeine_log.json`

```json
[
  {"amount": 80,  "timestamp": "2026-03-01T08:00:00"},
  {"amount": 120, "timestamp": "2026-03-01T10:30:00"}
]
```

- **Created automatically** if it does not exist.
- **Reset to `[]`** if empty or unparseable (corrupt JSON).
- Written atomically (write to `.tmp`, then rename) to prevent data loss.

---

## Sensor Reference

| Sensor | Unit | Description |
|---|---|---|
| `caffeine_current_level_mg` | mg | Active caffeine in bloodstream right now |
| `caffeine_time_until_zero` | h | Hours until level drops below 1 mg |
| `caffeine_remaining_to_goal` | mg | `goal − current`, floor 0 |
| `caffeine_status` | — | `OK` / `Goal exceeded` / `High` |

### Status values

| Value | Condition |
|---|---|
| `OK` | Level ≤ daily goal and ≤ 400 mg |
| `Goal exceeded` | Level > daily goal (and ≤ 400 mg) |
| `High` | Level > 400 mg |

---

## Automations

| ID | Trigger | Action |
|---|---|---|
| `caffeine_minutely_update` | Every minute | Sync half-life file, refresh sensors, update peak |
| `caffeine_midnight_reset` | 00:00:00 daily | Call `script.caffeine_reset_day` |
| `caffeine_goal_exceeded_warning` | Level crosses daily goal | `persistent_notification` |
| `caffeine_high_level_warning` | Level crosses 400 mg | `persistent_notification` |

---

## Troubleshooting

**Sensors show `unavailable`**  
→ Check HA logs. Ensure Python 3 is available in the container: `python3 --version`.

**`caffeine_log.json` not created**  
→ Run `script.caffeine_add_custom` with a dose once; the file is created on first write.

**Half-life change not reflected immediately**  
→ Wait up to 60 seconds for the minutely automation to sync the file, or trigger `shell_command.caffeine_write_halflife` manually.

**`command_line` sensor not updating**  
→ Check `scan_interval` (set to 60 s). You can force an update via  
`service: homeassistant.update_entity` → `sensor.caffeine_current_level_mg`.

**JSON file corrupt after power loss**  
→ The next write operation detects an invalid file and resets it to `[]`.  
  You can also run `script.caffeine_reset_day` manually.

---

## Requirements

- Home Assistant **2022.9+** (numeric_state trigger with template `above:` value)
- **Python 3.8+** in the HA Docker container (always present in official images)
- No additional packages, HACS, or custom integrations required
