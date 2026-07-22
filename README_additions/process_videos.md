自动处理 assets/ 目录内视频并生成候选模板（工作流程说明）

我已在仓库中准备了两个处理方式：一个 GitHub Actions workflow（.github/workflows/process_videos.yml）和一个本地运行脚本（tools/process_assets.sh）。

功能：
- workflow（手动触发）会在 GitHub runner 上为每个 assets/*.mp4 抽帧（默认 2 fps），对每帧运行 tools/auto_template_generator.py，生成候选模板与 debug 标注图，最终把 templates/auto_templates/ 提交回仓库。
- 如果你更愿意在本地运行（例如因为视频较大或想先调参），可以运行 tools/process_assets.sh（需安装 ffmpeg 与 Python 依赖）。

如何使用 GitHub Actions（在仓库里执行）：
1. 打开仓库页面：https://github.com/xh962/sekai-auto-play
2. 点击 Actions 标签页，选择 "Generate templates from videos" 工作流（或在左侧 workflow 列表里找到它）。
3. 点击 "Run workflow"（工作流触发器）并执行。Actions runner 会处理 assets/*.mp4 并在处理后把生成的模板提交到 templates/auto_templates/。

本地运行方法：
1. 在本地克隆仓库并进入目录：
   git clone https://github.com/xh962/sekai-auto-play.git
   cd sekai-auto-play
2. 确保安装了 ffmpeg 并在 PATH 中可用。
3. 运行脚本：
   bash tools/process_assets.sh
4. 结果将保存到 templates/auto_templates/，并在 debug 图片中（debug_detect.png）包含标注，便于人工挑选。

下一步建议：
- 运行 workflow 或本地脚本后，请检查 templates/auto_templates/，手动挑选并把有效模板重命名为语义名（如 start.png、confirm.png、note_red.png）并移动到 templates/sample_buttons/，然后用 dry-run 验证：
  python sekai_autotest.py --dry-run --scene sample_show
