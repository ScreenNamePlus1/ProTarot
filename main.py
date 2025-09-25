import random
import json
import os
import sys
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
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle, Ellipse, Animation
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
import logging
import traceback

# Logging setup for crash and error reporting
def setup_logging():
    downloads_path = "/storage/emulated/0/Download"
    try:
        os.makedirs(downloads_path, exist_ok=True)
        log_file = os.path.join(downloads_path, "app_crash_log.txt")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        print(f"Logging set up: {log_file}")
        return log_file
    except Exception as e:
        print(f"Failed to set up logging: {e}")
        return None

def custom_exception_handler(exc_type, exc_value, exc_traceback):
    stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error(f"Unhandled exception:\n{stack_trace}")
    print(f"Crash logged to /storage/emulated/0/Download/app_crash_log.txt")
    sys.exit(1)

def log_error(tag, message, exception=None):
    full_msg = f"{tag}: {message}"
    if exception:
        full_msg += f"\n{traceback.format_exc()}"
    logging.error(full_msg)
    print(f"Error logged to /storage/emulated/0/Download/app_crash_log.txt")

def log_info(tag, message):
    logging.info(f"{tag}: {message}")
    print(f"Info logged: {message}")

# Set mystical dark gradient background (approximated)
Window.clearcolor = (0.05, 0.05, 0.25, 1)  # Approx #0a0a2e to #1a1a40

# Base path for Android compatibility
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
    "Ace of Wands": {"upright": "Inspiration, new opportunities, growth", "reversed": "Lack of energy, delayed timing, lack of direction"},
    "King of Wands": {"upright": "Natural born leader, vision, entrepreneur", "reversed": "Impulsiveness, haste, ruthless"},
}

def get_card_meaning(card_name, orientation):
    try:
        meanings = CARD_MEANINGS.get(card_name, {})
        if orientation.lower() in meanings:
            return meanings[orientation.lower()]
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
    except Exception as e:
        log_error("PictureTarot", f"Error getting card meaning for {card_name}", e)
        return f"Error retrieving meaning for {card_name}"

# Spread definitions
SPREADS = {
    "Daily Guidance": {"cards": 1, "positions": ["Your guidance for today"], "description": "A single card to guide your day"},
    "Past-Present-Future": {"cards": 3, "positions": ["Past influences", "Present situation", "Future potential"], "description": "Classic three-card timeline reading"},
    "Love & Relationships": {"cards": 5, "positions": ["You in love", "Your partner/potential", "The relationship", "Challenges to overcome", "Outcome/advice"], "description": "Deep dive into your romantic life"},
    "Career Path": {"cards": 4, "positions": ["Current career energy", "Hidden talents", "Obstacles to address", "Next steps to take"], "description": "Navigate your professional journey"},
    "Celtic Cross": {"cards": 10, "positions": ["Present situation", "Challenge/cross", "Distant past/foundation", "Recent past", "Possible outcome", "Near future", "Your approach", "External influences", "Hopes & fears", "Final outcome"], "description": "The most comprehensive tarot spread"},
    "Chakra Balance": {"cards": 7, "positions": ["Root Chakra (survival)", "Sacral Chakra (creativity)", "Solar Plexus (power)", "Heart Chakra (love)", "Throat Chakra (communication)", "Third Eye (intuition)", "Crown Chakra (spirituality)"], "description": "Align your spiritual energy centers"},
    "Essential Oil Guidance": {"cards": 3, "positions": ["Physical needs", "Emotional needs", "Spiritual needs"], "description": "Perfect for holistic wellness consultations"}
}

tarot_cards = [f"{rank} of {suit}" for suit in suits for rank in ranks] + major_arcana

class MysticalButton(Button):
    def __init__(self, text="", **kwargs):
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('font_size', '16sp')
        kwargs.setdefault('bold', True)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(60))
        super().__init__(text=text, **kwargs)
        try:
            log_info("MysticalButton", f"Initializing button: {text}")
            with self.canvas.before:
                Color(0.1, 0.1, 0.2, 0.9)
                self.border = Rectangle(pos=self.pos, size=self.size)
                Color(0.15, 0.05, 0.25, 0.9)
                self.inner_rect = Rectangle(pos=(self.x + 2, self.y + 2), size=(self.width - 4, self.height - 4))
            self.bind(pos=self._update_graphics, size=self._update_graphics)
        except Exception as e:
            log_error("MysticalButton", "Error initializing button graphics", e)

    def _update_graphics(self, *args):
        try:
            log_info("MysticalButton", f"Updating graphics for button: {self.text}")
            self.border.pos = self.pos
            self.border.size = self.size
            self.inner_rect.pos = (self.x + 2, self.y + 2)
            self.inner_rect.size = (self.width - 4, self.height - 4)
        except Exception as e:
            log_error("MysticalButton", "Error updating button graphics", e)

