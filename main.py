import random
import json
import os
import sys
import logging
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

# Configure logging to Downloads folder
def setup_logging():
    """Set up logging to save to the Downloads folder with a timestamped filename"""
    try:
        # Determine Downloads folder path
        if sys.platform == 'win32':
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        elif sys.platform == 'darwin':  # macOS
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        elif sys.platform == 'linux':
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            # Android or other platforms
            try:
                from android.storage import app_storage_path
                downloads_path = os.path.join(app_storage_path(), 'Download')
            except ImportError:
                # Fallback to user data dir or home directory
                downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        # Ensure Downloads directory exists
        os.makedirs(downloads_path, exist_ok=True)

        # Create timestamped log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(downloads_path, f"PictureTarotApp_{timestamp}.log")

        # Configure logging
        logging.basicConfig(
            filename=log_filename,
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Also log to Kivy Logger for compatibility
        kivy_handler = KivyLoggerHandler()
        logging.getLogger().addHandler(kivy_handler)

        logging.info(f"Logging initialized. Log file saved to: {log_filename}")
        return log_filename

    except Exception as e:
        Logger.error(f"Failed to set up logging: {e}")
        return None

# Custom handler to integrate with Kivy Logger
class KivyLoggerHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        if record.levelno >= logging.ERROR:
            Logger.error(log_entry)
        elif record.levelno >= logging.WARNING:
            Logger.warning(log_entry)
        elif record.levelno >= logging.INFO:
            Logger.info(log_entry)
        else:
            Logger.debug(log_entry)

# Initialize logging at startup
log_file_path = setup_logging()

# Base path for Android compatibility
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):  # PyInstaller compatibility
    BASE_PATH = sys._MEIPASS

# Card definitions (unchanged)
suits = ["Wands", "Cups", "Swords", "Pentacles"]
ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
major_arcana = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers",
    "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death",
    "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

# Card meanings (unchanged)
CARD_MEANINGS = {
    # Major Arcana
    "The Fool": {"upright": "New beginnings, innocence, spontaneity, free spirit", "reversed": "Recklessness, taken advantage of, inconsideration"},
    # ... (rest of the card meanings unchanged)
}

# Spread definitions (unchanged)
SPREADS = {
    "Daily Guidance": {
        "cards": 1, 
        "positions": ["Your guidance for today"], 
        "description": "A single card to guide your day"
    },
    # ... (rest of the spreads unchanged)
}

# Create full deck (unchanged)
tarot_cards = [f"{rank} of {suit}" for suit in suits for rank in ranks] + major_arcana

# Custom button with improved mystical styling (unchanged)
class MysticalButton(Button):
    def __init__(self, text="", **kwargs):
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('bold', True)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        super().__init__(text=text, **kwargs)

        with self.canvas.before:
            Color(0.4, 0.2, 0.6, 0.8)
            self.border = Rectangle(pos=self.pos, size=self.size)
            Color(0.15, 0.05, 0.25, 0.9)
            self.inner_rect = Rectangle(pos=(self.x + 2, self.y + 2), size=(self.width - 4, self.height - 4))

        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size
        self.inner_rect.pos = (self.x + 2, self.y + 2)
        self.inner_rect.size = (self.width - 4, self.height - 4)

# Rest of the classes (ClientButton, AnimatedButton, TarotCardImage, ClientManager, PictureTarotApp) remain unchanged
# except for minor logging adjustments

class ClientButton(MysticalButton):
    def __init__(self, client_name, is_active=False, **kwargs):
        self.client_name = client_name
        self.is_active = is_active
        super().__init__(text=f"👤 {client_name}", **kwargs)

        with self.canvas.before:
            if is_active:
                Color(0.3, 0.6, 0.2, 0.9)
            else:
                Color(0.4, 0.2, 0.6, 0.8)
            self.border = Rectangle(pos=self.pos, size=self.size)

class AnimatedButton(ButtonBehavior, FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_size = None
        self.animation_running = False

    def on_press(self):
        if self.animation_running:
            return

        if not self.original_size:
            self.original_size = self.size[:]

        self.animation_running = True
        anim1 = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.1)
        anim2 = Animation(size=self.original_size, duration=0.1)

        def reset_animation(*args):
            self.animation_running = False

        anim2.bind(on_complete=reset_animation)
        anim1.bind(on_complete=lambda *x: anim2.start(self))
        anim1.start(self)

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

