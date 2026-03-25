# src/shieldnoc/client/gui/widgets/top_processes_chart.py
import random
from collections import Counter

import psutil
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


class TopProcessesChart(QWidget):
    def __init__(self, parent=None, use_demo: bool = True):
        super().__init__(parent)

        # Config
        self._use_demo = use_demo

        # State
        self._categories = ["-", "-", "-", "-", "-"]
        self._current_values = [0, 0, 0, 0, 0]
        self._target_values = [0, 0, 0, 0, 0]

        # Demo pool
        self._demo_processes_pool = [
            "chrome.exe",
            "python.exe",
            "discord.exe",
            "steam.exe",
            "code.exe",
            "explorer.exe",
            "svchost.exe",
            "firefox.exe",
            "spotify.exe",
            "teams.exe",
        ]
        self._demo_state = {
            name: random.randint(1, 10)
            for name in self._demo_processes_pool
        }

        # Series
        self._bar_set = QBarSet("Connections")
        self._bar_set.append(self._current_values)
        self._bar_set.setColor(QColor("#52b6ff"))

        self._series = QBarSeries()
        self._series.append(self._bar_set)

        # Chart
        self._chart = QChart()
        self._chart.addSeries(self._series)
        self._chart.setAnimationOptions(QChart.NoAnimation)
        self._chart.setBackgroundVisible(False)
        self._chart.legend().hide()

        self._axis_x = QBarCategoryAxis()
        self._axis_x.append(self._categories)
        self._axis_x.setTitleText("Processes")

        self._axis_y = QValueAxis()
        self._axis_y.setRange(0, 12)
        self._axis_y.setTitleText("Connections")
        self._axis_y.setTickCount(5)

        label_font = QFont("Segoe UI", 8)
        title_font = QFont("Segoe UI", 8)
        title_font.setBold(True)

        self._axis_x.setLabelsFont(label_font)
        self._axis_y.setLabelsFont(label_font)
        self._axis_x.setTitleFont(title_font)
        self._axis_y.setTitleFont(title_font)

        self._chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._chart.addAxis(self._axis_y, Qt.AlignLeft)
        self._series.attachAxis(self._axis_x)
        self._series.attachAxis(self._axis_y)

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self._chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._chart_view)

        # Timers
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(1800)
        self._refresh_timer.timeout.connect(self.refresh_data)

        self._animate_timer = QTimer(self)
        self._animate_timer.setInterval(40)
        self._animate_timer.timeout.connect(self._animate_step)

        self._refresh_timer.start()
        self._animate_timer.start()

        self.refresh_data()

    def refresh_data(self):
        top_processes = self._get_top_processes()
        new_categories = [name for name, _ in top_processes]
        new_values = [count for _, count in top_processes]

        while len(new_categories) < 5:
            new_categories.append("-")
            new_values.append(0)

        categories_changed = new_categories != self._categories

        self._categories = new_categories
        self._target_values = new_values

        if categories_changed:
            self._rebuild_x_axis()

        self._update_y_axis_range()

    def _get_top_processes(self) -> list[tuple[str, int]]:
        if self._use_demo:
            return self._get_demo_top_processes()

        process_counter = Counter()

        try:
            for conn in psutil.net_connections(kind="inet"):
                if not conn.pid:
                    continue

                try:
                    process_name = psutil.Process(conn.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

                process_counter[process_name] += 1
        except Exception:
            return self._get_demo_top_processes()

        return process_counter.most_common(5)

    def _get_demo_top_processes(self) -> list[tuple[str, int]]:
        # יוצר דינמיות אמיתית יותר:
        # ערכים משתנים, לפעמים תהליך חדש "פורץ" למעלה, ולפעמים שם משתנה
        for name in list(self._demo_state.keys()):
            delta = random.randint(-3, 4)
            self._demo_state[name] = max(0, self._demo_state[name] + delta)

        # מדי פעם תהליך כלשהו מקבל "בוסט"
        if random.random() < 0.35:
            burst_name = random.choice(self._demo_processes_pool)
            self._demo_state[burst_name] += random.randint(4, 10)

        # מדי פעם תהליך נחלש משמעותית
        if random.random() < 0.20:
            drop_name = random.choice(self._demo_processes_pool)
            self._demo_state[drop_name] = max(0, self._demo_state[drop_name] - random.randint(3, 8))

        # מדי פעם "מכניס" שם חדש/אחר לדינמיות ויזואלית
        if random.random() < 0.18:
            replacement_candidates = [
                "obs64.exe",
                "notion.exe",
                "telegram.exe",
                "postman.exe",
                "msedge.exe",
            ]
            new_name = random.choice(replacement_candidates)
            if new_name not in self._demo_state:
                # מחליף תהליך חלש קיים
                weakest_name = min(self._demo_state, key=self._demo_state.get)
                self._demo_state.pop(weakest_name, None)
                self._demo_state[new_name] = random.randint(5, 14)
                if weakest_name in self._demo_processes_pool:
                    self._demo_processes_pool.remove(weakest_name)
                self._demo_processes_pool.append(new_name)

        top = sorted(
            self._demo_state.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]

        return top

    def _rebuild_x_axis(self):
        try:
            self._series.detachAxis(self._axis_x)
            self._chart.removeAxis(self._axis_x)
        except Exception:
            pass

        self._axis_x = QBarCategoryAxis()
        self._axis_x.append(self._categories)
        self._axis_x.setTitleText("Processes")

        label_font = QFont("Segoe UI", 8)
        title_font = QFont("Segoe UI", 8)
        title_font.setBold(True)

        self._axis_x.setLabelsFont(label_font)
        self._axis_x.setTitleFont(title_font)

        self._chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._series.attachAxis(self._axis_x)

    def _update_y_axis_range(self):
        max_value = max(max(self._current_values), max(self._target_values), 1)
        wanted_max = max_value + 2
        self._axis_y.setRange(0, wanted_max)

    def _animate_step(self):
        changed = False

        for i in range(len(self._current_values)):
            current_value = self._current_values[i]
            target_value = self._target_values[i]

            if current_value == target_value:
                continue

            diff = target_value - current_value

            if abs(diff) <= 1:
                self._current_values[i] = target_value
            else:
                step = max(1, abs(diff) // 4)
                self._current_values[i] += step if diff > 0 else -step

            self._bar_set.replace(i, self._current_values[i])
            changed = True

        if changed:
            self._update_y_axis_range()