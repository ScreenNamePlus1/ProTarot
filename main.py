import random
import json
import os
from datetime import datetime, date
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.logger import Logger
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

# Set mystical dark background
Window.clearcolor = (0.05, 0.05, 0.15, 1)  # Deep purple-black

# Base path for Android compatibility
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Card definitions
suits = ["Wands", "Cups", "Swords", "Pentacles"]
ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
major_arcana = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers",
    "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death",
    "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

# Card meanings (expanded for reliability)
CARD_MEANINGS = {
    "The Fool": {"upright": "New beginnings, innocence, spontaneity", "reversed": "Recklessness, risk"},
    "The Magician": {"upright": "Manifestation, resourcefulness", "reversed": "Manipulation, poor planning"},
    "The High Priestess": {"upright": "Intuition, mystery", "reversed": "Secrets, disconnected intuition"},
    "The Empress": {"upright": "Abundance, nurturing", "reversed": "Creative block, dependency"},
    "The Emperor": {"upright": "Authority, structure", "reversed": "Control, rigidity"},
    "The Hierophant": {"upright": "Tradition, spiritual guidance", "reversed": "Rebellion, nonconformity"},
    "The Lovers": {"upright": "Love, harmony", "reversed": "Imbalance, misalignment"},
    "The Chariot": {"upright": "Determination, control", "reversed": "Lack of direction"},
    "Strength": {"upright": "Courage, inner strength", "reversed": "Self-doubt, weakness"},
    "The Hermit": {"upright": "Soul-searching, introspection", "reversed": "Isolation, withdrawal"},
    "Wheel of Fortune": {"upright": "Luck, cycles", "reversed": "Bad luck, resistance to change"},
    "Justice": {"upright": "Fairness, truth", "reversed": "Unfairness, dishonesty"},
    "The Hanged Man": {"upright": "Surrender, new perspective", "reversed": "Stagnation, delay"},
    "Death": {"upright": "Transformation, endings", "reversed": "Resistance to change"},
    "Temperance": {"upright": "Balance, moderation", "reversed": "Imbalance, excess"},
    "The Devil": {"upright": "Addiction, materialism", "reversed": "Freedom, detachment"},
    "The Tower": {"upright": "Sudden change, upheaval", "reversed": "Fear of change, avoidance"},
    "The Star": {"upright": "Hope, renewal", "reversed": "Lack of faith, despair"},
    "The Moon": {"upright": "Illusion, intuition", "reversed": "Confusion, fear"},
    "The Sun": {"upright": "Joy, success", "reversed": "Temporary depression, lack of clarity"},
    "Judgement": {"upright": "Rebirth, inner calling", "reversed": "Self-doubt, refusal to change"},
    "The World": {"upright": "Completion, fulfillment", "reversed": "Incompletion, lack of closure"},
}

# Spread definitions
SPREADS = {
    "Daily Guidance": {"cards": 1, "positions": ["Your guidance for today"], "description": "A single card to guide your day"},
    "Past-Present-Future": {"cards": 3, "positions": ["Past influences", "Present situation", "Future potential"], "description": "Classic three-card timeline reading"},
    "Love & Relationships": {"cards": 5, "positions": ["You in love", "Your partner", "The relationship", "Challenges", "Outcome"], "description": "Deep dive into your romantic life"},
    "Career Path": {"cards": 4, "positions": ["Current career", "Hidden talents", "Obstacles", "Next steps"], "description": "Navigate your professional journey"},
    "Celtic Cross": {"cards": 10, "positions": ["Present", "Challenge", "Distant Past", "Recent Past", "Possible Outcome", "Near Future", "Your Approach", "External Influences", "Hopes & Fears", "Final Outcome"], "description": "The most comprehensive tarot spread"},
    "Chakra Balance": {"cards": 7, "positions": ["Root Chakra", "Sacral Chakra", "Solar Plexus", "Heart Chakra", "Throat Chakra", "Third Eye", "Crown Chakra"], "description": "Align your spiritual energy centers"},
    "Essential Oil Guidance": {"cards": 3, "positions": ["Physical needs", "Emotional needs", "Spiritual needs"], "description": "Perfect for DoTerra consultations"}
}

# Create full deck
tarot_cards = [f"{rank} of {suit}" for suit in suits for rank in ranks] + major_arcana