class ClientManager:
    def __init__(self):
        try:
            if hasattr(App.get_running_app(), 'user_data_dir'):
                data_dir = App.get_running_app().user_data_dir
            else:
                data_dir = BASE_PATH
        except:
            data_dir = BASE_PATH

        self.clients_file = os.path.join(data_dir, "clients.json")
        self.clients = {}
        self.current_client_id = None
        self.load_clients()
        logging.info(f"ClientManager initialized with data dir: {data_dir}")

        if not self.clients:
            self.add_client("Personal", "Your personal readings", is_default=True)

    def load_clients(self):
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.clients = data.get("clients", {})
                    self.current_client_id = data.get("current_client_id")
                logging.info(f"Loaded {len(self.clients)} clients from {self.clients_file}")
            else:
                logging.info("No clients.json found, starting fresh")
                self.clients = {}
                self.current_client_id = None
        except Exception as e:
            logging.error(f"Failed to load clients: {e}")
            self.clients = {}
            self.current_client_id = None

    def save_clients(self):
        try:
            os.makedirs(os.path.dirname(self.clients_file), exist_ok=True)
            data = {
                "clients": self.clients, 
                "current_client_id": self.current_client_id
            }
            temp_file = self.clients_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.rename(temp_file, self.clients_file)
            logging.info("Clients saved successfully")
        except Exception as e:
            logging.error(f"Failed to save clients: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def add_client(self, name, description="", is_default=False):
        if not name or not name.strip():
            logging.warning("Cannot add client with empty name")
            return None

        name = name.strip()
        if any(client["name"].lower() == name.lower() for client in self.clients.values()):
            logging.warning(f"Client with name '{name}' already exists")
            return None

        client_id = f"client_{len(self.clients) + 1}_{name.lower().replace(' ', '_').replace('-', '_')}"
        counter = 1
        original_id = client_id
        while client_id in self.clients:
            client_id = f"{original_id}_{counter}"
            counter += 1

        self.clients[client_id] = {
            "name": name,
            "description": description.strip(),
            "created_date": datetime.now().isoformat(),
            "readings": [],
            "journal": [],
            "settings": {
                "daily_limit": True, 
                "preferred_spreads": [],
                "notes": ""
            }
        }

        if is_default or not self.current_client_id:
            self.current_client_id = client_id

        self.save_clients()
        logging.info(f"Added client: {name} (ID: {client_id})")
        return client_id

    def get_current_client(self):
        if not self.current_client_id or self.current_client_id not in self.clients:
            return None
        return self.clients[self.current_client_id]

    def get_current_client_name(self):
        client = self.get_current_client()
        return client["name"] if client else "No Client Selected"

    def switch_client(self, client_id):
        if client_id in self.clients:
            self.current_client_id = client_id
            self.save_clients()
            logging.info(f"Switched to client: {self.clients[client_id]['name']}")
            return True
        logging.warning(f"Cannot switch to non-existent client: {client_id}")
        return False

    def add_reading_to_current_client(self, spread_name, cards, orientations, notes=""):
        if not self.current_client_id:
            logging.warning("No current client selected for reading")
            return False

        if not cards or not orientations or len(cards) != len(orientations):
            logging.warning("Invalid cards/orientations data for reading")
            return False

        reading = {
            "date": datetime.now().isoformat(),
            "spread": spread_name,
            "cards": cards,
            "orientations": orientations,
            "notes": notes.strip()
        }

        self.clients[self.current_client_id]["readings"].insert(0, reading)
        if len(self.clients[self.current_client_id]["readings"]) > 100:
            self.clients[self.current_client_id]["readings"] = self.clients[self.current_client_id]["readings"][:100]

        self.save_clients()
        logging.info(f"Added {spread_name} reading with {len(cards)} cards")
        return True

    def add_journal_entry_to_current_client(self, entry_text):
        if not self.current_client_id:
            logging.warning("No current client selected for journal entry")
            return False

        if not entry_text or not entry_text.strip():
            logging.warning("Cannot add empty journal entry")
            return False

        entry = {
            "date": datetime.now().isoformat(), 
            "text": entry_text.strip()
        }

        self.clients[self.current_client_id]["journal"].insert(0, entry)
        if len(self.clients[self.current_client_id]["journal"]) > 200:
            self.clients[self.current_client_id]["journal"] = self.clients[self.current_client_id]["journal"][:200]

        self.save_clients()
        logging.info("Added journal entry")
        return True

    def check_daily_reading_done(self, spread_name="Daily Guidance"):
        if not self.current_client_id:
            return False

        today = date.today().isoformat()
        readings = self.clients.get(self.current_client_id, {}).get("readings", [])
        return any(
            r.get("date", "").startswith(today) and r.get("spread") == spread_name 
            for r in readings
        )

    def delete_client(self, client_id):
        if client_id not in self.clients:
            logging.warning(f"Cannot delete non-existent client: {client_id}")
            return False

        if len(self.clients) <= 1:
            logging.warning("Cannot delete the last remaining client")
            return False

        client_name = self.clients[client_id]["name"]
        del self.clients[client_id]
        if self.current_client_id == client_id:
            self.current_client_id = list(self.clients.keys())[0]

        self.save_clients()
        logging.info(f"Deleted client: {client_name}")
        return True

class PictureTarotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_manager = ClientManager()
        self.animation_enabled = True
        self.load_settings()
        self.current_cards = []
        self.current_orientations = []
        self.current_spread_name = ""
        self.current_spread_info = {}
        self.card_index = 0
        self.is_special = False
        self.current_card_widget = None
        logging.info("PictureTarotApp initialized")

    def load_settings(self):
        try:
            settings_file = os.path.join(self.user_data_dir, "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.animation_enabled = settings.get("animation_enabled", True)
                logging.info("Settings loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            self.animation_enabled = True

    def save_settings(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            settings = {"animation_enabled": self.animation_enabled}
            settings_file = os.path.join(self.user_data_dir, "settings.json")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            logging.info("Settings saved successfully")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def build(self):
        icon_path = os.path.join(BASE_PATH, "images", "AppIcons", "transparent.png")
        if os.path.exists(icon_path):
            self.icon = icon_path

        self.title = "Picture Tarot - Multi-Client Edition"
        self.main_layout = FloatLayout()
        self.show_main_menu()
        logging.info("App built and main menu displayed")
        return self.main_layout

    def get_image_base_path(self):
        possible_paths = [
            os.path.join(BASE_PATH, "images", "rider-waite-tarot"),
            os.path.join(BASE_PATH, "images", "tarot"),
            os.path.join(BASE_PATH, "images"),
            os.path.join(BASE_PATH, "assets", "images"),
            BASE_PATH
        ]

        for path in possible_paths:
            test_files = ["CardBacks.png", "The_Fool.png", "cardback.png", "the_fool.png"]
            if any(os.path.exists(os.path.join(path, test_file)) for test_file in test_files):
                logging.info(f"Found card images at: {path}")
                return path

        logging.warning("No valid image path found, using BASE_PATH")
        return BASE_PATH

    def get_card_image_path(self, card_name):
        base_path = self.get_image_base_path()
        naming_variants = [
            card_name.replace(" ", "_"),
            card_name.replace(" ", "_").lower(),
            card_name.replace(" ", "-"),
            card_name.replace(" ", "-").lower(),
            card_name.replace(" ", ""),
            card_name.replace(" ", "").lower()
        ]

        for variant in naming_variants:
            for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                image_path = os.path.join(base_path, f"{variant}{ext}")
                if os.path.exists(image_path):
                    logging.debug(f"Found image for {card_name}: {image_path}")
                    return image_path

        logging.warning(f"Card image not found for '{card_name}', using card back")
        return self.get_card_back_path()

    def get_card_back_path(self):
        base_path = self.get_image_base_path()
        back_names = ["CardBacks", "cardback", "card_back", "back"]

        for name in back_names:
            for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                path = os.path.join(base_path, f"{name}{ext}")
                if os.path.exists(path):
                    logging.debug(f"Found card back image: {path}")
                    return path

        logging.warning("Card back image not found")
        return None

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        error_label = Label(
            text=message,
            font_size='16sp',
            color=(1, 0.8, 0.8, 1),
            size_hint_y=0.7,
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        error_label.bind(size=error_label.setter('text_size'))
        close_btn = MysticalButton("OK", size_hint_y=0.3)
        content.add_widget(error_label)
        content.add_widget(close_btn)
        popup = Popup(
            title="⚠️ Error", 
            content=content, 
            size_hint=(0.8, 0.4),
            background_color=(0.1, 0.05, 0.2, 0.95)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        logging.error(f"Displayed error popup: {message}")

    def show_main_menu(self):
        # ... (unchanged, but add logging)
        self.main_layout.clear_widgets()
        # ... (rest of the method unchanged)
        logging.info("Displayed main menu")

    def show_client_manager(self):
        # ... (unchanged, but add logging)
        self.main_layout.clear_widgets()
        # ... (rest of the method unchanged)
        logging.info("Displayed client manager")

    def switch_to_client(self, client_id):
        if self.client_manager.switch_client(client_id):
            self.show_main_menu()
        else:
            self.show_error_popup("Failed to switch client!")
        logging.info(f"Attempted to switch to client ID: {client_id}")

    def add_new_client(self):
        # ... (unchanged, but add logging)
        logging.info("Opened add new client dialog")
        # ... (rest of the method unchanged)

    def confirm_delete_client(self, client_id):
        # ... (unchanged, but add logging)
        logging.info(f"Opened confirm delete dialog for client ID: {client_id}")
        # ... (rest of the method unchanged)

    def start_daily_reading(self):
        if not self.client_manager.current_client_id:
            self.show_error_popup("Please select a client first!")
            logging.warning("Attempted daily reading with no client selected")
            return
        if self.client_manager.check_daily_reading_done("Daily Guidance"):
            self.show_error_popup("Daily reading already completed today!")
            logging.info("Daily reading already completed today")
            return
        self.start_reading(1, "Daily Guidance", special=True)
        logging.info("Started daily reading")

    def show_spreads_menu(self):
        # ... (unchanged, but add logging)
        self.main_layout.clear_widgets()
        # ... (rest of the method unchanged)
        logging.info("Displayed spreads menu")

    def start_reading(self, num_cards, spread_name, special=False):
        # ... (unchanged, but add logging)
        logging.info(f"Started {spread_name} reading with {num_cards} cards")
        # ... (rest of the method unchanged)

    def show_card_with_position(self):
        # ... (unchanged, but add logging)
        logging.info(f"Showing card {self.card_index + 1} of {len(self.current_cards)} for {self.current_spread_name}")
        # ... (rest of the method unchanged)

    def reveal_card_with_meaning_text(self, card_name, orientation):
        # ... (unchanged, but add logging)
        logging.info(f"Revealed card (text mode): {card_name} ({orientation})")
        # ... (rest of the method unchanged)

    def reveal_card_with_meaning(self, instance):
        # ... (unchanged, but add logging)
        logging.info(f"Revealed card: {instance.card_name} ({instance.orientation})")
        # ... (rest of the method unchanged)

    def show_card_meaning_popup(self, card_name, orientation):
        # ... (unchanged, but add logging)
        logging.info(f"Displayed meaning popup for {card_name} ({orientation})")
        # ... (rest of the method unchanged)

    def next_card_or_complete(self):
        # ... (unchanged, but add logging)
        logging.info(f"Moving to next card or completing reading (index: {self.card_index})")
        # ... (rest of the method unchanged)

    def complete_reading(self):
        # ... (unchanged, but add logging)
        logging.info(f"Completed reading: {self.current_spread_name}")
        # ... (rest of the method unchanged)

    def show_reading_complete(self):
        # ... (unchanged, but add logging)
        logging.info("Displayed reading complete screen")
        # ... (rest of the method unchanged)

    def quick_journal_entry(self):
        # ... (unchanged, but add logging)
        logging.info("Opened quick journal entry dialog")
        # ... (rest of the method unchanged)

    def show_history(self):
        # ... (unchanged, but add logging)
        logging.info("Displayed reading history")
        # ... (rest of the method unchanged)

    def show_journal(self):
        # ... (unchanged, but add logging)
        logging.info("Displayed journal entries")
        # ... (rest of the method unchanged)

    def add_journal_entry(self):
        # ... (unchanged, but add logging)
        logging.info("Opened add journal entry dialog")
        # ... (rest of the method unchanged)

    def show_settings(self):
        # ... (unchanged, but add logging)
        logging.info("Displayed settings screen")
        # ... (rest of the method unchanged)

    def toggle_animations(self, instance, value):
        self.animation_enabled = value
        self.save_settings()
        logging.info(f"Animations {'enabled' if value else 'disabled'}")

if __name__ == '__main__':
    logging.info("Starting PictureTarotApp - Multi-Client Edition with Logging")
    try:
        PictureTarotApp().run()
    except Exception as e:
        logging.error(f"Application crashed: {e}", exc_info=True)