class ClientButton(MysticalButton):
    def __init__(self, client_name, is_active=False, **kwargs):
        self.client_name = client_name
        self.is_active = is_active
        super().__init__(text=f"👤 {client_name}", **kwargs)
        try:
            log_info("ClientButton", f"Initializing client button: {client_name}, active: {is_active}")
            with self.canvas.before:
                if is_active:
                    Color(0.3, 0.6, 0.2, 0.9)
                else:
                    Color(0.4, 0.2, 0.6, 0.8)
                self.border = Rectangle(pos=self.pos, size=self.size)
        except Exception as e:
            log_error("ClientButton", f"Error initializing button for {client_name}", e)

class AnimatedButton(ButtonBehavior, FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_size = None
        self.animation_running = False

    def on_press(self):
        try:
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
        except Exception as e:
            log_error("AnimatedButton", "Error in button press animation", e)

class TarotCardImage(AnimatedButton, Image):
    def __init__(self, card_name, orientation, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.card_name = card_name
        self.orientation = orientation
        self.is_revealed = False
        self.app_instance = app_instance
        try:
            log_info("TarotCardImage", f"Initializing card: {card_name}, orientation: {orientation}")
            if orientation == "Reversed":
                self._apply_rotation()
        except Exception as e:
            log_error("TarotCardImage", f"Error initializing card {card_name}", e)

    def _apply_rotation(self):
        try:
            log_info("TarotCardImage", f"Applying rotation to card: {self.card_name}")
            with self.canvas.before:
                PushMatrix()
                Rotate(angle=180, origin=(self.center_x, self.center_y))
            with self.canvas.after:
                PopMatrix()
            self.bind(pos=self._update_rotation, size=self._update_rotation)
        except Exception as e:
            log_error("TarotCardImage", f"Error applying rotation to {self.card_name}", e)

    def _update_rotation(self, *args):
        try:
            log_info("TarotCardImage", f"Updating rotation for card: {self.card_name}")
            if self.orientation == "Reversed":
                self.canvas.before.clear()
                self.canvas.after.clear()
                with self.canvas.before:
                    PushMatrix()
                    Rotate(angle=180, origin=(self.center_x, self.center_y))
                with self.canvas.after:
                    PopMatrix()
        except Exception as e:
            log_error("TarotCardImage", f"Error updating rotation for {self.card_name}", e)

class ParticleWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        Clock.schedule_once(self.create_particles, 0)

    def create_particles(self, dt):
        for _ in range(50):  # Match particle count from HTML
            x = random.uniform(0, Window.width)
            y = random.uniform(0, Window.height)
            with self.canvas:
                Color(1, 1, 1, 0.8)  # White with opacity
                particle = Ellipse(pos=(x, y), size=(2, 2))
            self.particles.append(particle)
            self.animate_particle(particle)

    def animate_particle(self, particle):
        anim = Animation(pos=(particle.pos[0], particle.pos[1] - 100), duration=15)
        anim += Animation(pos=particle.pos, duration=15)
        anim.repeat = True
        anim.start(particle)

class OrbWidget(Widget):
    def __init__(self, size, color, pos, delay, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        with self.canvas:
            Color(*color)
            self.orb = Ellipse(pos=pos, size=size)
        self.animate_orb(delay)

    def animate_orb(self, delay):
        anim = Animation(pos=(self.orb.pos[0] + 30, self.orb.pos[1] - 30), duration=5)
        anim += Animation(pos=(self.orb.pos[0] - 20, self.orb.pos[1] - 20), duration=5)
        anim += Animation(pos=(self.orb.pos[0] - 30, self.orb.pos[1] + 30), duration=5)
        anim += Animation(pos=self.orb.pos, duration=5)
        anim.repeat = True
        anim.start(self.orb, delay)

class MenuCard(BoxLayout):
    scale_factor = NumericProperty(1.0)

    def __init__(self, icon, title, description, callback, completed=False, **kwargs):
        super().__init__(orientation='vertical', padding=dp(25), spacing=dp(5), **kwargs)
        self.callback = callback
        self.completed = completed
        with self.canvas.before:
            Color(0, 0, 0, 0.05)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Apply daily card styling if applicable
        if "Daily" in title:
            if completed:
                with self.canvas.before:
                    Color(0.13, 0.76, 0.36, 0.1)  # Green gradient approx
                    self.rect = Rectangle(pos=self.pos, size=self.size)
            else:
                with self.canvas.before:
                    Color(1, 0.84, 0, 0.1)  # Gold gradient approx
                    self.rect = Rectangle(pos=self.pos, size=self.size)

        self.add_widget(Label(text=icon, font_size='32sp', color=(1, 1, 1, 1)))
        self.add_widget(Label(text=title, font_size='20sp', bold=True, color=(1, 1, 1, 1)))
        self.add_widget(Label(text=description if not completed else f"{description} ✅", font_size='14sp', color=(0.72, 0.72, 0.82, 1)))

        self.bind(on_touch_down=self.on_touch)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            if touch.is_double_tap:
                self.callback()
            elif not self.animation_is_active():
                anim = Animation(scale_factor=1.02, duration=0.4)
                anim.start(self)
                anim.bind(on_complete=lambda *x: Animation(scale_factor=1.0, duration=0.4).start(self))

    def animation_is_active(self):
        return any(anim.state == 'in_progress' for anim in Animation.transitions)

class ClientManager:
    # [Previous ClientManager code remains unchanged]
    pass

class PictureTarotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
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
        except Exception as e:
            log_error("PictureTarot", "Error initializing app", e)

    def load_settings(self):
        try:
            settings_file = os.path.join(self.user_data_dir, "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.animation_enabled = settings.get("animation_enabled", True)
                    log_info("PictureTarot", "Settings loaded successfully")
            else:
                log_info("PictureTarot", f"Settings file not found at {settings_file}, using defaults")
        except Exception as e:
            log_error("PictureTarot", f"Failed to load settings: {str(e)}")
            log_info("PictureTarot", "Falling back to default animation setting")
            self.animation_enabled = True

    def save_settings(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            settings = {"animation_enabled": self.animation_enabled}
            settings_file = os.path.join(self.user_data_dir, "settings.json")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            log_info("PictureTarot", "Settings saved successfully")
        except Exception as e:
            log_error("PictureTarot", f"Failed to save settings: {str(e)}")
            log_info("PictureTarot", "Failed to save settings")

    def build(self):
        log_file = setup_logging()
        if not log_file:
            log_error("PictureTarot", "Failed to set up logging to Downloads folder")
            return Label(text="Failed to access Downloads folder for logging")
        sys.excepthook = custom_exception_handler
        try:
            icon_path = os.path.join(BASE_PATH, "images", "AppIcons", "transparent.png")
            if os.path.exists(icon_path):
                self.icon = icon_path
                log_info("PictureTarot", f"App icon loaded from {icon_path}")
            else:
                log_info("PictureTarot", f"App icon not found at {icon_path}, using default")
            self.title = "Picture Tarot - Mystical Edition"
            self.main_layout = FloatLayout()
            self.particle_widget = ParticleWidget()
            self.main_layout.add_widget(self.particle_widget)
            self.orb1 = OrbWidget((dp(100), dp(100)), (0.4, 0.49, 0.92, 0.3), (dp(10), dp(Window.height * 0.1)), 0)
            self.orb2 = OrbWidget((dp(80), dp(80)), (1, 0.55, 0, 0.3), (dp(Window.width * 0.8 - 80), dp(Window.height * 0.7)), 5)
            self.orb3 = OrbWidget((dp(60), dp(60)), (0.66, 0.9, 0.81, 0.3), (dp(Window.width * 0.9 - 60), dp(Window.height * 0.4)), 10)
            self.main_layout.add_widget(self.orb1)
            self.main_layout.add_widget(self.orb2)
            self.main_layout.add_widget(self.orb3)
            self.show_main_menu()
            return self.main_layout
        except Exception as e:
            log_error("PictureTarot", "Error building main app", e)
            raise

    def get_image_base_path(self):
        try:
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
                    log_info("PictureTarot", f"Found card images at: {path}")
                    return path
            log_info("PictureTarot", "No valid image path found, using BASE_PATH")
            return BASE_PATH
        except Exception as e:
            log_error("PictureTarot", "Error finding image base path", e)
            return BASE_PATH

    def get_card_image_path(self, card_name):
        try:
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
                        log_info("PictureTarot", f"Found image for {card_name} at {image_path}")
                        return image_path
            log_info("PictureTarot", f"Card image not found for '{card_name}', using card back")
            return self.get_card_back_path()
        except Exception as e:
            log_error("PictureTarot", f"Error getting card image path for {card_name}", e)
            return self.get_card_back_path()

    def get_card_back_path(self):
        try:
            base_path = self.get_image_base_path()
            back_names = ["CardBacks", "cardback", "card_back", "back"]
            for name in back_names:
                for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                    path = os.path.join(base_path, f"{name}{ext}")
                    if os.path.exists(path):
                        log_info("PictureTarot", f"Found card back image at {path}")
                        return path
            log_info("PictureTarot", "Card back image not found")
            return None
        except Exception as e:
            log_error("PictureTarot", "Error getting card back path", e)
            return None

    def show_error_popup(self, message):
        try:
            log_info("PictureTarot", f"Showing error popup: {message}")
            content = BoxLayout(orientation='vertical', spacing=10, padding=15)
            error_label = Label(text=message, font_size='16sp', color=(1, 0.8, 0.8, 1), size_hint_y=0.7, halign='center', valign='middle', text_size=(None, None))
            error_label.bind(size=error_label.setter('text_size'))
            close_btn = MysticalButton("OK", size_hint_y=0.3)
            content.add_widget(error_label)
            content.add_widget(close_btn)
            popup = Popup(title="⚠️ Error", content=content, size_hint=(0.8, 0.4), background_color=(0.1, 0.05, 0.2, 0.95))
            close_btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            log_error("PictureTarot", f"Error showing popup: {message}", e)

    def show_main_menu(self):
        try:
            log_info("PictureTarot", "Rendering main menu")
            self.main_layout.clear_widgets()
            with self.main_layout.canvas.before:
                log_info("PictureTarot", "Setting background color")
                Color(0.05, 0.05, 0.25, 1)
                Rectangle(pos=(0, 0), size=Window.size)
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint=(0.95, 0.95), pos_hint={'center_x': 0.5, 'center_y': 0.5})
            log_info("PictureTarot", f"Container created with size_hint: {container.size_hint}, pos_hint: {container.pos_hint}")

            # Header
            header = BoxLayout(size_hint_y=0.15, padding=dp(15), spacing=dp(10), background_color=(0, 0, 0, 0.05))
            client_label = Label(text=f"👤 Client: {self.client_manager.get_current_client_name()}", font_size='16sp', color=(0.66, 0.9, 0.81, 1), size_hint_x=0.6)
            switch_btn = MysticalButton("Switch Client", size_hint_x=0.2)
            add_client_btn = MysticalButton("+ Add Client", size_hint_x=0.2)
            switch_btn.bind(on_press=lambda x: self.show_client_manager())
            add_client_btn.bind(on_press=lambda x: self.add_new_client())
            header.add_widget(client_label)
            header.add_widget(switch_btn)
            header.add_widget(add_client_btn)
            log_info("PictureTarot", "Client header widgets added")

            # Title
            title = Label(text="✦ PICTURE TAROT ✦", font_size='28sp', bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.12, pos_hint={'center_x': 0.5})
            subtitle = Label(text="UNLOCK YOUR DESTINY", font_size='16sp', color=(0.72, 0.72, 0.82, 1), size_hint_y=0.08, pos_hint={'center_x': 0.5})
            log_info("PictureTarot", "Title and subtitle created")

            # Menu options
            daily_drawn = self.client_manager.check_daily_reading_done("Daily Guidance")
            menu_options = [
                ("🔮", "Daily Card", "Receive guidance for your day ahead", lambda x: self.start_daily_reading(), not daily_drawn),
                ("📚", "Tarot Spreads", "Explore deeper with specialized readings", lambda x: self.show_spreads_menu(), True),
                ("📖", "Reading History", "Review your past revelations", lambda x: self.show_history(), True),
                ("✍️", "Client Journal", "Document insights and reflections", lambda x: self.show_journal(), True),
                ("⚙️", "Settings", "Customize your mystical experience", lambda x: self.show_settings(), True)
            ]
            container.add_widget(header)
            container.add_widget(title)
            container.add_widget(subtitle)
            for icon, title, desc, callback, enabled in menu_options:
                card = MenuCard(icon, title, desc, callback, completed=("Daily" in title and not enabled))
                container.add_widget(card)
            log_info("PictureTarot", f"Added {len(menu_options)} menu cards to container")

            scroll = ScrollView()
            scroll.add_widget(container)
            log_info("PictureTarot", "Added container to ScrollView")
            self.main_layout.add_widget(scroll)
            log_info("PictureTarot", "Main layout updated with ScrollView")
        except Exception as e:
            log_error("PictureTarot", "Error showing main menu", e)
            self.show_error_popup(f"Error displaying main menu: {str(e)}")

    def show_client_manager(self):
        try:
            self.main_layout.clear_widgets()
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            header = BoxLayout(size_hint_y=0.1)
            back_btn = MysticalButton("← Back", size_hint_x=0.3)
            back_btn.bind(on_press=lambda x: self.show_main_menu())
            title = Label(text="👥 Client Manager", font_size='24sp', bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7)
            header.add_widget(back_btn)
            header.add_widget(title)
            container.add_widget(header)
            scroll = ScrollView()
            client_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            client_container.bind(minimum_height=client_container.setter('height'))
            for client_id, client_data in self.client_manager.clients.items():
                is_active = client_id == self.client_manager.current_client_id
                client_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80), spacing=dp(10))
                client_btn = ClientButton(client_data["name"], is_active=is_active, size_hint_x=0.6)
                if not is_active:
                    client_btn.bind(on_press=lambda btn, cid=client_id: self.switch_to_client(cid))
                readings_count = len(client_data["readings"])
                journal_count = len(client_data["journal"])
                info_label = Label(text=f"📚 {readings_count} readings\n📝 {journal_count} entries", font_size='12sp', color=(0.8, 0.8, 0.8, 1), size_hint_x=0.3, halign='center')
                info_label.bind(size=info_label.setter('text_size'))
                client_box.add_widget(client_btn)
                client_box.add_widget(info_label)
                if len(self.client_manager.clients) > 1:
                    delete_btn = MysticalButton("🗑️", size_hint_x=0.1)
                    delete_btn.bind(on_press=lambda btn, cid=client_id: self.confirm_delete_client(cid))
                    client_box.add_widget(delete_btn)
                client_container.add_widget(client_box)
            scroll.add_widget(client_container)
            container.add_widget(scroll)
            add_btn = MysticalButton("➕ Add New Client", size_hint_y=0.1)
            add_btn.bind(on_press=lambda x: self.add_new_client())
            container.add_widget(add_btn)
            self.main_layout.add_widget(container)
        except Exception as e:
            log_error("PictureTarot", "Error showing client manager", e)
            self.show_error_popup(f"Error displaying client manager: {str(e)}")

    def switch_to_client(self, client_id):
        try:
            if self.client_manager.switch_client(client_id):
                self.show_main_menu()
            else:
                self.show_error_popup("Failed to switch client!")
        except Exception as e:
            log_error("PictureTarot", f"Error switching to client {client_id}", e)
            self.show_error_popup(f"Error switching client: {str(e)}")

    def add_new_client(self):
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
            title_label = Label(text="👤 Add New Client", font_size='20sp', bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.2)
            name_input = TextInput(hint_text="Client name (e.g., Sarah Johnson)", multiline=False, size_hint_y=0.2, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1), font_size='16sp')
            desc_input = TextInput(hint_text="Description (e.g., DoTerra consultation client)", multiline=True, size_hint_y=0.4, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1), font_size='14sp')
            buttons = BoxLayout(size_hint_y=0.2, spacing=dp(10))
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
        except Exception as e:
            log_error("PictureTarot", "Error adding new client", e)
            self.show_error_popup(f"Error adding client: {str(e)}")

    def confirm_delete_client(self, client_id):
        try:
            client_name = self.client_manager.clients[client_id]["name"]
            content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
            warning_label = Label(text=f"⚠️ Delete Client?\n\n'{client_name}'\n\nThis will permanently delete all readings and journal entries for this client.", font_size='16sp', color=(1, 1, 1, 1), halign='center', size_hint_y=0.7)
            warning_label.bind(size=warning_label.setter('text_size'))
            buttons = BoxLayout(size_hint_y=0.3, spacing=dp(10))
            delete_btn = MysticalButton("🗑️ Delete", background_color=(0.8, 0.2, 0.2, 0.9))
            cancel_btn = MysticalButton("❌ Cancel")
            buttons.add_widget(delete_btn)
            buttons.add_widget(cancel_btn)
            content.add_widget(warning_label)
            content.add_widget(buttons)
            popup = Popup(title="⚠️ Confirm Deletion", content=content, size_hint=(0.8, 0.5))
            def delete_client(*args):
                if self.client_manager.delete_client(client_id):
                    popup.dismiss()
                    self.show_client_manager()
                else:
                    self.show_error_popup("Cannot delete the last client!")
            delete_btn.bind(on_press=delete_client)
            cancel_btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            log_error("PictureTarot", f"Error confirming deletion of client {client_id}", e)
            self.show_error_popup(f"Error deleting client: {str(e)}")

    def start_daily_reading(self):
        try:
            if not self.client_manager.current_client_id:
                self.show_error_popup("Please select a client first!")
                return
            if self.client_manager.check_daily_reading_done("Daily Guidance"):
                self.show_error_popup("Daily reading already completed today!")
                return
            self.start_reading(1, "Daily Guidance", special=True)
        except Exception as e:
            log_error("PictureTarot", "Error starting daily reading", e)
            self.show_error_popup(f"Error starting daily reading: {str(e)}")

    def show_spreads_menu(self):
        try:
            self.main_layout.clear_widgets()
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            header = BoxLayout(size_hint_y=0.12)
            back_btn = MysticalButton("← Back", size_hint_x=0.25)
            back_btn.bind(on_press=lambda x: self.show_main_menu())
            title = Label(text="Choose Your Spread", font_size='20sp', bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.5)
            client_info = Label(text=f"👤 {self.client_manager.get_current_client_name()}", font_size='14sp', color=(0.66, 0.9, 0.81, 1), size_hint_x=0.25)
            header.add_widget(back_btn)
            header.add_widget(title)
            header.add_widget(client_info)
            container.add_widget(header)
            scroll = ScrollView()
            spread_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            spread_container.bind(minimum_height=spread_container.setter('height'))
            for spread_name, spread_info in SPREADS.items():
                if spread_name == "Daily Guidance":
                    continue
                spread_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), padding=dp(10), spacing=dp(5))
                with spread_layout.canvas.before:
                    Color(0.15, 0.1, 0.25, 0.7)
                    rect = Rectangle(pos=spread_layout.pos, size=spread_layout.size)
                    spread_layout.bg_rect = rect
                spread_layout.bind(pos=self._update_spread_bg, size=self._update_spread_bg)
                name_label = Label(text=f"✨ {spread_name} ({spread_info['cards']} cards)", font_size='18sp', bold=True, color=(1, 1, 1, 1), size_hint_y=0.6, halign='left')
                name_label.bind(size=name_label.setter('text_size'))
                desc_label = Label(text=spread_info['description'], font_size='14sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=0.4, halign='left')
                desc_label.bind(size=desc_label.setter('text_size'))
                spread_layout.add_widget(name_label)
                spread_layout.add_widget(desc_label)
                clickable = AnimatedButton(size_hint_y=None, height=dp(120))
                clickable.bind(on_press=lambda x, s=spread_name: self.start_reading(SPREADS[s]["cards"], s))
                spread_layout.add_widget(clickable)
                spread_container.add_widget(spread_layout)
            scroll.add_widget(spread_container)
            container.add_widget(scroll)
            self.main_layout.add_widget(container)
        except Exception as e:
            log_error("PictureTarot", "Error showing spreads menu", e)
            self.show_error_popup(f"Error displaying spreads menu: {str(e)}")

    def _update_spread_bg(self, instance, value):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

    def start_reading(self, num_cards, spread_name, special=False):
        try:
            self.current_spread_name = spread_name
            self.current_spread_info = SPREADS[spread_name]
            self.current_cards = random.sample(tarot_cards, num_cards)
            self.current_orientations = [random.choice(["Upright", "Reversed"]) for _ in range(num_cards)]
            self.card_index = 0
            self.is_special = special
            self.show_reading_screen()
        except Exception as e:
            log_error("PictureTarot", f"Error starting reading for {spread_name}", e)
            self.show_error_popup(f"Error starting reading: {str(e)}")

    def show_reading_screen(self):
        try:
            self.main_layout.clear_widgets()
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            header = BoxLayout(size_hint_y=0.1)
            back_btn = MysticalButton("← Back", size_hint_x=0.3)
            back_btn.bind(on_press=lambda x: self.show_main_menu())
            title = Label(text=f"{self.current_spread_name} Reading", font_size='24sp', bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7)
            header.add_widget(back_btn)
            header.add_widget(title)
            container.add_widget(header)
            scroll = ScrollView()
            card_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            card_container.bind(minimum_height=card_container.setter('height'))
            for i in range(len(self.current_cards)):
                card = TarotCardImage(self.current_cards[i], self.current_orientations[i], self, size_hint_y=None, height=dp(300))
                card.bind(on_touch_down=lambda instance, touch, idx=i: self.reveal_card(idx) if instance.collide_point(*touch.pos) else None)
                meaning = get_card_meaning(self.current_cards[i], self.current_orientations[i])
                meaning_label = Label(text=f"Position {i+1}: {meaning}", font_size='14sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(50))
                card_container.add_widget(card)
                card_container.add_widget(meaning_label)
            scroll.add_widget(card_container)
            container.add_widget(scroll)
            self.main_layout.add_widget(container)
        except Exception as e:
            log_error("PictureTarot", "Error showing reading screen", e)
            self.show_error_popup(f"Error displaying reading: {str(e)}")

    def reveal_card(self, index):
        try:
            if index == self.card_index and not self.current_card_widget.is_revealed:
                self.current_card_widget.source = self.get_card_image_path(self.current_cards[index])
                self.current_card_widget.is_revealed = True
                self.card_index += 1
                if self.card_index < len(self.current_cards):
                    self.current_card_widget = self.main_layout.children[0].children[0].children[self.card_index * 2]  # Adjust for layout
                if self.is_special and self.card_index == len(self.current_cards):
                    self.client_manager.add_reading_to_current_client(self.current_spread_name, self.current_cards, self.current_orientations)
        except Exception as e:
            log_error("PictureTarot", f"Error revealing card at index {index}", e)
            self.show_error_popup(f"Error revealing card: {str(e)}")

    def show_history(self):
        try:
            self.main_layout.clear_widgets()
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            header = BoxLayout(size_hint_y=0.1)
            back_btn = MysticalButton("← Back", size_hint_x=0.3)
            back_btn.bind(on_press=lambda x: self.show_main_menu())
            title = Label(text="Reading History", font_size='24sp', bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7)
            header.add_widget(back_btn)
            header.add_widget(title)
            container.add_widget(header)
            scroll = ScrollView()
            history_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            history_container.bind(minimum_height=history_container.setter('height'))
            client = self.client_manager.get_current_client()
            if client and client.get("readings"):
                for reading in client["readings"]:
                    date_str = datetime.fromisoformat(reading["date"]).strftime("%Y-%m-%d %H:%M")
                    text = f"{date_str} - {reading['spread']} ({len(reading['cards'])} cards)"
                    history_label = Label(text=text, font_size='16sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(40))
                    history_container.add_widget(history_label)
            else:
                history_label = Label(text="No readings found.", font_size='16sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(40))
                history_container.add_widget(history_label)
            scroll.add_widget(history_container)
            container.add_widget(scroll)
            self.main_layout.add_widget(container)
        except Exception as e:
            log_error("PictureTarot", "Error showing history", e)
            self.show_error_popup(f"Error displaying history: {str(e)}")

    def show_journal(self):
        try:
            self.main_layout.clear_widgets()
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            header = BoxLayout(size_hint_y=0.1)
            back_btn = MysticalButton("← Back", size_hint_x=0.3)
            back_btn.bind(on_press=lambda x: self.show_main_menu())
            title = Label(text="Client Journal", font_size='24sp', bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7)
            header.add_widget(back_btn)
            header.add_widget(title)
            container.add_widget(header)
            scroll = ScrollView()
            journal_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            journal_container.bind(minimum_height=journal_container.setter('height'))
            client = self.client_manager.get_current_client()
            if client and client.get("journal"):
                for entry in client["journal"]:
                    date_str = datetime.fromisoformat(entry["date"]).strftime("%Y-%m-%d %H:%M")
                    text = f"{date_str}\n{entry['text']}"
                    journal_label = Label(text=text, font_size='14sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(80))
                    journal_container.add_widget(journal_label)
            else:
                journal_label = Label(text="No journal entries found.", font_size='16sp', color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(40))
                journal_container.add_widget(journal_label)
            scroll.add_widget(journal_container)
            add_entry_btn = MysticalButton("➕ Add Entry", size_hint_y=0.1)
            add_entry_btn.bind(on_press=lambda x: self.add_journal_entry())
            container.add_widget(scroll)
            container.add_widget(add_entry_btn)
            self.main_layout.add_widget(container)
        except Exception as e:
            log_error("PictureTarot", "Error showing journal", e)
            self.show_error_popup(f"Error displaying journal: {str(e)}")

    def add_journal_entry(self):
        try:
            content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
            title_label = Label(text="✍️ Add Journal Entry", font_size='20sp', bold=True, color=(1, 1, 0.8, 1), size_hint_y=0.2)
            entry_input = TextInput(hint_text="Write your thoughts...", multiline=True, size_hint_y=0.6, background_color=(0.2, 0.15, 0.3, 0.8), foreground_color=(1, 1, 1, 1), font_size='14sp')
            buttons = BoxLayout(size_hint_y=0.2, spacing=dp(10))
            save_btn = MysticalButton("💾 Save")
            cancel_btn = MysticalButton("❌ Cancel")
            buttons.add_widget(save_btn)
            buttons.add_widget(cancel_btn)
            content.add_widget(title_label)
            content.add_widget(entry_input)
            content.add_widget(buttons)
            popup = Popup(title="", content=content, size_hint=(0.9, 0.7), background_color=(0.05, 0.05, 0.15, 0.95))
            def save_entry(*args):
                text = entry_input.text.strip()
                if text and self.client_manager.add_journal_entry_to_current_client(text):
                    popup.dismiss()
                    self.show_journal()
                else:
                    self.show_error_popup("Failed to save entry!")
            save_btn.bind(on_press=save_entry)
            cancel_btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            log_error("PictureTarot", "Error adding journal entry", e)
            self.show_error_popup(f"Error adding entry: {str(e)}")

    def show_settings(self):
        try:
            self.main_layout.clear_widgets()
            container = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            header = BoxLayout(size_hint_y=0.1)
            back_btn = MysticalButton("← Back", size_hint_x=0.3)
            back_btn.bind(on_press=lambda x: self.show_main_menu())
            title = Label(text="⚙️ Settings", font_size='24sp', bold=True, color=(1, 1, 0.8, 1), size_hint_x=0.7)
            header.add_widget(back_btn)
            header.add_widget(title)
            container.add_widget(header)
            scroll = ScrollView()
            settings_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            settings_container.bind(minimum_height=settings_container.setter('height'))
            anim_switch = Switch(active=self.animation_enabled, size_hint=(0.2, 1))
            anim_switch.bind(active=lambda instance, value: setattr(self, 'animation_enabled', value))
            anim_label = Label(text="Enable Animations", font_size='16sp', color=(0.9, 0.9, 0.9, 1), size_hint_x=0.8)
            settings_container.add_widget(anim_label)
            settings_container.add_widget(anim_switch)
            scroll.add_widget(settings_container)
            container.add_widget(scroll)
            save_btn = MysticalButton("💾 Save Settings", size_hint_y=0.1)
            save_btn.bind(on_press=lambda x: self.save_settings())
            container.add_widget(save_btn)
            self.main_layout.add_widget(container)
        except Exception as e:
            log_error("PictureTarot", "Error showing settings", e)
            self.show_error_popup(f"Error displaying settings: {str(e)}")

if __name__ == "__main__":
    PictureTarotApp().run()