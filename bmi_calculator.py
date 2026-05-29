import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient
from urllib.parse import quote_plus

# ── MongoDB Atlas Connection ────────────────────────────────────────────────
username = quote_plus("admin")
password = quote_plus("admin@12345")
cluster_host = "cluster0.mongodb.net"
db_name = "bmi_app"
MONGO_URI = (
    f"mongodb+srv://{username}:{password}@{cluster_host}"
    f"/{db_name}?retryWrites=true&w=majority"
)


# ── In-memory fallback ──────────────────────────────────────────────────────
class _FakeCursor:
    def __init__(self, records):
        self._records = list(records)

    def sort(self, key, direction=1):
        return sorted(
            self._records,
            key=lambda r: r.get(key, ""),
            reverse=(direction == -1),
        )

    def __iter__(self):
        return iter(self._records)


class _FakeCollection:
    def __init__(self):
        self._data = []

    def insert_one(self, doc):
        self._data.append(dict(doc))

    def insert_many(self, docs):
        for d in docs:
            self._data.append(dict(d))

    def find(self, *args, **kwargs):
        return _FakeCursor(self._data)

    def find_one(self, *args, **kwargs):
        return self._data[0] if self._data else None

    def delete_many(self, *args, **kwargs):
        self._data.clear()


try:
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    bmi_collection = db["bmi_history"]
    profile_collection = db["user_profile"]
    client.server_info()
except Exception as e:
    print("MongoDB unavailable – using in-memory storage:", e)
    client = None
    bmi_collection = _FakeCollection()
    profile_collection = _FakeCollection()

# ── Theme ───────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ── Palette ─────────────────────────────────────────────────────────────────
C = {
    "bg":          "#F5F7FF",      # page background (soft lavender-white)
    "sidebar":     "#FFFFFF",      # sidebar white
    "sidebar_bd":  "#E8ECF8",      # sidebar right border
    "card":        "#FFFFFF",      # card white
    "card_bd":     "#E8ECF8",      # card border
    "accent":      "#5B6EF5",      # indigo accent
    "accent2":     "#22C993",      # teal accent (success)
    "accent3":     "#F59E0B",      # amber
    "accent4":     "#EF4444",      # red
    "accent_lt":   "#EEF0FF",      # light indigo tint
    "text_h":      "#1A1F36",      # headings
    "text_b":      "#4B5280",      # body text
    "text_m":      "#8B91B5",      # muted
    "nav_act_bg":  "#EEF0FF",      # active nav bg
    "nav_act_txt": "#5B6EF5",      # active nav text
    "input_bg":    "#F5F7FF",      # input bg
    "input_bd":    "#D0D5F0",      # input border
    "btn_fg":      "#FFFFFF",      # button text
    "green_lt":    "#DCFAF1",      # light green tint
    "amber_lt":    "#FEF3C7",
    "red_lt":      "#FEE2E2",
    "cyan_lt":     "#E0F2FE",
}

FONT_TITLE  = ("Georgia", 13, "bold")
FONT_BRAND  = ("Georgia", 16, "bold")
FONT_NAV    = ("Helvetica Neue", 12)
FONT_NAV_B  = ("Helvetica Neue", 12, "bold")
FONT_LABEL  = ("Helvetica Neue", 11)
FONT_SMALL  = ("Helvetica Neue", 10)
FONT_NUM    = ("Georgia", 26, "bold")
FONT_NUM_SM = ("Georgia", 18, "bold")
FONT_BODY   = ("Helvetica Neue", 12)
FONT_MONO   = ("Courier New", 11)


# ── Helpers ─────────────────────────────────────────────────────────────────
def make_card(parent, **kw):
    """Rounded white card with a subtle border."""
    defaults = dict(
        fg_color=C["card"],
        border_color=C["card_bd"],
        border_width=1,
        corner_radius=14,
    )
    defaults.update(kw)
    return ctk.CTkFrame(parent, **defaults)


def stat_card(parent, icon, label, value, sub, icon_bg, sub_color):
    """Mini stat card used on Dashboard & Analytics."""
    card = make_card(parent)
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(padx=16, pady=14, fill="both", expand=True)

    # icon circle
    icon_circle = ctk.CTkFrame(inner, fg_color=icon_bg, corner_radius=10, width=36, height=36)
    icon_circle.pack(anchor="w")
    icon_circle.pack_propagate(False)
    ctk.CTkLabel(icon_circle, text=icon, font=("Helvetica Neue", 16),
                 text_color=C["accent"]).place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(inner, text=value, font=FONT_NUM_SM,
                 text_color=C["text_h"]).pack(anchor="w", pady=(10, 0))
    ctk.CTkLabel(inner, text=label, font=FONT_SMALL,
                 text_color=C["text_m"]).pack(anchor="w")
    ctk.CTkLabel(inner, text=sub, font=FONT_SMALL,
                 text_color=sub_color).pack(anchor="w", pady=(4, 0))
    return card


def primary_btn(parent, text, command, width=220, color=None):
    color = color or C["accent"]
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=color, hover_color="#4858D4",
        text_color=C["btn_fg"],
        font=FONT_NAV_B, corner_radius=10,
        height=38, width=width,
    )


