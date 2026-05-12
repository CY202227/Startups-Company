# Startups 桌游 Python 实现（核心规则引擎）

## Language / 语言

中文 | [English](./README.md)

这是一个用 Python 实现的《初创公司》桌游原型。  
项目按“核心引擎 + 可替换展示层”结构开发，当前实现先覆盖 CLI 与单机 AI 对战，便于后续接入 GUI、API 或更高级 AI。

## 特性

- 不可变状态模型（`dataclass(frozen=True)`）
- 统一动作入口：`apply_action(state, player_id, action)`
- 两阶段回合流程（先拿牌，再打牌）
- 隐藏信息保留到引擎层
- 反垄断筹码动态归属
- 结算与边界分支（平局、欠付、负分记录）
- 支持单人局 AI（随机切换两种策略）

## 快速开始

### 1) 进入项目并建立运行环境

```powershell
cd D:\Dev\Startups-Company
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) 安装本地包（可选）

```powershell
python -m pip install -U pip
pip install -e .
```

安装后可直接使用 `startups` 命令；若不想装脚本，也可直接运行模块文件。

## 运行方式

### 2.1 CLI 单机（多玩家）

```powershell
startups --players 3 --seed 101
```

### 2.2 CLI 单人局（你 + AI）

```powershell
startups --players 3 --seed 101 --single-player
```

- `--single-player`：P0 为真人，其余玩家由 AI 控制
- AI 每一步会在 `greedy` 与 `anti_pressure` 两个策略里随机选择一种
- AI 决策是基于“可见信息”进行：它只看到自己的手牌，不直接看到他人手牌

### 2.3 不装脚本也能跑

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python .\src\startups\main.py --players 3 --seed 101 --single-player
```

### 2.4 可视化界面（GitHub Pages）

- 打开目录 `docs/` 下新增了一个静态页面，可直接通过 GitHub Pages 托管。
- 目前支持：
  - 多人基础交互（默认从 P0 开始）
  - `3~7` 人
  - 单人局 AI（P0 人类，P1+ AI）
  - 回合阶段提示、市场状态、反垄断持有者与结算结果
- 本地快速预览：

```powershell
cd D:\Dev\Startups-Company
python -m http.server 8080 --directory docs
```
- 在浏览器打开 `http://localhost:8080` 即可运行。
- GitHub Pages 发布建议：
  - 将仓库 Pages Source 设为 `docs/` 目录
  - 页面地址会变为仓库 `https://<你的用户名>.github.io/<仓库名>/`

## 命令说明（CLI）

- `d` / `draw`：从牌堆拿牌
- `m <idx>`：从市场拿牌，例如 `m 0`
- `p <idx>`：打到个人区域，例如 `p 1`
- `s <idx>`：打到市场，例如 `s 1`
- `state`：打印当前状态
- `h`：显示帮助
- `q`：退出

## 项目结构

- `src/startups/domain.py`：领域对象（`GameState`, `PlayerState`, `CompanyState`, `MarketCard`）
- `src/startups/rules.py`：动作/阶段枚举、游戏参数与牌组配置
- `src/startups/engine.py`：状态机与动作执行器
- `src/startups/actions.py`：命令解析
- `src/startups/scoring.py`：结算逻辑
- `src/startups/ai.py`：AI 决策（单人局）
- `src/startups/cli.py`：命令行交互层
- `src/startups/main.py`：程序入口
- `docs/rules_ref_en.md`：规则映射（英文，默认展示）
- `docs/rules_ref.md`：规则映射（中文）
- `tests/`：单元测试（阶段、动作、结算、复现性）

## 已知限制（当前版本）

- 结算时对不足支付采用了可重放友好的负分记账策略（`penalty`）以保持状态可计算
- 目前是单回合模型的最小玩法，尚未接入更高级 AI 与多人网络模式
- 牌面规则与官方边界仍可继续用官方规则补齐（已预留接口）

## 运行测试

```powershell
pytest
```

## 许可证与说明

- 本项目仅用于实现与学习用途，未内置商业内容/资源文件。
- 规则文本与牌名来源可见 `docs/rules_ref_en.md` 与 `docs/rules_ref.md`。  
`docs/rules_ref_en.md` 为默认显示版本，`docs/rules_ref.md` 为中文版本，均采用可执行规则映射，后续可用于回归校验。
