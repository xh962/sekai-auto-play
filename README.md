# sekai-autotest

这是一个通用的 Android UI 自动化 / 测试 框架示例（Python + ADB + OpenCV）。

目的：用于 UI 自动化测试、回归验证与可访问性验证。禁止用于任何规避检测、作弊或降低封禁风险的用途。

主要说明（快速开始）
1. 安装依赖：
   - 本地需要安装 adb（并设置到 PATH）。
   - Python 3.8+，然后：
     pip install -r requirements.txt

2. 准备模板：
   - 将目标设备的界面截图中感兴趣按钮或 UI 元素裁切为 PNG，放到 templates/sample_buttons/，命名为描述性文件名（如 start.png、confirm.png）。
   - templates/README.md 中有更详细说明。

3. 校准设备（建议先执行校准以自动获取分辨率）：
   python sekai_autotest.py --calibrate

4. Dry-run 验证（只检测，不发送触控）：
   python sekai_autotest.py --dry-run --scene sample_show

5. 运行测试流程（需 `--confirm-run` 明确授权发送触控事件）：
   python sekai_autotest.py --run --scene sample_show --confirm-run

重要：所有模板、动作序列与参数均可在 config/default_config.yaml 中配置。请先在 Dry-run 模式下验证识别与坐标，再执行发送触控操作。

日文の簡単な説明：
- テンプレート画像を templates/sample_buttons に配置してから、キャリブレーションと Dry-run を行ってください。
- 実際の操作は --confirm-run フラグが必要です。

---

项目结构（已上传文件）
- sekai_autotest.py  主入口脚本与示例场景
- lib/adb_helper.py   ADB 接口（截图、发送触控、录屏）
- lib/image_matcher.py  图像匹配（模板匹配与简单多尺度搜索）
- lib/gestures.py     手势生成（tap/long_press/swipe/track_path）
- config/default_config.yaml  默认配置示例
- requirements.txt    Python 依赖
- templates/README.md 模板制作说明
- templates/sample_buttons/placeholder.txt 占位说明文件
- LICENSE             MIT 许可证

使用与合规声明：
本工具仅用于测试/自动化/可访问性验证用途，禁止用于违反第三方服务条款或任何形式的作弊行为。作者（我）不会对用户将此代码用于违法或违规用途负责。