def section_title(parent, text):
    ctk.CTkLabel(parent, text=text, font=FONT_BRAND,
                 text_color=C["text_h"]).pack(anchor="w", pady=(0, 4))


def divider(parent):
    ctk.CTkFrame(parent, fg_color=C["card_bd"], height=1).pack(fill="x", pady=8)


# ════════════════════════════════════════════════════════════════════════════
#  Main Application
# ════════════════════════════════════════════════════════════════════════════
class BMIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Premium BMI Analyzer")
        self.geometry("920x660")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])

        self._build_sidebar()
        self._build_container()
        self.show_home()

    # ── Sidebar ─────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(
            self, width=220, fg_color=C["sidebar"],
            border_color=C["sidebar_bd"], border_width=1,
            corner_radius=0,
        )
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Brand
        brand_row = ctk.CTkFrame(sb, fg_color="transparent")
        brand_row.pack(fill="x", padx=20, pady=(28, 20))

        dot = ctk.CTkFrame(brand_row, fg_color=C["accent"],
                            corner_radius=10, width=38, height=38)
        dot.pack(side="left")
        dot.pack_propagate(False)
        ctk.CTkLabel(dot, text="♥", font=("Helvetica Neue", 18),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        brand_text = ctk.CTkFrame(brand_row, fg_color="transparent")
        brand_text.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(brand_text, text="BMI Analyzer",
                     font=FONT_BRAND, text_color=C["text_h"]).pack(anchor="w")
        ctk.CTkLabel(brand_text, text="Health Suite Pro",
                     font=FONT_SMALL, text_color=C["text_m"]).pack(anchor="w")

        ctk.CTkFrame(sb, fg_color=C["card_bd"], height=1).pack(fill="x", padx=0)

        # Nav label
        ctk.CTkLabel(sb, text="MAIN MENU", font=("Helvetica Neue", 9, "bold"),
                     text_color=C["text_m"]).pack(anchor="w", padx=20, pady=(18, 6))

        self._nav_btns = {}
        nav_items = [
            ("🏠  Dashboard",   self.show_home,       "home"),
            ("🧮  Calculator",  self.show_calculator, "calc"),
            ("📋  History",     self.show_history,    "hist"),
            ("📈  Analytics",   self.show_analytics,  "analy"),
            ("👤  Profile",     self.show_profile,    "prof"),
        ]
        for label, cmd, key in nav_items:
            btn = ctk.CTkButton(
                sb, text=label, anchor="w",
                font=FONT_NAV, height=40,
                fg_color="transparent", hover_color=C["nav_act_bg"],
                text_color=C["text_b"], corner_radius=10,
                command=lambda c=cmd, k=key: self._nav_click(c, k),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_btns[key] = btn

        ctk.CTkLabel(sb, text="DATA", font=("Helvetica Neue", 9, "bold"),
                     text_color=C["text_m"]).pack(anchor="w", padx=20, pady=(14, 6))

        ctk.CTkButton(
            sb, text="⬆  Export Data", anchor="w",
            font=FONT_NAV, height=38,
            fg_color="transparent", hover_color=C["nav_act_bg"],
            text_color=C["text_b"], corner_radius=10,
            command=self.export_data,
        ).pack(fill="x", padx=12, pady=2)

        ctk.CTkButton(
            sb, text="⬇  Import Data", anchor="w",
            font=FONT_NAV, height=38,
            fg_color="transparent", hover_color=C["nav_act_bg"],
            text_color=C["text_b"], corner_radius=10,
            command=self.import_data,
        ).pack(fill="x", padx=12, pady=2)

        ctk.CTkButton(
            sb, text="☀  Toggle Theme", anchor="w",
            font=FONT_NAV, height=38,
            fg_color="transparent", hover_color=C["nav_act_bg"],
            text_color=C["text_b"], corner_radius=10,
            command=self.toggle_theme,
        ).pack(fill="x", padx=12, pady=2)

        # Exit
        ctk.CTkButton(
            sb, text="← Exit", anchor="w",
            font=FONT_NAV, height=38,
            fg_color="transparent", hover_color="#FEE2E2",
            text_color=C["accent4"], corner_radius=10,
            command=self.quit,
        ).pack(side="bottom", fill="x", padx=12, pady=20)

    def _nav_click(self, cmd, key):
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(
                    fg_color=C["nav_act_bg"],
                    text_color=C["nav_act_txt"],
                    font=FONT_NAV_B,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=C["text_b"],
                    font=FONT_NAV,
                )
        cmd()

    # ── Container ───────────────────────────────────────────────────────────
    def _build_container(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="left", fill="both", expand=True)

        self.pages = {}
        for Page in (HomePage, CalculatorPage, HistoryPage, AnalyticsPage, ProfilePage):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

    # ── Navigation ──────────────────────────────────────────────────────────
    def show_home(self):
        self._nav_click(lambda: None, "home")
        self.pages[HomePage].refresh()
        self.pages[HomePage].tkraise()
        self._nav_btns["home"].configure(
            fg_color=C["nav_act_bg"], text_color=C["nav_act_txt"], font=FONT_NAV_B)

    def show_calculator(self):
        self._nav_click(lambda: None, "calc")
        self.pages[CalculatorPage].tkraise()
        self._nav_btns["calc"].configure(
            fg_color=C["nav_act_bg"], text_color=C["nav_act_txt"], font=FONT_NAV_B)

    def show_history(self):
        self._nav_click(lambda: None, "hist")
        self.pages[HistoryPage].refresh()
        self.pages[HistoryPage].tkraise()
        self._nav_btns["hist"].configure(
            fg_color=C["nav_act_bg"], text_color=C["nav_act_txt"], font=FONT_NAV_B)

    def show_analytics(self):
        self._nav_click(lambda: None, "analy")
        self.pages[AnalyticsPage].refresh()
        self.pages[AnalyticsPage].tkraise()
        self._nav_btns["analy"].configure(
            fg_color=C["nav_act_bg"], text_color=C["nav_act_txt"], font=FONT_NAV_B)

    def show_profile(self):
        self._nav_click(lambda: None, "prof")
        self.pages[ProfilePage].refresh()
        self.pages[ProfilePage].tkraise()
        self._nav_btns["prof"].configure(
            fg_color=C["nav_act_bg"], text_color=C["nav_act_txt"], font=FONT_NAV_B)

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Dark" if mode == "Light" else "Light")

    def export_data(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")]
        )
        if path:
            history = list(bmi_collection.find({}, {"_id": 0}))
            profile = profile_collection.find_one({}, {"_id": 0}) or {}
            with open(path, "w") as f:
                json.dump({"bmi_history": history, "profile": profile}, f, indent=2, default=str)
            messagebox.showinfo("Export", "Data exported successfully!")

    def import_data(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path) as f:
                data = json.load(f)
            bmi_collection.delete_many({})
            if data.get("bmi_history"):
                bmi_collection.insert_many(data["bmi_history"])
            if data.get("profile"):
                profile_collection.delete_many({})
                profile_collection.insert_one(data["profile"])
            messagebox.showinfo("Import", "Data imported successfully!")
            self.pages[HistoryPage].refresh()
            self.pages[ProfilePage].refresh()


# ════════════════════════════════════════════════════════════════════════════
#  Home Page
# ════════════════════════════════════════════════════════════════════════════
class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=C["bg"])
        self.controller = controller
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=C["card_bd"])
        scroll.pack(fill="both", expand=True, padx=28, pady=24)

        # ── Header ──────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 18))
        self._greeting = ctk.CTkLabel(
            hdr, text="Good morning, Guest! 👋",
            font=("Georgia", 18, "bold"), text_color=C["text_h"])
        self._greeting.pack(side="left")
        self._date_badge = ctk.CTkLabel(
            hdr,
            text=datetime.datetime.now().strftime("%d %B %Y"),
            font=FONT_SMALL,
            fg_color=C["accent_lt"],
            text_color=C["accent"],
            corner_radius=20,
            padx=14, pady=5,
        )
        self._date_badge.pack(side="right")

        # ── Profile hero card ───────────────────────────────────────────────
        hero = make_card(scroll)
        hero.pack(fill="x", pady=(0, 16))
        hero.configure(fg_color=C["accent"], border_color=C["accent"])

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=22, pady=18)

        # avatar
        av = ctk.CTkFrame(hero_inner, fg_color="white", corner_radius=30,
                           width=54, height=54)
        av.pack(side="left")
        av.pack_propagate(False)
        self._av_label = ctk.CTkLabel(av, text="G", font=("Georgia", 22, "bold"),
                                       text_color=C["accent"])
        self._av_label.place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(hero_inner, fg_color="transparent")
        info.pack(side="left", padx=(16, 0))
        self._hero_name = ctk.CTkLabel(
            info, text="Hello, Gowtham!", font=("Georgia", 15, "bold"),
            text_color="white")
        self._hero_name.pack(anchor="w")
        self._hero_meta = ctk.CTkLabel(
            info, text="Use the sidebar to navigate.",
            font=FONT_BODY, text_color="#FFFFFF")
        self._hero_meta.pack(anchor="w")
        self._hero_profile = ctk.CTkLabel(
            info, text="Profile: Age –, Gender –",
            font=FONT_SMALL, text_color="#FFFFFF")
        self._hero_profile.pack(anchor="w", pady=(3, 0))

        # live bmi bubble
        bmi_bubble = ctk.CTkFrame(
            hero_inner,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_color="#FFFFFF",
            border_width=1,
        )
        bmi_bubble.pack(side="right")
        bmi_inner = ctk.CTkFrame(bmi_bubble, fg_color="transparent")
        bmi_inner.pack(padx=18, pady=12)
        ctk.CTkLabel(bmi_inner, text="LATEST BMI", font=FONT_SMALL,
                 text_color="#FFFFFF").pack()
        self._hero_bmi = ctk.CTkLabel(bmi_inner, text="—", font=FONT_NUM,
                                       text_color="white")
        self._hero_bmi.pack()
        self._hero_cat = ctk.CTkLabel(bmi_inner, text="—", font=FONT_LABEL,
                           text_color="#FFFFFF")
        self._hero_cat.pack()

        # ── Stat grid ───────────────────────────────────────────────────────
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 16))
        for i in range(4):
            grid.columnconfigure(i, weight=1)

        self._s_total  = stat_card(grid, "📋", "Total Records", "—",  "Calculations",   C["accent_lt"], C["accent"])
        self._s_avg    = stat_card(grid, "📈", "Average BMI",   "—",  "Normal range",   C["green_lt"],  C["accent2"])
        self._s_high   = stat_card(grid, "⬆",  "Highest BMI",  "—",  "Check category", C["amber_lt"],  C["accent3"])
        self._s_latest = stat_card(grid, "📅", "Latest Entry",  "—",  "Most recent",    C["cyan_lt"],   "#0EA5E9")

        self._s_total.grid( row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")
        self._s_avg.grid(   row=0, column=1, padx=4,      pady=4, sticky="nsew")
        self._s_high.grid(  row=0, column=2, padx=4,      pady=4, sticky="nsew")
        self._s_latest.grid(row=0, column=3, padx=(8, 0), pady=4, sticky="nsew")

        # ── Bottom two-col ──────────────────────────────────────────────────
        bot = ctk.CTkFrame(scroll, fg_color="transparent")
        bot.pack(fill="x", pady=(0, 8))
        bot.columnconfigure(0, weight=3)
        bot.columnconfigure(1, weight=2)

        # classification guide card
        cls_card = make_card(bot)
        cls_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        cls_in = ctk.CTkFrame(cls_card, fg_color="transparent")
        cls_in.pack(fill="both", expand=True, padx=18, pady=16)

        row_top = ctk.CTkFrame(cls_in, fg_color="transparent")
        row_top.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(row_top, text="BMI Classification Guide",
                     font=FONT_TITLE, text_color=C["text_h"]).pack(side="left")
        ctk.CTkLabel(row_top, text="WHO Standard", font=FONT_SMALL,
                     fg_color=C["accent_lt"], text_color=C["accent"],
                     corner_radius=20, padx=10, pady=3).pack(side="right")

        # color bar segments
        bar_frame = ctk.CTkFrame(cls_in, fg_color="transparent", height=10)
        bar_frame.pack(fill="x")
        bar_frame.pack_propagate(False)
        segs = [
            ("#67E8F9", 20), ("#4ADE80", 26), ("#FBBF24", 20),
            ("#FB923C", 20), ("#EF4444", 14),
        ]
        for color, weight in segs:
            ctk.CTkFrame(bar_frame, fg_color=color, corner_radius=5,
                         height=10).pack(side="left", fill="x",
                                         expand=True, padx=1)

        # labels
        labels_row = ctk.CTkFrame(cls_in, fg_color="transparent")
        labels_row.pack(fill="x", pady=(8, 0))
        cls_items = [
            ("< 18.5",    "Underweight", "#67E8F9"),
            ("18.5–24.9", "Normal",      "#4ADE80"),
            ("25–29.9",   "Overweight",  "#FBBF24"),
            ("30–34.9",   "Obese",       "#FB923C"),
            ("> 35",      "Extreme",     "#EF4444"),
        ]
        for i in range(5):
            labels_row.columnconfigure(i, weight=1)
        for i, (rng, name, clr) in enumerate(cls_items):
            col = ctk.CTkFrame(labels_row, fg_color="transparent")
            col.grid(row=0, column=i, sticky="nsew")
            ctk.CTkLabel(col, text=rng, font=("Georgia", 10, "bold"),
                         text_color=clr).pack()
            ctk.CTkLabel(col, text=name, font=FONT_SMALL,
                         text_color=C["text_m"]).pack()

        ctk.CTkLabel(cls_in, text="Maintain a healthy BMI for a better life!",
                     font=FONT_SMALL, text_color=C["text_m"]).pack(pady=(12, 0))

        # advice card
        advice_card = make_card(bot)
        advice_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        adv_in = ctk.CTkFrame(advice_card, fg_color="transparent")
        adv_in.pack(fill="both", expand=True, padx=18, pady=16)

        ctk.CTkLabel(adv_in, text="Daily Advice", font=FONT_TITLE,
                     text_color=C["text_h"]).pack(anchor="w", pady=(0, 10))

        advices = [
            ("🥗", "#4ADE80", "Maintain a balanced diet with varied nutritious foods."),
            ("🏃", "#5B6EF5", "30 min of moderate cardio 5× per week is ideal."),
            ("💧", "#0EA5E9", "Aim for 2.5–3 L of water each day."),
            ("📊", "#F59E0B", "Log your BMI weekly to track progress."),
        ]
        for icon, dot_clr, text in advices:
            row = ctk.CTkFrame(adv_in, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text="●", font=("Helvetica", 8),
                         text_color=dot_clr).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=text, font=FONT_LABEL,
                         text_color=C["text_b"], wraplength=230, justify="left").pack(side="left")

    def refresh(self):
        profile = profile_collection.find_one() or {}
        name = profile.get("name", "Guest")
        age  = profile.get("age", "")
        gen  = profile.get("gender", "")

        self._greeting.configure(
            text=f"Good morning, {name}! 👋")
        self._hero_name.configure(text=f"Hello, {name}!")
        self._hero_meta.configure(text="Use the sidebar to navigate.")
        self._hero_profile.configure(
            text=f"Profile: Age {age}, Gender {gen}")
        self._av_label.configure(text=name[0].upper() if name else "G")

        records = list(bmi_collection.find())
        total = len(records)
        if total:
            avg   = round(sum(r["bmi"] for r in records) / total, 2)
            high  = round(max(r["bmi"] for r in records), 2)
            latest_r = sorted(records, key=lambda r: r.get("date", ""), reverse=True)[0]
            latest_bmi = latest_r["bmi"]
            latest_cat = latest_r.get("category", "")
            try:
                latest_date = latest_r["date"].strftime("%d-%b-%Y")
            except Exception:
                latest_date = str(latest_r.get("date", ""))[:10]

            self._hero_bmi.configure(text=str(latest_bmi))
            self._hero_cat.configure(text=f"✓ {latest_cat}")
        else:
            avg = high = latest_bmi = "—"
            latest_cat = latest_date = "—"

        # update stat cards (re-pack values by label widget position)
        def _update_card(card, val, sub):
            for w in card.winfo_children()[0].winfo_children():
                if isinstance(w, ctk.CTkLabel):
                    txt = w.cget("text")
                    if txt not in ("📋", "📈", "⬆", "📅",
                                   "Total Records", "Average BMI",
                                   "Highest BMI", "Latest Entry",
                                   "Calculations", "Normal range",
                                   "Check category", "Most recent"):
                        # find value label (Georgia font) and sub label
                        pass

        # simpler: just rebuild text on inner labels by index
        def _set_stat(card, value, sub_text):
            inner = card.winfo_children()[0]
            labels = [w for w in inner.winfo_children()
                      if isinstance(w, ctk.CTkLabel)]
            # labels order: icon(skipped – it's inside frame), value, label, sub
            # icon_circle is a CTkFrame, then labels follow
            lbl_list = [w for w in inner.winfo_children()
                        if isinstance(w, ctk.CTkLabel)]
            if len(lbl_list) >= 2:
                lbl_list[0].configure(text=str(value))   # value
                if len(lbl_list) >= 3:
                    lbl_list[2].configure(text=sub_text)  # sub

        _set_stat(self._s_total,  total,        "Calculations")
        _set_stat(self._s_avg,    avg,           "Normal range" if avg != "—" and float(str(avg).replace("—","0") or 0) < 25 else "Check range")
        _set_stat(self._s_high,   high,          "Peak value")
        _set_stat(self._s_latest, latest_date,   "Most recent")


