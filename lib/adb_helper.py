"""
lib/adb_helper.py
ADB 封装：截图、发送触控事件、获取设备信息
"""
import subprocess
import shlex
import os
import time


class AdbHelper:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def _cmd(self, cmd):
        print(f"[ADB CMD] {cmd}")
        if self.dry_run:
            return ""
        proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.decode('utf-8', errors='ignore')
        return out

    def get_device_info(self):
        out = self._cmd('adb shell wm size')
        # 示例输出: Physical size: 2400x1080
        size = None
        for line in out.splitlines():
            if 'Physical size' in line or 'PhysicalSize' in line:
                parts = line.strip().split()[-1]
                size = parts
                break
        if not size:
            # 有些设备返回不同格式，尝试另一命令
            out2 = self._cmd('adb shell getprop ro.product.model')
            model = out2.strip()
            return {'model': model}
        w, h = size.split('x')
        return {'resolution': (int(w), int(h))}

    def save_screenshot(self, local_path='screen.png'):
        tmp_remote = '/sdcard/__tmp_screen.png'
        self._cmd(f'adb shell screencap -p {tmp_remote}')
        if not self.dry_run:
            self._cmd(f'adb pull {tmp_remote} {shlex.quote(local_path)}')
            self._cmd(f'adb shell rm {tmp_remote}')
        else:
            open(local_path, 'wb').close()
        return local_path

    def tap(self, x, y):
        cmd = f'adb shell input tap {int(x)} {int(y)}'
        return self._cmd(cmd)

    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        # adb swipe 参数为毫秒
        cmd = f'adb shell input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {int(duration_ms)}'
        return self._cmd(cmd)

    def screenrecord(self, duration=10, local_path='record.mp4'):
        remote = '/sdcard/__tmp_record.mp4'
        self._cmd(f'adb shell screenrecord --time-limit {int(duration)} {remote}')
        if not self.dry_run:
            self._cmd(f'adb pull {remote} {shlex.quote(local_path)}')
            self._cmd(f'adb shell rm {remote}')
        return local_path
