# WeYGO 游戏王自动任务脚本设计文档

## 1. 项目目标

WeYGO 是一个面向游戏王相关客户端的本地自动任务辅助脚本项目，用于把重复、低风险、可预期的日常操作抽象成可配置任务流程，例如启动检查、界面导航、领取奖励、活动入口巡检、基础资源统计和任务完成状态记录。

项目优先服务于个人本地使用、学习自动化工程和辅助无障碍操作。设计上不以竞技对战作弊、绕过反作弊、篡改客户端、破解通信协议、刷榜或破坏其他玩家体验为目标。

## 2. 设计原则

- 本地优先：脚本只在用户本机运行，不依赖私有服务保存账号信息。
- 可观察：每一步任务都有日志、截图或状态记录，失败时可以追踪原因。
- 可暂停：所有自动操作必须支持热键暂停、停止和人工接管。
- 可配置：任务流程、等待时间、识别阈值和快捷键通过配置文件调整。
- 低侵入：优先使用屏幕识别、窗口控制和模拟输入，不修改游戏文件或进程内存。
- 合规边界：不实现 PvP 自动决策、卡组代打、反检测绕过、协议模拟或批量账号操作。

## 3. 使用边界

### 推荐场景

- 日常任务入口导航。
- 奖励领取提醒和半自动领取。
- 资源数量截图归档。
- 活动页面巡检。
- 任务完成状态记录。
- 对固定 UI 的重复点击流程自动化。

### 不支持场景

- 自动进行排位、竞技、PvP 对局。
- 自动分析对手手牌、场面并代替玩家决策。
- 修改客户端文件、内存或网络请求。
- 绕过验证码、反作弊或登录保护。
- 多账号批量脚本。
- 以牟利、刷资源、刷排名为目的的无人值守运行。

## 4. 总体架构

```text
WeYGO
├─ Task Runner          任务调度与状态机
├─ Vision Layer         屏幕截图、模板匹配、OCR
├─ Input Controller     鼠标、键盘、窗口控制
├─ Task Definitions     可配置任务流程
├─ Safety Guard         暂停、超时、异常保护
├─ Logger               日志、截图、运行报告
└─ Config               用户配置、阈值、路径、热键
```

### 4.1 Task Runner

Task Runner 是核心执行器，负责加载任务定义、按步骤执行、处理失败重试、记录状态并响应暂停/停止信号。

任务执行模型建议采用有限状态机：

```text
idle -> prepare -> detect -> act -> verify -> complete
                         \-> retry -> failed
```

每个任务步骤包含：

- `name`：步骤名称。
- `detect`：判断当前 UI 是否符合预期。
- `action`：执行点击、按键或等待。
- `verify`：验证操作是否成功。
- `timeout`：最大等待时间。
- `retry`：失败重试次数。
- `fallback`：失败后的人工提示或截图保存。

### 4.2 Vision Layer

视觉层负责把游戏画面转成可判断的结构化信号。

优先级建议：

1. 窗口截图。
2. 模板匹配：按钮、图标、入口、状态标记。
3. OCR：任务文本、奖励数量、活动标题。
4. 颜色/区域判断：加载状态、弹窗遮罩、按钮可用状态。

模板资源应按游戏版本和分辨率组织：

```text
assets/templates/
├─ common/
├─ daily/
├─ rewards/
└─ events/
```

### 4.3 Input Controller

输入控制层负责执行用户级输入：

- 移动鼠标。
- 点击指定坐标或识别到的目标中心点。
- 发送快捷键。
- 激活游戏窗口。
- 等待 UI 稳定。

所有输入动作都应经过 Safety Guard 检查，确保脚本未暂停、目标窗口仍然存在、当前画面符合预期。

### 4.4 Task Definitions

任务定义建议采用 YAML 或 JSON。示例：

```yaml
tasks:
  daily_check:
    enabled: true
    steps:
      - name: open_daily_panel
        detect:
          template: home_daily_button.png
        action:
          click: detected_center
        verify:
          template: daily_panel_title.png
        timeout_ms: 5000
        retry: 2
```

### 4.5 Safety Guard

安全保护模块必须在第一版就实现：

- 全局暂停热键，例如 `F8`。
- 全局停止热键，例如 `F9`。
- 单步骤超时。
- 连续失败自动停止。
- 鼠标移动到屏幕角落触发急停。
- 非目标窗口激活时暂停。
- 关键操作前截图。

