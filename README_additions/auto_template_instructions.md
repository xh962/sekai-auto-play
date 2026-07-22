## 自动生成模板（工具说明）

新增文件： tools/auto_template_generator.py

功能概述：
- 从设备截图或本地截图自动检测可能的按键/按钮区域（圆形按钮、矩形/卡片），并裁切保存到指定目录（默认 templates/auto_templates/）。
- 会同时生成一个 debug 标注图（debug_detect.png），便于人工核对检测结果。

如何使用：
1. 从设备截屏并自动生成：
   python tools/auto_template_generator.py --from-device --out-dir templates/auto_templates --debug

2. 使用本地图像：
   python tools/auto_template_generator.py --image screenshots/s1.png --out-dir templates/auto_templates --debug

3. 运行后请人工检查 templates/auto_templates/ 下的图片，删除误判或重命名为更语义化的文件名（如 start.png, note_red.png）。

注意与建议：
- 自动检测是基于常见的圆形检测（HoughCircles）与边缘轮廓检测实现的，对不同 UI 风格/亮度/动态效果的适应性有限，需要人工复核。对于节奏游戏的谱面按键（高频、动态）特别是实时移动轨迹，建议由人工从多张截图中提取代表性模板或结合轨迹分割工具处理。
- 请在仓库的 README 指示的 Dry-run 模式下先验证模板匹配结果，确认无误后再允许脚本发送触控事件。

合规提醒：本工具用于 UI 自动化测试与模板生成，请勿用于违反服务条款的用途。
