# main.py
import os
import sys
import json
import shutil
import subprocess
import threading
import time
import webbrowser
import datetime
import tempfile
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import requests
import minecraft_launcher_lib

# ============================================================
# КОНСТАНТЫ
# ============================================================
CURRENT_VERSION = "1.0.0-beta"
GITHUB_REPO = "CatLauncher-Launcher/CatLauncher"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DISCORD_URL = "https://discord.gg/catlauncher"
BUG_REPORT_URL = "https://github.com/CatLauncher-Launcher/CatLauncher/issues"
MODRINTH_API = "https://api.modrinth.com/v2"

APPDATA = Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~"))) / "CatLauncher"
APPDATA.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE = APPDATA / "settings.json"
ACCOUNTS_FILE = APPDATA / "accounts.json"
PROGRESS_FILE = APPDATA / "progress.json"
MINECRAFT_DIR = Path(minecraft_launcher_lib.utils.get_minecraft_directory())
CATS_DIR = APPDATA / "cats"
CATS_DIR.mkdir(exist_ok=True)
CUSTOM_SKINS_DIR = APPDATA / "custom_skins"
CUSTOM_SKINS_DIR.mkdir(exist_ok=True)

# Пиксельные цвета "Блок Земли и Травы"
COLOR_BG = "#1e1e1e"
COLOR_PANEL = "#2c2c2c"
COLOR_TEXT = "#f0f0f0"
COLOR_TEXT_DIM = "#a0a0a0"
COLOR_SUCCESS = "#22c55e"
COLOR_DANGER = "#ef4444"

GRASS_TOP = "#4caf50"
GRASS_EDGE = "#2e7d32"
DIRT_MAIN = "#5d4037"
DIRT_SPOT1 = "#4e342e"
DIRT_SPOT2 = "#3e2723"

# ============================================================
# ДАННЫЕ ГАРДЕРОБА
# ============================================================
CAPES = {
    "starter": {"name": "Стартовый плащ CatLauncher", "price": 0, "icon": "🐾"},
    "potato": {"name": "Картофельный плащ", "price": 0, "icon": "🥔"},
    "minecon": {"name": "Классический красный Minecon-плащ", "price": 0, "icon": "🔴"},
    "golden_potato": {"name": "Золотой Картофельный Король", "price": 1200, "icon": "👑🥔"},
    "moon_cat": {"name": "Лунный Кот", "price": 1500, "icon": "🌙🐱"},
}

HATS = {
    "season_winter": {"name": "Шапка Деда Мороза", "icon": "🎅", "price": 50, "type": "season", "months": [12, 1, 2]},
    "season_spring": {"name": "Венок из зелёных листьев", "icon": "🌿", "price": 50, "type": "season", "months": [3, 4, 5]},
    "season_summer": {"name": "Летняя кепка", "icon": "🧢", "price": 50, "type": "season", "months": [6, 7, 8]},
    "season_autumn": {"name": "Венок из жёлтых листьев", "icon": "🍂", "price": 50, "type": "season", "months": [9, 10, 11]},
    "event_26.11": {"name": "Корона основателя CatLauncher", "icon": "👑", "price": 50, "type": "event", "date": "26.11"},
    "event_01.04": {"name": "Шапка клоуна", "icon": "🤡", "price": 50, "type": "event", "date": "01.04"},
    "event_09.05": {"name": "Праздничная шапка с флагом", "icon": "🎖️", "price": 50, "type": "event", "date": "09.05"},
    "hat_cat": {"name": "Кошачьи ушки", "icon": "🐱", "price": 100, "type": "normal"},
    "hat_crown": {"name": "Золотая корона", "icon": "👑", "price": 200, "type": "normal"},
    "hat_halo": {"name": "Святой нимб", "icon": "😇", "price": 150, "type": "normal"},
}

QUESTS = {
    "play_30min": {"name": "Отыграть 30 минут", "reward": 30, "target": 1800},
    "play_1h": {"name": "Отыграть 1 час", "reward": 60, "target": 3600},
    "play_3h": {"name": "Отыграть 3 часа", "reward": 150, "target": 10800},
    "play_10h": {"name": "Отыграть 10 часов", "reward": 400, "target": 36000},
    "play_24h": {"name": "Отыграть 24 часа", "reward": 600, "target": 86400},
}

POPULAR_VERSIONS = ["1.21.11", "1.21.1", "1.20.4", "1.19.4", "1.16.5", "1.12.2", "1.8.9"]

