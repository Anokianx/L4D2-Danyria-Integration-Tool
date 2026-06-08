# =============================================================================
# 模块说明：外置透明 HUD 程序，读取 L4D2 遥测并绘制速度表与敌人血量窗口。
# Module overview: External transparent HUD that reads L4D2 telemetry and paints speedometer and enemy-health windows.
# =============================================================================

from __future__ import annotations

import os
import sys
import time
import locale
import math
import json
import queue
import threading
from pathlib import Path

try:
    from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
    from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPainterPath, QLinearGradient, QConicalGradient
    from PySide6.QtWidgets import QApplication, QWidget
except Exception:
    from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
    from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QPainterPath, QLinearGradient, QConicalGradient
    from PyQt6.QtWidgets import QApplication, QWidget

# ---------------------------------------------------------------------------
# HUD 常量、颜色和默认参数。
# HUD constants, colors, and default settings.
# ---------------------------------------------------------------------------
APP_NAME = "Danyria HUD"
TELEMETRY = "danyria_hud_telemetry.txt"
CONFIG_FILE = "danyria_hud_config.json"


def hud_config_path() -> Path:
    raw = os.environ.get("DANYRIA_HUD_CONFIG", "").strip()
    if raw:
        try:
            return Path(raw).expanduser()
        except Exception:
            pass
    return Path(__file__).with_name(CONFIG_FILE)
POLL_INTERVAL = 0.01

COL = {
    "text": QColor("#F7FBFF"),
    "muted": QColor("#AFC1E8"),
    "accent": QColor("#7ED0FF"),
    "accent2": QColor("#F0A6FF"),
    "danger": QColor("#FF7BAE"),
    "warn": QColor("#FFD07A"),
    "good": QColor("#8FF2DA"),
    "ghost": QColor(80, 95, 130, 120),
    "shadow": QColor(0, 0, 0, 100),
}

DEFAULT_CONFIG = {
    "language": "auto",
    "speed": {"enabled": False, "x": 80, "y": 90, "w": 320, "h": 230, "opacity": 0.92, "max_speed": 420},
    "enemy": {"enabled": False, "x": 80, "y": 320, "w": 460, "h": 424, "opacity": 0.92, "max_enemies": 6, "max_distance": 1800},
    "penalty": {"enabled": False, "x": 500, "y": 90, "w": 390, "h": 330, "opacity": 0.92},
}

# ---------------------------------------------------------------------------
# HUD 配置读写与遥测解析。
# HUD configuration I/O and telemetry parsing.
# ---------------------------------------------------------------------------
def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    p = hud_config_path()
    try:
        if p.exists():
            loaded = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(loaded.get("language"), str):
                cfg["language"] = loaded.get("language")
            for section in ("speed", "enemy", "penalty"):
                if isinstance(loaded.get(section), dict):
                    cfg.setdefault(section, {}).update(loaded[section])
    except Exception:
        pass
    return cfg

def save_config(cfg):
    try:
        cfg.setdefault("language", "auto")
        p = hud_config_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass



def load_i18n_pack():
    candidates = []
    here = Path(__file__).resolve()
    try:
        candidates.append(here.parents[2] / "assets" / "i18n.json")
    except Exception:
        pass
    candidates.append(here.with_name("i18n.json"))
    for p in candidates:
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {
        "en": {
            "hud_speed_title": "DANYRIA SPEEDOMETER", "hud_peak": "PEAK", "hud_units_per_sec": "UNITS / SEC",
            "hud_enemy_title": "DANYRIA HEALTH", "hud_waiting_telemetry": "WAITING TELEMETRY", "hud_no_tracked_enemies": "NO TRACKED ENEMIES", "hud_enemy_fallback": "ENEMY",
            "hud_penalty_title": "DANYRIA SCORE SYSTEM", "hud_level_good": "GOOD", "hud_level_warn": "WARN", "hud_level_danger": "DANGER",
            "hud_grade_ex_desc": "Exceptional", "hud_grade_s_desc": "Superior", "hud_grade_a_desc": "Excellent", "hud_grade_b_desc": "Stable", "hud_grade_c_desc": "Passing", "hud_grade_d_desc": "Needs work",
            "hud_incap": "INCAP", "hud_dead": "DEAD", "hud_save": "SAVE", "hud_avg": "AVG", "hud_ledge": "LEDGE",
            "hud_heal": "HEAL", "hud_pills": "PILL", "hud_adrenaline": "ADR", "hud_items": "SUPPLY", "hud_common": "CI", "hud_special": "SI", "hud_witch": "WITCH", "hud_tank": "TANK", "hud_damage_taken": "DMG-", "hud_damage_done": "DMG OUT", "hud_rescued_by_team": "SAVED BY", "hud_healed_by_team": "HEALED BY",
            "hud_heal": "HEAL", "hud_pills": "PILL", "hud_adrenaline": "ADR", "hud_kill": "KILL", "hud_common": "CI", "hud_special": "SI",
            "hud_witch": "WITCH", "hud_tank": "TANK", "hud_damage_taken": "DMG", "hud_items": "ITEM",
            "hud_team_line": "TEAM {alive} alive / {incap} incap / {dead} dead",
            "hud_waiting": "Waiting for telemetry", "hud_no_incident": "No incident",
        }
    }


I18N = load_i18n_pack()


def detect_system_language():
    candidates = []
    try:
        candidates.append(locale.getlocale()[0])
    except Exception:
        pass
    try:
        candidates.append(locale.getdefaultlocale()[0])
    except Exception:
        pass
    for env_name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(env_name)
        if value:
            candidates.append(value)
    for value in candidates:
        if not value:
            continue
        code = str(value).split(".", 1)[0].replace("-", "_").lower()
        if code.startswith("zh"):
            return "zh" if "zh" in I18N else "en"
        short = code.split("_", 1)[0]
        if short in I18N:
            return short
    return "en"


def active_language(cfg):
    lang = str(cfg.get("language", "auto") or "auto")
    if lang == "auto":
        lang = detect_system_language()
    return lang if lang in I18N else "en"


