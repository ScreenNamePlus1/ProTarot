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

# Base path for Android compatibility - Fixed path resolution
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):  # PyInstaller compatibility
    BASE_PATH = sys._MEIPASS

# Card definitions
suits = ["Wands", "Cups", "Swords", "Pentacles"]
ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
major_arcana = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers",
    "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death",
    "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

# Expanded card meanings with minor arcana
CARD_MEANINGS = {
    # Major Arcana
    "The Fool": {"upright": "New beginnings, innocence, spontaneity, free spirit", "reversed": "Recklessness, taken advantage of, inconsideration"},
    "The Magician": {"upright": "Manifestation, resourcefulness, power, inspired action", "reversed": "Manipulation, poor planning, untapped talents"},
    "The High Priestess": {"upright": "Intuition, sacred knowledge, divine feminine, subconscious", "reversed": "Secrets, disconnected intuition, withdrawal"},
    "The Empress": {"upright": "Femininity, beauty, nature, nurturing, abundance", "reversed": "Creative block, dependency on others"},
    "The Emperor": {"upright": "Authority, establishment, structure, father figure", "reversed": "Domination, excessive control, rigidity"},
    "The Hierophant": {"upright": "Spiritual wisdom, religious beliefs, conformity, tradition", "reversed": "Personal beliefs, freedom, challenging status quo"},
    "The Lovers": {"upright": "Love, harmony, relationships, values alignment", "reversed": "Self-love, disharmony, imbalance, misalignment"},
    "The Chariot": {"upright": "Control, willpower, success, determination", "reversed": "Self-discipline, opposition, lack of direction"},
    "Strength": {"upright": "Strength, courage, persuasion, influence, compassion", "reversed": "Self-doubt, low energy, raw emotion"},
    "The Hermit": {"upright": "Soul searching, introspection, inner guidance", "reversed": "Isolation, loneliness, withdrawal"},
    "Wheel of Fortune": {"upright": "Good luck, karma, life cycles, destiny", "reversed": "Bad luck, lack of control, clinging to control"},
    "Justice": {"upright": "Justice, fairness, truth, cause and effect", "reversed": "Unfairness, lack of accountability, dishonesty"},
    "The Hanged Man": {"upright": "Surrender, letting go, sacrifice, patience", "reversed": "Delays, resistance, stalling, indecision"},
    "Death": {"upright": "Endings, change, transformation, transition", "reversed": "Resistance to change, personal transformation"},
    "Temperance": {"upright": "Balance, moderation, patience, purpose", "reversed": "Imbalance, excess, self-healing, re-alignment"},
    "The Devil": {"upright": "Shadow self, attachment, addiction, restriction", "reversed": "Releasing limiting beliefs, exploring dark thoughts"},
    "The Tower": {"upright": "Sudden change, upheaval, chaos, revelation", "reversed": "Personal transformation, fear of change, averting disaster"},
    "The Star": {"upright": "Hope, faith, purpose, renewal, spirituality", "reversed": "Lack of faith, despair, self-trust, disconnection"},
    "The Moon": {"upright": "Illusion, fear, anxiety, subconscious, intuition", "reversed": "Release of fear, repressed emotion, inner confusion"},
    "The Sun": {"upright": "Positivity, fun, warmth, success, vitality", "reversed": "Inner child, feeling down, overly optimistic"},
    "Judgement": {"upright": "Judgement, rebirth, inner calling, absolution", "reversed": "Self-doubt, inner critic, ignoring the call"},
    "The World": {"upright": "Completion, integration, accomplishment, travel", "reversed": "Seeking personal closure, short-cut to success"},
    
    # Minor Arcana - Wands (sample entries for key cards)
    "Ace of Wands": {"upright": "Inspiration, new opportunities, growth", "reversed": "Lack of energy, delayed timing, lack of direction"},
    "King of Wands": {"upright": "Natural born leader, vision, entrepreneur", "reversed": "Impulsiveness, haste, ruthless"},
    
    # Add more minor arcana as needed...
}

# Add default meanings for cards not in the dictionary
def get_card_meaning(card_name, orientation):
    """Get card meaning with fallback for missing cards"""
    meanings = CARD_MEANINGS.get(card_name, {})
    if orientation.lower() in meanings:
        return meanings[orientation.lower()]
    
    # Generate meaningful fallback for minor arcana
    if " of " in card_name:
        suit = card_name.split(" of ")[1]
        rank = card_name.split(" of ")[0]
        suit_themes = {
            "Wands": "creativity, passion, growth",
            "Cups": "emotions, relationships, intuition", 
            "Swords": "thoughts, communication, conflict",
            "Pentacles": "material matters, work, resources"
        }
        theme = suit_themes.get(suit, "life lessons")
        return f"Focus on {theme}. {rank} energy brings new perspectives."
    
    return f"Meditate on the symbolism of {card_name}. Trust your intuition for guidance."