## 5. 任务流程示例

### 5.1 每日状态检查

```text
启动脚本
-> 查找游戏窗口
-> 激活窗口
-> 截图识别主页
-> 检查每日任务入口
-> 打开任务面板
-> 识别完成/未完成状态
-> 保存运行报告
-> 等待用户确认后领取
```

### 5.2 奖励领取辅助

```text
识别奖励按钮
-> 判断按钮是否可领取
-> 截图记录
-> 弹出确认提示
-> 用户确认
-> 点击领取
-> 验证奖励弹窗
-> 保存结果
```

## 6. 配置设计

建议配置文件路径：

```text
config/default.yaml
config/local.yaml
```

`default.yaml` 保存默认配置，`local.yaml` 保存本机私有配置并加入 `.gitignore`。

配置项示例：

```yaml
window:
  title_keyword: "Yu-Gi-Oh"
  resolution:
    width: 1280
    height: 720

safety:
  pause_hotkey: "F8"
  stop_hotkey: "F9"
  max_consecutive_failures: 3
  step_timeout_ms: 8000

vision:
  template_threshold: 0.86
  ocr_enabled: true

tasks:
  daily_check: true
  reward_assist: true
```

## 7. 日志与报告

每次运行生成一个独立目录：

```text
runs/2026-06-06_112700/
├─ run.log
├─ summary.json
└─ screenshots/
```

日志字段：

- 运行时间。
- 游戏窗口信息。
- 当前任务。
- 步骤名称。
- 识别结果。
- 点击位置。
- 重试次数。
- 失败原因。
- 截图路径。

## 8. 技术选型建议

第一阶段建议使用 Python：

- `pyautogui`：鼠标键盘输入与截图。
- `opencv-python`：模板匹配。
- `pillow`：图像处理。
- `pytesseract` 或其他 OCR：文本识别。
- `pydantic`：配置校验。
- `pyyaml`：配置文件。
- `loguru` 或标准 `logging`：日志。

后续如需要更好的界面体验，可以增加桌面控制台或 Web UI。

## 9. 目录结构规划

```text
WeYGO
├─ assets/
│  └─ templates/
├─ config/
│  ├─ default.yaml
│  └─ local.example.yaml
├─ docs/
│  └─ design.md
├─ src/
│  └─ weygo/
│     ├─ main.py
│     ├─ runner.py
│     ├─ vision.py
│     ├─ input_controller.py
│     ├─ safety.py
│     ├─ config.py
│     └─ logger.py
├─ tests/
├─ runs/
├─ README.md
└─ .gitignore
```

`runs/`、`config/local.yaml`、临时截图和缓存文件不应提交到 Git。

## 10. 风险与应对

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| UI 版本变化 | 模板匹配失败 | 模板按版本管理，失败时保存截图 |
| 分辨率差异 | 坐标不准 | 使用窗口相对坐标和目标中心点 |
| 加载慢 | 误点 | 增加等待 UI 稳定和 verify 步骤 |
| 弹窗干扰 | 流程中断 | 增加通用弹窗检测 |
| 误操作 | 影响账号体验 | 暂停热键、急停、关键步骤确认 |
| 违反平台规则 | 账号风险 | 限制功能边界，不做竞技代打和绕过检测 |

## 11. 里程碑

### M1：项目骨架

- 创建 Python 项目结构。
- 配置加载。
- 日志系统。
- 全局暂停/停止。
- 示例任务 dry-run。

### M2：基础识别

- 窗口截图。
- 模板匹配。
- 区域截图保存。
- 识别调试工具。

### M3：任务执行

- 任务状态机。
- 点击动作。
- verify 验证。
- 失败重试。
- 运行报告。

### M4：每日辅助任务

- 每日入口识别。
- 奖励状态识别。
- 半自动领取。
- 人工确认模式。

### M5：体验优化

- 简单 UI 或命令行菜单。
- 模板管理工具。
- 配置向导。
- 失败回放报告。

## 12. 后续待定问题

- 目标客户端是哪个游戏王版本或平台。
- 默认分辨率和窗口模式。
- 是否需要中文 OCR。
- 第一批要支持的具体任务清单。
- 是否只做提示和半自动，还是允许部分无人值守流程。
