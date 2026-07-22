#!/usr/bin/env python3
"""
auto_template_generator.py

从设备或本地截图中自动检测并裁切可能的按钮/按键模板，保存到 templates/auto_templates/。

用途：辅助制作模板以用于 UI 自动化测试。始终在 dry-run 下先核对识别结果。

用法示例：
  python tools/auto_template_generator.py --from-device --out-dir templates/auto_templates --debug
  python tools/auto_template_generator.py --image screenshots/s1.png --out-dir templates/auto_templates

注意：这是一个通用的图像处理辅助工具，不能保证在所有界面或主题下都能准确识别，请人工核对生成的模板。
"""
import argparse
import os
import cv2
import numpy as np
from lib.adb_helper import AdbHelper


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def detect_circular_buttons(img, dp=1.2, min_dist=50, param1=100, param2=30, min_radius=8, max_radius=200):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist,
                               param1=param1, param2=param2,
                               minRadius=min_radius, maxRadius=max_radius)
    out = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for c in circles[0, :]:
            x, y, r = int(c[0]), int(c[1]), int(c[2])
            out.append((x, y, r))
    return out


def detect_contour_buttons(img, min_area=400, approx_eps=0.02):
    # 基于边缘和轮廓的通用检测（矩形/多边形/卡片）
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        # 过滤过长或过窄项
        if w < 20 or h < 20:
            continue
        rects.append((x, y, w, h, area))
    # 合并重叠的 rect
    rects = sorted(rects, key=lambda r: r[4], reverse=True)
    merged = []
    for r in rects:
        x, y, w, h, a = r
        keep = True
        for i, m in enumerate(merged):
            mx, my, mw, mh = m
            # 如果相交较多则认为是同一目标，扩大已有框
            if (x < mx + mw and mx < x + w and y < my + mh and my < y + h):
                nx = min(x, mx)
                ny = min(y, my)
                nw = max(x + w, mx + mw) - nx
                nh = max(y + h, my + mh) - ny
                merged[i] = (nx, ny, nw, nh)
                keep = False
                break
        if keep:
            merged.append((x, y, w, h))
    return merged


def crop_and_save(img, box, out_dir, base_name, pad=8):
    x, y, w, h = box
    h_img, w_img = img.shape[:2]
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(w_img, x + w + pad)
    y2 = min(h_img, y + h + pad)
    crop = img[y1:y2, x1:x2]
    idx = len([name for name in os.listdir(out_dir) if name.startswith(base_name)])
    out_path = os.path.join(out_dir, f"{base_name}_{idx+1}.png")
    # 使用 imwrite 写入；Windows 下避免 cv2.imwrite 中文路径问题
    cv2.imencode('.png', crop)[1].tofile(out_path)
    return out_path


def generate_from_image(img_path, out_dir, debug=False):
    ensure_dir(out_dir)
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError('无法读取图片: ' + img_path)

    saved = []
    # 1) 圆形按钮检测（如节奏按键）
    circles = detect_circular_buttons(img)
    for i, (x, y, r) in enumerate(circles):
        box = (x - r, y - r, 2 * r, 2 * r)
        p = crop_and_save(img, box, out_dir, 'circle')
        saved.append(p)

    # 2) 轮廓/卡片检测（例如曲目卡片、确认按钮等）
    rects = detect_contour_buttons(img)
    for i, (x, y, w, h) in enumerate(rects):
        p = crop_and_save(img, (x, y, w, h), out_dir, 'rect')
        saved.append(p)

    # debug 可视化
    if debug:
        vis = img.copy()
        for (x, y, r) in circles:
            cv2.circle(vis, (x, y), r, (0, 255, 0), 2)
        for (x, y, w, h) in rects:
            cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 2)
        out_vis = os.path.join(out_dir, 'debug_detect.png')
        cv2.imencode('.png', vis)[1].tofile(out_vis)
        saved.append(out_vis)

    return saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-device', action='store_true', help='直接通过 adb 从已连接设备截屏并处理')
    parser.add_argument('--image', type=str, help='本地截图文件路径')
    parser.add_argument('--out-dir', type=str, default='templates/auto_templates', help='输出目录')
    parser.add_argument('--debug', action='store_true', help='输出带标注的 debug 图片')
    parser.add_argument('--min-area', type=int, default=400, help='轮廓最小面积过滤')
    args = parser.parse_args()

    ensure_dir(args.out_dir)

    if args.from_device:
        adb = AdbHelper(dry_run=False)
        tmp = os.path.join(args.out_dir, 'device_screenshot.png')
        adb.save_screenshot(tmp)
        saved = generate_from_image(tmp, args.out_dir, debug=args.debug)
    elif args.image:
        saved = generate_from_image(args.image, args.out_dir, debug=args.debug)
    else:
        print('请指定 --from-device 或 --image')
        return

    print('生成的模板与调试文件：')
    for s in saved:
        print(' -', s)


if __name__ == '__main__':
    main()