# ════════════════════════════════════════════════════════════════════════════
#  Calculator Page
# ════════════════════════════════════════════════════════════════════════════
class CalculatorPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=C["bg"])
        self.controller = controller
        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.place(relx=0.5, rely=0.5, anchor="center")

        # title
        ctk.CTkLabel(outer, text="BMI Calculator",
                     font=("Georgia", 20, "bold"),
                     text_color=C["text_h"]).pack(pady=(0, 4))
        ctk.CTkLabel(outer, text="Enter your measurements below",
                     font=FONT_BODY, text_color=C["text_m"]).pack(pady=(0, 20))

        card = make_card(outer)
        card.pack(ipadx=10)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=26, fill="both", expand=True)

        # unit toggle
        unit_frame = ctk.CTkFrame(inner, fg_color=C["input_bg"],
                                   corner_radius=10, border_color=C["input_bd"],
                                   border_width=1)
        unit_frame.pack(fill="x", pady=(0, 18))
        self.unit_var = ctk.StringVar(value="Metric")
        ctk.CTkRadioButton(
            unit_frame, text="Metric (kg / cm)",
            variable=self.unit_var, value="Metric",
            font=FONT_BODY, text_color=C["text_b"],
            fg_color=C["accent"],
        ).pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(
            unit_frame, text="Imperial (lb / in)",
            variable=self.unit_var, value="Imperial",
            font=FONT_BODY, text_color=C["text_b"],
            fg_color=C["accent"],
        ).pack(side="left", padx=10, pady=10)

        # inputs
        form = ctk.CTkFrame(inner, fg_color="transparent")
        form.pack(fill="x", pady=(0, 18))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        def input_col(parent, col, lbl_text):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=0, column=col, padx=(0 if col else 0, 8 if col == 0 else 0), sticky="ew")
            ctk.CTkLabel(frame, text=lbl_text, font=FONT_LABEL,
                         text_color=C["text_m"]).pack(anchor="w")
            entry = ctk.CTkEntry(
                frame, width=200, height=42,
                fg_color=C["input_bg"], border_color=C["input_bd"],
                text_color=C["text_h"], font=FONT_BODY,
                corner_radius=10, border_width=1,
            )
            entry.pack(fill="x", pady=(4, 0))
            return entry

        self.weight_entry = input_col(form, 0, "Weight (kg / lb)")
        self.height_entry = input_col(form, 1, "Height (cm / in)")

        primary_btn(inner, "Calculate BMI ➜",
                    self.calculate_bmi, width=420).pack(fill="x")

        # result card (hidden initially)
        self.result_card = make_card(inner)
        self.result_card.pack(fill="x", pady=(16, 0))
        self.result_card.pack_forget()

        result_inner = ctk.CTkFrame(self.result_card, fg_color="transparent")
        result_inner.pack(padx=20, pady=16, fill="x")

        top_row = ctk.CTkFrame(result_inner, fg_color="transparent")
        top_row.pack(fill="x")
        self.result_bmi_lbl = ctk.CTkLabel(
            top_row, text="23.61", font=FONT_NUM, text_color=C["accent"])
        self.result_bmi_lbl.pack(side="left")
        self.result_cat_lbl = ctk.CTkLabel(
            top_row, text="Normal weight",
            font=FONT_BODY, fg_color=C["green_lt"],
            text_color=C["accent2"], corner_radius=20, padx=12, pady=4)
        self.result_cat_lbl.pack(side="left", padx=(14, 0), pady=4)

        divider(result_inner)

        self.diet_lbl = ctk.CTkLabel(
            result_inner, text="", font=FONT_BODY,
            text_color=C["text_b"], wraplength=360, justify="left")
        self.diet_lbl.pack(anchor="w")
        self.exercise_lbl = ctk.CTkLabel(
            result_inner, text="", font=FONT_BODY,
            text_color=C["text_b"], wraplength=360, justify="left")
        self.exercise_lbl.pack(anchor="w", pady=(4, 0))

    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            if weight <= 0 or height <= 0:
                raise ValueError

            if self.unit_var.get() == "Metric":
                bmi = weight / (height / 100) ** 2
            else:
                bmi = 703 * weight / (height ** 2)

            bmi = round(bmi, 2)

            if bmi < 18.5:
                cat, cat_bg, cat_fg = "Underweight", C["cyan_lt"],  "#0EA5E9"
                diet = "🥗 Increase calorie intake with nutrient-dense foods."
                ex   = "🏋️ Focus on strength training to build muscle mass."
            elif bmi < 25:
                cat, cat_bg, cat_fg = "Normal weight", C["green_lt"], C["accent2"]
                diet = "🥗 Maintain your current balanced and varied diet."
                ex   = "🏃 Continue regular physical activity 150 min/week."
            elif bmi < 30:
                cat, cat_bg, cat_fg = "Overweight", C["amber_lt"], C["accent3"]
                diet = "🥗 Reduce calories and prioritize fruits & vegetables."
                ex   = "🏃 Increase cardio frequency and add strength workouts."
            else:
                cat, cat_bg, cat_fg = "Obese", C["red_lt"], C["accent4"]
                diet = "🥗 Consult a registered dietitian for a tailored plan."
                ex   = "🏃 Start with low-impact exercise, increase gradually."

            self.result_bmi_lbl.configure(text=str(bmi))
            self.result_cat_lbl.configure(
                text=f"  {cat}  ", fg_color=cat_bg, text_color=cat_fg)
            self.diet_lbl.configure(text=f"Diet:     {diet}")
            self.exercise_lbl.configure(text=f"Exercise: {ex}")
            self.result_card.pack(fill="x", pady=(16, 0))

            bmi_collection.insert_one({
                "weight": weight, "height": height,
                "unit": self.unit_var.get(), "bmi": bmi,
                "category": cat,
                "date": datetime.datetime.now(),
            })

        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Please enter valid positive numbers for weight and height.")