# ============================================================
# УТИЛИТЫ
# ============================================================
def load_json(path, default=None):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default if default is not None else {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ============================================================
# КЛАССЫ ДАННЫХ
# ============================================================
class Settings:
    def __init__(self):
        data = load_json(SETTINGS_FILE, {})
        self.show_cat = data.get("show_cat", True)
        self.cat_image = data.get("cat_image", "")
        self.ram_mb = data.get("ram_mb", 2048)
        self.last_version = data.get("last_version", "1.21.11")
        self.last_mode = data.get("last_mode", "Fabulously Optimized")
        self.played_seconds = data.get("played_seconds", 0)
        self.claimed_quests = data.get("claimed_quests", [])
        self.social_quest_done = data.get("social_quest_done", False)
        self.save()

    def save(self):
        save_json(SETTINGS_FILE, {
            "show_cat": self.show_cat, "cat_image": self.cat_image,
            "ram_mb": self.ram_mb, "last_version": self.last_version,
            "last_mode": self.last_mode,
            "played_seconds": self.played_seconds, "claimed_quests": self.claimed_quests,
            "social_quest_done": self.social_quest_done,
        })

class AccountManager:
    def __init__(self):
        data = load_json(ACCOUNTS_FILE, {})
        self.accounts = data.get("accounts", [])
        self.active_index = data.get("active_index", 0)
        if not self.accounts:
            self.accounts.append({"type": "offline", "username": "Player", "skin_path": "", "slim": False})
            self.active_index = 0
            self.save()

    def get_active(self):
        return self.accounts[self.active_index] if 0 <= self.active_index < len(self.accounts) else self.accounts[0]

    def add(self, account):
        self.accounts.append(account)
        self.active_index = len(self.accounts) - 1
        self.save()

    def set_active(self, index):
        if 0 <= index < len(self.accounts):
            self.active_index = index
            self.save()

    def save(self):
        save_json(ACCOUNTS_FILE, {"accounts": self.accounts, "active_index": self.active_index})

class ProgressManager:
    def __init__(self):
        data = load_json(PROGRESS_FILE, {})
        self.rubies = data.get("rubies", 0)
        self.owned_capes = data.get("owned_capes", ["starter"])
        self.owned_hats = data.get("owned_hats", [])
        self.selected_cape = data.get("selected_cape", "starter")
        self.selected_hat = data.get("selected_hat", "")
        self.starter_bonus_claimed = data.get("starter_bonus_claimed", False)
        
        if not self.starter_bonus_claimed:
            self.rubies += 50
            if "starter" not in self.owned_capes:
                self.owned_capes.append("starter")
            self.starter_bonus_claimed = True
            self.save()

    def save(self):
        save_json(PROGRESS_FILE, {
            "rubies": self.rubies, "owned_capes": self.owned_capes,
            "owned_hats": self.owned_hats, "selected_cape": self.selected_cape,
            "selected_hat": self.selected_hat,
            "starter_bonus_claimed": self.starter_bonus_claimed,
        })

# ============================================================
# ВИДЖЕТ "БЛОК ЗЕМЛИ И ТРАВЫ"
# ============================================================
class GrassDirtButton(ctk.CTkFrame):
    def __init__(self, master, text, command=None, width=200, height=50, font=("Consolas", 14, "bold"), **kwargs):
        super().__init__(master, width=width, height=height, fg_color="transparent", **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.command = command
        self.text = text
        self.font = font
        self.is_hover = False
        self.canvas = ctk.CTkCanvas(self, width=width, height=height, highlightthickness=0, bg=COLOR_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw_block)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)

    def draw_block(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return
        self.canvas.delete("all")
        grass_h = int(h * 0.35)
        self.canvas.create_rectangle(0, 0, w, grass_h, fill=GRASS_TOP, outline="")
        self.canvas.create_rectangle(0, grass_h, w, grass_h + 2, fill=GRASS_EDGE, outline="")
        import random
        random.seed(42)
        for i in range(0, w, 8):
            if random.choice([True, False]):
                self.canvas.create_rectangle(i, grass_h - 2, i + 4, grass_h, fill=GRASS_EDGE, outline="")
        dirt_h = h - grass_h - 2
        self.canvas.create_rectangle(0, grass_h + 2, w, h, fill=DIRT_MAIN, outline="")
        random.seed(100)
        for _ in range(int(w * dirt_h / 150)):
            px = random.randint(0, w - 4)
            py = random.randint(grass_h + 4, h - 4)
            color = random.choice([DIRT_SPOT1, DIRT_SPOT2])
            size = random.choice([2, 3, 4])
            self.canvas.create_rectangle(px, py, px + size, py + size, fill=color, outline="")
        if self.is_hover:
            self.canvas.create_rectangle(0, 0, w, h, fill="#000000", outline="", stipple="gray25")
        self.canvas.create_text(w//2, h//2, text=self.text, fill="#ffffff", font=self.font, anchor="center")

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.is_hover = True
        self.draw_block()

    def _on_leave(self, event):
        self.is_hover = False
        self.draw_block()

    def configure_text(self, text):
        self.text = text
        self.draw_block()

# ============================================================
# ПРЕДПРОСМОТР СКИНА (2D)
# ============================================================
def render_skin_preview(skin_path, slim=False, scale=4):
    try:
        img = Image.open(skin_path).convert("RGBA")
    except:
        return None
    if img.width < 64 or img.height < 32:
        return None
    fig_w, fig_h = 32, 32
    s = 4
    canvas = Image.new("RGBA", (fig_w * s, fig_h * s), (0, 0, 0, 0))
    def copy_part(src_box, dest_box):
        if src_box[2] > img.width or src_box[3] > img.height:
            return
        part = img.crop(src_box)
        part = part.resize(((dest_box[2]-dest_box[0])*s, (dest_box[3]-dest_box[1])*s), Image.Resampling.NEAREST)
        canvas.paste(part, (dest_box[0]*s, dest_box[1]*s), part)
    copy_part((8, 8, 16, 16), (12, 0, 20, 8))
    copy_part((40, 8, 48, 16), (12, 0, 20, 8))
    copy_part((20, 20, 28, 32), (12, 8, 20, 20))
    if img.height == 64:
        copy_part((20, 36, 28, 48), (12, 8, 20, 20))
    if slim:
        copy_part((44, 20, 47, 32), (8, 8, 11, 20))
        copy_part((36, 52, 39, 64), (21, 8, 24, 20))
    else:
        copy_part((44, 20, 48, 32), (8, 8, 12, 20))
        copy_part((36, 52, 40, 64), (20, 8, 24, 20))
    copy_part((4, 20, 8, 32), (12, 20, 16, 32))
    copy_part((20, 52, 24, 64), (16, 20, 20, 32))
    return canvas.resize((fig_w * scale, fig_h * scale), Image.Resampling.NEAREST)

# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
class CatLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CatLauncher")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        try:
            icon_path = self.resource_path("cat_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLOR_BG)
        self.settings = Settings()
        self.accounts = AccountManager()
        self.progress = ProgressManager()
        self.current_tab = "home"
        self.installing = False
        self.game_running = False
        self.play_start_time = None
        self.quest_update_timer = None
        self.build_ui()
        threading.Thread(target=self.check_updates, daemon=True).start()
        self.schedule_quest_update()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def resource_path(self, relative):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)

    def build_ui(self):
        self.top_bar = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=60, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)
        ctk.CTkLabel(self.top_bar, text="🐱 CatLauncher", font=("Consolas", 20, "bold"), text_color=COLOR_TEXT).pack(side="left", padx=20)
        self.profile_frame = ctk.CTkFrame(self.top_bar, fg_color="#1a1a1a", corner_radius=8, cursor="hand2")
        self.profile_frame.pack(side="right", padx=20, pady=8)
        self.profile_head_label = ctk.CTkLabel(self.profile_frame, text="", width=32, height=32)
        self.profile_head_label.pack(side="left", padx=(5, 5))
        active = self.accounts.get_active()
        username = active.get("username", "Player") if active else "Player"
        self.profile_label = ctk.CTkLabel(self.profile_frame, text=f"🐾 {username}", font=("Consolas", 13, "bold"), text_color=COLOR_TEXT)
        self.profile_label.pack(side="left", padx=(0, 10))
        for widget in [self.profile_frame, self.profile_head_label, self.profile_label]:
            widget.bind("<Button-1>", lambda e: self.switch_tab("accounts"))
        self.update_profile_head()
        tab_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        tab_frame.pack(side="left", padx=40)
        self.tab_buttons = {}
        tabs = [("home", "Главная"), ("mods", "Сборки и Моды"), ("accounts", "Аккаунты и Скины"), ("quests", "Квесты и Гардероб"), ("settings", "Настройки")]
        for key, label in tabs:
            btn = ctk.CTkButton(tab_frame, text=label, width=120, height=32, fg_color="transparent", text_color=COLOR_TEXT_DIM, hover_color="#3a3a3a", corner_radius=0, border_width=1, border_color=COLOR_PANEL, font=("Consolas", 12), command=lambda k=key: self.switch_tab(k))
            btn.pack(side="left", padx=2)
            self.tab_buttons[key] = btn
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        self.tab_frames = {}
        self.build_home_tab()
        self.build_mods_tab()
        self.build_accounts_tab()
        self.build_quests_tab()
        self.build_settings_tab()
        self.switch_tab("home")

    def build_home_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frames["home"] = frame
        self.bg_label = ctk.CTkLabel(frame, text="🐱", font=("Segoe UI", 200))
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
        self.bg_label.lower()
        self.update_cat_background()
        frame.bind("<Configure>", self.on_resize_bg)
        center = ctk.CTkFrame(frame, fg_color="transparent")
        center.place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(center, text="🐱 CatLauncher", font=("Consolas", 36, "bold"), text_color=COLOR_TEXT).pack(pady=(0, 10))
        ctk.CTkLabel(center, text="Современный лаунчер с котиками", font=("Consolas", 14), text_color=COLOR_TEXT_DIM).pack(pady=(0, 30))
        bottom_right_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_right_frame.place(relx=0.98, rely=0.98, anchor="se")
        self.version_btn = GrassDirtButton(bottom_right_frame, text=f"📦 {self.settings.last_version} • {self.settings.last_mode}", command=self.show_version_dialog, width=240, height=50, font=("Consolas", 12, "bold"))
        self.version_btn.pack(side="left", padx=(0, 10), pady=5)
        self.play_btn = GrassDirtButton(bottom_right_frame, text="▶ PLAY", command=self.launch_game, width=220, height=60, font=("Consolas", 20, "bold"))
        self.play_btn.pack(side="left", pady=5)
        bottom_left_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_left_frame.place(relx=0.02, rely=0.98, anchor="sw")
        self.open_folder_btn = GrassDirtButton(bottom_left_frame, text="📁 Открыть папку игры", command=self.open_game_folder, width=180, height=40, font=("Consolas", 12, "bold"))
        self.open_folder_btn.pack(side="left", padx=5)
        self.bug_btn = GrassDirtButton(bottom_left_frame, text="🐞 Сообщить о баге", command=lambda: webbrowser.open(BUG_REPORT_URL), width=180, height=40, font=("Consolas", 12, "bold"))
        self.bug_btn.pack(side="left", padx=5)

    def on_resize_bg(self, event):
        if self.settings.show_cat and self.settings.cat_image:
            self.update_cat_background(event.width, event.height)

    def update_cat_background(self, w=None, h=None):
        if not self.settings.show_cat or not self.settings.cat_image:
            self.bg_label.configure(image="", text="🐱", font=("Segoe UI", 200))
            return
        path = CATS_DIR / self.settings.cat_image
        if path.exists():
            try:
                img = Image.open(path)
                target_w = w if w else 800
                target_h = h if h else 500
                img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.bg_label.configure(image=photo, text="")
                self.bg_label.image = photo
            except:
                self.bg_label.configure(image="", text="🐱", font=("Segoe UI", 200))
        else:
            self.bg_label.configure(image="", text="🐱", font=("Segoe UI", 200))

    def update_profile_head(self):
        active = self.accounts.get_active()
        if not active:
            return
        head_img = None
        skin_path = active.get("skin_path", "")
        if skin_path and os.path.exists(skin_path):
            try:
                img = Image.open(skin_path).convert("RGBA")
                if img.width >= 16:
                    head = img.crop((8, 8, 16, 16))
                    if img.height >= 16 and img.width >= 48:
                        helmet = img.crop((40, 8, 48, 16))
                        head.paste(helmet, (0, 0), helmet)
                    head_img = head.resize((32, 32), Image.Resampling.NEAREST)
            except:
                pass
        if head_img:
            photo = ImageTk.PhotoImage(head_img)
            self.profile_head_label.configure(image=photo, text="")
            self.profile_head_label.image = photo
        else:
            head = Image.new("RGBA", (8, 8), (100, 100, 100, 255))
            draw = ImageDraw.Draw(head)
            draw.rectangle((0, 0, 8, 2), fill=(50, 50, 50, 255))
            draw.rectangle((2, 3, 3, 4), fill=(0, 0, 0, 255))
            draw.rectangle((5, 3, 6, 4), fill=(0, 0, 0, 255))
            draw.rectangle((3, 5, 5, 6), fill=(0, 0, 0, 255))
            head = head.resize((32, 32), Image.Resampling.NEAREST)
            photo = ImageTk.PhotoImage(head)
            self.profile_head_label.configure(image=photo, text="")
            self.profile_head_label.image = photo

    def build_mods_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frames["mods"] = frame
        ctk.CTkLabel(frame, text="🔍 Поиск модов на Modrinth", font=("Consolas", 18, "bold"), text_color=COLOR_TEXT).pack(pady=10)
        search_frame = ctk.CTkFrame(frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=5)
        self.mod_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Название мода...", width=400, corner_radius=0, border_width=2)
        self.mod_search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Искать", width=100, fg_color="#3a3a3a", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12), command=self.search_mods).pack(side="left", padx=5)
        self.mod_results = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.mod_results.pack(fill="both", expand=True, padx=20, pady=10)

    def build_accounts_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frames["accounts"] = frame
        ctk.CTkLabel(frame, text="👤 Аккаунты", font=("Consolas", 18, "bold"), text_color=COLOR_TEXT).pack(pady=10)
        self.accounts_list = ctk.CTkScrollableFrame(frame, fg_color=COLOR_PANEL, height=150)
        self.accounts_list.pack(fill="x", padx=20, pady=5)
        self.refresh_accounts_list()
        add_frame = ctk.CTkFrame(frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(add_frame, text="➕ Офлайн-аккаунт", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12), command=self.add_offline_account).pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="🔗 Ely.by", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12), command=lambda: webbrowser.open("https://ely.by")).pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="🔗 Microsoft", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12), command=self.start_ms_auth).pack(side="left", padx=5)
        skin_main = ctk.CTkFrame(frame, fg_color="transparent")
        skin_main.pack(fill="both", expand=True, padx=20, pady=10)
        left = ctk.CTkFrame(skin_main, fg_color=COLOR_PANEL)
        left.pack(side="left", fill="y", padx=(0, 10), ipadx=10, ipady=10)
        ctk.CTkLabel(left, text="🎨 Скин (для офлайн)", font=("Consolas", 14, "bold"), text_color=COLOR_TEXT).pack(pady=(5, 10))
        ctk.CTkButton(left, text="📂 Выбрать .png", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 11), command=self.select_skin_file).pack(pady=5)
        self.slim_var = ctk.StringVar(value="classic")
        ctk.CTkRadioButton(left, text="Classic (Толстые)", variable=self.slim_var, value="classic", font=("Consolas", 11)).pack(pady=2)
        ctk.CTkRadioButton(left, text="Slim (Тонкие)", variable=self.slim_var, value="slim", font=("Consolas", 11)).pack(pady=2)
        ctk.CTkButton(left, text="💾 Сохранить скин", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 11), command=self.save_skin).pack(pady=(15, 5))
        right = ctk.CTkFrame(skin_main, fg_color="#1a1a1a")
        right.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(right, text="Предпросмотр персонажа", font=("Consolas", 12, "bold"), text_color=COLOR_TEXT_DIM).pack(pady=5)
        self.skin_preview_label = ctk.CTkLabel(right, text="Загрузите скин\nдля предпросмотра", font=("Consolas", 11), text_color=COLOR_TEXT_DIM)
        self.skin_preview_label.pack(expand=True)

    def build_quests_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frames["quests"] = frame
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        balance_frame = ctk.CTkFrame(scroll, fg_color=COLOR_PANEL, corner_radius=8)
        balance_frame.pack(fill="x", pady=5)
        self.rubies_label = ctk.CTkLabel(balance_frame, text=f"💎 {self.progress.rubies} рубинов", font=("Consolas", 20, "bold"), text_color="#fbbf24")
        self.rubies_label.pack(pady=10)
        ctk.CTkLabel(scroll, text="📋 Квесты", font=("Consolas", 18, "bold"), text_color=COLOR_TEXT).pack(anchor="w", pady=(15, 5))
        quest_frame = ctk.CTkFrame(scroll, fg_color=COLOR_PANEL, corner_radius=8)
        quest_frame.pack(fill="x", pady=5)
        played = self.settings.played_seconds
        for qid, q in QUESTS.items():
            row = ctk.CTkFrame(quest_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            status = "✅" if qid in self.settings.claimed_quests else "⏳"
            progress_text = f"{min(played, q['target'])}/{q['target']} сек"
            ctk.CTkLabel(row, text=f"{status} {q['name']} (+{q['reward']}💎) {progress_text}", text_color=COLOR_TEXT if qid not in self.settings.claimed_quests else COLOR_SUCCESS).pack(side="left")
            if qid not in self.settings.claimed_quests and played >= q["target"]:
                ctk.CTkButton(row, text="Забрать", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda q=qid: self.claim_quest(q)).pack(side="right")
        social_row = ctk.CTkFrame(quest_frame, fg_color="transparent")
        social_row.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(social_row, text="💬 Зайти в наш Discord (+300💎)", text_color=COLOR_TEXT if not self.settings.social_quest_done else COLOR_SUCCESS).pack(side="left")
        if not self.settings.social_quest_done:
            ctk.CTkButton(social_row, text="Перейти", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=self.social_quest).pack(side="right")
        ctk.CTkLabel(scroll, text="👕 Гардероб", font=("Consolas", 18, "bold"), text_color=COLOR_TEXT).pack(anchor="w", pady=(20, 5))
        capes_frame = ctk.CTkFrame(scroll, fg_color=COLOR_PANEL, corner_radius=8)
        capes_frame.pack(fill="x", pady=5)
        for cid, cape in CAPES.items():
            row = ctk.CTkFrame(capes_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            owned = cid in self.progress.owned_capes
            selected = self.progress.selected_cape == cid
            prefix = "✅" if selected else ("📦" if owned else "🔒")
            ctk.CTkLabel(row, text=f"{prefix} {cape['icon']} {cape['name']} — {cape['price']}💎", text_color=COLOR_SUCCESS if selected else COLOR_TEXT).pack(side="left")
            if not owned:
                ctk.CTkButton(row, text="Купить", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda c=cid: self.buy_cape(c)).pack(side="right")
            elif not selected:
                ctk.CTkButton(row, text="Надеть", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda c=cid: self.equip_cape(c)).pack(side="right")
        now = datetime.datetime.now()
        today_str = now.strftime("%d.%m")
        month = now.month
        hats_frame = ctk.CTkFrame(scroll, fg_color=COLOR_PANEL, corner_radius=8)
        hats_frame.pack(fill="x", pady=5)
        for hid, hat in HATS.items():
            if hat["type"] == "season" and month not in hat.get("months", []):
                continue
            if hat["type"] == "event" and hat.get("date") != today_str:
                continue
            row = ctk.CTkFrame(hats_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            owned = hid in self.progress.owned_hats
            selected = self.progress.selected_hat == hid
            prefix = "✅" if selected else ("📦" if owned else "🔒")
            ctk.CTkLabel(row, text=f"{prefix} {hat['icon']} {hat['name']} — {hat['price']}💎", text_color=COLOR_SUCCESS if selected else COLOR_TEXT).pack(side="left")
            if not owned:
                ctk.CTkButton(row, text="Купить", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda h=hid: self.buy_hat(h)).pack(side="right")
            elif not selected:
                ctk.CTkButton(row, text="Надеть", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda h=hid: self.equip_hat(h)).pack(side="right")
            else:
                ctk.CTkButton(row, text="Снять", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda h=hid: self.unequip_hat(h)).pack(side="right")

    def build_settings_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.tab_frames["settings"] = frame
        ctk.CTkLabel(frame, text="⚙️ Настройки", font=("Consolas", 18, "bold"), text_color=COLOR_TEXT).pack(pady=10)
        cat_frame = ctk.CTkFrame(frame, fg_color=COLOR_PANEL)
        cat_frame.pack(fill="x", padx=20, pady=5)
        self.cat_switch = ctk.CTkSwitch(cat_frame, text="Показывать кота", command=self.toggle_cat)
        self.cat_switch.pack(padx=10, pady=10)
        if self.settings.show_cat: self.cat_switch.select()
        ctk.CTkLabel(cat_frame, text="Картинка котика:").pack(anchor="w", padx=10)
        self.cat_listbox = ctk.CTkOptionMenu(cat_frame, values=self.get_cat_images(), command=self.select_cat_image, corner_radius=0)
        self.cat_listbox.pack(fill="x", padx=10, pady=5)
        ram_frame = ctk.CTkFrame(frame, fg_color=COLOR_PANEL)
        ram_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(ram_frame, text="Оперативная память (МБ):").pack(anchor="w", padx=10, pady=(10, 0))
        self.ram_slider = ctk.CTkSlider(ram_frame, from_=2048, to=8192, number_of_steps=12, command=self.on_ram_change)
        self.ram_slider.pack(fill="x", padx=10, pady=5)
        self.ram_slider.set(self.settings.ram_mb)
        self.ram_label = ctk.CTkLabel(ram_frame, text=f"{self.settings.ram_mb} МБ")
        self.ram_label.pack(padx=10, pady=(0, 10))

    def switch_tab(self, key):
        for k, f in self.tab_frames.items():
            f.pack_forget()
        self.tab_frames[key].pack(fill="both", expand=True)
        self.current_tab = key
        for k, btn in self.tab_buttons.items():
            if k == key:
                btn.configure(fg_color="#4caf50", text_color="#ffffff", border_color="#2e7d32")
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_DIM, border_color=COLOR_PANEL)
        if key == "home":
            self.update_profile_head()
        elif key == "accounts":
            self.update_profile_head()

    def get_cat_images(self):
        cats = [f.name for f in CATS_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif")]
        return cats if cats else ["(пусто)"]

    def toggle_cat(self):
        self.settings.show_cat = bool(self.cat_switch.get())
        self.settings.save()
        self.update_cat_background()

    def select_cat_image(self, choice):
        self.settings.cat_image = "" if choice == "(пусто)" else choice
        self.settings.save()
        self.update_cat_background()

    def on_ram_change(self, value):
        mb = int(value)
        self.settings.ram_mb = mb
        self.ram_label.configure(text=f"{mb} МБ")
        self.settings.save()

    def refresh_profile(self):
        active = self.accounts.get_active()
        username = active.get("username", "Player") if active else "Player"
        self.profile_label.configure(text=f"🐾 {username}")
        self.update_profile_head()

    def refresh_accounts_list(self):
        for w in self.accounts_list.winfo_children():
            w.destroy()
        for i, acc in enumerate(self.accounts.accounts):
            row = ctk.CTkFrame(self.accounts_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            active = i == self.accounts.active_index
            prefix = "✅" if active else "⚪"
            ctk.CTkLabel(row, text=f"{prefix} {acc.get('type', 'offline')} · {acc.get('username', '?')}").pack(side="left")
            if not active:
                ctk.CTkButton(row, text="Выбрать", width=80, height=24, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda idx=i: self.set_active_account(idx)).pack(side="right")

    def set_active_account(self, index):
        self.accounts.set_active(index)
        self.refresh_profile()
        self.refresh_accounts_list()

    def add_offline_account(self):
        dialog = ctk.CTkInputDialog(text="Введите никнейм:", title="Офлайн-аккаунт")
        name = dialog.get_input()
        if name and name.strip():
            self.accounts.add({"type": "offline", "username": name.strip(), "skin_path": "", "slim": False})
            self.refresh_profile()
            self.refresh_accounts_list()

    def start_ms_auth(self):
        webbrowser.open("https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf")

    def select_skin_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if path:
            self.selected_skin_path = path
            slim = self.slim_var.get() == "slim"
            preview = render_skin_preview(path, slim=slim, scale=6)
            if preview:
                photo = ImageTk.PhotoImage(preview)
                self.skin_preview_label.configure(image=photo, text="")
                self.skin_preview_label.image = photo
            else:
                self.skin_preview_label.configure(text="Не удалось загрузить скин", image="")
            active = self.accounts.get_active()
            if active:
                username = active["username"]
                dest = CUSTOM_SKINS_DIR / f"{username}.png"
                shutil.copy2(path, dest)

    def save_skin(self):
        active = self.accounts.get_active()
        if not active or active.get("type") != "offline":
            return
        skin_path = getattr(self, "selected_skin_path", "")
        if not skin_path or not os.path.exists(skin_path):
            return
        username = active["username"]
        skins_dir = MINECRAFT_DIR / "CustomSkinLoader" / "LocalSkin" / "skins"
        skins_dir.mkdir(parents=True, exist_ok=True)
        dest = skins_dir / f"{username}.png"
        shutil.copy2(skin_path, dest)
        active["skin_path"] = str(dest)
        active["slim"] = self.slim_var.get() == "slim"
        self.accounts.save()
        self.update_profile_head()

    def social_quest(self):
        webbrowser.open(DISCORD_URL)
        if not self.settings.social_quest_done:
            self.progress.rubies += 300
            self.settings.social_quest_done = True
            self.progress.save()
            self.settings.save()
            self.rubies_label.configure(text=f"💎 {self.progress.rubies} рубинов")

    def claim_quest(self, qid):
        if qid in self.settings.claimed_quests: return
        q = QUESTS[qid]
        self.progress.rubies += q["reward"]
        self.settings.claimed_quests.append(qid)
        self.progress.save()
        self.settings.save()
        self.rubies_label.configure(text=f"💎 {self.progress.rubies} рубинов")
        self.build_quests_tab()

    def buy_cape(self, cid):
        cape = CAPES[cid]
        if self.progress.rubies < cape["price"]:
            return
        self.progress.rubies -= cape["price"]
        self.progress.owned_capes.append(cid)
        self.progress.save()
        self.rubies_label.configure(text=f"💎 {self.progress.rubies} рубинов")
        self.build_quests_tab()

    def equip_cape(self, cid):
        self.progress.selected_cape = cid
        self.progress.save()
        self.build_quests_tab()

    def buy_hat(self, hat_key):
        hat = HATS[hat_key]
        if self.progress.rubies < hat["price"]:
            return
        self.progress.rubies -= hat["price"]
        self.progress.owned_hats.append(hat_key)
        self.progress.save()
        self.rubies_label.configure(text=f"💎 {self.progress.rubies} рубинов")
        self.build_quests_tab()

    def equip_hat(self, hat_key):
        self.progress.selected_hat = hat_key
        self.progress.save()
        self.build_quests_tab()

    def unequip_hat(self, hat_key):
        self.progress.selected_hat = ""
        self.progress.save()
        self.build_quests_tab()

    def schedule_quest_update(self):
        if self.game_running and self.play_start_time:
            self.settings.played_seconds += 1
            self.settings.save()
        self.quest_update_timer = self.after(1000, self.schedule_quest_update)

    def open_game_folder(self):
        os.startfile(str(MINECRAFT_DIR))

    def show_version_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Выбор версии и загрузчика")
        dialog.geometry("720x680")
        dialog.configure(fg_color=COLOR_BG)
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="📦 Выбор версии и загрузчика", font=("Consolas", 20, "bold"), text_color=COLOR_TEXT).pack(pady=(15, 5))
        ctk.CTkLabel(dialog, text="Выберите режим и версию Minecraft", font=("Consolas", 11), text_color=COLOR_TEXT_DIM).pack(pady=(0, 10))
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(scroll, text="🎮 Режим запуска", font=("Consolas", 15, "bold"), text_color=COLOR_TEXT).pack(anchor="w", pady=(5, 5))
        modes = [
            ("Fabulously Optimized", "Готовая сборка на оптимизацию (Sodium, Lithium и др.)", "🐱"),
            ("Cat Client (ручной)", "Только базовые моды оптимизации от CatLauncher", "🐾"),
            ("Vanilla", "Чистая игра без модификаций", "🌿"),
            ("Fabric", "Пустой Fabric для своих модов", "🧵"),
        ]
        mode_var = ctk.StringVar(value=self.settings.last_mode)
        for mode, desc, icon in modes:
            card = ctk.CTkFrame(scroll, fg_color=COLOR_PANEL, corner_radius=8, border_width=2, border_color="#444444")
            card.pack(fill="x", pady=3)
            rb = ctk.CTkRadioButton(card, text="", variable=mode_var, value=mode, width=20)
            rb.pack(side="left", padx=10, pady=10)
            icon_label = ctk.CTkLabel(card, text=icon, font=("Segoe UI", 20), width=40)
            icon_label.pack(side="left", padx=5)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkLabel(info, text=mode, font=("Consolas", 13, "bold"), text_color=COLOR_TEXT).pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=("Consolas", 10), text_color=COLOR_TEXT_DIM).pack(anchor="w")
        ctk.CTkLabel(scroll, text="📋 Версия Minecraft", font=("Consolas", 15, "bold"), text_color=COLOR_TEXT).pack(anchor="w", pady=(15, 5))
        version_entry = ctk.CTkEntry(scroll, placeholder_text="1.21.11", width=300, height=32, corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12))
        version_entry.pack(pady=5)
        version_entry.insert(0, self.settings.last_version)
        ctk.CTkLabel(scroll, text="Популярные версии:", font=("Consolas", 11), text_color=COLOR_TEXT_DIM).pack(anchor="w", pady=(10, 5))
        quick_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        quick_grid.pack(fill="x", pady=5)
        for i, v in enumerate(POPULAR_VERSIONS):
            row = i // 3
            col = i % 3
            btn = ctk.CTkButton(quick_grid, text=v, width=120, height=32, corner_radius=0, border_width=1, border_color="#555555", fg_color="#3a3a3a", hover_color="#4caf50", font=("Consolas", 11, "bold"),
                                command=lambda v=v: (version_entry.delete(0, "end"), version_entry.insert(0, v)))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
        for c in range(3):
            quick_grid.grid_columnconfigure(c, weight=1)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        def apply():
            self.settings.last_version = version_entry.get().strip()
            self.settings.last_mode = mode_var.get()
            self.settings.save()
            self.version_btn.configure_text(f"📦 {self.settings.last_version} • {self.settings.last_mode}")
            dialog.destroy()
        ctk.CTkButton(btn_frame, text="✅ Применить", width=200, height=36, corner_radius=0, border_width=2, border_color="#555555", fg_color="#4caf50", hover_color="#388e3c", font=("Consolas", 13, "bold"), command=apply).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", width=120, height=36, corner_radius=0, border_width=2, border_color="#555555", fg_color="#3a3a3a", font=("Consolas", 12), command=dialog.destroy).pack(side="right", padx=5)

    def launch_game(self):
        if self.installing: return
        if self.game_running: return
        self.installing = True
        self.play_btn.configure_text("⏳ Установка...")
        threading.Thread(target=self._do_launch, daemon=True).start()

    def _do_launch(self):
        try:
            version = self.settings.last_version
            mode = self.settings.last_mode
            callback = {"setStatus": lambda s: None, "setProgress": lambda p: None, "setMax": lambda m: None}
            launch_version = version

            if mode == "Fabulously Optimized":
                # Скачиваем последний .mrpack для выбранной версии
                r = requests.get(f"{MODRINTH_API}/project/fabulously-optimized/version", timeout=15)
                r.raise_for_status()
                versions = r.json()
                target = None
                for v in versions:
                    if version in v.get("game_versions", []) and v.get("version_type") in ("release", "beta"):
                        target = v
                        break
                if not target:
                    raise Exception(f"Fabulously Optimized не найден для {version}")
                file_info = target["files"][0]
                mrpack_path = Path(tempfile.gettempdir()) / file_info["filename"]
                with open(mrpack_path, "wb") as f:
                    f.write(requests.get(file_info["url"], timeout=60).content)
                # Устанавливаем
                minecraft_launcher_lib.mrpack.install_mrpack(str(mrpack_path), str(MINECRAFT_DIR), callback=callback)
                launch_version = minecraft_launcher_lib.mrpack.get_mrpack_launch_version(str(mrpack_path))
                mrpack_path.unlink(missing_ok=True)

            elif mode == "Cat Client (ручной)":
                minecraft_launcher_lib.install.install_minecraft_version(version, str(MINECRAFT_DIR), callback=callback)
                fabric = minecraft_launcher_lib.mod_loader.get_mod_loader("fabric")
                fabric.install(version, str(MINECRAFT_DIR), callback=callback)
                launch_version = f"fabric-loader-{version}"
                self.download_cat_mods(version)
            else:
                minecraft_launcher_lib.install.install_minecraft_version(version, str(MINECRAFT_DIR), callback=callback)

            active = self.accounts.get_active()
            username = active.get("username", "Player") if active else "Player"
            options = {"username": username, "uuid": "", "token": "", "jvmArguments": [f"-Xmx{self.settings.ram_mb}M", f"-Xms{self.settings.ram_mb // 2}M"]}
            self.play_start_time = time.time()
            self.game_running = True
            cmd = minecraft_launcher_lib.command.get_minecraft_command(launch_version, str(MINECRAFT_DIR), options)
            subprocess.run(cmd, cwd=str(MINECRAFT_DIR))
            self.game_running = False
            elapsed = int(time.time() - self.play_start_time)
            self.settings.played_seconds += elapsed
            self.settings.save()
        except Exception as e:
            print(f"Ошибка запуска: {e}")
        finally:
            self.installing = False
            self.play_btn.configure_text("▶ PLAY")
            self.play_start_time = None

    def download_cat_mods(self, version):
        mods_dir = MINECRAFT_DIR / "mods"
        mods_dir.mkdir(exist_ok=True)
        mod_slugs = ["sodium", "lithium", "ferrite-core", "immediatelyfast", "entityculling"]
        for slug in mod_slugs:
            try:
                url = f"{MODRINTH_API}/project/{slug}/version"
                params = {"game_versions": json.dumps([version]), "loaders": json.dumps(["fabric"])}
                r = requests.get(url, params=params, timeout=15)
                r.raise_for_status()
                versions = r.json()
                if versions:
                    files = versions[0].get("files", [])
                    if files:
                        resp = requests.get(files[0]["url"], timeout=60)
                        (mods_dir / files[0]["filename"]).write_bytes(resp.content)
            except:
                pass

    def search_mods(self):
        query = self.mod_search_entry.get().strip()
        if not query: return
        for w in self.mod_results.winfo_children(): w.destroy()
        def do_search():
            try:
                url = f"{MODRINTH_API}/search"
                params = {"query": query, "limit": 20, "facets": json.dumps([["project_type:mod"]])}
                r = requests.get(url, params=params, timeout=15)
                r.raise_for_status()
                for hit in r.json().get("hits", []):
                    row = ctk.CTkFrame(self.mod_results, fg_color=COLOR_PANEL)
                    row.pack(fill="x", pady=2)
                    info = ctk.CTkFrame(row, fg_color="transparent")
                    info.pack(side="left", fill="x", expand=True, padx=5)
                    ctk.CTkLabel(info, text=hit["title"], font=("Consolas", 12, "bold")).pack(anchor="w")
                    ctk.CTkLabel(info, text=hit.get("description", "")[:80], text_color=COLOR_TEXT_DIM).pack(anchor="w")
                    ctk.CTkButton(row, text="Скачать", width=80, height=28, corner_radius=0, border_width=1, font=("Consolas", 11), command=lambda s=hit["slug"]: self.install_mod(s)).pack(side="right", padx=5)
            except:
                pass
        threading.Thread(target=do_search, daemon=True).start()

    def install_mod(self, slug):
        def do_install():
            try:
                version = self.settings.last_version
                url = f"{MODRINTH_API}/project/{slug}/version"
                params = {"game_versions": json.dumps([version]), "loaders": json.dumps(["fabric"])}
                r = requests.get(url, params=params, timeout=15)
                r.raise_for_status()
                versions = r.json()
                if versions:
                    files = versions[0].get("files", [])
                    if files:
                        mods_dir = MINECRAFT_DIR / "mods"
                        mods_dir.mkdir(exist_ok=True)
                        resp = requests.get(files[0]["url"], timeout=60)
                        (mods_dir / files[0]["filename"]).write_bytes(resp.content)
            except:
                pass
        threading.Thread(target=do_install, daemon=True).start()

    def check_updates(self):
        try:
            r = requests.get(GITHUB_API_URL, timeout=10)
            if r.status_code == 200:
                data = r.json()
                latest = data.get("tag_name", "").lstrip("v")
                if latest and latest != CURRENT_VERSION:
                    self.after(0, lambda: self.show_update_dialog(latest))
        except:
            pass

    def show_update_dialog(self, new_version):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Обновление")
        dialog.geometry("400x200")
        dialog.configure(fg_color=COLOR_BG)
        ctk.CTkLabel(dialog, text="🐱 Доступно обновление!", font=("Consolas", 16, "bold"), text_color=COLOR_TEXT).pack(pady=20)
        ctk.CTkLabel(dialog, text=f"Текущая: {CURRENT_VERSION}\nНовая: {new_version}", text_color=COLOR_TEXT).pack(pady=5)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Скачать", fg_color="#3a3a3a", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12), command=lambda: [webbrowser.open(GITHUB_RELEASES_URL), dialog.destroy()]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Позже", fg_color="#2a2a2a", corner_radius=0, border_width=2, border_color="#555555", font=("Consolas", 12), command=dialog.destroy).pack(side="left", padx=5)

    def on_close(self):
        if self.quest_update_timer:
            self.after_cancel(self.quest_update_timer)
        self.settings.save()
        self.progress.save()
        self.destroy()

if __name__ == "__main__":
    app = CatLauncher()
    app.mainloop()