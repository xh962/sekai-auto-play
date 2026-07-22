"""
lib/image_matcher.py
模板匹配工具，包含简单的多尺度搜索以及长条（track）区域的轮廓检测示例。
"""
import cv2
import numpy as np
import os


class ImageMatcher:
    def __init__(self, adb_helper, cfg):
        self.adb = adb_helper
        self.cfg = cfg
        self.templates_dir = cfg.get('templates_dir', 'templates/sample_buttons')

    def _load_template(self, name):
        path = os.path.join(self.templates_dir, name)
        if not os.path.exists(path):
            return None
        tpl = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        return tpl

    def find_template(self, name, threshold=0.8, max_scale=1.0, min_scale=0.5, scale_steps=10):
        """在当前屏幕中多尺度查找模板，返回 x,y,w,h,score 或 None"""
        screen_path = self.adb.save_screenshot('tmp_screen.png')
        screen = cv2.imdecode(np.fromfile(screen_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        tpl = self._load_template(name)
        if tpl is None or screen is None:
            return None
        th, tw = tpl.shape[:2]
        best = None
        for i in range(scale_steps + 1):
            scale = max_scale - (max_scale - min_scale) * (i / scale_steps)
            h = int(th * scale)
            w = int(tw * scale)
            if h < 10 or w < 10:
                continue
            resized_tpl = cv2.resize(tpl, (w, h))
            res = cv2.matchTemplate(screen, resized_tpl, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if best is None or max_val > best[0]:
                best = (max_val, max_loc, (w, h))
        if best and best[0] >= threshold:
            score, loc, (w, h) = best
            x, y = loc
            return (int(x), int(y), int(w), int(h), float(score))
        return None

    def find_track_path(self, color_lower=(0, 100, 100), color_upper=(10, 255, 255)):
        """示例：基于颜色阈值提取条状轨迹并返回骨架点序列。
        仅为示例，实际需要根据目标 UI 调整阈值或用模板分割。
        返回点列表 [(x,y), ...] 或 None
        """
        screen_path = self.adb.save_screenshot('tmp_screen.png')
        screen = cv2.imdecode(np.fromfile(screen_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if screen is None:
            return None
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(color_lower), np.array(color_upper))
        # 形态学开闭，去噪
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        # 选最大轮廓
        c = max(contours, key=cv2.contourArea)
        # 计算骨架/拟合曲线：这里简单用轮廓点抽样
        pts = c.squeeze().tolist()
        if len(pts) < 5:
            return None
        # 降采样为最多 64 个点
        step = max(1, len(pts) // 64)
        sampled = pts[::step]
        return [(int(p[0]), int(p[1])) for p in sampled]