# Custom button with mystical styling
class MysticalButton(Button):
    def __init__(self, text="", **kwargs):
        kwargs.setdefault('background_color', (0.2, 0.1, 0.4, 0.9))
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('bold', True)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        super().__init__(text=text, **kwargs)
        
        with self.canvas.before:
            Color(0.4, 0.2, 0.6, 0.8)
            self.border = Rectangle(pos=self.pos, size=self.size)
        with self.canvas.after:
            Color(0.15, 0.05, 0.25, 0.9)
            self.inner_rect = Rectangle(pos=(self.x + 2, self.y + 2), size=(self.width - 4, self.height - 4))
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size
        self.inner_rect.pos = (self.x + 2, self.y + 2)
        self.inner_rect.size = (self.width - 4, self.height - 4)

class ClientButton(MysticalButton):
    def __init__(self, client_name, is_active=False, **kwargs):
        self.client_name = client_name
        self.is_active = is_active
        kwargs['background_color'] = (0.3, 0.6, 0.2, 0.9) if is_active else (0.2, 0.1, 0.4, 0.9)
        super().__init__(text=f"👤 {client_name}", **kwargs)

class AnimatedButton(ButtonBehavior, FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_size = None
    
    def on_press(self):
        if not self.original_size:
            self.original_size = self.size[:]
        anim = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.1)
        anim.bind(on_complete=lambda *x: Animation(size=self.original_size, duration=0.1).start(self))
        anim.start(self)

class TarotCardImage(AnimatedButton, Image):
    def __init__(self, card_name, orientation, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.card_name = card_name
        self.orientation = orientation
        self.is_revealed = False
        self.app_instance = app_instance
        if orientation == "Reversed":
            self._apply_rotation()
    
    def _apply_rotation(self):
        self.canvas.before.clear()
        self.canvas.after.clear()
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=180, origin=(self.center_x, self.center_y))
        with self.canvas.after:
            PopMatrix()
        self.bind(pos=self._update_rotation, size=self._update_rotation)
    
    def _update_rotation(self, *args):
        if self.orientation == "Reversed":
            self.canvas.before.clear()
            self.canvas.after.clear()
            with self.canvas.before:
                PushMatrix()
                Rotate(angle=180, origin=(self.center_x, self.center_y))
            with self.canvas.after:
                PopMatrix()
    
    def on_press(self):
        super().on_press()