# Spread definitions
SPREADS = {
    "Daily Guidance": {
        "cards": 1, 
        "positions": ["Your guidance for today"], 
        "description": "A single card to guide your day"
    },
    "Past-Present-Future": {
        "cards": 3, 
        "positions": ["Past influences", "Present situation", "Future potential"], 
        "description": "Classic three-card timeline reading"
    },
    "Love & Relationships": {
        "cards": 5, 
        "positions": ["You in love", "Your partner/potential", "The relationship", "Challenges to overcome", "Outcome/advice"], 
        "description": "Deep dive into your romantic life"
    },
    "Career Path": {
        "cards": 4, 
        "positions": ["Current career energy", "Hidden talents", "Obstacles to address", "Next steps to take"], 
        "description": "Navigate your professional journey"
    },
    "Celtic Cross": {
        "cards": 10, 
        "positions": ["Present situation", "Challenge/cross", "Distant past/foundation", "Recent past", "Possible outcome", "Near future", "Your approach", "External influences", "Hopes & fears", "Final outcome"], 
        "description": "The most comprehensive tarot spread"
    },
    "Chakra Balance": {
        "cards": 7, 
        "positions": ["Root Chakra (survival)", "Sacral Chakra (creativity)", "Solar Plexus (power)", "Heart Chakra (love)", "Throat Chakra (communication)", "Third Eye (intuition)", "Crown Chakra (spirituality)"], 
        "description": "Align your spiritual energy centers"
    },
    "Essential Oil Guidance": {
        "cards": 3, 
        "positions": ["Physical needs", "Emotional needs", "Spiritual needs"], 
        "description": "Perfect for holistic wellness consultations"
    }
}

# Create full deck
tarot_cards = [f"{rank} of {suit}" for suit in suits for rank in ranks] + major_arcana

# Custom button with improved mystical styling
class MysticalButton(Button):
    def __init__(self, text="", **kwargs):
        # Set default styling
        kwargs.setdefault('background_color', (0, 0, 0, 0))  # Transparent background
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('bold', True)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        super().__init__(text=text, **kwargs)
        
        # Create custom background
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