# ════════════════════════════════════════════════════════════════════════════
#  History Page
# ════════════════════════════════════════════════════════════════════════════
class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=C["bg"])
        self.controller = controller
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        ctk.CTkLabel(hdr, text="BMI History",
                     font=("Georgia", 20, "bold"),
                     text_color=C["text_h"]).pack(side="left")
        self._count_badge = ctk.CTkLabel(
            hdr, text="0 Records", font=FONT_SMALL,
            fg_color=C["accent_lt"], text_color=C["accent"],
            corner_radius=20, padx=12, pady=4)
        self._count_badge.pack(side="right")

        card = make_card(self)
        card.pack(fill="both", expand=True, padx=28, pady=16)

        # header row
        hdr_row = ctk.CTkFrame(card, fg_color=C["bg"], corner_radius=8)
        hdr_row.pack(fill="x", padx=12, pady=(12, 4))
        cols = ["Date & Time", "Weight", "Height", "Unit", "BMI", "Category"]
        widths = [160, 80, 80, 70, 70, 110]
        for i, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hdr_row, text=col, font=("Helvetica Neue", 10, "bold"),
                         text_color=C["text_m"], width=w, anchor="w").pack(
                side="left", padx=(16 if i == 0 else 0, 0))

        ctk.CTkFrame(card, fg_color=C["card_bd"], height=1).pack(fill="x", padx=12)

        self.scroll_body = ctk.CTkScrollableFrame(
            card, fg_color="transparent",
            scrollbar_button_color=C["card_bd"])
        self.scroll_body.pack(fill="both", expand=True, padx=4, pady=4)

    def refresh(self):
        for w in self.scroll_body.winfo_children():
            w.destroy()

        records = list(bmi_collection.find())
        try:
            records = sorted(records, key=lambda r: r.get("date", ""), reverse=True)
        except Exception:
            pass

        self._count_badge.configure(text=f"{len(records)} Records")

        cat_styles = {
            "Normal weight": (C["green_lt"], C["accent2"]),
            "Overweight":    (C["amber_lt"], C["accent3"]),
            "Underweight":   (C["cyan_lt"],  "#0EA5E9"),
            "Obese":         (C["red_lt"],   C["accent4"]),
        }

        for i, r in enumerate(records):
            row = ctk.CTkFrame(
                self.scroll_body,
                fg_color="white" if i % 2 == 0 else C["bg"],
                corner_radius=8,
            )
            row.pack(fill="x", pady=1)

            try:
                dt = r["date"].strftime("%Y-%m-%d %H:%M")
            except Exception:
                dt = str(r.get("date", ""))[:16]

            cat = r.get("category", "")
            cat_bg, cat_fg = cat_styles.get(cat, (C["accent_lt"], C["accent"]))

            vals = [dt, f"{r.get('weight','')} ", f"{r.get('height','')} ",
                    r.get("unit", ""), str(r.get("bmi", ""))]
            widths = [160, 80, 80, 70, 70]
            for j, (val, w) in enumerate(zip(vals, widths)):
                ctk.CTkLabel(row, text=val, font=FONT_BODY,
                             text_color=C["text_b"], width=w, anchor="w").pack(
                    side="left", padx=(16 if j == 0 else 0, 0), pady=8)

            ctk.CTkLabel(row, text=f"  {cat}  ", font=FONT_SMALL,
                         fg_color=cat_bg, text_color=cat_fg,
                         corner_radius=20).pack(side="left", padx=4)


