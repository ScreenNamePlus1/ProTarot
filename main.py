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
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.logger import Logger
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

# Force portrait orientation and set mystical dark background
Window.clearcolor = (0.05, 0.05, 0.15, 1)  # Deep purple-black

# Enhanced card definitions with meanings
suits = ["Wands", "Cups", "Swords", "Pentacles"]
ranks = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
major_arcana = ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers",
                "The Chariot", "Strength", "The Hermit", "Wheel of Fortune", "Justice", "The Hanged Man", "Death",
                "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"]

# Card meanings database
CARD_MEANINGS = {
    # Major Arcana
    "The Fool": {
        "upright": "New beginnings, innocence, spontaneity, free spirit",
        "reversed": "Recklessness, taken advantage of, inconsideration"
    },
    "The Magician": {
        "upright": "Manifestation, resourcefulness, power, inspired action",
        "reversed": "Manipulation, poor planning, untapped talents"
    },
    "Death": {
        "upright": "Endings, transformation, transition, new beginnings",
        "reversed": "Resistance to change, personal transformation, inner purging"
    },
    "The Star": {
        "upright": "Hope, faith, purpose, renewal, spirituality",
        "reversed": "Lack of faith, despair, self-trust, disconnection"
    },
}

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
        "positions": ["You in love", "Your partner", "The relationship", "Challenges", "Outcome"],
        "description": "Deep dive into your romantic life"
    },
    "Career Path": {
        "cards": 4,
        "positions": ["Current career", "Hidden talents", "Obstacles", "Next steps"],
        "description": "Navigate your professional journey"
    },
    "Celtic Cross": {
        "cards": 10,
        "positions": ["Present", "Challenge", "Distant Past", "Recent Past", "Possible Outcome", 
                     "Near Future", "Your Approach", "External Influences", "Hopes & Fears", "Final Outcome"],
        "description": "The most comprehensive tarot spread"
    },
    "Chakra Balance": {
        "cards": 7,
        "positions": ["Root Chakra", "Sacral Chakra", "Solar Plexus", "Heart Chakra", 
                     "Throat Chakra", "Third Eye", "Crown Chakra"],
        "description": "Align your spiritual energy centers"
    },
    "Essential Oil Guidance": {
        "cards": 3,
        "positions": ["Physical needs", "Emotional needs", "Spiritual needs"],
        "description": "Perfect for DoTerra consultations"
    }
}

# Create full deck
tarot_cards = []
for suit in suits:
    for rank in ranks:
        tarot_cards.append(f"{rank} of {suit}")
tarot_cards.extend(major_arcana)


