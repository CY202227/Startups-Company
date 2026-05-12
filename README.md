# Startups Board Game (Python) — Core Rule Engine

## Language / 语言

[中文](./README.zh.md) | English (default)

This project is a prototype implementation of the board game *Startups* in Python.
It follows a **core engine + replaceable UI** architecture, currently covering CLI and
single-player AI modes first, with future extension points for GUI, API, and stronger AI.

## Features

- Immutable state model (`dataclass(frozen=True)`)
- Unified action entry: `apply_action(state, player_id, action)`
- Two-phase turns: `TAKE`, then `PLAY`
- Hidden information handled in the engine layer
- Dynamic anti-monopoly token ownership
- Scoring with edge cases (ties, underpayment, penalty records)
- Single-player AI with two randomized strategies

## Quick Start

### 1) Prepare environment

```powershell
cd D:\Dev\Startups-Company
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install local package (optional)

```powershell
python -m pip install -U pip
pip install -e .
```

After installation, use the `startups` command directly.
If you prefer not to install the console script, run the module directly.

## Run Modes

### 2.1 CLI Multiplayer (local turns)

```powershell
startups --players 3 --seed 101
```

### 2.2 CLI Single Player (You + AI)

```powershell
startups --players 3 --seed 101 --single-player
```

- `--single-player`: P0 is human, P1+ are AI.
- AI randomly picks between `greedy` and `anti_pressure` each turn.
- AI uses visible information only: it knows its own hand and public states.

### 2.3 Run without installed CLI script

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python .\src\startups\main.py --players 3 --seed 101 --single-player
```

### 2.4 Visualization UI (GitHub Pages)

- A static page is available in `docs/`, including:
  - Basic multi-player interaction (starts from P0)
  - `3~7` players
  - Single-player with AI (P0 human, P1+ AI)
  - Turn stage, market status, anti-monopoly owner, and score display
- Local preview:

```powershell
cd D:\Dev\Startups-Company
python -m http.server 8080 --directory docs
```

- Open `http://localhost:8080` in your browser.
- GitHub Pages deployment:
  - Set Pages Source to `docs/`
  - Page URL: `https://<your-username>.github.io/<repo-name>/`

## CLI Commands

- `d` / `draw`: draw from deck
- `m <idx>`: take from market, e.g., `m 0`
- `p <idx>`: place in personal holdings, e.g., `p 1`
- `s <idx>`: place into market, e.g., `s 1`
- `state`: print current state
- `h`: help
- `q`: quit

## Project Structure

- `src/startups/domain.py`: domain entities (`GameState`, `PlayerState`, `CompanyState`, `MarketCard`)
- `src/startups/rules.py`: action/stage enums, game constants, card setup
- `src/startups/engine.py`: state machine and action reducer
- `src/startups/actions.py`: command parsing
- `src/startups/scoring.py`: scoring logic
- `src/startups/ai.py`: AI decision module
- `src/startups/cli.py`: CLI interactive layer
- `src/startups/main.py`: program entrypoint
- `docs/rules_ref_en.md`: rule mapping (default display)
- `docs/rules_ref.md`: rule mapping (Chinese)
- `tests/`: unit tests (phase, action, scoring, reproducibility)

## Current Limitations

- Underpayment at scoring is tracked using a replay-friendly negative penalty (`penalty`).
- Current implementation is a minimal one-round model; advanced AI and network multiplayer
  are not yet integrated.
- Rule details from the original game can be expanded further while preserving the same structure.

## Run Tests

```powershell
pytest
```

## License and notes

- This project is for learning/implementation purposes.
- No commercial assets are included.
- Rule text references and company names are in `docs/rules_ref_en.md` and
  `docs/rules_ref.md` (Chinese translation), plus the project plan.
# Startups Board Game (Python) — Core Rule Engine

## Language / 语言

[中文](./README.zh.md) | English

This project is a prototype implementation of the board game *Startups* in Python.
It follows a **core engine + replaceable UI** architecture, currently covering CLI and
single-player AI modes first, with future extension points for GUI, API, and stronger AI.

## 特性

- Immutable state model (`dataclass(frozen=True)`)
- Unified action entry: `apply_action(state, player_id, action)`
- Two-phase turns: `TAKE`, then `PLAY`
- Hidden information handled in the engine layer
- Dynamic anti-monopoly token ownership
- Scoring with edge cases (ties, underpayment, penalty records)
- Single-player AI with two randomized strategies

## 快速开始

### 1) Prepare environment

```powershell
cd D:\Dev\Startups-Company
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install local package (optional)

```powershell
python -m pip install -U pip
pip install -e .
```

After installation, use the `startups` command directly.  
If you prefer not to install the console script, run the module directly.

## Run Modes

### 2.1 CLI Multiplayer (local turns)

```powershell
startups --players 3 --seed 101
```

### 2.2 CLI Single Player (You + AI)

```powershell
startups --players 3 --seed 101 --single-player
```

- `--single-player`: P0 is human, P1+ are AI.
- AI randomly picks between `greedy` and `anti_pressure` each turn.
- AI uses visible information only: it knows its own hand and public states.

### 2.3 Run without installed CLI script

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python .\src\startups\main.py --players 3 --seed 101 --single-player
```

### 2.4 Visualization UI (GitHub Pages)

 - A static page is available in `docs/`, including:
  - Basic multi-player interaction (starts from P0)
  - `3~7` players
  - Single-player with AI (P0 human, P1+ AI)
  - Turn stage, market status, anti-monopoly owner, and score display
- 本地快速预览：
```powershell
cd D:\Dev\Startups-Company
python -m http.server 8080 --directory docs
```
- Open `http://localhost:8080` in your browser.
- GitHub Pages 发布建议：
  - 将仓库 Pages Source 设为 `docs/` 目录
  - 页面地址会变为仓库 `https://<你的用户名>.github.io/<仓库名>/`

## CLI Commands

- `d` / `draw`: draw from deck
- `m <idx>`: take from market, e.g., `m 0`
- `p <idx>`: place in personal holdings, e.g., `p 1`
- `s <idx>`: place into market, e.g., `s 1`
- `state`: print current state
- `h`: help
- `q`: quit

## Project Structure

- `src/startups/domain.py`: domain entities (`GameState`, `PlayerState`, `CompanyState`, `MarketCard`)
- `src/startups/rules.py`: action/stage enums, game constants, card setup
- `src/startups/engine.py`: state machine and action reducer
- `src/startups/actions.py`: command parsing
- `src/startups/scoring.py`: scoring logic
- `src/startups/ai.py`: AI decision module
- `src/startups/cli.py`: CLI interactive layer
- `src/startups/main.py`: program entrypoint
- `docs/rules_ref_en.md`: rule mapping (default display)
- `docs/rules_ref.md`: rule mapping (Chinese)
- `tests/`: unit tests (phase, action, scoring, reproducibility)

## Current Limitations

- Underpayment at scoring is tracked using a replay-friendly negative penalty (`penalty`).
- Current implementation is a minimal one-round model; advanced AI and network multiplayer are not yet integrated.
- Rule details from the original game can be expanded further while preserving the same structure.

## Run Tests

```powershell
pytest
```

## License and notes

- This project is for learning/implementation purposes.
- No commercial assets are included.
- Rule text references and company names are in `docs/rules_ref_en.md` and `docs/rules_ref.md` (Chinese translation), plus the project plan.