class ClientButton(MysticalButton):
    def __init__(self, client_name, is_active=False, **kwargs):
        self.client_name = client_name
        self.is_active = is_active
        super().__init__(text=f"👤 {client_name}", **kwargs)
        
        # Update colors for active state
        with self.canvas.before:
            if is_active:
                Color(0.3, 0.6, 0.2, 0.9)  # Green for active
            else:
                Color(0.4, 0.2, 0.6, 0.8)  # Purple for inactive
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
        # Scale down animation
        anim1 = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.1)
        # Scale back up animation
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
        
        # Apply rotation for reversed cards
        if orientation == "Reversed":
            self._apply_rotation()
    
    def _apply_rotation(self):
        """Apply rotation for reversed cards"""
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=180, origin=(self.center_x, self.center_y))
        with self.canvas.after:
            PopMatrix()
        
        self.bind(pos=self._update_rotation, size=self._update_rotation)
    
    def _update_rotation(self, *args):
        """Update rotation when position/size changes"""
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
        # Use app's data directory for better Android compatibility
        if hasattr(App.get_running_app(), 'user_data_dir'):
            data_dir = App.get_running_app().user_data_dir
        else:
            data_dir = BASE_PATH
        
        self.clients_file = os.path.join(data_dir, "clients.json")
        self.clients = {}
        self.current_client_id = None
        self.load_clients()
        
        # Ensure we have at least one client
        if not self.clients:
            self.add_client("Personal", "Your personal readings", is_default=True)
    
    def load_clients(self):
        """Load clients from JSON file with better error handling"""
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.clients = data.get("clients", {})
                    self.current_client_id = data.get("current_client_id")
                Logger.info(f"Loaded {len(self.clients)} clients")
            else:
                Logger.info("No clients.json found, starting fresh")
                self.clients = {}
                self.current_client_id = None
        except (json.JSONDecodeError, IOError) as e:
            Logger.error(f"Failed to load clients: {e}")
            self.clients = {}
            self.current_client_id = None
        except Exception as e:
            Logger.error(f"Unexpected error loading clients: {e}")
            self.clients = {}
            self.current_client_id = None
    
    def save_clients(self):
        """Save clients to JSON file with better error handling"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.clients_file), exist_ok=True)
            
            data = {
                "clients": self.clients, 
                "current_client_id": self.current_client_id
            }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.clients_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            os.rename(temp_file, self.clients_file)
            Logger.info("Clients saved successfully")
            
        except Exception as e:
            Logger.error(f"Failed to save clients: {e}")
            # Clean up temp file if it exists
            temp_file = self.clients_file + '.tmp'
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def add_client(self, name, description="", is_default=False):
        """Add new client with validation"""
        if not name or not name.strip():
            Logger.warning("Cannot add client with empty name")
            return None
            
        name = name.strip()
        
        # Check for duplicate names (case-insensitive)
        if any(client["name"].lower() == name.lower() for client in self.clients.values()):
            Logger.warning(f"Client with name '{name}' already exists")
            return None
        
        # Generate unique client ID
        client_id = f"client_{len(self.clients) + 1}_{name.lower().replace(' ', '_').replace('-', '_')}"
        
        # Ensure ID is unique
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
        Logger.info(f"Added client: {name} (ID: {client_id})")
        return client_id
    
    def get_current_client(self):
        """Get current client data"""
        if not self.current_client_id or self.current_client_id not in self.clients:
            return None
        return self.clients[self.current_client_id]
    
    def get_current_client_name(self):
        """Get current client name"""
        client = self.get_current_client()
        return client["name"] if client else "No Client Selected"
    
    def switch_client(self, client_id):
        """Switch to different client"""
        if client_id in self.clients:
            self.current_client_id = client_id
            self.save_clients()
            Logger.info(f"Switched to client: {self.clients[client_id]['name']}")
            return True
        Logger.warning(f"Cannot switch to non-existent client: {client_id}")
        return False
    
    def add_reading_to_current_client(self, spread_name, cards, orientations, notes=""):
        """Add reading to current client with validation"""
        if not self.current_client_id:
            Logger.warning("No current client selected for reading")
            return False
        
        if not cards or not orientations or len(cards) != len(orientations):
            Logger.warning("Invalid cards/orientations data for reading")
            return False
        
        reading = {
            "date": datetime.now().isoformat(),
            "spread": spread_name,
            "cards": cards,
            "orientations": orientations,
            "notes": notes.strip()
        }
        
        # Add to beginning of readings list
        self.clients[self.current_client_id]["readings"].insert(0, reading)
        
        # Keep only last 100 readings to prevent excessive storage
        if len(self.clients[self.current_client_id]["readings"]) > 100:
            self.clients[self.current_client_id]["readings"] = self.clients[self.current_client_id]["readings"][:100]
        
        self.save_clients()
        Logger.info(f"Added {spread_name} reading with {len(cards)} cards")
        return True
    
    def add_journal_entry_to_current_client(self, entry_text):
        """Add journal entry to current client"""
        if not self.current_client_id:
            Logger.warning("No current client selected for journal entry")
            return False
        
        if not entry_text or not entry_text.strip():
            Logger.warning("Cannot add empty journal entry")
            return False
        
        entry = {
            "date": datetime.now().isoformat(), 
            "text": entry_text.strip()
        }
        
        self.clients[self.current_client_id]["journal"].insert(0, entry)
        
        # Keep only last 200 journal entries
        if len(self.clients[self.current_client_id]["journal"]) > 200:
            self.clients[self.current_client_id]["journal"] = self.clients[self.current_client_id]["journal"][:200]
        
        self.save_clients()
        Logger.info("Added journal entry")
        return True
    
    def check_daily_reading_done(self, spread_name="Daily Guidance"):
        """Check if daily reading was already done today"""
        if not self.current_client_id:
            return False
        
        today = date.today().isoformat()
        readings = self.clients.get(self.current_client_id, {}).get("readings", [])
        
        return any(
            r.get("date", "").startswith(today) and r.get("spread") == spread_name 
            for r in readings
        )
    
    def delete_client(self, client_id):
        """Delete client with safety checks"""
        if client_id not in self.clients:
            Logger.warning(f"Cannot delete non-existent client: {client_id}")
            return False
        
        if len(self.clients) <= 1:
            Logger.warning("Cannot delete the last remaining client")
            return False
        
        client_name = self.clients[client_id]["name"]
        del self.clients[client_id]
        
        # Switch to another client if we deleted the current one
        if self.current_client_id == client_id:
            self.current_client_id = list(self.clients.keys())[0]
        
        self.save_clients()
        Logger.info(f"Deleted client: {client_name}")
        return True

class PictureTarotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_manager = ClientManager()
        self.animation_enabled = True
        self.load_settings()
        
        # Initialize reading variables
        self.current_cards = []
        self.current_orientations = []
        self.current_spread_name = ""
        self.current_spread_info = {}
        self.card_index = 0
        self.is_special = False
        self.current_card_widget = None
    
    def load_settings(self):
        """Load app settings"""
        try:
            settings_file = os.path.join(self.user_data_dir, "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.animation_enabled = settings.get("animation_enabled", True)
                    Logger.info("Settings loaded successfully")
        except Exception as e:
            Logger.error(f"Failed to load settings: {e}")
            self.animation_enabled = True
    
    def save_settings(self):
        """Save app settings"""
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            settings = {"animation_enabled": self.animation_enabled}
            settings_file = os.path.join(self.user_data_dir, "settings.json")
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            Logger.info("Settings saved successfully")
        except Exception as e:
            Logger.error(f"Failed to save settings: {e}")
    
    def build(self):
        """Build the main app"""
        # Set app icon
        icon_path = os.path.join(BASE_PATH, "images", "AppIcons", "transparent.png")
        if os.path.exists(icon_path):
            self.icon = icon_path
        
        self.title = "Picture Tarot - Multi-Client Edition"
        self.main_layout = FloatLayout()
        self.show_main_menu()
        return self.main_layout
    
    def get_image_base_path(self):
        """Find the correct path for tarot card images"""
        possible_paths = [
            os.path.join(BASE_PATH, "images", "rider-waite-tarot"),
            os.path.join(BASE_PATH, "images", "tarot"),
            os.path.join(BASE_PATH, "images"),
            os.path.join(BASE_PATH, "assets", "images"),
            BASE_PATH
        ]
        
        for path in possible_paths:
            # Check for common card files
            test_files = ["CardBacks.png", "The_Fool.png", "cardback.png", "the_fool.png"]
            if any(os.path.exists(os.path.join(path, test_file)) for test_file in test_files):
                Logger.info(f"Found card images at: {path}")
                return path
        
        Logger.warning("No valid image path found, using BASE_PATH")
        return BASE_PATH
    
    def get_card_image_path(self, card_name):
        """Get the file path for a specific card image"""
        base_path = self.get_image_base_path()
        
        # Try different naming conventions
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
                    return image_path
        
        Logger.warning(f"Card image not found for '{card_name}', using card back")
        return self.get_card_back_path()
    
    def get_card_back_path(self):
        """Get the card back image path"""
        base_path = self.get_image_base_path()
        
        # Try different card back naming conventions
        back_names = ["CardBacks", "cardback", "card_back", "back"]
        
        for name in back_names:
            for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                path = os.path.join(base_path, f"{name}{ext}")
                if os.path.exists(path):
                    return path
        
        Logger.warning("Card back image not found")
        # Return a placeholder or create a simple colored rectangle
        return None
    
    def show_error_popup(self, message):
        """Show error popup with improved styling"""
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
    
    def show_main_menu(self):
        """Show the main menu with client info"""
        self.main_layout.clear_widgets()
        
        # Set background
        with self.main_layout.canvas.before:
            Color(0.05, 0.05, 0.15, 1)
            Rectangle(pos=(0, 0), size=Window.size)
        
        container = BoxLayout(
            orientation='vertical', 
            padding=20, 
            spacing=15,
            size_hint=(0.95, 0.95), 
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Client header section
        client_header = BoxLayout(size_hint_y=0.15, spacing=10)
        current_client = self.client_manager.get_current_client_name()
        
        client_label = Label(
            text=f"👤 Client: {current_client}", 
            font_size='18sp',
            bold=True, 
            color=(0.8, 1, 0.8, 1), 
            size_hint_x=0.6,
            halign='left'
        )
        client_label.bind(size=client_label.setter('text_size'))
        
        switch_btn = MysticalButton("Switch Client", size_hint_x=0.2)
        switch_btn.bind(on_press=lambda x: self.show_client_manager())
        
        add_client_btn = MysticalButton("+ Add Client", size_hint_x=0.2)
        add_client_btn.bind(on_press=lambda x: self.add_new_client())
        
        client_header.add_widget(client_label)
        client_header.add_widget(switch_btn)
        client_header.add_widget(add_client_btn)
        
        # App title
        title = Label(
            text="✦ PICTURE TAROT ✦", 
            font_size='32sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.12
        )
        
        # Check if daily reading was done
        daily_drawn = self.client_manager.check_daily_reading_done("Daily Guidance")
        
        # Menu options
        menu_options = [
            ("🔮 Daily Card", lambda x: self.start_daily_reading(), not daily_drawn),
            ("📚 Tarot Spreads", lambda x: self.show_spreads_menu(), True),
            ("📖 Reading History", lambda x: self.show_history(), True),
            ("✍️ Client Journal", lambda x: self.show_journal(), True),
            ("⚙️ Settings", lambda x: self.show_settings(), True)
        ]
        
        # Add widgets to container
        container.add_widget(client_header)
        container.add_widget(title)
        
        for text, callback, enabled in menu_options:
            if "Daily" in text and not enabled:
                display_text = f"{text} ✅ (Done Today)"
                btn = MysticalButton(display_text, size_hint_y=0.12)
                btn.color = (0.7, 0.7, 0.7, 1)
            else:
                btn = MysticalButton(text, size_hint_y=0.12)
                if enabled:
                    btn.bind(on_press=callback)
            
            container.add_widget(btn)
        
        self.main_layout.add_widget(container)
    
    def show_client_manager(self):
        """Show client management interface"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.2)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        
        client_name = self.client_manager.get_current_client_name()
        title = Label(
            text=f"📖 {client_name}'s Journal", 
            font_size='18sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_x=0.6
        )
        
        add_btn = MysticalButton("+ New Entry", size_hint_x=0.2)
        add_btn.bind(on_press=lambda x: self.add_journal_entry())
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_btn)
        container.add_widget(header)
        
        # Journal entries list
        scroll = ScrollView()
        journal_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        journal_container.bind(minimum_height=journal_container.setter('height'))
        
        current_client = self.client_manager.get_current_client()
        entries = current_client.get("journal", []) if current_client else []
        
        if not entries:
            no_entries = Label(
                text=f"📝 No journal entries yet for {client_name}.\n\nStart documenting their tarot insights and progress!",
                font_size='16sp', 
                color=(0.7, 0.7, 0.7, 1), 
                size_hint_y=None, 
                height=100, 
                halign='center'
            )
            no_entries.bind(size=no_entries.setter('text_size'))
            journal_container.add_widget(no_entries)
        else:
            for entry in entries[:100]:  # Show last 100 entries
                try:
                    date_str = datetime.fromisoformat(entry["date"]).strftime("%B %d, %Y at %I:%M %p")
                except:
                    date_str = "Unknown date"
                
                entry_box = BoxLayout(
                    orientation='vertical', 
                    size_hint_y=None, 
                    height=120, 
                    padding=15, 
                    spacing=5
                )
                
                # Background styling
                with entry_box.canvas.before:
                    Color(0.15, 0.1, 0.25, 0.5)
                    rect = Rectangle(pos=entry_box.pos, size=entry_box.size)
                    entry_box.bg_rect = rect
                
                entry_box.bind(pos=self._update_entry_bg, size=self._update_entry_bg)
                
                date_label = Label(
                    text=f"✨ {date_str}", 
                    font_size='14sp',
                    bold=True, 
                    color=(1, 1, 0.8, 1), 
                    size_hint_y=0.3, 
                    halign='left'
                )
                date_label.bind(size=date_label.setter('text_size'))
                
                # Truncate long text for preview
                text_content = entry.get("text", "")
                preview_text = text_content[:200] + ("..." if len(text_content) > 200 else "")
                
                text_label = Label(
                    text=preview_text,
                    font_size='13sp', 
                    color=(0.9, 0.9, 0.9, 1), 
                    size_hint_y=0.7, 
                    halign='left', 
                    valign='top'
                )
                text_label.bind(size=text_label.setter('text_size'))
                
                entry_box.add_widget(date_label)
                entry_box.add_widget(text_label)
                journal_container.add_widget(entry_box)
        
        scroll.add_widget(journal_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)
    
    def _update_entry_bg(self, instance, *args):
        """Update journal entry background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def add_journal_entry(self):
        """Show dialog to add new journal entry"""
        client_name = self.client_manager.get_current_client_name()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        title_label = Label(
            text=f"✍️ New Journal Entry for {client_name}", 
            font_size='20sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.15
        )
        
        text_input = TextInput(
            hint_text=f"Share insights, observations, or notes about {client_name}'s readings and spiritual journey...", 
            multiline=True,
            size_hint_y=0.6, 
            background_color=(0.2, 0.15, 0.3, 0.8), 
            foreground_color=(1, 1, 1, 1),
            font_size='14sp'
        )
        
        buttons = BoxLayout(size_hint_y=0.25, spacing=10)
        save_btn = MysticalButton("💾 Save Entry")
        cancel_btn = MysticalButton("❌ Cancel")
        
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(title_label)
        content.add_widget(text_input)
        content.add_widget(buttons)
        
        popup = Popup(
            title="", 
            content=content, 
            size_hint=(0.9, 0.8), 
            background_color=(0.05, 0.05, 0.15, 0.95)
        )
        
        def save_entry(*args):
            if text_input.text.strip():
                if self.client_manager.add_journal_entry_to_current_client(text_input.text.strip()):
                    popup.dismiss()
                    self.show_journal()  # Refresh the journal view
                else:
                    self.show_error_popup("Failed to save journal entry!")
            else:
                self.show_error_popup("Journal entry cannot be empty!")
        
        save_btn.bind(on_press=save_entry)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_settings(self):
        """Show app settings"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back_btn = MysticalButton("← Back", size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        
        title = Label(
            text="⚙️ Settings", 
            font_size='24sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_x=0.7
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        container.add_widget(header)
        
        # Settings options
        settings_container = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.6)
        
        # Animation toggle
        anim_box = BoxLayout(size_hint_y=None, height=60, spacing=15)
        anim_label = Label(
            text="✨ Card Animations", 
            font_size='18sp',
            color=(1, 1, 1, 1), 
            size_hint_x=0.7, 
            halign='left'
        )
        anim_label.bind(size=anim_label.setter('text_size'))
        
        anim_switch = Switch(active=self.animation_enabled, size_hint_x=0.3)
        anim_switch.bind(active=self.toggle_animations)
        
        anim_box.add_widget(anim_label)
        anim_box.add_widget(anim_switch)
        settings_container.add_widget(anim_box)
        
        # Client management shortcut
        client_mgmt_btn = MysticalButton("👥 Manage Clients", size_hint_y=None, height=60)
        client_mgmt_btn.bind(on_press=lambda x: self.show_client_manager())
        settings_container.add_widget(client_mgmt_btn)
        
        # Data export/backup (placeholder for future feature)
        data_btn = MysticalButton("💾 Export Client Data (Coming Soon)", size_hint_y=None, height=60)
        data_btn.color = (0.6, 0.6, 0.6, 1)  # Disabled appearance
        settings_container.add_widget(data_btn)
        
        container.add_widget(settings_container)
        
        # App info section
        info_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        
        client_count = len(self.client_manager.clients)
        current_client = self.client_manager.get_current_client_name()
        
        # Calculate total readings across all clients
        total_readings = sum(len(client.get("readings", [])) for client in self.client_manager.clients.values())
        total_journal_entries = sum(len(client.get("journal", [])) for client in self.client_manager.clients.values())
        
        app_info = Label(
            text=f"📱 Picture Tarot v1.0\nMulti-Client Professional Edition ✨\n\n"
                 f"👥 {client_count} clients managed\n"
                 f"🔮 Current: {current_client}\n"
                 f"📚 Total readings: {total_readings}\n"
                 f"📝 Total journal entries: {total_journal_entries}\n\n"
                 f"Perfect for tarot readers, spiritual advisors,\nand wellness practitioners serving multiple clients.",
            font_size='14sp', 
            color=(0.7, 0.7, 0.8, 1), 
            halign='center'
        )
        app_info.bind(size=app_info.setter('text_size'))
        
        info_container.add_widget(app_info)
        container.add_widget(info_container)
        
        self.main_layout.add_widget(container)
    
    def toggle_animations(self, instance, value):
        """Toggle animation setting"""
        self.animation_enabled = value
        self.save_settings()
        Logger.info(f"Animations {'enabled' if value else 'disabled'}")