class ClientManager:
    def __init__(self):
        self.clients_file = os.path.join(BASE_PATH, "clients.json")
        self.clients = {}
        self.current_client_id = None
        self.load_clients()
        if not self.clients:
            self.add_client("Personal", "Your personal readings", is_default=True)
    
    def load_clients(self):
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r') as f:
                    data = json.load(f)
                    self.clients = data.get("clients", {})
                    self.current_client_id = data.get("current_client_id")
            else:
                Logger.info("No clients.json found, starting fresh")
        except Exception as e:
            Logger.error(f"Failed to load clients: {e}")
            self.clients = {}
            self.current_client_id = None
    
    def save_clients(self):
        try:
            os.makedirs(BASE_PATH, exist_ok=True)
            data = {"clients": self.clients, "current_client_id": self.current_client_id}
            with open(self.clients_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            Logger.error(f"Failed to save clients: {e}")
    
    def add_client(self, name, description="", is_default=False):
        if any(client["name"].lower() == name.lower() for client in self.clients.values()):
            Logger.warning(f"Duplicate client name: {name}")
            return None
        client_id = f"client_{len(self.clients) + 1}_{name.lower().replace(' ', '_')}"
        self.clients[client_id] = {
            "name": name,
            "description": description,
            "created_date": datetime.now().isoformat(),
            "readings": [],
            "journal": [],
            "settings": {"daily_limit": True, "preferred_spreads": []}
        }
        if is_default or not self.current_client_id:
            self.current_client_id = client_id
        self.save_clients()
        return client_id
    
    def get_current_client(self):
        return self.clients.get(self.current_client_id)
    
    def get_current_client_name(self):
        client = self.get_current_client()
        return client["name"] if client else "No Client"
    
    def switch_client(self, client_id):
        if client_id in self.clients:
            self.current_client_id = client_id
            self.save_clients()
            return True
        return False
    
    def add_reading_to_current_client(self, spread_name, cards, orientations, notes=""):
        if not self.current_client_id:
            return False
        reading = {
            "date": datetime.now().isoformat(),
            "spread": spread_name,
            "cards": cards,
            "orientations": orientations,
            "notes": notes
        }
        self.clients[self.current_client_id]["readings"].insert(0, reading)
        if len(self.clients[self.current_client_id]["readings"]) > 50:
            self.clients[self.current_client_id]["readings"] = self.clients[self.current_client_id]["readings"][:50]
        self.save_clients()
        return True
    
    def add_journal_entry_to_current_client(self, entry_text):
        if not self.current_client_id:
            return False
        entry = {"date": datetime.now().isoformat(), "text": entry_text}
        self.clients[self.current_client_id]["journal"].insert(0, entry)
        if len(self.clients[self.current_client_id]["journal"]) > 100:
            self.clients[self.current_client_id]["journal"] = self.clients[self.current_client_id]["journal"][:100]
        self.save_clients()
        return True
    
    def check_daily_reading_done(self, spread_name="Daily Guidance"):
        if not self.current_client_id:
            return False
        today = date.today().isoformat()
        readings = self.clients.get(self.current_client_id, {}).get("readings", [])
        return any(r.get("date", "").startswith(today) and r.get("spread") == spread_name for r in readings)
    
    def delete_client(self, client_id):
        if client_id in self.clients and len(self.clients) > 1:
            del self.clients[client_id]
            if self.current_client_id == client_id:
                self.current_client_id = list(self.clients.keys())[0]
            self.save_clients()
            return True
        return False

class PictureTarotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_manager = ClientManager()
        self.animation_enabled = True
        self.load_settings()
    
    def load_settings(self):
        try:
            settings_file = os.path.join(BASE_PATH, "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.animation_enabled = settings.get("animation_enabled", True)
        except Exception as e:
            Logger.error(f"Failed to load settings: {e}")
    
    def save_settings(self):
        try:
            settings = {"animation_enabled": self.animation_enabled}
            with open(os.path.join(BASE_PATH, "settings.json"), 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            Logger.error(f"Failed to save settings: {e}")
    
    def build(self):
        self.icon = os.path.join(BASE_PATH, "images", "AppIcons", "transparent.png")
        self.main_layout = FloatLayout()
        self.show_main_menu()
        return self.main_layout
    
    def get_image_base_path(self):
        possible_paths = [
            os.path.join(BASE_PATH, "images", "rider-waite-tarot"),
            os.path.join(BASE_PATH, "images"),
            BASE_PATH
        ]
        for path in possible_paths:
            if os.path.exists(os.path.join(path, "CardBacks.png")) or os.path.exists(os.path.join(path, "The_Fool.png")):
                return path
        Logger.warning("No valid image path found, using BASE_PATH")
        return BASE_PATH
    
    def get_card_image_path(self, card_name):
        base_path = self.get_image_base_path()
        formatted_name = card_name.replace(" ", "_")
        for ext in ['.png', '.jpg', '.jpeg']:
            image_path = os.path.join(base_path, f"{formatted_name}{ext}")
            if os.path.exists(image_path):
                return image_path
        Logger.warning(f"Card image not found for {card_name}, using card back")
        return self.get_card_back_path() or os.path.join(BASE_PATH, "images", "CardBacks.png")
    
    def get_card_back_path(self):
        base_path = self.get_image_base_path()
        for ext in ['.png', '.jpg', '.jpeg']:
            path = os.path.join(base_path, f"CardBacks{ext}")
            if os.path.exists(path):
                return path
        Logger.warning("Card back image not found")
        return None
    
    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        error_label = Label(
            text=message,
            font_size='16sp',
            color=(1, 0.8, 0.8, 1),
            size_hint_y=0.7,
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        close_btn = MysticalButton("OK", size_hint_y=0.3)
        content.add_widget(error_label)
        content.add_widget(close_btn)
        popup = Popup(title="Error", content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_main_menu(self):
        self.main_layout.clear_widgets()
        with self.main_layout.canvas.before:
            Color(0.05, 0.05, 0.15, 1)
            Rectangle(pos=(0, 0), size=Window.size)
        
        container = BoxLayout(
            orientation='vertical', padding=20, spacing=15,
            size_hint=(0.95, 0.95), pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        client_header = BoxLayout(size_hint_y=0.15, spacing=10)
        current_client = self.client_manager.get_current_client_name()
        client_label = Label(
            text=f"👤 Client: {current_client}", font_size='18sp',
            bold=True, color=(0.8, 1, 0.8, 1), size_hint_x=0.6
        )
        switch_btn = MysticalButton("Switch Client", size_hint_x=0.2)
        switch_btn.bind(on_press=lambda x: self.show_client_manager())
        add_client_btn = MysticalButton("+ Add Client", size_hint_x=0.2)
        add_client_btn.bind(on_press=lambda x: self.add_new_client())
        client_header.add_widget(client_label)
        client_header.add_widget(switch_btn)
        client_header.add_widget(add_client_btn)
        container.add_widget(client_header)
        
        title = Label(
            text="✦ PICTURE TAROT ✦", font_size='32sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.12
        )
        container.add_widget(title)
        
        daily_drawn = self.client_manager.check_daily_reading_done("Daily Guidance")
        menu_options = [
            ("🔮 Daily Card", lambda x: self.start_daily_reading(), not daily_drawn),
            ("📚 Tarot Spreads", lambda x: self.show_spreads_menu(), True),
            ("📖 Reading History", lambda x: self.show_history(), True),
            ("✍️ Client Journal", lambda x: self.show_journal(), True),
            ("⚙️ Settings", lambda x: self.show_settings(), True)
        ]
        
        for text, callback, enabled in menu_options:
            display_text = text if enabled else f"{text} (Done Today)" if "Daily" in text else text
            btn = MysticalButton(display_text, size_hint_y=0.12)
            if enabled:
                btn.bind(on_press=callback)
            else:
                btn.color = (0.5, 0.5, 0.5, 1)
            container.add_widget(btn)
        
        self.main_layout.add_widget(container)
    
    def show_client_manager(self):
        self.main_layout.clear_widgets()
        container = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        header = BoxLayout(size_hint_y=0.1)
        back_btn = MysticalButton("← Back", size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        title = Label(
            text="👥 Client Manager", font_size='24sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7
        )
        header.add_widget(back_btn)
        header.add_widget(title)
        container.add_widget(header)
        
        scroll = ScrollView()
        client_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        client_container.bind(minimum_height=client_container.setter('height'))
        
        for client_id, client_data in self.client_manager.clients.items():
            is_active = client_id == self.client_manager.current_client_id
            client_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)
            client_btn = ClientButton(client_data["name"], is_active=is_active, size_hint_x=0.6)
            if not is_active:
                client_btn.bind(on_press=lambda btn, cid=client_id: self.switch_to_client(cid))
            readings_count = len(client_data["readings"])
            journal_count = len(client_data["journal"])
            info_label = Label(
                text=f"📚 {readings_count} readings\n📝 {journal_count} entries",
                font_size='12sp', color=(0.8, 0.8, 0.8, 1), size_hint_x=0.3
            )
            delete_btn = None
            if len(self.client_manager.clients) > 1:
                delete_btn = MysticalButton("🗑️", size_hint_x=0.1)
                delete_btn.bind(on_press=lambda btn, cid=client_id: self.confirm_delete_client(cid))
            client_box.add_widget(client_btn)
            client_box.add_widget(info_label)
            if delete_btn:
                client_box.add_widget(delete_btn)
            client_container.add_widget(client_box)
        
        scroll.add_widget(client_container)
        container.add_widget(scroll)
        
        add_btn = MysticalButton("➕ Add New Client", size_hint_y=0.1)
        add_btn.bind(on_press=lambda x: self.add_new_client())
        container.add_widget(add_btn)
        
        self.main_layout.add_widget(container)
    
    def switch_to_client(self, client_id):
        if self.client_manager.switch_client(client_id):
            self.show_main_menu()
    
    def add_new_client(self):
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        title_label = Label(
            text="👤 Add New Client", font_size='20sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.2
        )
        name_input = TextInput(
            hint_text="Client name (e.g., Sarah Johnson)", multiline=False,
            size_hint_y=0.2, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1)
        )
        desc_input = TextInput(
            hint_text="Description (e.g., DoTerra consultation client)", multiline=True,
            size_hint_y=0.4, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1)
        )
        buttons = BoxLayout(size_hint_y=0.2, spacing=10)
        add_btn = MysticalButton("✅ Add Client")
        cancel_btn = MysticalButton("❌ Cancel")
        buttons.add_widget(add_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(title_label)
        content.add_widget(name_input)
        content.add_widget(desc_input)
        content.add_widget(buttons)
        
        popup = Popup(title="", content=content, size_hint=(0.9, 0.7), background_color=(0.05, 0.05, 0.15, 0.95))
        
        def add_client(*args):
            name = name_input.text.strip()
            if not name:
                self.show_error_popup("Client name cannot be empty!")
                return
            if any(client["name"].lower() == name.lower() for client in self.client_manager.clients.values()):
                self.show_error_popup("Client name already exists!")
                return
            desc = desc_input.text.strip()
            client_id = self.client_manager.add_client(name, desc)
            if client_id:
                self.client_manager.switch_client(client_id)
                popup.dismiss()
                self.show_client_manager()
            else:
                self.show_error_popup("Failed to add client.")
        
        add_btn.bind(on_press=add_client)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def confirm_delete_client(self, client_id):
        client_name = self.client_manager.clients[client_id]["name"]
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        warning_label = Label(
            text=f"⚠️ Delete Client?\n\n'{client_name}'\n\nThis will permanently delete all readings and journal entries.",
            font_size='16sp', color=(1, 1, 1, 1), halign='center', size_hint_y=0.7
        )
        warning_label.bind(size=warning_label.setter('text_size'))
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        delete_btn = MysticalButton("🗑️ Delete", background_color=(0.8, 0.2, 0.2, 0.9))
        cancel_btn = MysticalButton("❌ Cancel")
        buttons.add_widget(delete_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(warning_label)
        content.add_widget(buttons)
        popup = Popup(title="Confirm Deletion", content=content, size_hint=(0.8, 0.5))
        
        def delete_client(*args):
            self.client_manager.delete_client(client_id)
            popup.dismiss()
            self.show_client_manager()
        
        delete_btn.bind(on_press=delete_client)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def start_daily_reading(self):
        if not self.client_manager.current_client_id:
            self.show_error_popup("Please select a client first!")
            return
        self.start_reading(1, "Daily Guidance", special=True)
    
    def show_spreads_menu(self):
        self.main_layout.clear_widgets()
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.25)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        title = Label(
            text="Choose Your Spread", font_size='20sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.5
        )
        client_info = Label(
            text=f"👤 {self.client_manager.get_current_client_name()}",
            font_size='14sp', color=(0.8, 1, 0.8, 1), size_hint_x=0.25
        )
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(client_info)
        container.add_widget(header)
        
        scroll = ScrollView()
        spread_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        spread_container.bind(minimum_height=spread_container.setter('height'))
        
        for spread_name, spread_info in SPREADS.items():
            if spread_name == "Daily Guidance":
                continue
            spread_btn = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=10)
            with spread_btn.canvas.before:
                Color(0.15, 0.1, 0.25, 0.7)
                Rectangle(pos=spread_btn.pos, size=spread_btn.size)
            name_label = Label(
                text=f"✨ {spread_name} ({spread_info['cards']} cards)",
                font_size='18sp', bold=True, color=(1, 1, 1, 1), size_hint_y=0.6
            )
            desc_label = Label(
                text=spread_info['description'], font_size='14sp',
                color=(0.9, 0.9, 0.9, 1), size_hint_y=0.4
            )
            spread_btn.add_widget(name_label)
            spread_btn.add_widget(desc_label)
            clickable = AnimatedButton(size_hint_y=None, height=120)
            clickable.add_widget(spread_btn)
            clickable.bind(on_press=lambda btn, name=spread_name, info=spread_info: self.start_reading(info['cards'], name))
            spread_container.add_widget(clickable)
        
        scroll.add_widget(spread_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)
    
    def start_reading(self, num_cards, spread_name, special=False):
        if not self.client_manager.current_client_id:
            self.show_error_popup("Please select a client first!")
            return
        try:
            self.current_cards = random.sample(tarot_cards, num_cards)
            self.current_orientations = [random.choice(["Upright", "Reversed"]) for _ in range(num_cards)]
            self.current_spread_name = spread_name
            self.current_spread_info = SPREADS.get(spread_name, {"positions": [f"Card {i+1}" for i in range(num_cards)]})
            self.card_index = 0
            self.is_special = special
            self.show_card_with_position()
        except Exception as e:
            Logger.error(f"Failed to start reading: {e}")
            self.show_error_popup("Failed to start reading.")
    
    def show_card_with_position(self):
        self.main_layout.clear_widgets()
        card_name = self.current_cards[self.card_index]
        orientation = self.current_orientations[self.card_index]
        positions = self.current_spread_info["positions"]
        position = positions[self.card_index] if self.card_index < len(positions) else f"Card {self.card_index + 1}"
        
        container = BoxLayout(
            orientation='vertical', padding=30, spacing=15,
            size_hint=(0.95, 0.95), pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        client_info = Label(
            text=f"👤 Reading for: {self.client_manager.get_current_client_name()}",
            font_size='14sp', color=(0.8, 1, 0.8, 1), size_hint_y=0.06, halign='center'
        )
        client_info.bind(size=client_info.setter('text_size'))
        progress_label = Label(
            text=f"✨ {self.current_spread_name} ✨\nCard {self.card_index + 1} of {len(self.current_cards)}",
            font_size='16sp', color=(1, 1, 0.8, 1), size_hint_y=0.1, halign='center'
        )
        progress_label.bind(size=progress_label.setter('text_size'))
        position_label = Label(
            text=f"Position: {position}", font_size='18sp',
            bold=True, color=(0.9, 0.9, 1, 1), size_hint_y=0.08, halign='center'
        )
        position_label.bind(size=position_label.setter('text_size'))
        
        card_back_path = self.get_card_back_path()
        if not card_back_path:
            Logger.error("Card back path not found")
            self.show_error_popup("Card images are missing!")
            return
        self.current_card_widget = TarotCardImage(
            card_name=card_name, orientation=orientation, app_instance=self,
            source=card_back_path, allow_stretch=True, keep_ratio=True, size_hint=(1, 0.61)
        )
        self.current_card_widget.bind(on_press=self.reveal_card_with_meaning)
        
        instruction_label = Label(
            text="🎭 Tap the card to reveal your destiny 🎭",
            font_size='16sp', color=(1, 1, 0.8, 1), size_hint_y=0.15, halign='center'
        )
        instruction_label.bind(size=instruction_label.setter('text_size'))
        
        container.add_widget(client_info)
        container.add_widget(progress_label)
        container.add_widget(position_label)
        container.add_widget(self.current_card_widget)
        container.add_widget(instruction_label)
        self.main_layout.add_widget(container)
    
    def reveal_card_with_meaning(self, instance):
        if instance.is_revealed:
            self.next_card_or_complete()
            return
        card_image_path = self.get_card_image_path(instance.card_name)
        if card_image_path:
            instance.source = card_image_path
            instance.is_revealed = True
            self.show_card_meaning_popup(instance.card_name, instance.orientation)
        else:
            Logger.error(f"Failed to load card image: {instance.card_name}")
            self.show_error_popup("Failed to load card image.")
    
    def show_card_meaning_popup(self, card_name, orientation):
        meaning_key = orientation.lower()
        meaning = CARD_MEANINGS.get(card_name, {}).get(meaning_key, f"Meditate on the symbolism of {card_name} in {orientation.lower()} position.")
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        title = Label(
            text=f"{card_name}\n({orientation})", font_size='20sp',
            bold=True, size_hint_y=0.3, halign='center'
        )
        title.bind(size=title.setter('text_size'))
        meaning_label = Label(
            text=meaning, font_size='16sp', size_hint_y=0.5, halign='center', valign='middle'
        )
        meaning_label.bind(size=meaning_label.setter('text_size'))
        close_btn = MysticalButton("Continue", size_hint_y=0.2)
        content.add_widget(title)
        content.add_widget(meaning_label)
        content.add_widget(close_btn)
        popup = Popup(title="Card Revealed", content=content, size_hint=(0.9, 0.7), background_color=(0.1, 0.05, 0.2, 0.95))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def next_card_or_complete(self):
        self.card_index += 1
        if self.card_index >= len(self.current_cards):
            self.complete_reading()
        else:
            self.show_card_with_position()
    
    def complete_reading(self):
        self.client_manager.add_reading_to_current_client(
            self.current_spread_name, self.current_cards, self.current_orientations
        )
        self.show_reading_complete()
    
    def show_reading_complete(self):
        self.main_layout.clear_widgets()
        container = BoxLayout(orientation='vertical', padding=30, spacing=20)
        client_name = self.client_manager.get_current_client_name()
        title = Label(
            text=f"🌟 Reading Complete! 🌟\n\nReading for {client_name} has been saved",
            font_size='24sp', bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.25, halign='center'
        )
        title.bind(size=title.setter('text_size'))
        message = Label(
            text=f"Your {self.current_spread_name} reading for {client_name} has been saved to their personal journal.\n\nTake time to reflect on the messages revealed.",
            font_size='16sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=0.25, halign='center'
        )
        message.bind(size=message.setter('text_size'))
        options_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        journal_btn = MysticalButton("📝 Add to Client Journal")
        journal_btn.bind(on_press=lambda x: self.quick_journal_entry())
        history_btn = MysticalButton("📚 View Client History")
        history_btn.bind(on_press=lambda x: self.show_history())
        switch_btn = MysticalButton("👥 Switch Client")
        switch_btn.bind(on_press=lambda x: self.show_client_manager())
        new_reading_btn = MysticalButton("🔮 New Reading")
        new_reading_btn.bind(on_press=lambda x: self.show_spreads_menu())
        home_btn = MysticalButton("🏠 Home")
        home_btn.bind(on_press=lambda x: self.show_main_menu())
        options_layout.add_widget(journal_btn)
        options_layout.add_widget(history_btn)
        options_layout.add_widget(switch_btn)
        options_layout.add_widget(new_reading_btn)
        options_layout.add_widget(home_btn)
        container.add_widget(title)
        container.add_widget(message)
        container.add_widget(options_layout)
        self.main_layout.add_widget(container)
    
    def quick_journal_entry(self):
        client_name = self.client_manager.get_current_client_name()
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        title_label = Label(
            text=f"📝 Journal Entry for {client_name}", font_size='18sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.15
        )
        text_input = TextInput(
            hint_text=f"Reflect on {client_name}'s reading...", multiline=True,
            size_hint_y=0.55, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1)
        )
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        save_btn = MysticalButton("Save")
        cancel_btn = MysticalButton("Cancel")
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(title_label)
        content.add_widget(text_input)
        content.add_widget(buttons)
        popup = Popup(title="", content=content, size_hint=(0.9, 0.6))
        
        def save_entry(*args):
            if text_input.text.strip():
                self.client_manager.add_journal_entry_to_current_client(text_input.text.strip())
            popup.dismiss()
        
        save_btn.bind(on_press=save_entry)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_history(self):
        self.main_layout.clear_widgets()
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.25)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        title = Label(
            text="Reading History", font_size='20sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.5
        )
        client_info = Label(
            text=f"👤 {self.client_manager.get_current_client_name()}",
            font_size='14sp', color=(0.8, 1, 0.8, 1), size_hint_x=0.25
        )
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(client_info)
        container.add_widget(header)
        
        scroll = ScrollView()
        history_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        history_container.bind(minimum_height=history_container.setter('height'))
        current_client = self.client_manager.get_current_client()
        readings = current_client["readings"] if current_client else []
        
        if not readings:
            no_history = Label(
                text=f"No readings yet for {self.client_manager.get_current_client_name()}.\nStart their tarot journey!",
                font_size='16sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=100, halign='center'
            )
            no_history.bind(size=no_history.setter('text_size'))
            history_container.add_widget(no_history)
        else:
            for reading in readings:
                date_str = datetime.fromisoformat(reading["date"]).strftime("%B %d, %Y at %I:%M %p")
                item = Label(
                    text=f"🔮 {reading['spread']}\n📅 {date_str}\n🃏 {len(reading['cards'])} cards drawn",
                    font_size='14sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=80, halign='left'
                )
                item.bind(size=item.setter('text_size'))
                history_container.add_widget(item)
        
        scroll.add_widget(history_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)
    
    def show_journal(self):
        self.main_layout.clear_widgets()
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.2)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        client_name = self.client_manager.get_current_client_name()
        title = Label(
            text=f"📖 {client_name}'s Journal", font_size='18sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.6
        )
        add_btn = MysticalButton("+ New Entry", size_hint_x=0.2)
        add_btn.bind(on_press=lambda x: self.add_journal_entry())
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_btn)
        container.add_widget(header)
        
        scroll = ScrollView()
        journal_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        journal_container.bind(minimum_height=journal_container.setter('height'))
        current_client = self.client_manager.get_current_client()
        entries = current_client["journal"] if current_client else []
        
        if not entries:
            no_entries = Label(
                text=f"📝 No journal entries yet for {client_name}.\nStart documenting their tarot insights!",
                font_size='16sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=100, halign='center'
            )
            no_entries.bind(size=no_entries.setter('text_size'))
            journal_container.add_widget(no_entries)
        else:
            for entry in entries:
                date_str = datetime.fromisoformat(entry["date"]).strftime("%B %d, %Y")
                entry_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=15, spacing=5)
                with entry_box.canvas.before:
                    Color(0.15, 0.1, 0.25, 0.5)
                    Rectangle(pos=entry_box.pos, size=entry_box.size)
                entry_box.bind(pos=self._update_entry_bg, size=self._update_entry_bg)
                date_label = Label(
                    text=f"✨ {date_str}", font_size='14sp',
                    bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.3, halign='left'
                )
                date_label.bind(size=date_label.setter('text_size'))
                text_label = Label(
                    text=entry["text"][:150] + ("..." if len(entry["text"]) > 150 else ""),
                    font_size='13sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=0.7, halign='left', valign='top'
                )
                text_label.bind(size=text_label.setter('text_size'))
                entry_box.add_widget(date_label)
                entry_box.add_widget(text_label)
                journal_container.add_widget(entry_box)
        
        scroll.add_widget(journal_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)
    
    def _update_entry_bg(self, instance, *args):
        if hasattr(instance, 'canvas') and instance.canvas.before:
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.15, 0.1, 0.25, 0.5)
                Rectangle(pos=instance.pos, size=instance.size)
    
    def add_journal_entry(self):
        client_name = self.client_manager.get_current_client_name()
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        title_label = Label(
            text=f"✍️ New Entry for {client_name}", font_size='20sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.15
        )
        text_input = TextInput(
            hint_text=f"Share insights about {client_name}'s reading...", multiline=True,
            size_hint_y=0.6, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1)
        )
        buttons = BoxLayout(size_hint_y=0.25, spacing=10)
        save_btn = MysticalButton("💾 Save Entry")
        cancel_btn = MysticalButton("❌ Cancel")
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(title_label)
        content.add_widget(text_input)
        content.add_widget(buttons)
        popup = Popup(title="", content=content, size_hint=(0.9, 0.8), background_color=(0.05, 0.05, 0.15, 0.95))
        
        def save_entry(*args):
            if text_input.text.strip():
                self.client_manager.add_journal_entry_to_current_client(text_input.text.strip())
                popup.dismiss()
                self.show_journal()
        
        save_btn.bind(on_press=save_entry)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_settings(self):
        self.main_layout.clear_widgets()
        container = BoxLayout(orientation='vertical', padding=25, spacing=20)
        header = BoxLayout(size_hint_y=0.1)
        back_btn = MysticalButton("← Back", size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        title = Label(
            text="⚙️ Settings", font_size='24sp',
            bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7
        )
        header.add_widget(back_btn)
        header.add_widget(title)
        container.add_widget(header)
        
        settings_container = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.6)
        anim_box = BoxLayout(size_hint_y=None, height=60, spacing=15)
        anim_label = Label(
            text="✨ Animations", font_size='18sp',
            color=(1, 1, 1, 1), size_hint_x=0.7, halign='left'
        )
        anim_label.bind(size=anim_label.setter('text_size'))
        anim_switch = Switch(active=self.animation_enabled, size_hint_x=0.3)
        anim_switch.bind(active=self.toggle_animations)
        anim_box.add_widget(anim_label)
        anim_box.add_widget(anim_switch)
        
        settings_container.add_widget(anim_box)
        
        client_mgmt_btn = MysticalButton("👥 Manage Clients", size_hint_y=None, height=60)
        client_mgmt_btn.bind(on_press=lambda x: self.show_client_manager())
        settings_container.add_widget(client_mgmt_btn)
        
        info_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        client_count = len(self.client_manager.clients)
        current_client = self.client_manager.get_current_client_name()
        app_info = Label(
            text=f"📱 Picture Tarot v1.0\nMulti-Client Edition ✨\n\n👥 {client_count} clients managed\n🔮 Current: {current_client}\n\nPerfect for practitioners serving multiple clients",
            font_size='14sp', color=(0.7, 0.7, 0.8, 1), halign='center'
        )
        app_info.bind(size=app_info.setter('text_size'))
        info_container.add_widget(app_info)
        
        container.add_widget(settings_container)
        container.add_widget(info_container)
        self.main_layout.add_widget(container)
    
    def toggle_animations(self, instance, value):
        self.animation_enabled = value
        self.save_settings()
        Logger.info(f"Animations {'enabled' if value else 'disabled'}")

if __name__ == '__main__':
    Logger.info("Starting PictureTarotApp")
    try:
        PictureTarotApp().run()
    except Exception as e:
        Logger.error(f"Application crashed: {e}")