# ════════════════════════════════════════════════════════════════════════════
#  Analytics Page
# ════════════════════════════════════════════════════════════════════════════
class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=C["bg"])
        self.controller = controller
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=C["card_bd"])
        scroll.pack(fill="both", expand=True, padx=28, pady=24)

        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(hdr, text="Analytics",
                     font=("Georgia", 20, "bold"),
                     text_color=C["text_h"]).pack(side="left")

        # stat grid
        self._grid = ctk.CTkFrame(scroll, fg_color="transparent")
        self._grid.pack(fill="x", pady=(0, 16))
        for i in range(4):
            self._grid.columnconfigure(i, weight=1)

        self._s1 = stat_card(self._grid, "📉", "BMI Drop (2mo)", "—", "↓ Improving",  C["green_lt"], C["accent2"])
        self._s2 = stat_card(self._grid, "📊", "7-entry Avg",   "—", "Normal",        C["accent_lt"], C["accent"])
        self._s3 = stat_card(self._grid, "⬆",  "All-time High", "—", "Peak value",    C["amber_lt"], C["accent3"])
        self._s4 = stat_card(self._grid, "⬇",  "All-time Low",  "—", "Lowest value",  C["cyan_lt"],  "#0EA5E9")

        self._s1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self._s2.grid(row=0, column=1, padx=4,      sticky="nsew")
        self._s3.grid(row=0, column=2, padx=4,      sticky="nsew")
        self._s4.grid(row=0, column=3, padx=(8, 0), sticky="nsew")

        # chart card
        chart_card = make_card(scroll)
        chart_card.pack(fill="x", pady=(0, 16))
        chart_in = ctk.CTkFrame(chart_card, fg_color="transparent")
        chart_in.pack(fill="both", expand=True, padx=18, pady=16)

        top = ctk.CTkFrame(chart_in, fg_color="transparent")
        top.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(top, text="BMI Over Time",
                     font=FONT_TITLE, text_color=C["text_h"]).pack(side="left")
        ctk.CTkLabel(top, text="View Chart ➜",
                     font=FONT_SMALL, text_color=C["accent"],
                     cursor="hand2").pack(side="right")

        self._chart_frame = ctk.CTkFrame(chart_in, fg_color="transparent")
        self._chart_frame.pack(fill="both", expand=True)
        self._canvas_widget = None

    def refresh(self):
        records = list(bmi_collection.find())
        if not records:
            return

        try:
            records = sorted(records, key=lambda r: r["date"])
        except Exception:
            pass

        dates     = [r["date"] for r in records]
        bmi_vals  = [r["bmi"]  for r in records]
        total     = len(records)
        avg_bmi   = round(sum(bmi_vals) / total, 2) if total else "—"
        high_bmi  = round(max(bmi_vals), 2)         if total else "—"
        low_bmi   = round(min(bmi_vals), 2)          if total else "—"
        drop      = round(bmi_vals[-1] - bmi_vals[0], 2) if total > 1 else "—"

        def _update_stat(card, v, sub=""):
            inner = card.winfo_children()[0]
            lbls = [w for w in inner.winfo_children() if isinstance(w, ctk.CTkLabel)]
            if len(lbls) >= 1:
                lbls[0].configure(text=str(v))

        _update_stat(self._s1, drop)
        _update_stat(self._s2, avg_bmi)
        _update_stat(self._s3, high_bmi)
        _update_stat(self._s4, low_bmi)

        # rebuild chart
        if self._canvas_widget:
            self._canvas_widget.get_tk_widget().destroy()

        fig = Figure(figsize=(8, 2.8), dpi=96, facecolor="#FFFFFF")
        ax  = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFF")
        fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.18)

        ax.plot(range(len(dates)), bmi_vals,
                color=C["accent"], linewidth=2.2,
                marker="o", markersize=5, markerfacecolor="white",
                markeredgewidth=2, markeredgecolor=C["accent"])
        ax.axhline(24.9, color=C["accent2"], linewidth=1.2,
                   linestyle="--", alpha=0.7, label="Normal limit (24.9)")
        ax.fill_between(range(len(dates)), bmi_vals,
                        alpha=0.07, color=C["accent"])

        ax.set_xticks(range(len(dates)))
        try:
            ax.set_xticklabels(
                [d.strftime("%d %b") for d in dates],
                fontsize=8, color=C["text_m"], rotation=30, ha="right")
        except Exception:
            ax.set_xticklabels([str(d)[:10] for d in dates],
                                fontsize=8, color=C["text_m"])

        ax.tick_params(axis="y", labelsize=8, colors=C["text_m"])
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["left","bottom"]].set_color(C["card_bd"])
        ax.grid(axis="y", color=C["card_bd"], linewidth=0.6, linestyle="--")
        ax.set_ylabel("BMI", fontsize=9, color=C["text_m"])

        legend_patch = mpatches.Patch(color=C["accent2"], label="Normal limit (24.9)")
        ax.legend(handles=[legend_patch], fontsize=8,
                  framealpha=0, labelcolor=C["text_m"])

        self._canvas_widget = FigureCanvasTkAgg(fig, master=self._chart_frame)
        self._canvas_widget.draw()
        self._canvas_widget.get_tk_widget().pack(fill="both", expand=True)


