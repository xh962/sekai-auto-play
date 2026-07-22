#!/usr/bin/env python3
"""
sekai_autotest.py - 主运行脚本（示例）

用法示例：
  python sekai_autotest.py --calibrate
  python sekai_autotest.py --dry-run --scene sample_show
  python sekai_autotest.py --run --scene sample_show --confirm-run

注意：运行任何会发送触控事件的命令前请先用 --dry-run 验证识别结果。
"""
import argparse
import time
import yaml
from lib.adb_helper import AdbHelper
from lib.image_matcher import ImageMatcher
from lib.gestures import Gestures

CONFIG_PATH = 'config/default_config.yaml'


def load_config(path=CONFIG_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def scene_sample_show(adb, matcher, gestures, cfg, dry_run=False):
    """示例场景：按顺序查找模板并触发点击（用于 UI 测试示例）
    模板文件放在 templates/sample_buttons/ 下，如 start.png, confirm.png
    """
    templates = cfg.get('scene_templates', {}).get('sample_show', ['start.png', 'confirm.png'])
    for t in templates:
        print(f"查找模板: {t}")
        res = matcher.find_template(t, threshold=cfg.get('match_threshold', 0.75))
        if res is None:
            print(f"未找到模板 {t}")
            return False
        x, y, w, h, score = res
        cx, cy = x + w // 2, y + h // 2
        print(f"匹配到 {t} 在({cx},{cy}) 置信度={score:.2f}")
        if dry_run:
            print("Dry-run 模式：不发送触控事件。")
        else:
            gestures.tap(cx, cy)
            time.sleep(cfg.get('post_tap_wait', 1.0))
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--calibrate', action='store_true', help='校准并保存设备分辨率')
    parser.add_argument('--dry-run', action='store_true', help='只进行识别，不发送触控')
    parser.add_argument('--run', action='store_true', help='执行场景（需要 --confirm-run）')
    parser.add_argument('--confirm-run', action='store_true', help='确认允许发送触控事件')
    parser.add_argument('--scene', type=str, default='sample_show')
    args = parser.parse_args()

    cfg = load_config()
    adb = AdbHelper(dry_run=args.dry_run)
    device_info = adb.get_device_info()
    print('设备信息：', device_info)

    if args.calibrate:
        print('开始校准...')
        adb.save_screenshot('calibrate_full.png')
        print('屏幕截图已保存为 calibrate_full.png，请根据 README 进行模板制作。')
        return

    matcher = ImageMatcher(adb, cfg)
    gestures = Gestures(adb, cfg)

    if args.dry_run:
        print('Dry-run 模式：不会发送触控。')

    if args.run and not args.confirm_run:
        print('要实际发送触控事件，请加上 --confirm-run')
        return

    if args.scene == 'sample_show':
        ok = scene_sample_show(adb, matcher, gestures, cfg, dry_run=args.dry_run)
        print('场景完成' if ok else '场景未全部完成')


if __name__ == '__main__':
    main()
