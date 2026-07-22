templates/README

templates/sample_buttons 目录用于存放你自己的 UI 元素截图（PNG），示例：
- start.png   # 主界面的“开始”按钮截取图
- confirm.png # 确认对话框的“确定”按钮截取图

制作模板的建议：
1. 在设备上截取完整屏幕截图（adb shell screencap -p /sdcard/s.png; adb pull /sdcard/s.png .）。
2. 在电脑上打开该截图，裁切出按钮或 UI 元素，将其保存为 PNG。
3. 将 PNG 放到 templates/sample_buttons/ 下，确保文件名与 config 中一致。

注意：不同分辨率/主题下需要分别准备模板或使用更通用的裁切。