# ════════════════════════════════════════════════════════════════════════════
#  Profile Page
# ════════════════════════════════════════════════════════════════════════════
class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=C["bg"])
        self.controller = controller
        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(outer, text="User Profile",
                     font=("Georgia", 20, "bold"),
                     text_color=C["text_h"]).pack(pady=(0, 4))
        ctk.CTkLabel(outer, text="Manage your personal details",
                     font=FONT_BODY, text_color=C["text_m"]).pack(pady=(0, 20))

        card = make_card(outer)
        card.pack()
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=34, pady=28)

        # avatar row
        av_row = ctk.CTkFrame(inner, fg_color="transparent")
        av_row.pack(fill="x", pady=(0, 22))
        av = ctk.CTkFrame(av_row, fg_color=C["accent"],
                           corner_radius=36, width=64, height=64)
        av.pack(side="left")
        av.pack_propagate(False)
        self._av = ctk.CTkLabel(av, text="G", font=("Georgia", 26, "bold"),
                                 text_color="white")
        self._av.place(relx=0.5, rely=0.5, anchor="center")

        av_info = ctk.CTkFrame(av_row, fg_color="transparent")
        av_info.pack(side="left", padx=(16, 0))
        self._av_name = ctk.CTkLabel(
            av_info, text="Gowtham",
            font=("Georgia", 15, "bold"), text_color=C["text_h"])
        self._av_name.pack(anchor="w")
        self._av_since = ctk.CTkLabel(
            av_info, text="Member since 2025",
            font=FONT_SMALL, text_color=C["text_m"])
        self._av_since.pack(anchor="w")

        divider(inner)

        # form
        def field(parent, label):
            ctk.CTkLabel(parent, text=label, font=FONT_LABEL,
                         text_color=C["text_m"]).pack(anchor="w", pady=(10, 2))
            e = ctk.CTkEntry(
                parent, width=340, height=40,
                fg_color=C["input_bg"], border_color=C["input_bd"],
                text_color=C["text_h"], font=FONT_BODY,
                corner_radius=10, border_width=1,
            )
            e.pack(fill="x")
            return e

        self.name_entry   = field(inner, "Full Name")
        self.age_entry    = field(inner, "Age")

        ctk.CTkLabel(inner, text="Gender", font=FONT_LABEL,
                     text_color=C["text_m"]).pack(anchor="w", pady=(10, 4))
        self.gender_var = ctk.StringVar(value="Male")
        g_row = ctk.CTkFrame(inner, fg_color="transparent")
        g_row.pack(fill="x")
        for val in ("Male", "Female", "Other"):
            ctk.CTkRadioButton(
                g_row, text=val, variable=self.gender_var, value=val,
                font=FONT_BODY, text_color=C["text_b"],
                fg_color=C["accent"],
            ).pack(side="left", padx=(0, 20))

        divider(inner)

        primary_btn(inner, "Save Profile ✓", self.save_profile, width=340).pack(fill="x")

        self.status_lbl = ctk.CTkLabel(
            inner, text="", font=FONT_BODY, text_color=C["accent2"])
        self.status_lbl.pack(pady=(8, 0))

    def refresh(self):
        profile = profile_collection.find_one() or {}
        name = profile.get("name", "")
        age  = str(profile.get("age", ""))
        gen  = profile.get("gender", "Male")

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, name)
        self.age_entry.delete(0, "end")
        self.age_entry.insert(0, age)
        self.gender_var.set(gen)

        if name:
            self._av.configure(text=name[0].upper())
            self._av_name.configure(text=name)
        self.status_lbl.configure(text="")

    def save_profile(self):
        try:
            name = self.name_entry.get().strip()
            age  = int(self.age_entry.get().strip())
            gen  = self.gender_var.get()
            if not name or age <= 0:
                raise ValueError

            profile_collection.delete_many({})
            profile_collection.insert_one({"name": name, "age": age, "gender": gen})

            self._av.configure(text=name[0].upper())
            self._av_name.configure(text=name)
            self.status_lbl.configure(text="✓ Profile saved successfully!")
            self.after(3000, lambda: self.status_lbl.configure(text=""))

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter a valid name and a positive integer for age.")


# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()