# src/states/stats_state.py
import pygame
import os
import json
import csv
from datetime import datetime
from collections import defaultdict, OrderedDict
from typing import Any, Dict, List, Tuple

from src.state import BaseState

FONT_MAIN = None
FONT_SMALL = None
PADDING = 14
STATS_PATH = os.path.join('data', 'stats', 'stats.json')
EXPORT_PATH = os.path.join('data', 'stats', 'export_stats.csv')
METRIC_KEYS = [
    ('total_score', 'Суммарно score'),
    ('best_max_focus', 'Макс. фокус (s)'),
    ('max_time', 'Макс. время игры (s)'),
    ('avg_time', 'Сред. время игры (s)')
]

def _ensure_fonts():
    global FONT_MAIN, FONT_SMALL
    if FONT_MAIN is None:
        FONT_MAIN = pygame.font.SysFont('Arial', 20)
    if FONT_SMALL is None:
        FONT_SMALL = pygame.font.SysFont('Arial', 14)

def _parse_timestamp(ts_val: Any):
    if ts_val is None:
        return None
    if isinstance(ts_val, (int, float)):
        try:
            return datetime.utcfromtimestamp(int(ts_val))
        except Exception:
            return None
    if isinstance(ts_val, str):
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(ts_val, fmt)
            except Exception:
                continue
    return None