class MysticalButton(Button):
    """Mystical-themed button with proper text display"""
    def __init__(self, text="", **kwargs):
        # Set default styling
        kwargs.setdefault('background_color', (0.2, 0.1, 0.4, 0.9))
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('bold', True)
        
        super().__init__(text=text, **kwargs)
        
        # Add mystical border effect
        with self.canvas.before:
            Color(0.4, 0.2, 0.6, 0.8)
            self.border = Rectangle(pos=self.pos, size=self.size)
        
        with self.canvas.after:
            Color(0.15, 0.05, 0.25, 0.9)
            self.inner_rect = Rectangle(
                pos=(self.x + 2, self.y + 2), 
                size=(self.width - 4, self.height - 4)
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size
        self.inner_rect.pos = (self.x + 2, self.y + 2)
        self.inner_rect.size = (self.width - 4, self.height - 4)


class ClientButton(MysticalButton):
    """Special button for client selection with different colors"""
    def __init__(self, client_name, is_active=False, **kwargs):
        self.client_name = client_name
        self.is_active = is_active
        
        # Different colors for active client
        if is_active:
            kwargs['background_color'] = (0.3, 0.6, 0.2, 0.9)  # Green for active
        else:
            kwargs['background_color'] = (0.2, 0.1, 0.4, 0.9)  # Purple for inactive
            
        super().__init__(text=f"👤 {client_name}", **kwargs)


class AnimatedButton(ButtonBehavior, FloatLayout):
    """Animated button with glow effects"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_size = None
        
    def on_press(self):
        if not self.original_size:
            self.original_size = self.size[:]
        # Subtle press animation
        anim = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.1)
        anim.bind(on_complete=lambda *x: Animation(size=self.original_size, duration=0.1).start(self))
        anim.start(self)


class TarotCardImage(AnimatedButton, Image):
    """Enhanced tarot card with animations and sound"""
    def __init__(self, card_name, orientation, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.card_name = card_name
        self.orientation = orientation
        self.is_revealed = False
        self.app_instance = app_instance
        
        # Apply rotation immediately if reversed
        if orientation == "Reversed":
            self._apply_rotation()
    
    def _apply_rotation(self):
        """Apply 180-degree rotation with smooth animation"""
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
        # Play card flip sound if enabled
        if self.app_instance.sound_enabled and hasattr(self.app_instance, 'flip_sound'):
            try:
                self.app_instance.flip_sound.play()
            except:
                pass


class ClientManager:
    """Manages multiple client profiles and their data"""
    def __init__(self):
        self.clients_file = "clients.json"
        self.load_clients()
        self.current_client_id = None
        
        # Create default personal profile if no clients exist
        if not self.clients:
            self.add_client("Personal", "Your personal readings", is_default=True)
    
    def load_clients(self):
        try:
            with open(self.clients_file, 'r') as f:
                data = json.load(f)
                self.clients = data.get("clients", {})
                self.current_client_id = data.get("current_client_id")
        except:
            self.clients = {}
            self.current_client_id = None
    
    def save_clients(self):
        try:
            data = {
                "clients": self.clients,
                "current_client_id": self.current_client_id
            }
            with open(self.clients_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            Logger.error(f"Failed to save clients: {e}")
    
    def add_client(self, name, description="", is_default=False):
        client_id = f"client_{len(self.clients) + 1}_{name.lower().replace(' ', '_')}"
        
        self.clients[client_id] = {
            "name": name,
            "description": description,
            "created_date": datetime.now().isoformat(),
            "readings": [],
            "journal": [],
            "settings": {
                "daily_limit": True,
                "preferred_spreads": []
            }
        }
        
        if is_default or not self.current_client_id:
            self.current_client_id = client_id
        
        self.save_clients()
        return client_id
    
    def get_current_client(self):
        if self.current_client_id and self.current_client_id in self.clients:
            return self.clients[self.current_client_id]
        return None
    
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
        
        # Keep only last 50 readings per client
        if len(self.clients[self.current_client_id]["readings"]) > 50:
            self.clients[self.current_client_id]["readings"] = self.clients[self.current_client_id]["readings"][:50]
        
        self.save_clients()
        return True
    
    def add_journal_entry_to_current_client(self, entry_text):
        if not self.current_client_id:
            return False
        
        entry = {
            "date": datetime.now().isoformat(),
            "text": entry_text
        }
        
        self.clients[self.current_client_id]["journal"].insert(0, entry)
        
        # Keep only last 100 entries per client
        if len(self.clients[self.current_client_id]["journal"]) > 100:
            self.clients[self.current_client_id]["journal"] = self.clients[self.current_client_id]["journal"][:100]
        
        self.save_clients()
        return True
    
    def check_daily_reading_done(self, spread_name="Daily Guidance"):
        """Check if daily reading was already done for current client today"""
        if not self.current_client_id:
            return False
        
        today = date.today().isoformat()
        readings = self.clients[self.current_client_id]["readings"]
        
        return any(r["date"].startswith(today) and r["spread"] == spread_name for r in readings)
    
    def delete_client(self, client_id):
        if client_id in self.clients and len(self.clients) > 1:  # Don't delete last client
            del self.clients[client_id]
            if self.current_client_id == client_id:
                self.current_client_id = list(self.clients.keys())[0]  # Switch to first available
            self.save_clients()
            return True
        return False


class PictureTarotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info("PictureTarotApp: Initializing multi-client app")
        self.client_manager = ClientManager()
        self.sound_enabled = True
        self.animation_enabled = True
        self.load_settings()
        self.load_sounds()

    def load_settings(self):
        """Load user settings"""
        try:
            with open("settings.json", 'r') as f:
                settings = json.load(f)
                self.sound_enabled = settings.get("sound_enabled", True)
                self.animation_enabled = settings.get("animation_enabled", True)
        except:
            pass  # Use defaults

    def save_settings(self):
        """Save user settings"""
        try:
            settings = {
                "sound_enabled": self.sound_enabled,
                "animation_enabled": self.animation_enabled
            }
            with open("settings.json", 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            Logger.error(f"Failed to save settings: {e}")

    def load_sounds(self):
        """Load sound effects"""
        try:
            sound_paths = ['sounds/card_flip.wav', 'sounds/flip.wav', 'card_flip.wav']
            for path in sound_paths:
                if os.path.exists(path):
                    self.flip_sound = SoundLoader.load(path)
                    break
        except:
            self.flip_sound = None

    def build(self):
        Logger.info("PictureTarotApp: Building multi-client app")
        
        # Set application icon
        icon_paths = [
            'images/AppIcons/transparent.png',
            'images/AppIcons/playstore.png',
            'images/rider-waite-tarot/CardBacks.jpg'
        ]

        for path in icon_paths:
            if os.path.exists(path):
                self.icon = path
                break

        self.main_layout = FloatLayout()
        self.show_main_menu()
        return self.main_layout

    def get_image_base_path(self):
        """Determine the correct base path for images"""
        possible_paths = ['images/rider-waite-tarot/', 'images/', '']
        for path in possible_paths:
            test_files = ['CardBacks.png', 'CardBacks.jpg', 'The_Fool.png']
            for test_file in test_files:
                if os.path.exists(f"{path}{test_file}"):
                    return path
        return 'images/'

    def get_card_image_path(self, card_name):
        """Get the correct image path for a card"""
        base_path = self.get_image_base_path()
        formatted_name = card_name.replace(" ", "_")
        
        if formatted_name == "CardBacks" or card_name == "CardBacks":
            for ext in ['.png', '.jpg', '.jpeg']:
                path = f'{base_path}CardBacks{ext}'
                if os.path.exists(path):
                    return path
            return None

        for ext in ['.png', '.jpg', '.jpeg']:
            image_path = f'{base_path}{formatted_name}{ext}'
            if os.path.exists(image_path):
                return image_path

        return self.get_card_back_path()

    def get_card_back_path(self):
        """Get the path to the card back image"""
        base_path = self.get_image_base_path()
        for ext in ['.png', '.jpg', '.jpeg']:
            path = f'{base_path}CardBacks{ext}'
            if os.path.exists(path):
                return path
        return None

    def show_main_menu(self):
        """Enhanced main menu with client switcher"""
        self.main_layout.clear_widgets()
        
        # Mystical background
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

        # Client selector at top
        client_header = BoxLayout(size_hint_y=0.15, spacing=10)
        
        current_client = self.client_manager.get_current_client_name()
        client_label = Label(
            text=f"👤 Client: {current_client}",
            font_size='18sp',
            bold=True,
            color=(0.8, 1, 0.8, 1),  # Light green
            size_hint_x=0.6
        )
        
        switch_btn = MysticalButton("Switch Client", size_hint_x=0.2)
        switch_btn.bind(on_press=lambda x: self.show_client_manager())
        
        add_client_btn = MysticalButton("+ Add Client", size_hint_x=0.2)
        add_client_btn.bind(on_press=lambda x: self.add_new_client())
        
        client_header.add_widget(client_label)
        client_header.add_widget(switch_btn)
        client_header.add_widget(add_client_btn)
        container.add_widget(client_header)

        # Mystical title
        title = Label(
            text="✦ PICTURE TAROT ✦",
            font_size='32sp',
            bold=True,
            color=(1, 1, 0.8, 1),
            outline_color=(0.3, 0.1, 0.5, 1),
            outline_width=2,
            size_hint_y=0.12
        )
        container.add_widget(title)

        # Check if daily card was drawn for current client
        daily_drawn = self.client_manager.check_daily_reading_done("Daily Guidance")

        # Menu options
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
        """Show client selection and management screen"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
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
            
            # Client info
            readings_count = len(client_data["readings"])
            journal_count = len(client_data["journal"])
            
            info_label = Label(
                text=f"📚 {readings_count} readings\n📝 {journal_count} entries",
                font_size='12sp',
                color=(0.8, 0.8, 0.8, 1),
                size_hint_x=0.3
            )
            
            # Delete button (if not the only client)
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
        
        # Add new client button
        add_btn = MysticalButton("➕ Add New Client", size_hint_y=0.1)
        add_btn.bind(on_press=lambda x: self.add_new_client())
        container.add_widget(add_btn)
        
        self.main_layout.add_widget(container)

    def switch_to_client(self, client_id):
        """Switch to a different client"""
        if self.client_manager.switch_client(client_id):
            self.show_main_menu()

    def add_new_client(self):
        """Add a new client popup"""
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
            foreground_color=(1, 1, 1, 1)
        )
        
        desc_input = TextInput(
            hint_text="Description (e.g., DoTerra consultation client)",
            multiline=True,
            size_hint_y=0.4,
            background_color=(0.2, 0.15, 0.3, 0.8),
            foreground_color=(1, 1, 1, 1)
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
            if name:
                desc = desc_input.text.strip()
                client_id = self.client_manager.add_client(name, desc)
                self.client_manager.switch_client(client_id)  # Switch to new client
                popup.dismiss()
                self.show_client_manager()
        
        add_btn.bind(on_press=add_client)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def confirm_delete_client(self, client_id):
        """Confirm client deletion"""
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
            title="Confirm Deletion",
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        def delete_client(*args):
            self.client_manager.delete_client(client_id)
            popup.dismiss()
            self.show_client_manager()
        
        delete_btn.bind(on_press=delete_client)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def start_daily_reading(self):
        """Start daily guidance reading for current client"""
        self.start_reading(1, "Daily Guidance", special=True)

    def show_spreads_menu(self):
        """Show available tarot spreads"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header with current client info
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
        
        # Scrollable spread list
        scroll = ScrollView()
        spread_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        spread_container.bind(minimum_height=spread_container.setter('height'))
        
        for spread_name, spread_info in SPREADS.items():
            if spread_name == "Daily Guidance":
                continue  # Skip daily card here
                
            spread_btn = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                height=120,
                padding=10
            )
            
            # Add mystical background
            with spread_btn.canvas.before:
                Color(0.15, 0.1, 0.25, 0.7)
                Rectangle(pos=spread_btn.pos, size=spread_btn.size)
            
            name_label = Label(
                text=f"✨ {spread_name} ({spread_info['cards']} cards)",
                font_size='18sp',
                bold=True,
                color=(1, 1, 1, 1),
                size_hint_y=0.6
            )
            
            desc_label = Label(
                text=spread_info['description'],
                font_size='14sp',
                color=(0.9, 0.9, 0.9, 1),
                size_hint_y=0.4
            )
            
            spread_btn.add_widget(name_label)
            spread_btn.add_widget(desc_label)
            
            # Make clickable
            clickable = AnimatedButton(size_hint_y=None, height=120)
            clickable.add_widget(spread_btn)
            clickable.bind(on_press=lambda btn, name=spread_name, info=spread_info: 
                          self.start_reading(info['cards'], name))
            
            spread_container.add_widget(clickable)
        
        scroll.add_widget(spread_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)

    def start_reading(self, num_cards, spread_name, special=False):
        """Start a tarot reading with enhanced features"""
        Logger.info(f"Starting {spread_name} reading with {num_cards} cards for {self.client_manager.get_current_client_name()}")
        
        self.current_cards = random.sample(tarot_cards, num_cards)
        self.current_orientations = [random.choice(["Upright", "Reversed"]) for _ in range(num_cards)]
        self.current_spread_name = spread_name
        self.current_spread_info = SPREADS.get(spread_name, {"positions": [f"Card {i+1}" for i in range(num_cards)]})
        self.card_index = 0
        self.is_special = special
        
        self.show_card_with_position()

    def show_card_with_position(self):
        """Display card with position meaning and client info"""
        self.main_layout.clear_widgets()
        
        card_name = self.current_cards[self.card_index]
        orientation = self.current_orientations[self.card_index]
        positions = self.current_spread_info["positions"]
        position = positions[self.card_index] if self.card_index < len(positions) else f"Card {self.card_index + 1}"
        
        container = BoxLayout(
            orientation='vertical',
            padding=30,
            spacing=15,
            size_hint=(0.95, 0.95),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Client and progress info
        client_info = Label(
            text=f"👤 Reading for: {self.client_manager.get_current_client_name()}",
            font_size='14sp',
            color=(0.8, 1, 0.8, 1),
            size_hint_y=0.06,
            halign='center'
        )
        client_info.bind(size=client_info.setter('text_size'))
        
        progress_text = f"✨ {self.current_spread_name} ✨\nCard {self.card_index + 1} of {len(self.current_cards)}"
        progress_label = Label(
            text=progress_text,
            font_size='16sp',
            color=(1, 1, 0.8, 1),
            size_hint_y=0.1,
            halign='center'
        )
        progress_label.bind(size=progress_label.setter('text_size'))
        
        position_label = Label(
            text=f"Position: {position}",
            font_size='18sp',
            bold=True,
            color=(0.9, 0.9, 1, 1),
            size_hint_y=0.08,
            halign='center'
        )
        position_label.bind(size=position_label.setter('text_size'))
        
        container.add_widget(client_info)
        container.add_widget(progress_label)
        container.add_widget(position_label)

        # Card image
        card_back_path = self.get_card_back_path()
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
        container.add_widget(self.current_card_widget)

        # Instructions
        instruction_label = Label(
            text="🎭 Tap the card to reveal your destiny 🎭",
            font_size='16sp',
            color=(1, 1, 0.8, 1),
            size_hint_y=0.15,
            halign='center'
        )
        instruction_label.bind(size=instruction_label.setter('text_size'))
        container.add_widget(instruction_label)

        self.main_layout.add_widget(container)

    def reveal_card_with_meaning(self, instance):
        """Reveal card with meaning and interpretation"""
        if instance.is_revealed:
            self.next_card_or_complete()
            return
            
        # Reveal the card
        card_image_path = self.get_card_image_path(instance.card_name)
        if card_image_path and os.path.exists(card_image_path):
            instance.source = card_image_path
            instance.is_revealed = True
            
            # Show meaning popup
            self.show_card_meaning_popup(instance.card_name, instance.orientation)

    def show_card_meaning_popup(self, card_name, orientation):
        """Show card meaning in a popup"""
        # Get meaning from database or create generic one
        meaning_key = orientation.lower()
        meaning = CARD_MEANINGS.get(card_name, {}).get(meaning_key, 
                  f"Meditate on the symbolism of {card_name} in {orientation.lower()} position.")
        
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
            text_size=(None, None),
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
            title="Card Revealed",
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
        """Complete the reading and save to current client"""
        # Save reading to current client
        self.client_manager.add_reading_to_current_client(
            self.current_spread_name,
            self.current_cards,
            self.current_orientations
        )
        
        # Show completion screen
        self.show_reading_complete()

    def show_reading_complete(self):
        """Show reading completion with client-specific options"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Client completion info
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
            text=f"Your {self.current_spread_name} reading for {client_name} has been saved to their personal journal.\n\nTake time to reflect on the messages revealed.",
            font_size='16sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=0.25,
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        
        # Options
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
        """Quick journal entry popup for current client"""
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
            foreground_color=(1, 1, 1, 1)
        )
        
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        save_btn = MysticalButton("Save")
        cancel_btn = MysticalButton("Cancel")
        
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(title_label)
        content.add_widget(text_input)
        content.add_widget(buttons)
        
        popup = Popup(
            title="",
            content=content,
            size_hint=(0.9, 0.6)
        )
        
        def save_entry(*args):
            if text_input.text.strip():
                self.client_manager.add_journal_entry_to_current_client(text_input.text.strip())
            popup.dismiss()
        
        save_btn.bind(on_press=save_entry)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def show_history(self):
        """Show reading history for current client"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header with client info
        header = BoxLayout(size_hint_y=0.12)
        back_btn = MysticalButton("← Back", size_hint_x=0.25)
        back_btn.bind(on_press=lambda x: self.show_main_menu())
        
        title = Label(
            text="Reading History",
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
        readings = current_client["readings"] if current_client else []
        
        if not readings:
            no_history = Label(
                text=f"No readings yet for {self.client_manager.get_current_client_name()}.\nStart their tarot journey!",
                font_size='16sp',
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=100,
                halign='center'
            )
            no_history.bind(size=no_history.setter('text_size'))
            history_container.add_widget(no_history)
        else:
            for reading in readings:
                date_str = datetime.fromisoformat(reading["date"]).strftime("%B %d, %Y at %I:%M %p")
                
                item = Label(
                    text=f"🔮 {reading['spread']}\n📅 {date_str}\n🃏 {len(reading['cards'])} cards drawn",
                    font_size='14sp',
                    color=(0.9, 0.9, 0.9, 1),
                    size_hint_y=None,
                    height=80,
                    halign='left'
                )
                item.bind(size=item.setter('text_size'))
                history_container.add_widget(item)
        
        scroll.add_widget(history_container)
        container.add_widget(scroll)
        self.main_layout.add_widget(container)

    def show_journal(self):
        """Show tarot journal for current client"""
        self.main_layout.clear_widgets()
        
        container = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header with client info and add entry button
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
        
        # Journal entries
        scroll = ScrollView()
        journal_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        journal_container.bind(minimum_height=journal_container.setter('height'))
        
        current_client = self.client_manager.get_current_client()
        entries = current_client["journal"] if current_client else []
        
        if not entries:
            no_entries = Label(
                text=f"📝 No journal entries yet for {client_name}.\nStart documenting their tarot insights!",
                font_size='16sp',
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=100,
                halign='center'
            )
            no_entries.bind(size=no_entries.setter('text_size'))
            journal_container.add_widget(no_entries)
        else:
            for entry in entries:
                date_str = datetime.fromisoformat(entry["date"]).strftime("%B %d, %Y")
                
                entry_box = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=120,
                    padding=15,
                    spacing=5
                )
                
                # Add mystical background to entry
                with entry_box.canvas.before:
                    Color(0.15, 0.1, 0.25, 0.5)
                    Rectangle(pos=entry_box.pos, size=entry_box.size)
                
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
                
                text_label = Label(
                    text=entry["text"][:150] + ("..." if len(entry["text"]) > 150 else ""),
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
        if hasattr(instance, 'canvas') and instance.canvas.before:
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.15, 0.1, 0.25, 0.5)
                Rectangle(pos=instance.pos, size=instance.size)

    def add_journal_entry(self):
        """Add new journal entry for current client"""
        client_name = self.client_manager.get_current_client_name()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        title_label = Label(
            text=f"✍️ New Entry for {client_name}",
            font_size='20sp',
            bold=True,
            color=(1, 1, 0.8, 1),
            size_hint_y=0.15
        )
        
        text_input = TextInput(
            hint_text=f"Share insights about {client_name}'s reading, reflections, or guidance...",
            multiline=True,
            size_hint_y=0.6,
            background_color=(0.2, 0.15, 0.3, 0.8),
            foreground_color=(1, 1, 1, 1)
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
            background_color=(0.05, 0.05, 0.15, 0.95),
            separator_color=(0.3, 0.2, 0.5, 1)
        )
        
        def save_entry(*args):
            if text_input.text.strip():
                self.client_manager.add_journal_entry_to_current_client(text_input.text.strip())
                popup.dismiss()
                self.show_journal()  # Refresh the journal view
        
        save_btn.bind(on_press=save_entry)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()

    def show_settings(self):
        """Show app settings with client management info"""
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
        
        # Sound setting
        sound_box = BoxLayout(size_hint_y=None, height=60, spacing=15)
        sound_label = Label(
            text="🔊 Sound Effects",
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint_x=0.7,
            halign='left'
        )
        sound_label.bind(size=sound_label.setter('text_size'))
        
        sound_switch = Switch(
            active=self.sound_enabled,
            size_hint_x=0.3
        )
        sound_switch.bind(active=self.toggle_sound)
        
        sound_box.add_widget(sound_label)
        sound_box.add_widget(sound_switch)
        
        # Animation setting
        anim_box = BoxLayout(size_hint_y=None, height=60, spacing=15)
        anim_label = Label(
            text="✨ Animations",
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint_x=0.7,
            halign='left'
        )
        anim_label.bind(size=anim_label.setter('text_size'))
        
        anim_switch = Switch(
            active=self.animation_enabled,
            size_hint_x=0.3
        )
        anim_switch.bind(active=self.toggle_animations)
        
        anim_box.add_widget(anim_label)
        anim_box.add_widget(anim_switch)
        
        settings_container.add_widget(sound_box)
        settings_container.add_widget(anim_box)
        
        # Client management button
        client_mgmt_btn = MysticalButton("👥 Manage Clients", size_hint_y=None, height=60)
        client_mgmt_btn.bind(on_press=lambda x: self.show_client_manager())
        settings_container.add_widget(client_mgmt_btn)
        
        # App info
        info_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.3)
        
        client_count = len(self.client_manager.clients)
        current_client = self.client_manager.get_current_client_name()
        
        app_info = Label(
            text=f"📱 Picture Tarot v1.0\nMulti-Client Edition ✨\n\n👥 {client_count} clients managed\n🔮 Current: {current_client}\n\nPerfect for practitioners serving multiple clients",
            font_size='14sp',
            color=(0.7, 0.7, 0.8, 1),
            halign='center'
        )
        app_info.bind(size=app_info.setter('text_size'))
        
        info_container.add_widget(app_info)
        
        container.add_widget(settings_container)
        container.add_widget(info_container)
        
        self.main_layout.add_widget(container)

    def toggle_sound(self, instance, value):
        """Toggle sound effects"""
        self.sound_enabled = value
        self.save_settings()
        Logger.info(f"Sound effects {'enabled' if value else 'disabled'}")

    def toggle_animations(self, instance, value):
        """Toggle animations"""
        self.animation_enabled = value
        self.save_settings()
        Logger.info(f"Animations {'enabled' if value else 'disabled'}")


if __name__ == '__main__':
    Logger.info("PictureTarotApp: Starting multi-client mystical application")
    PictureTarotApp().run()