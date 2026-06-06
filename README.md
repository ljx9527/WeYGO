# WeYGO

WeYGO project repository.

## NPC 自动决斗脚本

当前版本提供一个本地自动化任务：从可见的游戏主界面/NPC 流程中启动游戏内置的 NPC 自动决斗。

脚本只使用屏幕坐标和鼠标点击，不修改游戏文件、进程内存或网络请求。默认是 dry-run，只打印计划动作，不会移动鼠标。

### 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 试运行

```powershell
python -m src.weygo.main npc-auto-duel
```

### 窗口模式

```powershell
python -m src.weygo.gui
```

窗口里可以：

- 点击“手动选中游戏窗口”，然后在 3 秒内切到/点击游戏窗口。
- 点击“开始”运行 NPC 自动决斗。
- 点击“停止”请求任务在下一步前停止。
- 取消“实际点击执行”后，只做 dry-run。

### 实际执行

先把游戏窗口放到前台，并停在主界面或 NPC 对话流程附近，然后运行：

```powershell
python -m src.weygo.main npc-auto-duel --execute
```

执行模式必须能定位游戏区域。推荐复制 `config/local.example.json` 到 `config/local.json`，然后设置：

- `app.window_title`：模拟器或游戏窗口标题的一部分。
- 或 `app.viewport`：游戏画面在桌面上的 `x/y/width/height`。

急停方式：

- 将鼠标移动到屏幕角落，触发 PyAutoGUI failsafe。
- 按 `Ctrl+C` 停止命令行。
- 在仓库根目录创建 `STOP_WEYGO` 文件，脚本会在下一步前停止。

### 调整坐标

默认坐标来自 `temp/` 目录下 `627x1114` 的游戏截图，并以相对比例保存到 `config/default.json`。

如需本机微调，复制示例配置：

```powershell
Copy-Item config/local.example.json config/local.json
```

然后修改 `config/local.json`。该文件不会提交到 Git。