class StatsState(BaseState):
    def __init__(self, manager):
        super().__init__(manager)
        _ensure_fonts()
        self.raw_list: List[Dict[str, Any]] = []
        self.date_series: 'OrderedDict[str, Dict[str, Any]]' = OrderedDict()
        self.dates_list: List[str] = []
        self.selected_metric_index = 0
        self.offset = 0
        self.window_days = 10
        self.metric_rects: List[pygame.Rect] = []
        self.btn_back_rect = pygame.Rect(18, 18, 120, 36)
        self.btn_export_rect = pygame.Rect(156, 18, 160, 36)
        self.btn_prev_rect = pygame.Rect(332, 18, 36, 36)
        self.btn_next_rect = pygame.Rect(380, 18, 36, 36)
        self.load_stats()

    def enter(self, **kwargs):
        self.load_stats()

    def load_stats(self) -> None:
        try:
            with open(STATS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.raw_list = data
                elif isinstance(data, dict) and 'games' in data and isinstance(data['games'], list):
                    self.raw_list = data['games']
                else:
                    self.raw_list = []
        except FileNotFoundError:
            self.raw_list = []
        except Exception:
            self.raw_list = []
        self._aggregate_by_date()

    def _aggregate_by_date(self) -> None:
        by_date = defaultdict(list)
        for rec in self.raw_list:
            ts = rec.get('timestamp')
            dt = _parse_timestamp(ts)
            if dt is None:
                continue
            date_key = dt.strftime('%Y-%m-%d')
            by_date[date_key].append(rec)
        ordered = OrderedDict()
        for date_key in sorted(by_date.keys()):
            records = by_date[date_key]
            total_score = sum(int(r.get('score', 0)) for r in records)
            best_max_focus = max(float(r.get('max_focus', 0.0)) for r in records) if records else 0.0
            max_time = max(float(r.get('time', 0.0)) for r in records) if records else 0.0
            avg_time = (sum(float(r.get('time', 0.0)) for r in records) / len(records)) if records else 0.0
            errors_agg: Dict[str, int] = {}
            for r in records:
                errs = r.get('errors') or {}
                if isinstance(errs, dict):
                    for k, v in errs.items():
                        try:
                            errors_agg[k] = errors_agg.get(k, 0) + int(v)
                        except Exception:
                            pass
            ordered[date_key] = {
                'total_score': total_score,
                'best_max_focus': best_max_focus,
                'max_time': max_time,
                'avg_time': avg_time,
                'games_count': len(records),
                'errors': errors_agg
            }
        if not ordered:
            today = datetime.utcnow().strftime('%Y-%m-%d')
            ordered[today] = {
                'total_score': 0,
                'best_max_focus': 0.0,
                'max_time': 0.0,
                'avg_time': 0.0,
                'games_count': 0,
                'errors': {}
            }
        self.date_series = ordered
        self.dates_list = list(ordered.keys())
        max_off = max(0, len(self.dates_list) - self.window_days)
        if self.offset > max_off:
            self.offset = max_off

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.manager.pop()

            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if self.btn_back_rect.collidepoint((mx, my)):
                    self.manager.pop()
                    return

                if self.btn_export_rect.collidepoint((mx, my)):
                    ok = self.export_csv(EXPORT_PATH)
                    print('Export CSV:', EXPORT_PATH if ok else 'failed')
                    return

                if self.btn_prev_rect.collidepoint((mx, my)):
                    self.offset = max(0, self.offset - self.window_days)
                    return

                if self.btn_next_rect.collidepoint((mx, my)):
                    self.offset = min(max(0, len(self.dates_list) - self.window_days), self.offset + self.window_days)
                    return

                for i, rect in enumerate(self.metric_rects):
                    if rect.collidepoint((mx, my)):
                        self.selected_metric_index = i
                        return

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.manager.pop()

                elif e.key == pygame.K_LEFT:
                    self.offset = max(0, self.offset - 1)

                elif e.key == pygame.K_RIGHT:
                    self.offset = min(max(0, len(self.dates_list) - self.window_days), self.offset + 1)

    def update(self, dt: float):
        pass

    def render(self):
        screen = self.manager.screen
        width, height = screen.get_size()
        top_bar_h = 160
        left_margin = PADDING
        top_margin = top_bar_h + PADDING
        left_area_w = int(width * 0.55)
        right_area_w = width - left_area_w - PADDING * 3
        spacing_x = int(24 * (width / 1280))
        spacing_y = int(18 * (height / 720))
        metric_w = int((left_area_w - spacing_x) / 2) - PADDING
        metric_h = int((height * 0.22))
        right_x = left_margin + left_area_w + PADDING
        right_y = top_margin
        right_w = right_area_w
        right_h = metric_h * 2 + spacing_y
        screen.fill((18, 18, 20))
        _ensure_fonts()
        title = FONT_MAIN.render('Статистика — ингибиторный тренажёр', True, (240, 240, 240))
        screen.blit(title, (PADDING, PADDING + int((top_bar_h - 48) / 2)))
        self.btn_back_rect = pygame.Rect(PADDING, PADDING, 140, 36)
        self.btn_export_rect = pygame.Rect(PADDING + 156, PADDING, 160, 36)
        self.btn_prev_rect = pygame.Rect(PADDING + 332, PADDING, 36, 36)
        self.btn_next_rect = pygame.Rect(PADDING + 380, PADDING, 36, 36)
        pygame.draw.rect(screen, (60, 60, 60), self.btn_back_rect, border_radius=6)
        screen.blit(FONT_SMALL.render('Главное меню', True, (255, 255, 255)), (self.btn_back_rect.x + 10, self.btn_back_rect.y + 8))
        pygame.draw.rect(screen, (60, 60, 60), self.btn_export_rect, border_radius=6)
        screen.blit(FONT_SMALL.render('Экспорт в CSV', True, (255, 255, 255)), (self.btn_export_rect.x + 10, self.btn_export_rect.y + 8))
        pygame.draw.rect(screen, (80, 80, 80), self.btn_prev_rect, border_radius=6)
        screen.blit(FONT_SMALL.render('<', True, (255, 255, 255)), (self.btn_prev_rect.x + 11, self.btn_prev_rect.y + 8))
        pygame.draw.rect(screen, (80, 80, 80), self.btn_next_rect, border_radius=6)
        screen.blit(FONT_SMALL.render('>', True, (255, 255, 255)), (self.btn_next_rect.x + 11, self.btn_next_rect.y + 8))
        summary_txt = FONT_SMALL.render(f"Всего записей: {len(self.raw_list)}    Дат: {len(self.dates_list)}", True, (220, 220, 220))
        screen.blit(summary_txt, (left_margin, top_margin - 28))
        slice_dates = self.dates_list[self.offset:self.offset + self.window_days]
        metric_series_list = []
        for key, _label in METRIC_KEYS:
            vals = []
            for d in slice_dates:
                cell = self.date_series.get(d, {})
                if key == 'total_score':
                    vals.append(float(cell.get('total_score', 0)))
                elif key == 'best_max_focus':
                    vals.append(float(cell.get('best_max_focus', 0.0)))
                elif key == 'max_time':
                    vals.append(float(cell.get('max_time', 0.0)))
                elif key == 'avg_time':
                    vals.append(float(cell.get('avg_time', 0.0)))
            metric_series_list.append(vals)
        self.metric_rects = []
        base_x = left_margin
        base_y = top_margin
        idx = 0
        for r in range(2):
            for c in range(2):
                if idx >= len(METRIC_KEYS):
                    break
                x = base_x + c * (metric_w + spacing_x)
                y = base_y + r * (metric_h + spacing_y)
                rect = pygame.Rect(x, y, metric_w, metric_h)
                pygame.draw.rect(screen, (30, 30, 36), rect)
                key, label = METRIC_KEYS[idx]
                screen.blit(FONT_SMALL.render(label, True, (220, 220, 220)), (x + 8, y + 6))
                chart_inner = pygame.Rect(x + 8, y + 32, metric_w - 16, metric_h - 44)
                pygame.draw.rect(screen, (18, 18, 22), chart_inner)
                pygame.draw.rect(screen, (60, 60, 66), chart_inner, 1)
                vals = metric_series_list[idx]
                if vals:
                    self._draw_series_in_rect(screen, chart_inner, vals)
                last_val = vals[-1] if vals else 0.0
                screen.blit(FONT_SMALL.render(f'Последн: {round(float(last_val), 2)}', True, (190, 190, 190)), (x + metric_w - 120, y + metric_h - 24))
                self.metric_rects.append(rect)
                if idx == self.selected_metric_index:
                    pygame.draw.rect(screen, (120, 190, 120), rect, 2)
                else:
                    pygame.draw.rect(screen, (40, 40, 48), rect, 1)
                idx += 1
        right_rect = pygame.Rect(right_x, right_y, right_w, right_h)
        pygame.draw.rect(screen, (28, 28, 34), right_rect)
        sel_key, sel_label = METRIC_KEYS[self.selected_metric_index]
        screen.blit(FONT_MAIN.render(sel_label, True, (230, 230, 230)), (right_x + 12, right_y + 8))
        large_chart = pygame.Rect(right_x + 12, right_y + 44, right_w - 24, right_h - 64)
        pygame.draw.rect(screen, (18, 18, 24), large_chart)
        pygame.draw.rect(screen, (50, 50, 60), large_chart, 1)
        sel_vals = []
        for d in slice_dates:
            cell = self.date_series.get(d, {})
            if sel_key == 'total_score':
                sel_vals.append(float(cell.get('total_score', 0)))
            elif sel_key == 'best_max_focus':
                sel_vals.append(float(cell.get('best_max_focus', 0.0)))
            elif sel_key == 'max_time':
                sel_vals.append(float(cell.get('max_time', 0.0)))
            elif sel_key == 'avg_time':
                sel_vals.append(float(cell.get('avg_time', 0.0)))
        self._draw_series_in_rect(screen, large_chart, sel_vals, fill=True, draw_points=True)
        if slice_dates:
            n = min(6, len(slice_dates))
            step = max(1, len(slice_dates) // n)
            for i, d in enumerate(slice_dates):
                if i % step == 0 or i == len(slice_dates) - 1:
                    px = large_chart.x + int((i / (len(slice_dates) - 1 if len(slice_dates) > 1 else 1)) * (large_chart.w))
                    lbl = FONT_SMALL.render(d[5:], True, (160, 160, 160))
                    screen.blit(lbl, (px - 18, large_chart.y + large_chart.h + 6))
        agg = self._compute_overall_metrics()
        ay = right_y + right_h + 12
        screen.blit(FONT_SMALL.render(f"Всего записей: {len(self.raw_list)}    Сумма score: {int(agg.get('total_score', 0))}", True, (220, 220, 220)), (right_x, ay))
        screen.blit(FONT_SMALL.render(f"Макс время: {int(agg.get('max_time', 0))}s   Ср. время: {int(agg.get('avg_time', 0))}s", True, (190, 190, 190)), (right_x, ay + 22))

    def _draw_series_in_rect(self, surface: pygame.Surface, rect: pygame.Rect, values: List[float], fill: bool = False, draw_points: bool = False):
        if not values:
            return
        max_v = max(values) or 1.0
        min_v = min(values) or 0.0
        rng = max_v - min_v if (max_v - min_v) > 0 else 1.0
        n = len(values)
        points: List[Tuple[int, int]] = []
        for i, v in enumerate(values):
            x = rect.x + int((i / (n - 1 if n > 1 else 1)) * rect.w)
            y_norm = (v - min_v) / rng
            y = rect.y + rect.h - int(y_norm * rect.h)
            points.append((x, y))
        if fill and len(points) >= 2:
            poly = [(points[0][0], rect.y + rect.h)] + points + [(points[-1][0], rect.y + rect.h)]
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            offs = [(px - rect.x, py - rect.y) for px, py in poly]
            pygame.draw.polygon(s, (80, 160, 120, 80), offs)
            surface.blit(s, (rect.x, rect.y))
        if len(points) >= 2:
            pygame.draw.lines(surface, (120, 200, 140), False, points, 2)
        if draw_points:
            for p in points:
                pygame.draw.circle(surface, (200, 240, 200), p, 4)

    def _compute_overall_metrics(self) -> Dict[str, float]:
        if not self.raw_list:
            return {'total_score': 0, 'max_time': 0.0, 'avg_time': 0.0}
        total_score = sum(int(r.get('score', 0)) for r in self.raw_list)
        times = [float(r.get('time', 0.0)) for r in self.raw_list if r.get('time') is not None]
        max_time = max(times) if times else 0.0
        avg_time = (sum(times) / len(times)) if times else 0.0
        return {'total_score': total_score, 'max_time': max_time, 'avg_time': avg_time}

    def export_csv(self, path: str) -> bool:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'games_count', 'total_score', 'best_max_focus', 'max_time', 'avg_time', 'errors_json'])
                for d, vals in self.date_series.items():
                    writer.writerow([
                        d,
                        int(vals.get('games_count', 0)),
                        int(vals.get('total_score', 0)),
                        float(vals.get('best_max_focus', 0.0)),
                        float(vals.get('max_time', 0.0)),
                        float(vals.get('avg_time', 0.0)),
                        json.dumps(vals.get('errors', {}), ensure_ascii=False)
                    ])
            return True
        except Exception:
            return False