if __name__ == '__main__':
    import sys
    Logger.info("Starting PictureTarotApp - Multi-Client Edition")
    try:
        PictureTarotApp().run()
    except Exception as e:
        Logger.error(f"Application crashed: {e}")
        import traceback
        traceback.print_exc()
        header = BoxLayout(size_hint_y=0.1)
        back_btn = MysticalButton("← Back", size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        
        title = Label(
            text="👥 Client Manager", 
            font_size='24sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_x=0.7
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        container.add_widget(header)
        
        # Client list
        scroll = ScrollView()
        client_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        client_container.bind(minimum_height=client_container.setter('height'))
        
        for client_id, client_data in self.client_manager.clients.items():
            is_active = client_id == self.client_manager.current_client_id
            
            client_box = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height=80, 
                spacing=10
            )
            
            # Client button
            client_btn = ClientButton(
                client_data["name"], 
                is_active=is_active, 
                size_hint_x=0.6
            )
            
            if not is_active:
                client_btn.bind(on_press=lambda btn, cid=client_id: self.switch_to_client(cid))
            
            # Info label
            readings_count = len(client_data["readings"])
            journal_count = len(client_data["journal"])
            
            info_label = Label(
                text=f"📚 {readings_count} readings\n📝 {journal_count} entries",
                font_size='12sp', 
                color=(0.8, 0.8, 0.8, 1), 
                size_hint_x=0.3,
                halign='center'
            )
            info_label.bind(size=info_label.setter('text_size'))
            
            client_box.add_widget(client_btn)
            client_box.add_widget(info_label)
            
            # Delete button (only if more than one client)
            if len(self.client_manager.clients) > 1:
                delete_btn = MysticalButton("🗑️", size_hint_x=0.1)
                delete_btn.bind(on_press=lambda btn, cid=client_id: self.confirm_delete_client(cid))
                client_box.add_widget(delete_btn)
            
            client_container.add_widget(client_box)
        
        scroll.add_widget(client_container)
        container.add_widget(scroll)
        
        # Add new client button
        add_btn = MysticalButton("➕ Add New Client", size_hint_y=0.1)
        add_btn.bind(on_press=lambda x: self.add_new_client())
        container.add_widget(add_btn)
        
        self.main_layout.add_widget(container)
    
    def switch_to_client(self, client_id):
        """Switch to a different client"""
        if self.client_manager.switch_client(client_id):
            self.show_main_menu()
        else:
            self.show_error_popup("Failed to switch client!")
    
    def add_new_client(self):
        """Show dialog to add new client"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        title_label = Label(
            text="👤 Add New Client", 
            font_size='20sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.2
        )
        
        name_input = TextInput(
            hint_text="Client name (e.g., Sarah Johnson)", 
            multiline=False,
            size_hint_y=0.2, 
            background_color=(0.2, 0.15, 0.3, 0.8), 
            foreground_color=(1, 1, 1, 1),
            font_size='16sp'
        )
        
        desc_input = TextInput(
            hint_text="Description (e.g., DoTerra consultation client)", 
            multiline=True,
            size_hint_y=0.4, 
            background_color=(0.2, 0.15, 0.3, 0.8), 
            foreground_color=(1, 1, 1, 1),
            font_size='14sp'
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
        
        popup = Popup(
            title="", 
            content=content, 
            size_hint=(0.9, 0.7), 
            background_color=(0.05, 0.05, 0.15, 0.95)
        )
        
        def add_client(*args):
            name = name_input.text.strip()
            if not name:
                self.show_error_popup("Client name cannot be empty!")
                return
            
            desc = desc_input.text.strip()
            client_id = self.client_manager.add_client(name, desc)
            
            if client_id:
                self.client_manager.switch_client(client_id)
                popup.dismiss()
                self.show_client_manager()
            else:
                self.show_error_popup("Client name already exists or invalid!")
        
        add_btn.bind(on_press=add_client)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def confirm_delete_client(self, client_id):
        """Show confirmation dialog before deleting client"""
        client_name = self.client_manager.clients[client_id]["name"]
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        warning_label = Label(
            text=f"⚠️ Delete Client?\n\n'{client_name}'\n\nThis will permanently delete all readings and journal entries for this client.",
            font_size='16sp', 
            color=(1, 1, 1, 1), 
            halign='center', 
            size_hint_y=0.7
        )
        warning_label.bind(size=warning_label.setter('text_size'))
        
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        delete_btn = MysticalButton("🗑️ Delete", background_color=(0.8, 0.2, 0.2, 0.9))
        cancel_btn = MysticalButton("❌ Cancel")
        
        buttons.add_widget(delete_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(warning_label)
        content.add_widget(buttons)
        
        popup = Popup(
            title="⚠️ Confirm Deletion", 
            content=content, 
            size_hint=(0.8, 0.5)
        )
        
        def delete_client(*args):
            if self.client_manager.delete_client(client_id):
                popup.dismiss()
                self.show_client_manager()
            else:
                self.show_error_popup("Cannot delete the last client!")
        
        delete_btn.bind(on_press=delete_client)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def start_daily_reading(self):
        """Start daily guidance reading"""
        if not self.client_manager.current_client_id:
            self.show_error_popup("Please select a client first!")
            return
        
        # Check if already done today
        if self.client_manager.check_daily_reading_done("Daily Guidance"):
            self.show_error_popup("Daily reading already completed today!")
            return
        
        self.start_reading(1, "Daily Guidance", special=True)
    
    def show_spreads_menu(self):
        """Show tarot spreads selection menu"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.25)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        
        title = Label(
            text="Choose Your Spread", 
            font_size='20sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_x=0.5
        )
        
        client_info = Label(
            text=f"👤 {self.client_manager.get_current_client_name()}",
            font_size='14sp', 
            color=(0.8, 1, 0.8, 1), 
            size_hint_x=0.25
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(client_info)
        container.add_widget(header)
        
        # Scrollable spreads list
        scroll = ScrollView()
        spread_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        spread_container.bind(minimum_height=spread_container.setter('height'))
        
        for spread_name, spread_info in SPREADS.items():
            # Skip daily guidance (handled separately)
            if spread_name == "Daily Guidance":
                continue
            
            # Create spread option
            spread_layout = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                height=120, 
                padding=10,
                spacing=5
            )
            
            # Background styling
            with spread_layout.canvas.before:
                Color(0.15, 0.1, 0.25, 0.7)
                rect = Rectangle(pos=spread_layout.pos, size=spread_layout.size)
                spread_layout.bg_rect = rect
            
            spread_layout.bind(pos=self._update_spread_bg, size=self._update_spread_bg)
            
            name_label = Label(
                text=f"✨ {spread_name} ({spread_info['cards']} cards)",
                font_size='18sp', 
                bold=True, 
                color=(1, 1, 1, 1), 
                size_hint_y=0.6,
                halign='left'
            )
            name_label.bind(size=name_label.setter('text_size'))
            
            desc_label = Label(
                text=spread_info['description'], 
                font_size='14sp',
                color=(0.9, 0.9, 0.9, 1), 
                size_hint_y=0.4,
                halign='left'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            
            spread_layout.add_widget(name_label)
            spread_layout.add_widget(desc_label)
            
            # Make it clickable
            clickable = AnimatedButton(size_hint_y=None, height=120)
            clickable.add_widget(spread_layout)
            clickable.bind(on_press=lambda btn, name=spread_name, info=spread_info: self.start_reading(info['cards'], name))
            
            spread_container.add_widget(clickable)
        
        scroll.add_widget(spread_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)
    
    def _update_spread_bg(self, instance, *args):
        """Update spread background rectangle"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def start_reading(self, num_cards, spread_name, special=False):
        """Start a tarot reading"""
        if not self.client_manager.current_client_id:
            self.show_error_popup("Please select a client first!")
            return
        
        try:
            # Validate parameters
            if num_cards <= 0 or num_cards > len(tarot_cards):
                self.show_error_popup(f"Invalid number of cards: {num_cards}")
                return
            
            # Select random cards and orientations
            self.current_cards = random.sample(tarot_cards, num_cards)
            self.current_orientations = [random.choice(["Upright", "Reversed"]) for _ in range(num_cards)]
            self.current_spread_name = spread_name
            self.current_spread_info = SPREADS.get(spread_name, {
                "positions": [f"Card {i+1}" for i in range(num_cards)]
            })
            self.card_index = 0
            self.is_special = special
            
            Logger.info(f"Starting {spread_name} reading with {num_cards} cards")
            self.show_card_with_position()
            
        except Exception as e:
            Logger.error(f"Failed to start reading: {e}")
            self.show_error_popup(f"Failed to start reading: {str(e)}")
    
    def show_card_with_position(self):
        """Show current card with its position"""
        if self.card_index >= len(self.current_cards):
            Logger.warning("Card index out of range")
            self.complete_reading()
            return
        
        self.main_layout.clear_widgets()
        
        card_name = self.current_cards[self.card_index]
        orientation = self.current_orientations[self.card_index]
        positions = self.current_spread_info.get("positions", [])
        position = positions[self.card_index] if self.card_index < len(positions) else f"Card {self.card_index + 1}"
        
        container = BoxLayout(
            orientation='vertical', 
            padding=30, 
            spacing=15,
            size_hint=(0.95, 0.95), 
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Client info
        client_info = Label(
            text=f"👤 Reading for: {self.client_manager.get_current_client_name()}",
            font_size='14sp', 
            color=(0.8, 1, 0.8, 1), 
            size_hint_y=0.06, 
            halign='center'
        )
        client_info.bind(size=client_info.setter('text_size'))
        
        # Progress info
        progress_label = Label(
            text=f"✨ {self.current_spread_name} ✨\nCard {self.card_index + 1} of {len(self.current_cards)}",
            font_size='16sp', 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.1, 
            halign='center'
        )
        progress_label.bind(size=progress_label.setter('text_size'))
        
        # Position label
        position_label = Label(
            text=f"Position: {position}", 
            font_size='18sp',
            bold=True, 
            color=(0.9, 0.9, 1, 1), 
            size_hint_y=0.08, 
            halign='center'
        )
        position_label.bind(size=position_label.setter('text_size'))
        
        # Card image (initially showing back)
        card_back_path = self.get_card_back_path()
        if not card_back_path:
            Logger.error("Card back image not found")
            self.show_error_popup("Card images are missing! Please check image files.")
            return
        
        self.current_card_widget = TarotCardImage(
            card_name=card_name, 
            orientation=orientation, 
            app_instance=self,
            source=card_back_path, 
            allow_stretch=True, 
            keep_ratio=True, 
            size_hint=(1, 0.61)
        )
        self.current_card_widget.bind(on_press=self.reveal_card_with_meaning)
        
        # Instruction
        instruction_label = Label(
            text="🎭 Tap the card to reveal your destiny 🎭",
            font_size='16sp', 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.15, 
            halign='center'
        )
        instruction_label.bind(size=instruction_label.setter('text_size'))
        
        # Add all widgets
        container.add_widget(client_info)
        container.add_widget(progress_label)
        container.add_widget(position_label)
        container.add_widget(self.current_card_widget)
        container.add_widget(instruction_label)
        
        self.main_layout.add_widget(container)
    
    def reveal_card_with_meaning(self, instance):
        """Reveal card and show its meaning"""
        if instance.is_revealed:
            self.next_card_or_complete()
            return
        
        # Load the actual card image
        card_image_path = self.get_card_image_path(instance.card_name)
        if card_image_path and os.path.exists(card_image_path):
            instance.source = card_image_path
            instance.is_revealed = True
            self.show_card_meaning_popup(instance.card_name, instance.orientation)
        else:
            Logger.error(f"Failed to load card image: {instance.card_name}")
            self.show_error_popup(f"Card image not found: {instance.card_name}")
    
    def show_card_meaning_popup(self, card_name, orientation):
        """Show popup with card meaning"""
        meaning = get_card_meaning(card_name, orientation)
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title = Label(
            text=f"{card_name}\n({orientation})", 
            font_size='20sp',
            bold=True, 
            size_hint_y=0.3, 
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        meaning_label = Label(
            text=meaning, 
            font_size='16sp', 
            size_hint_y=0.5, 
            halign='center', 
            valign='middle'
        )
        meaning_label.bind(size=meaning_label.setter('text_size'))
        
        close_btn = MysticalButton("Continue", size_hint_y=0.2)
        
        content.add_widget(title)
        content.add_widget(meaning_label)
        content.add_widget(close_btn)
        
        popup = Popup(
            title="🔮 Card Revealed", 
            content=content, 
            size_hint=(0.9, 0.7), 
            background_color=(0.1, 0.05, 0.2, 0.95)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def next_card_or_complete(self):
        """Move to next card or complete reading"""
        self.card_index += 1
        if self.card_index >= len(self.current_cards):
            self.complete_reading()
        else:
            self.show_card_with_position()
    
    def complete_reading(self):
        """Complete the reading and save it"""
        try:
            success = self.client_manager.add_reading_to_current_client(
                self.current_spread_name, 
                self.current_cards, 
                self.current_orientations
            )
            
            if success:
                self.show_reading_complete()
            else:
                self.show_error_popup("Failed to save reading!")
                
        except Exception as e:
            Logger.error(f"Error completing reading: {e}")
            self.show_error_popup(f"Error completing reading: {str(e)}")
    
    def show_reading_complete(self):
        """Show reading completion screen"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        client_name = self.client_manager.get_current_client_name()
        
        title = Label(
            text=f"🌟 Reading Complete! 🌟\n\nReading for {client_name} has been saved",
            font_size='24sp', 
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.25, 
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        message = Label(
            text=f"Your {self.current_spread_name} reading for {client_name} has been saved to their personal history.\n\nTake time to reflect on the messages revealed.",
            font_size='16sp', 
            color=(0.9, 0.9, 0.9, 1), 
            size_hint_y=0.25, 
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        
        # Options buttons
        options_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        
        journal_btn = MysticalButton("📝 Add Journal Entry")
        journal_btn.bind(on_press=lambda x: self.quick_journal_entry())
        
        history_btn = MysticalButton("📚 View Reading History")
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
        """Show quick journal entry dialog"""
        client_name = self.client_manager.get_current_client_name()
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        title_label = Label(
            text=f"📝 Journal Entry for {client_name}", 
            font_size='18sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_y=0.15
        )
        
        text_input = TextInput(
            hint_text=f"Reflect on {client_name}'s reading...", 
            multiline=True,
            size_hint_y=0.55, 
            background_color=(0.2, 0.15, 0.3, 0.8), 
            foreground_color=(1, 1, 1, 1),
            font_size='14sp'
        )
        
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        save_btn = MysticalButton("💾 Save")
        cancel_btn = MysticalButton("❌ Cancel")
        
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(title_label)
        content.add_widget(text_input)
        content.add_widget(buttons)
        
        popup = Popup(
            title="", 
            content=content, 
            size_hint=(0.9, 0.6),
            background_color=(0.05, 0.05, 0.15, 0.95)
        )
        
        def save_entry(*args):
            if text_input.text.strip():
                if self.client_manager.add_journal_entry_to_current_client(text_input.text.strip()):
                    popup.dismiss()
                else:
                    self.show_error_popup("Failed to save journal entry!")
            else:
                popup.dismiss()
        
        save_btn.bind(on_press=save_entry)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_history(self):
        """Show reading history for current client"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.25)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        
        title = Label(
            text="📚 Reading History", 
            font_size='20sp',
            bold=True, 
            color=(1, 1, 0.8, 1), 
            size_hint_x=0.5
        )
        
        client_info = Label(
            text=f"👤 {self.client_manager.get_current_client_name()}",
            font_size='14sp', 
            color=(0.8, 1, 0.8, 1), 
            size_hint_x=0.25
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(client_info)
        container.add_widget(header)
        
        # History list
        scroll = ScrollView()
        history_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        history_container.bind(minimum_height=history_container.setter('height'))
        
        current_client = self.client_manager.get_current_client()
        readings = current_client.get("readings", []) if current_client else []
        
        if not readings:
            no_history = Label(
                text=f"📖 No readings yet for {self.client_manager.get_current_client_name()}.\n\nStart their tarot journey with a reading!",
                font_size='16sp', 
                color=(0.7, 0.7, 0.7, 1), 
                size_hint_y=None, 
                height=100, 
                halign='center'
            )
            no_history.bind(size=no_history.setter('text_size'))
            history_container.add_widget(no_history)
        else:
            for i, reading in enumerate(readings[:50]):  # Show last 50 readings
                try:
                    date_str = datetime.fromisoformat(reading["date"]).strftime("%B %d, %Y at %I:%M %p")
                except:
                    date_str = "Unknown date"
                
                # Create reading item
                item_layout = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=100,
                    padding=10,
                    spacing=5
                )
                
                # Background
                with item_layout.canvas.before:
                    Color(0.1, 0.1, 0.2, 0.5)
                    rect = Rectangle(pos=item_layout.pos, size=item_layout.size)
                    item_layout.bg_rect = rect
                
                item_layout.bind(pos=self._update_item_bg, size=self._update_item_bg)
                
                spread_label = Label(
                    text=f"🔮 {reading.get('spread', 'Unknown Spread')}",
                    font_size='16sp',
                    bold=True,
                    color=(1, 1, 0.8, 1),
                    size_hint_y=0.4,
                    halign='left'
                )
                spread_label.bind(size=spread_label.setter('text_size'))
                
                details_label = Label(
                    text=f"📅 {date_str}\n🃏 {len(reading.get('cards', []))} cards drawn",
                    font_size='12sp',
                    color=(0.9, 0.9, 0.9, 1),
                    size_hint_y=0.6,
                    halign='left'
                )
                details_label.bind(size=details_label.setter('text_size'))
                
                item_layout.add_widget(spread_label)
                item_layout.add_widget(details_label)
                history_container.add_widget(item_layout)
        
        scroll.add_widget(history_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)
    
    def _update_item_bg(self, instance, *args):
        """Update item background rectangle"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def show_journal(self):
        """Show journal entries for current client"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
