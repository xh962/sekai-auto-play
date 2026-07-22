"""
lib/gestures.py
提供 tap/long_press/swipe/track_path 等接口，使用 adb input 命令发送事件。
长按沿曲线路径通过分段短 swipe 实现。
"""
import time


class Gestures:
    def __init__(self, adb_helper, cfg):
        self.adb = adb_helper
        self.cfg = cfg

    def tap(self, x, y):
        print(f"tap at {x},{y}")
        return self.adb.tap(x, y)

    def long_press(self, x, y, duration=1500):
        # 使用 swipe 起点终点相同，duration 毫秒以模拟按住
        print(f"long_press at {x},{y} duration={duration}ms")
        return self.adb.swipe(x, y, x, y, duration_ms=duration)

    def swipe(self, x1, y1, x2, y2, duration=300):
        print(f"swipe {x1},{y1} -> {x2},{y2} duration={duration}ms")
        return self.adb.swipe(x1, y1, x2, y2, duration_ms=duration)

    def track_path(self, points, total_time=1000):
        """沿一系列点发送分段 swipe 来模拟沿路径的持续触摸
        points: [(x,y), ...]
        total_time: 毫秒
        """
        if not points or len(points) < 2:
            return None
        n = len(points)
        per = max(1, total_time // (n - 1))
        for i in range(n - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            # 每段用短时间滑动表示持续触摸
            self.adb.swipe(x1, y1, x2, y2, duration_ms=per)
            time.sleep(per / 1000.0)
        return True