def tr(lang, key, **kwargs):
    text = I18N.get(lang, {}).get(key, I18N.get("en", {}).get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def parse_telemetry(text: str):
    marker = "DHUD2|"
    idx = text.rfind(marker)
    if idx < 0:
        return None
    raw = text[idx + len(marker):].strip().splitlines()[0]
    data = {}
    for part in raw.split("|"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        data[k.strip()] = v.strip()

    enemies = []
    for item in data.get("enemies", "").split(";"):
        if not item:
            continue
        bits = item.split(",")
        if len(bits) < 4:
            continue
        try:
            enemies.append({
                "name": bits[0],
                "hp": int(float(bits[1])),
                "max": max(1, int(float(bits[2]))),
                "dist": int(float(bits[3])),
            })
        except Exception:
            pass
    data["enemy_list"] = enemies
    return data

def candidate_l4d2_dirs():
    dirs = []
    if len(sys.argv) >= 2:
        p = Path(sys.argv[1]).expanduser()
        dirs.append(p if p.is_dir() else p.parent)

    for base in [os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles")]:
        if base:
            dirs.append(Path(base) / "Steam" / "steamapps" / "common" / "Left 4 Dead 2" / "left4dead2")
    for drive in ["C:", "D:", "E:", "F:", "G:", "H:"]:
        dirs.append(Path(drive + r"\SteamLibrary\steamapps\common\Left 4 Dead 2\left4dead2"))
        dirs.append(Path(drive + r"\Steam\steamapps\common\Left 4 Dead 2\left4dead2"))
    dirs.append(Path.cwd())
    dirs.append(Path.cwd().parent)

    seen, out = set(), []
    for d in dirs:
        key = str(d).lower()
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out

def candidate_telemetry_files():
    files = []
    for d in candidate_l4d2_dirs():
        files.append(d / "ems" / TELEMETRY)
        files.append(d / TELEMETRY)
        if d.name.lower() == "ems":
            files.append(d / TELEMETRY)
    seen, out = set(), []
    for f in files:
        key = str(f).lower()
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def candidate_console_files():
    return []


def candidate_files():
    return candidate_telemetry_files()


def read_tail(path: Path, limit: int = 32768) -> str:
    try:
        size = path.stat().st_size
        with path.open("rb") as f:
            if size > limit:
                f.seek(max(0, size - limit))
            data = f.read()
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def queue_put_latest(q, item):
    try:
        while True:
            q.get_nowait()
    except queue.Empty:
        pass
    try:
        q.put_nowait(item)
    except Exception:
        pass


def newest_existing(files, now=None, max_age=None, start_wall=None):
    best = None
    best_mtime = -1.0
    now = time.time() if now is None else now
    for f in files:
        try:
            if not f.exists():
                continue
            st = f.stat()
            if st.st_size <= 0:
                continue
            if start_wall is not None and st.st_mtime < start_wall - 1.0:
                continue
            if max_age is not None and now - st.st_mtime > max_age:
                continue
            if st.st_mtime > best_mtime:
                best_mtime = st.st_mtime
                best = f
        except Exception:
            continue
    return best


def newest_console_packet(files, now=None, max_age=None):
    now = time.time() if now is None else now
    candidates = []
    for f in files:
        try:
            if not f.exists():
                continue
            st = f.stat()
            if st.st_size <= 0:
                continue
            if max_age is not None and now - st.st_mtime > max_age:
                continue
            candidates.append((st.st_mtime, f, st))
        except Exception:
            continue
    candidates.sort(reverse=True, key=lambda x: x[0])
    for _, f, st in candidates:
        text = read_tail(f)
        data = parse_telemetry(text) if text else None
        if data:
            return f, data, (st.st_mtime_ns, st.st_size)
    return None, None, None


def telemetry_worker(data_queue, status_queue, stop_event):
    direct_files = candidate_telemetry_files()
    console_files = []
    current = None
    current_is_console = False
    last_sig = None
    last_status = ""
    last_data_time = 0.0
    last_rescan = 0.0
    last_console_try = 0.0
    while not stop_event.is_set():
        now = time.time()

        if now - last_rescan > 0.35:
            last_rescan = now
            direct_files = candidate_telemetry_files()
            console_files = []

            direct = newest_existing(direct_files, now=now, max_age=1.2)
            if direct is not None and direct != current:
                current = direct
                current_is_console = False
                last_sig = None

        if current is None or not current.exists():
            msg = f"Waiting for ems/{TELEMETRY}"
            if msg != last_status:
                status_queue.put(msg)
                last_status = msg
            time.sleep(0.08)
            continue

        try:
            st = current.stat()
            sig = (st.st_mtime_ns, st.st_size)
            if sig != last_sig:
                last_sig = sig
                if current_is_console:
                    text = read_tail(current)
                else:
                    text = current.read_text(encoding="utf-8", errors="replace")
                data = parse_telemetry(text) if text else None
                if data:
                    queue_put_latest(data_queue, data)
                    last_data_time = now
                    msg = f"Telemetry: {current}"
                    if msg != last_status:
                        status_queue.put(msg)
                        last_status = msg
            elif not current_is_console and now - st.st_mtime > 1.2:
                current = None
                last_sig = None
            elif current_is_console and now - st.st_mtime > 2.0:
                current = None
                last_sig = None
        except Exception as exc:
            msg = f"Read failed: {exc}"
            if msg != last_status:
                status_queue.put(msg)
                last_status = msg
            current = None
            last_sig = None

        time.sleep(0.012 if not current_is_console else 0.06)


# ---------------------------------------------------------------------------
# 透明可拖动 HUD 窗口基类。
# Base class for transparent draggable HUD windows.
# ---------------------------------------------------------------------------
class HudWindow(QWidget):
    def __init__(self, app_ref, section, title, x, y, w, h, opacity):
        super().__init__()
        self.app_ref = app_ref
        self.section = section
        self.title = title
        self.drag_pos = None
        self.resize_mode = None
        self.press_global = None
        self.start_geometry = None
        self.resize_margin = 10
        self.min_w = 190
        self.min_h = 130
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setWindowOpacity(float(opacity))
        self.setGeometry(int(x), int(y), int(w), int(h))
        self.show()

    def _global_pos(self, e):
        return e.globalPosition().toPoint() if hasattr(e, "globalPosition") else e.globalPos()

    def hit_test_resize(self, pos):
        x = pos.x() if hasattr(pos, "x") else 0
        y = pos.y() if hasattr(pos, "y") else 0
        m = self.resize_margin
        edges = []
        if x <= m:
            edges.append("l")
        elif x >= self.width() - m:
            edges.append("r")
        if y <= m:
            edges.append("t")
        elif y >= self.height() - m:
            edges.append("b")
        return "".join(edges)

    def update_cursor_for_pos(self, pos):
        mode = self.hit_test_resize(pos)
        if mode in ("lt", "rb"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif mode in ("rt", "lb"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif mode in ("l", "r"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif mode in ("t", "b"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, e):
        pos = e.position().toPoint() if hasattr(e, "position") else e.pos()
        self.resize_mode = self.hit_test_resize(pos)
        self.press_global = self._global_pos(e)
        self.start_geometry = self.geometry()
        if self.resize_mode:
            self.drag_pos = None
        else:
            self.drag_pos = self.press_global - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, e):
        pos = e.position().toPoint() if hasattr(e, "position") else e.pos()
        gp = self._global_pos(e)
        if self.resize_mode and self.start_geometry is not None and self.press_global is not None:
            dx = gp.x() - self.press_global.x()
            dy = gp.y() - self.press_global.y()
            g = self.start_geometry
            left, top, right, bottom = g.left(), g.top(), g.right(), g.bottom()
            if "l" in self.resize_mode:
                left = min(right - self.min_w, left + dx)
            if "r" in self.resize_mode:
                right = max(left + self.min_w, right + dx)
            if "t" in self.resize_mode:
                top = min(bottom - self.min_h, top + dy)
            if "b" in self.resize_mode:
                bottom = max(top + self.min_h, bottom + dy)
            self.setGeometry(left, top, right - left + 1, bottom - top + 1)
            return
        if self.drag_pos is not None:
            self.move(gp - self.drag_pos)
            return
        self.update_cursor_for_pos(pos)

    def mouseReleaseEvent(self, e):
        self.drag_pos = None
        self.resize_mode = None
        self.press_global = None
        self.start_geometry = None
        self.app_ref.remember_geometry(self.section, self.x(), self.y(), self.width(), self.height())
        pos = e.position().toPoint() if hasattr(e, "position") else e.pos()
        self.update_cursor_for_pos(pos)

    def mouseDoubleClickEvent(self, e):
        pass

# ---------------------------------------------------------------------------
# HUD 绘制工具。
# HUD drawing helpers.
# ---------------------------------------------------------------------------
def logical_paint_setup(p, widget, logical_w: float, logical_h: float):
    sx = max(0.1, widget.width() / float(logical_w))
    sy = max(0.1, widget.height() / float(logical_h))
    p.scale(sx, sy)


def draw_hud_frame(p, rect: QRectF, accent=None):
    accent = QColor(accent or COL["accent"])
    soft = QColor(accent); soft.setAlpha(78)
    bright = QColor(accent); bright.setAlpha(150)
    path = QPainterPath()
    path.addRoundedRect(rect, 14, 14)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(soft, 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawPath(path)

    p.setPen(QPen(bright, 1.15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    c = 18
    p.drawLine(QPointF(rect.left()+10, rect.top()+6), QPointF(rect.left()+c, rect.top()+6))
    p.drawLine(QPointF(rect.left()+6, rect.top()+10), QPointF(rect.left()+6, rect.top()+c))
    p.drawLine(QPointF(rect.right()-10, rect.bottom()-6), QPointF(rect.right()-c, rect.bottom()-6))
    p.drawLine(QPointF(rect.right()-6, rect.bottom()-10), QPointF(rect.right()-6, rect.bottom()-c))


def draw_text_shadow(p, rect: QRectF, flags, text: str, color, font=None, shadow_alpha=150):
    if font is not None:
        p.setFont(font)
    p.setPen(QColor(0, 0, 0, shadow_alpha))
    p.drawText(rect.adjusted(1.4, 1.4, 1.4, 1.4), flags, text)
    p.setPen(color)
    p.drawText(rect, flags, text)


def draw_chip(p, rect: QRectF, text: str, color):
    bg = QColor(color)
    bg.setAlpha(24)
    p.setPen(QPen(QColor(color), 0.9))
    p.setBrush(QBrush(bg))
    p.drawRoundedRect(rect, 9, 9)
    font = QFont("Segoe UI Semibold")
    font.setPixelSize(9)
    draw_text_shadow(p, rect, Qt.AlignmentFlag.AlignCenter, text, color, font, 120)


def draw_bar(p, rect: QRectF, ratio: float, color):
    ratio = max(0.0, min(1.0, ratio))
    p.setPen(QPen(QColor(255, 255, 255, 56), 0.9))
    p.setBrush(QBrush(QColor(255, 255, 255, 22)))
    p.drawRoundedRect(rect, 5, 5)
    if ratio <= 0:
        return
    fill = QRectF(rect.left(), rect.top(), max(5.0, rect.width() * ratio), rect.height())
    p.setPen(Qt.PenStyle.NoPen)
    fill_color = QColor(color)
    fill_color.setAlpha(215)
    p.setBrush(QBrush(fill_color))
    p.drawRoundedRect(fill, 5, 5)


# ---------------------------------------------------------------------------
# 速度表绘制窗口。
# Speedometer drawing window.
# ---------------------------------------------------------------------------
class SpeedWindow(HudWindow):
    LOGICAL_W = 320
    LOGICAL_H = 230

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        logical_paint_setup(p, self, self.LOGICAL_W, self.LOGICAL_H)
        w, h = self.LOGICAL_W, self.LOGICAL_H
        stale = time.time() - self.app_ref.last_seen > 1.8
        speed = self.app_ref.speed
        peak = self.app_ref.peak_speed
        avg = self.app_ref.average_speed
        max_speed = max(100, self.app_ref.max_speed)
        ratio = max(0.0, min(1.0, speed / float(max_speed)))

        draw_hud_frame(p, QRectF(5, 5, w - 10, h - 10), COL["accent"])

        title_font = QFont("Segoe UI Semibold")
        title_font.setPixelSize(12)
        draw_text_shadow(p, QRectF(22, 13, w - 44, 22), Qt.AlignmentFlag.AlignCenter,
        self.app_ref.t("hud_speed_title"), COL["accent"], title_font)

        cx, cy = w / 2.0, 146
        r = 78
        arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        start_angle = 210
        span_angle = -240

        p.setPen(QPen(QColor(255, 255, 255, 42), 9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(arc_rect, int(start_angle * 16), int(span_angle * 16))
        p.setPen(QPen(COL["accent"], 9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(arc_rect, int(start_angle * 16), int(span_angle * ratio * 16))

        for i in range(0, 13):
            t = i / 12.0
            deg = math.radians(start_angle + span_angle * t)
            outer = QPointF(cx + math.cos(deg) * (r + 1), cy - math.sin(deg) * (r + 1))
            inner = QPointF(cx + math.cos(deg) * (r - (15 if i % 3 == 0 else 8)), cy - math.sin(deg) * (r - (15 if i % 3 == 0 else 8)))
            tick_col = QColor(COL["accent2"] if i % 3 == 0 else COL["muted"])
            tick_col.setAlpha(150 if i % 3 == 0 else 90)
            p.setPen(QPen(tick_col, 1.8 if i % 3 == 0 else 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(inner, outer)

        deg = math.radians(start_angle + span_angle * ratio)
        needle_end = QPointF(cx + math.cos(deg) * (r - 22), cy - math.sin(deg) * (r - 22))
        p.setPen(QPen(QColor(0, 0, 0, 160), 4.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx, cy), needle_end)
        p.setPen(QPen(COL["accent2"], 2.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx, cy), needle_end)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(COL["accent"]))
        p.drawEllipse(QPointF(cx, cy), 5.8, 5.8)

        big = QFont("Bahnschrift SemiBold")
        big.setPixelSize(40)
        draw_text_shadow(p, QRectF(cx - 74, 88, 148, 48), Qt.AlignmentFlag.AlignCenter,
                        str(speed), COL["text"] if not stale else COL["muted"], big)
        draw_chip(p, QRectF(34, h - 36, 108, 22), f"{self.app_ref.t('hud_avg')} {avg}", COL["accent"])
        draw_chip(p, QRectF(w - 142, h - 36, 108, 22), f"{self.app_ref.t('hud_peak')} {peak}", COL["accent2"])

        if stale:
            wait_font = QFont("Segoe UI Semibold")
            wait_font.setPixelSize(9)
            draw_text_shadow(p, QRectF(24, h - 60, w - 48, 18), Qt.AlignmentFlag.AlignCenter,
                            self.app_ref.t("hud_waiting"), COL["muted"], wait_font)
        p.end()



# ---------------------------------------------------------------------------
# 敌人血量绘制窗口。
# Enemy-health drawing window.
# ---------------------------------------------------------------------------
class EnemyWindow(HudWindow):
    LOGICAL_W = 460

    def logical_h(self):
        return max(192, 60 + int(self.app_ref.max_enemies) * 58)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        logical_h = self.logical_h()
        logical_paint_setup(p, self, self.LOGICAL_W, logical_h)
        w, h = self.LOGICAL_W, logical_h
        stale = time.time() - self.app_ref.last_seen > 1.8

        draw_hud_frame(p, QRectF(5, 5, w - 10, h - 10), COL["accent2"])

        title_font = QFont("Segoe UI Semibold")
        title_font.setPixelSize(12)
        title = self.app_ref.t("hud_enemy_title") if not stale else self.app_ref.t("hud_waiting_telemetry")
        draw_text_shadow(p, QRectF(22, 14, w - 44, 24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         title, COL["accent2"], title_font)

        y = 52
        enemies = self.app_ref.enemies[:self.app_ref.max_enemies]
        if stale and not enemies:
            font = QFont("Segoe UI Semibold")
            font.setPixelSize(12)
            draw_text_shadow(p, QRectF(24, y, w - 48, 70), Qt.TextFlag.TextWordWrap, self.app_ref.t("hud_waiting"), COL["muted"], font)
            p.end()
            return

        if not enemies:
            draw_chip(p, QRectF(24, y, w - 48, 30), self.app_ref.t("hud_no_tracked_enemies"), COL["muted"])
            p.end()
            return

        font_name = QFont("Segoe UI Semibold")
        font_name.setPixelSize(12)
        font_hp = QFont("Bahnschrift SemiBold")
        font_hp.setPixelSize(17)
        font_dist = QFont("Bahnschrift SemiBold")
        font_dist.setPixelSize(17)
        font_pct = QFont("Bahnschrift SemiBold")
        font_pct.setPixelSize(13)

        for e in enemies:
            if y > h - 52:
                break
            name = str(e.get("name", self.app_ref.t("hud_enemy_fallback"))).upper()
            hp = int(e.get("hp", 0))
            maxhp = max(1, int(e.get("max", hp if hp > 0 else 1)))
            dist = int(e.get("dist", 0))
            ratio = max(0.0, min(1.0, hp / float(maxhp)))
            color = COL["danger"] if ratio < 0.35 else COL["warn"] if ratio < 0.65 else COL["good"]

            draw_text_shadow(p, QRectF(28, y - 2, 185, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             name[:24], COL["text"], font_name)
            hp_text = f"{hp}/{maxhp}"
            draw_text_shadow(p, QRectF(196, y - 5, 112, 26), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             hp_text, color, font_hp)
            dist_m = max(0.0, dist * 0.0254)
            draw_text_shadow(p, QRectF(324, y - 5, 106, 26), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"{dist_m:.1f} M", COL["accent"], font_dist, 175)

            y += 25
            bar = QRectF(28, y, w - 56, 15)
            draw_bar(p, bar, ratio, color)
            pct = f"{int(round(ratio * 100))}%"
            draw_text_shadow(p, bar.adjusted(0, -1, 0, 1), Qt.AlignmentFlag.AlignCenter,
                             pct, COL["text"], font_pct, 185)
            y += 33

        p.end()



def score_grade(score: float):
    score = max(0.0, min(100.0, float(score)))
    if score >= 95:
        return "EX", "ex", QColor("#BDEBFF")
    if score >= 81:
        return "S", "s", QColor("#FF6B7C")
    if score >= 71:
        return "A", "a", QColor("#C8A0FF")
    if score >= 60:
        return "B", "b", QColor("#78C8FF")
    if score >= 50:
        return "C", "c", QColor("#8FF2DA")
    return "D", "d", QColor("#FFFFFF")

def draw_score_arc(p, rect: QRectF, ratio: float, grade_key: str, color):
    p.setPen(QPen(QColor(255, 255, 255, 38), 7.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawArc(rect, 90 * 16, -360 * 16)
    span_total = int(-360 * max(0.0, min(1.0, ratio)) * 16)
    if grade_key == "ex":
        stops = [
            (0.00, QColor("#B8F7FF")),
            (0.16, QColor("#7ED0FF")),
            (0.32, QColor("#A8A7FF")),
            (0.50, QColor("#F3A8FF")),
            (0.66, QColor("#FFD7EE")),
            (0.82, QColor("#FFF0A8")),
            (1.00, QColor("#B8F7FF")),
        ]

        def lerp_color(t: float) -> QColor:
            t = max(0.0, min(1.0, t))
            left_pos, left_col = stops[0]
            right_pos, right_col = stops[-1]
            for i in range(len(stops) - 1):
                if stops[i][0] <= t <= stops[i + 1][0]:
                    left_pos, left_col = stops[i]
                    right_pos, right_col = stops[i + 1]
                    break
            span = max(0.0001, right_pos - left_pos)
            k = (t - left_pos) / span
            return QColor(
                int(left_col.red() + (right_col.red() - left_col.red()) * k),
                int(left_col.green() + (right_col.green() - left_col.green()) * k),
                int(left_col.blue() + (right_col.blue() - left_col.blue()) * k),
                235,
            )

        ratio_clamped = max(0.0, min(1.0, ratio))
        slices = max(1, int(144 * ratio_clamped))
        for i in range(slices):
            t0 = i / 144.0
            t1 = min(ratio_clamped, (i + 1) / 144.0)
            if t1 <= t0:
                continue
            start = int((90 - 360 * t0) * 16)
            span = int(-360 * (t1 - t0) * 16) - 1
            p.setPen(QPen(lerp_color(t0), 7.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(rect, start, span)
    else:
        p.setPen(QPen(color, 7.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(rect, 90 * 16, span_total)


def iridescent_gradient(rect: QRectF):
    grad = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
    grad.setColorAt(0.00, QColor("#B8F7FF"))
    grad.setColorAt(0.20, QColor("#7ED0FF"))
    grad.setColorAt(0.38, QColor("#A8A7FF"))
    grad.setColorAt(0.56, QColor("#F3A8FF"))
    grad.setColorAt(0.74, QColor("#FFD7EE"))
    grad.setColorAt(0.90, QColor("#FFF0A8"))
    grad.setColorAt(1.00, QColor("#B8F7FF"))
    return grad

def draw_iridescent_text_shadow(p, rect: QRectF, align, text: str, font: QFont, shadow_alpha=150):
    text = str(text)
    p.save()
    p.setFont(font)
    fm = p.fontMetrics()
    tw = fm.horizontalAdvance(text)
    th = fm.height()
    x = rect.left()
    try:
        align_val = int(align.value)
    except Exception:
        try:
            align_val = int(align)
        except Exception:
            align_val = 0
    try:
        hcenter_val = int(Qt.AlignmentFlag.AlignHCenter.value)
    except Exception:
        hcenter_val = int(Qt.AlignmentFlag.AlignHCenter)
    try:
        right_val = int(Qt.AlignmentFlag.AlignRight.value)
    except Exception:
        right_val = int(Qt.AlignmentFlag.AlignRight)
    if align_val & hcenter_val:
        x = rect.left() + (rect.width() - tw) / 2.0
    elif align_val & right_val:
        x = rect.right() - tw
    y = rect.top() + (rect.height() - th) / 2.0 + fm.ascent()
    path = QPainterPath()
    path.addText(QPointF(x, y), font, text)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(0, 0, 0, max(0, min(255, int(shadow_alpha)))))
    for dx, dy in ((1.2, 1.2), (0.0, 1.4)):
        p.save()
        p.translate(dx, dy)
        p.drawPath(path)
        p.restore()
    p.setBrush(QBrush(iridescent_gradient(rect)))
    p.drawPath(path)
    p.restore()

# ---------------------------------------------------------------------------
# 惩罚机制绘制窗口。
# Penalty drawing window.
# ---------------------------------------------------------------------------
class PenaltyWindow(HudWindow):
    LOGICAL_W = 390
    LOGICAL_H = 330

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        logical_paint_setup(p, self, self.LOGICAL_W, self.LOGICAL_H)
        w, h = self.LOGICAL_W, self.LOGICAL_H
        stale = time.time() - self.app_ref.last_seen > 1.8
        draw_hud_frame(p, QRectF(5, 5, w - 10, h - 10), COL["warn"])

        score = max(0.0, min(100.0, float(self.app_ref.penalty_score)))
        ratio = score / 100.0
        level_text, level_key, color = score_grade(score)

        title_font = QFont("Segoe UI Semibold")
        title_font.setPixelSize(12)
        draw_text_shadow(p, QRectF(22, 15, w - 44, 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         self.app_ref.t("hud_penalty_title"), COL["warn"], title_font)

        cx, cy, r = 74, 88, 42
        draw_score_arc(p, QRectF(cx - r, cy - r, r * 2, r * 2), ratio, level_key, color)
        big = QFont("Bahnschrift SemiBold")
        big.setPixelSize(28)
        score_rect = QRectF(cx - r, cy - 18, r * 2, 36)
        if level_key == "ex":
            draw_iridescent_text_shadow(p, score_rect, Qt.AlignmentFlag.AlignCenter, f"{score:.1f}", big, 170)
        else:
            draw_text_shadow(p, score_rect, Qt.AlignmentFlag.AlignCenter, f"{score:.1f}", color, big)
        letter_font = QFont("Impact")
        letter_font.setPixelSize(32)
        letter_font.setBold(True)
        letter_rect = QRectF(cx + r + 8, cy - 24, 48, 48)
        if level_key == "ex":
            draw_iridescent_text_shadow(p, letter_rect, Qt.AlignmentFlag.AlignCenter, level_text.upper(), letter_font, 170)
        else:
            draw_text_shadow(p, letter_rect, Qt.AlignmentFlag.AlignCenter, level_text.upper(), color, letter_font, 170)

        penalty_col = COL["warn"]
        gain_col = COL["accent2"]
        x = 184
        draw_chip(p, QRectF(x, 46, 80, 22), f"{self.app_ref.t('hud_heal')} {self.app_ref.score_heals}", gain_col)
        draw_chip(p, QRectF(x + 88, 46, 86, 22), f"{self.app_ref.t('hud_damage_taken')} {self.app_ref.score_damage_taken}", penalty_col)
        draw_chip(p, QRectF(x, 74, 80, 22), f"{self.app_ref.t('hud_incap')} {self.app_ref.penalty_incaps}", penalty_col)
        draw_chip(p, QRectF(x + 88, 74, 86, 22), f"{self.app_ref.t('hud_dead')} {self.app_ref.penalty_deaths}", penalty_col)
        draw_chip(p, QRectF(x, 102, 80, 22), f"{self.app_ref.t('hud_ledge')} {self.app_ref.score_ledge}", penalty_col)
        draw_chip(p, QRectF(x + 88, 102, 86, 22), f"{self.app_ref.t('hud_items')} {self.app_ref.score_supplies}", penalty_col)

        y2 = 142
        draw_chip(p, QRectF(22, y2, 82, 22), f"{self.app_ref.t('hud_common')} {self.app_ref.score_common}", gain_col)
        draw_chip(p, QRectF(112, y2, 82, 22), f"{self.app_ref.t('hud_special')} {self.app_ref.score_special}", gain_col)
        draw_chip(p, QRectF(202, y2, 76, 22), f"{self.app_ref.t('hud_witch')} {self.app_ref.score_witch}", gain_col)
        draw_chip(p, QRectF(286, y2, 76, 22), f"{self.app_ref.t('hud_tank')} {self.app_ref.score_tank}", gain_col)

        y3 = 172
        draw_chip(p, QRectF(22, y3, 82, 22), f"{self.app_ref.t('hud_save')} {self.app_ref.penalty_revives}", gain_col)
        draw_chip(p, QRectF(112, y3, 82, 22), f"{self.app_ref.t('hud_pills')} {self.app_ref.score_pills}", penalty_col)
        draw_chip(p, QRectF(202, y3, 110, 22), f"{self.app_ref.t('hud_adrenaline')} {self.app_ref.score_adrenaline}", penalty_col)

        dmg_y = 205
        dmg_total = max(0, int(self.app_ref.score_damage_done))
        p.setPen(QPen(COL["accent2"], 1.0))
        dmg_bg = QColor(COL["accent2"])
        dmg_bg.setAlpha(22)
        p.setBrush(QBrush(dmg_bg))
        p.drawRoundedRect(QRectF(22, dmg_y, w - 44, 38), 12, 12)
        dmg_font = QFont("Segoe UI Semibold")
        dmg_font.setPixelSize(13)
        draw_text_shadow(p, QRectF(34, dmg_y + 7, 160, 24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         self.app_ref.t('hud_damage_done'), COL["text"], dmg_font, 120)
        dmg_num_font = QFont("Bahnschrift SemiBold")
        dmg_num_font.setPixelSize(24)
        draw_text_shadow(p, QRectF(178, dmg_y + 5, w - 212, 28), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         str(dmg_total), COL["accent2"], dmg_num_font, 150)

        team = self.app_ref.t("hud_team_line", alive=self.app_ref.team_alive, incap=self.app_ref.team_incap, dead=self.app_ref.team_dead, avg=self.app_ref.team_avg_hp)
        team_font = QFont("Segoe UI", 10)
        draw_text_shadow(p, QRectF(22, 253, w - 44, 20), Qt.AlignmentFlag.AlignLeft, team, COL["muted"], team_font, 125)

        last = self.app_ref.penalty_last or (self.app_ref.t("hud_waiting") if stale else self.app_ref.t("hud_no_incident"))
        dbg = self.app_ref.score_debug_score or self.app_ref.score_debug_event
        if dbg and (not last or last.lower() in {"round started", "no incident"}):
            last = "EVT " + dbg
        last_font = QFont("Segoe UI", 10)
        draw_text_shadow(p, QRectF(22, 276, w - 44, 42), Qt.TextFlag.TextWordWrap, last[:160], COL["text"] if not stale else COL["muted"], last_font, 125)
        p.end()

# ---------------------------------------------------------------------------
# HUD 应用控制器和后台遥测线程。
# HUD application controller and telemetry worker thread.
# ---------------------------------------------------------------------------
class HUDApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.cfg = load_config()
        self.lang = active_language(self.cfg)
        self.config_path = hud_config_path()
        self._last_cfg_check = 0.0
        self._last_cfg_sig = None
        self.data_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.speed = 0
        self.peak_speed = 0
        self.player = "-"
        self.player_hp = 0
        self.enemies = []
        self.penalty_score = 60.0
        self.penalty_level = "B"
        self.penalty_last = ""
        self.penalty_ff = 0
        self.penalty_incaps = 0
        self.penalty_deaths = 0
        self.penalty_revives = 0
        self.score_heals = 0
        self.score_defibs = 0
        self.score_pills = 0
        self.score_adrenaline = 0
        self.score_supplies = 0
        self.score_common = 0
        self.score_special = 0
        self.score_witch = 0
        self.score_tank = 0
        self.score_damage_taken = 0
        self.score_damage_done = 0
        self.score_damage_progress = 0
        self.score_damage_step = 200
        self.score_rescued_by_team = 0
        self.score_healed_by_team = 0
        self.score_ledge = 0
        self.team_alive = 0
        self.team_incap = 0
        self.team_dead = 0
        self.team_avg_hp = 0
        self.score_events_seen = 0
        self.score_event_reg = 0
        self.score_debug_event = ""
        self.score_debug_score = ""
        self._client_score_inited = False
        self._client_score_active = False
        self._client_score = 60.0
        self._client_last = "Round started"
        self._client_ff = 0
        self._client_incaps = 0
        self._client_deaths = 0
        self._client_revives = 0
        self._client_heals = 0
        self._client_supplies = 0
        self._client_damage_taken = 0
        self._client_rescued = 0
        self._client_ledge = 0
        self._client_prev_hp = None
        self._client_prev_team_alive = None
        self._client_prev_team_incap = None
        self._client_prev_team_dead = None
        self._client_prev_team_avg_hp = None
        self._client_prev_enemy_sig = None
        self.status = f"Waiting for ems/{TELEMETRY}"
        self.last_seen = 0

        self.max_speed = 420
        self.max_enemies = 6
        self.max_distance = 1800
        self.display_speed = 0.0
        self.speed_samples = []
        self.average_speed = 0
        self.speed_window = None
        self.enemy_window = None
        self.penalty_window = None
        self.apply_runtime_config(initial=True)

        self.worker = threading.Thread(target=telemetry_worker, args=(self.data_queue, self.status_queue, self.stop_event), daemon=True)
        self.worker.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

    def t(self, key, **kwargs):
        return tr(self.lang, key, **kwargs)

    def section_enabled(self, section):
        return bool(self.cfg.get(section, {}).get("enabled", False))

    def apply_runtime_config(self, initial=False):
        speed_cfg = self.cfg.get("speed", DEFAULT_CONFIG["speed"])
        enemy_cfg = self.cfg.get("enemy", DEFAULT_CONFIG["enemy"])
        penalty_cfg = self.cfg.get("penalty", DEFAULT_CONFIG["penalty"])
        self.max_speed = int(speed_cfg.get("max_speed", 420))
        self.max_enemies = int(enemy_cfg.get("max_enemies", 6))
        self.max_distance = int(enemy_cfg.get("max_distance", 1800))

        def safe_geometry(x, y, width, height):
            try:
                screen = QApplication.primaryScreen()
                if screen is None:
                    return int(x), int(y), int(width), int(height)
                area = screen.availableGeometry()
                width = max(180, min(int(width), max(180, area.width())))
                height = max(120, min(int(height), max(120, area.height())))
                x = int(x)
                y = int(y)
                if x > area.right() - 80 or x + width < area.left() + 80:
                    x = area.left() + 80
                if y > area.bottom() - 80 or y + height < area.top() + 80:
                    y = area.top() + 90
                x = max(area.left(), min(x, area.right() - width + 1))
                y = max(area.top(), min(y, area.bottom() - height + 1))
                return x, y, width, height
            except Exception:
                return int(x), int(y), int(width), int(height)

        def sync_window(attr, cls, section, title, width_fn, height_fn):
            cfg = self.cfg.get(section, DEFAULT_CONFIG[section])
            win = getattr(self, attr, None)
            if bool(cfg.get("enabled", False)):
                fallback_scale = float(cfg.get("scale", 1.0))
                width = int(cfg.get("w", int(width_fn() * fallback_scale)))
                height = int(cfg.get("h", int(height_fn() * fallback_scale)))
                x, y, width, height = safe_geometry(cfg.get("x", 80), cfg.get("y", 90), width, height)
                if win is None:
                    win = cls(self, section, title, x, y, width, height, cfg.get("opacity", 0.92))
                    setattr(self, attr, win)
                else:
                    win.setWindowOpacity(float(cfg.get("opacity", 0.92)))
                    win.setGeometry(x, y, width, height)
            else:
                if win is not None:
                    win.close()
                    setattr(self, attr, None)

        sync_window("speed_window", SpeedWindow, "speed", "Danyria Speedometer", lambda: 320, lambda: 230)
        sync_window("enemy_window", EnemyWindow, "enemy", "Danyria Health", lambda: 460, lambda: 76 + self.max_enemies * 58)
        sync_window("penalty_window", PenaltyWindow, "penalty", "Danyria Score System", lambda: 390, lambda: 330)

    def set_enabled(self, section, enabled):
        self.cfg.setdefault(section, {})["enabled"] = bool(enabled)
        save_config(self.cfg)
        self.apply_runtime_config()

    def refresh_language_from_config(self):
        now = time.time()
        if now - self._last_cfg_check < 0.6:
            return
        self._last_cfg_check = now
        try:
            if not self.config_path.exists():
                return
            sig = (self.config_path.stat().st_mtime_ns, self.config_path.stat().st_size)
            if sig == self._last_cfg_sig:
                return
            self._last_cfg_sig = sig
            cfg = load_config()
            self.cfg = cfg
            self.lang = active_language(cfg)
            self.apply_runtime_config()
        except Exception:
            pass

    def remember_geometry(self, section, x, y, w, h):
        self.cfg.setdefault(section, {})["x"] = int(x)
        self.cfg.setdefault(section, {})["y"] = int(y)
        self.cfg.setdefault(section, {})["w"] = int(w)
        self.cfg.setdefault(section, {})["h"] = int(h)
        save_config(self.cfg)

    def remember_position(self, section, x, y):
        win = getattr(self, section + "_window", None)
        if win is not None:
            self.remember_geometry(section, x, y, win.width(), win.height())
        else:
            self.cfg.setdefault(section, {})["x"] = int(x)
            self.cfg.setdefault(section, {})["y"] = int(y)
            save_config(self.cfg)

    def tick(self):
        self.refresh_language_from_config()
        latest_data = None
        try:
            while True:
                latest_data = self.data_queue.get_nowait()
        except queue.Empty:
            pass
        if latest_data is not None:
            self.apply_data(latest_data)
        try:
            while True:
                self.status = self.status_queue.get_nowait()
        except queue.Empty:
            pass
        if self.speed_window is not None:
            self.speed_window.update()
        if self.enemy_window is not None:
            self.enemy_window.update()
        if self.penalty_window is not None:
            self.penalty_window.update()

    def _score_total_from_script(self):
        total = (
            int(self.penalty_incaps) + int(self.penalty_deaths) +
            int(self.penalty_revives) + int(self.score_heals) + int(self.score_supplies) +
            int(self.score_common) + int(self.score_special) + int(self.score_witch) +
            int(self.score_tank) + int(self.score_damage_taken) +
            int(self.score_damage_done) + int(self.score_rescued_by_team) +
            int(self.score_healed_by_team) + int(self.score_ledge)
        )
        last = (self.penalty_last or "").strip().lower()
        if total > 0:
            return True
        if last and last not in {"round started", "waiting", "waiting for data"}:
            return True
        return False

    def _client_score_delta(self, delta, reason):
        try:
            d = float(delta)
        except Exception:
            d = 0.0
        self._client_score = max(0.0, min(100.0, float(self._client_score) + d))
        self._client_last = reason
        self._client_score_active = True

    def _client_score_remember(self, reason):
        self._client_last = reason
        self._client_score_active = True

    def _apply_client_score_fallback(self):
        if not self._client_score_inited:
            self._client_score_inited = True
            self._client_score = float(self.penalty_score) if self.penalty_score is not None else 60.0
            self._client_prev_hp = self.player_hp if self.player_hp > 0 else None
            self._client_prev_team_alive = self.team_alive
            self._client_prev_team_incap = self.team_incap
            self._client_prev_team_dead = self.team_dead
            self._client_prev_team_avg_hp = self.team_avg_hp
            self._client_prev_enemy_sig = tuple((e.get("name"), int(e.get("hp", 0)), int(e.get("dist", 0))) for e in self.enemies[:4])
            return

        script_working = self._score_total_from_script()
        if script_working:
            self._client_score_active = False
            self._client_score = float(self.penalty_score)
            self._client_prev_hp = self.player_hp if self.player_hp > 0 else self._client_prev_hp
            self._client_prev_team_alive = self.team_alive
            self._client_prev_team_incap = self.team_incap
            self._client_prev_team_dead = self.team_dead
            self._client_prev_team_avg_hp = self.team_avg_hp
            self._client_prev_enemy_sig = tuple((e.get("name"), int(e.get("hp", 0)), int(e.get("dist", 0))) for e in self.enemies[:4])
            return

        if self._client_prev_hp is not None and self.player_hp > 0:
            dhp = int(self.player_hp) - int(self._client_prev_hp)
            if dhp <= -2:
                self._client_damage_taken += -dhp
                pen = max(0.1, min(2.0, ((-dhp) / 10.0) * 0.25))
                self._client_score_delta(-pen, f"Damage taken {-dhp}")
            elif dhp >= 4:
                self._client_heals += dhp
                self._client_score_remember(f"Healing +{dhp} HP")

        sig = tuple((e.get("name"), int(e.get("hp", 0)), int(e.get("dist", 0))) for e in self.enemies[:4])
        if self._client_prev_enemy_sig is not None and len(sig) < len(self._client_prev_enemy_sig) and len(self._client_prev_enemy_sig) > 0:
            self._client_score_remember("Enemy list changed")
        self._client_prev_enemy_sig = sig

        self.penalty_score = max(0.0, min(100.0, float(self._client_score)))
        self.penalty_last = self._client_last
        self.score_heals = max(int(self.score_heals), int(self._client_heals))
        self.score_damage_taken = max(int(self.score_damage_taken), int(self._client_damage_taken))

        self._client_prev_hp = self.player_hp if self.player_hp > 0 else self._client_prev_hp
        self._client_prev_team_alive = self.team_alive
        self._client_prev_team_incap = self.team_incap
        self._client_prev_team_dead = self.team_dead
        self._client_prev_team_avg_hp = self.team_avg_hp

    def _apply_client_score_fallback_disabled_old(self):
        if not self._client_score_inited:
            self._client_score_inited = True
            self._client_prev_hp = self.player_hp if self.player_hp > 0 else None
            self._client_prev_team_alive = self.team_alive
            self._client_prev_team_incap = self.team_incap
            self._client_prev_team_dead = self.team_dead
            self._client_prev_team_avg_hp = self.team_avg_hp
            self._client_prev_enemy_sig = tuple((e.get("name"), int(e.get("hp", 0)), int(e.get("dist", 0))) for e in self.enemies[:4])
            return

        script_working = self._score_total_from_script()
        if script_working:
            self._client_score_active = False
            self._client_prev_hp = self.player_hp if self.player_hp > 0 else self._client_prev_hp
            self._client_prev_team_alive = self.team_alive
            self._client_prev_team_incap = self.team_incap
            self._client_prev_team_dead = self.team_dead
            self._client_prev_team_avg_hp = self.team_avg_hp
            self._client_prev_enemy_sig = tuple((e.get("name"), int(e.get("hp", 0)), int(e.get("dist", 0))) for e in self.enemies[:4])
            return

        if not script_working or self._client_score_active:
            if self._client_prev_team_incap is not None:
                d = int(self.team_incap) - int(self._client_prev_team_incap)
                if d > 0:
                    self._client_score_remember("Team incapacitated")
                elif d < 0:
                    self._client_score_remember("Team revived")
            if self._client_prev_team_dead is not None:
                d = int(self.team_dead) - int(self._client_prev_team_dead)
                if d > 0:
                    self._client_score_remember("Team death")
            if self._client_prev_team_avg_hp is not None and self.team_avg_hp > 0:
                d = int(self.team_avg_hp) - int(self._client_prev_team_avg_hp)
                members = max(1, int(self.team_alive) + int(self.team_incap))
                if d <= -5:
                    self._client_score_remember(f"Team HP changed {d * members}")
                elif d >= 8:
                    self._client_score_remember(f"Team healed +{d * members}")

            if self._client_prev_hp is not None and self.player_hp > 0:
                dhp = int(self.player_hp) - int(self._client_prev_hp)
                if dhp <= -4:
                    self._client_damage_taken += -dhp
                    pen = max(1, min(6, (-dhp) // 20))
                    self._client_score_delta(-pen, f"Damage taken {-dhp}")
                elif dhp >= 8:
                    self._client_heals += 1
                    self._client_score_remember(f"Healing +{dhp} HP")

            sig = tuple((e.get("name"), int(e.get("hp", 0)), int(e.get("dist", 0))) for e in self.enemies[:4])
            if self._client_prev_enemy_sig is not None:
                if len(sig) < len(self._client_prev_enemy_sig) and len(self._client_prev_enemy_sig) > 0:
                    self._client_score_remember("Enemy list changed")
            self._client_prev_enemy_sig = sig

            self.penalty_score = self._client_score
            self.penalty_last = self._client_last
            self.penalty_incaps = max(self.penalty_incaps, self._client_incaps)
            self.penalty_deaths = max(self.penalty_deaths, self._client_deaths)
            self.penalty_revives = max(self.penalty_revives, self._client_revives)
            self.score_heals = max(self.score_heals, self._client_heals)
            self.score_supplies = max(self.score_supplies, self._client_supplies)
            self.score_damage_taken = max(self.score_damage_taken, self._client_damage_taken)
            self.score_rescued_by_team = max(self.score_rescued_by_team, self._client_rescued)
            self.score_ledge = max(self.score_ledge, self._client_ledge)

        self._client_prev_hp = self.player_hp if self.player_hp > 0 else self._client_prev_hp
        self._client_prev_team_alive = self.team_alive
        self._client_prev_team_incap = self.team_incap
        self._client_prev_team_dead = self.team_dead
        self._client_prev_team_avg_hp = self.team_avg_hp

    def apply_data(self, data):
        try:
            raw_speed = int(float(data.get("speed", 0)))
        except Exception:
            raw_speed = 0

        if self.last_seen <= 0:
            self.display_speed = float(raw_speed)
        else:
            if abs(raw_speed - self.display_speed) >= 65:
                self.display_speed = float(raw_speed)
            else:
                self.display_speed = self.display_speed * 0.06 + raw_speed * 0.94
        self.speed = int(round(self.display_speed))

        self.peak_speed = max(self.peak_speed, raw_speed)
        now = time.time()
        self.speed_samples.append((now, raw_speed))
        self.speed_samples = [(t, s) for (t, s) in self.speed_samples if now - t <= 4.0]
        if self.speed_samples:
            self.average_speed = int(round(sum(s for _, s in self.speed_samples) / len(self.speed_samples)))
        self.player = data.get("player", "-")
        try:
            self.player_hp = int(float(data.get("hp", 0)))
        except Exception:
            self.player_hp = 0

        filtered = []
        for e in data.get("enemy_list", []):
            try:
                hp = int(e.get("hp", 0))
                mx = int(e.get("max", 1))
                dist = int(e.get("dist", 999999))
                name = str(e.get("name", "")).strip()
            except Exception:
                continue
            if hp <= 0 or mx <= 0:
                continue
            if dist > self.max_distance:
                continue
            if not name or name == "-":
                continue
            filtered.append(e)

        filtered.sort(key=lambda x: int(x.get("dist", 999999)))
        self.enemies = filtered[:self.max_enemies]

        def as_int(name, default=0):
            try:
                return int(float(data.get(name, default)))
            except Exception:
                return default

        def as_float(name, default=0.0):
            try:
                return float(data.get(name, default))
            except Exception:
                return default

        self.penalty_score = max(0.0, min(100.0, as_float("penalty_score", self.penalty_score)))
        self.penalty_level = str(data.get("penalty_level", self.penalty_level)).strip() or self.penalty_level
        self.penalty_last = str(data.get("penalty_last", self.penalty_last)).replace("_", " ").strip()
        self.penalty_ff = as_int("penalty_ff", self.penalty_ff)
        self.penalty_incaps = as_int("penalty_incaps", self.penalty_incaps)
        self.penalty_deaths = as_int("penalty_deaths", self.penalty_deaths)
        self.penalty_revives = as_int("penalty_revives", self.penalty_revives)
        self.score_heals = as_int("score_heals", self.score_heals)
        self.score_defibs = as_int("score_defibs", self.score_defibs)
        self.score_pills = as_int("score_pills", self.score_pills)
        self.score_adrenaline = as_int("score_adrenaline", self.score_adrenaline)
        self.score_supplies = as_int("score_supplies", self.score_supplies)
        self.score_common = as_int("score_common", self.score_common)
        self.score_special = as_int("score_special", self.score_special)
        self.score_witch = as_int("score_witch", self.score_witch)
        self.score_tank = as_int("score_tank", self.score_tank)
        self.score_damage_taken = as_int("score_damage_taken", self.score_damage_taken)
        self.score_damage_done = as_int("score_damage_done", self.score_damage_done)
        self.score_damage_progress = as_int("score_damage_progress", self.score_damage_progress)
        self.score_damage_step = max(1, as_int("score_damage_step", self.score_damage_step))
        self.score_rescued_by_team = as_int("score_rescued_by_team", self.score_rescued_by_team)
        self.score_healed_by_team = as_int("score_healed_by_team", self.score_healed_by_team)
        self.score_ledge = as_int("score_ledge", self.score_ledge)
        self.team_alive = as_int("team_alive", self.team_alive)
        self.team_incap = as_int("team_incap", self.team_incap)
        self.team_dead = as_int("team_dead", self.team_dead)
        self.team_avg_hp = as_int("team_avg_hp", self.team_avg_hp)
        self.score_event_reg = as_int("score_event_reg", self.score_event_reg)
        self.score_events_seen = as_int("score_events_seen", self.score_events_seen)
        self.score_debug_event = str(data.get("score_debug_event", self.score_debug_event)).replace("_", " ").strip()
        self.score_debug_score = str(data.get("score_debug_score", self.score_debug_score)).replace("_", " ").strip()
        self._apply_client_score_fallback()
        self.last_seen = time.time()

    def close_all(self):
        self.stop_event.set()
        self.timer.stop()
        for win in (self.speed_window, self.enemy_window, self.penalty_window):
            if win is not None:
                win.close()
        self.app.quit()

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    sys.exit(HUDApp().run())
