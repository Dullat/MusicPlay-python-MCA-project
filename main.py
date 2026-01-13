from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QSlider, QListWidget, 
                             QListWidgetItem, QScrollArea, QFrame, QFileDialog,
                             QLineEdit, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import sys
import os
from pathlib import Path
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
import io

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setFixedWidth(230)
        self.setStyleSheet("""
            background-color: #000000;
            color: #b3b3b3;
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        #logo and title
        logo = QLabel("♫ MyMusic")
        logo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(logo)
        #navigation
        self.home_btn = self.create_nav_button("🏠 Home")
        self.search_btn = self.create_nav_button("🔍 Search")
        library_btn = self.create_nav_button("📚 Your Library")

        self.home_btn.clicked.connect(lambda: self.main_window.switch_page(0))
        self.search_btn.clicked.connect(lambda: self.main_window.switch_page(1))

        layout.addWidget(self.home_btn)
        layout.addWidget(self.search_btn)
        layout.addWidget(library_btn)
        
        layout.addSpacing(20)
        #
        # folder selection btn
        self.folder_btn = QPushButton("📁 Select Music Folder")
        self.folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #1db954;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        self.folder_btn.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b3b3b3;
                border: none;
                text-align: left;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        return btn
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if folder:
            self.main_window.load_music_folder(folder)

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.setStyleSheet("""
            background-color: #121212;
            color: white;
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        
        # nav arrows // set nav switch later
        back_btn = QPushButton("◀")
        forward_btn = QPushButton("▶")
        
        for btn in [back_btn, forward_btn]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0,0,0,0.7);
                    border-radius: 16px;
                    color: white;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(40,40,40,0.9);
                }
            """)
        
        layout.addWidget(back_btn)
        layout.addWidget(forward_btn)
        layout.addStretch()
        
        self.setLayout(layout)

class MusicCard(QWidget):
    def __init__(self, title, artist, file_path, album_art=None, parent=None):
        super().__init__()
        self.file_path = file_path
        self.parent_window = parent
        self.setFixedSize(160, 220)
        self.setStyleSheet("""
            QWidget {
                background-color: #181818;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #282828;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # album art
        self.album_art = QLabel()
        self.album_art.setFixedSize(130, 130)
        self.album_art.setStyleSheet("""
            background-color: #282828;
            border-radius: 8px;
        """)
        self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if album_art:
            pixmap = QPixmap()
            pixmap.loadFromData(album_art)
            scaled_pixmap = pixmap.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                         Qt.TransformationMode.SmoothTransformation)
            self.album_art.setPixmap(scaled_pixmap)
        else:
            self.album_art.setText("🎵")
            self.album_art.setStyleSheet(self.album_art.styleSheet() + "font-size: 48px;")
        
        title_label = QLabel(title[:20] + "..." if len(title) > 20 else title)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        title_label.setWordWrap(True)
        
        artist_label = QLabel(artist[:20] + "..." if len(artist) > 20 else artist)
        artist_label.setStyleSheet("color: #b3b3b3; font-size: 12px;")
        
        layout.addWidget(self.album_art)
        layout.addWidget(title_label)
        layout.addWidget(artist_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # make it clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if self.parent_window:
            self.parent_window.play_song(self.file_path)

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.main_window = parent
        self.setStyleSheet("background-color: #121212;")
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 100)
        
        # section title
        self.title = QLabel("Your Music Library")
        self.title.setStyleSheet("color: white; font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title)
        
        # scrool for music cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
            QScrollBar:vertical {
                background-color: #121212;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #282828;
                border-radius: 6px;
            }
        """)
        
        self.cards_widget = QWidget()
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.cards_widget.setLayout(self.cards_layout)
        
        scroll.setWidget(self.cards_widget)
        self.main_layout.addWidget(scroll)
        
        self.setLayout(self.main_layout)
    
    def add_song_card(self, title, artist, file_path, album_art):
        card = MusicCard(title, artist, file_path, album_art, self.main_window)
        self.cards_layout.addWidget(card)

class SearchPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.main_window = parent
        self.setStyleSheet("background-color: #121212;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 100)
        
        # search title
        title = QLabel("Search")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("What do you want to listen to?")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 14px;
                color: black;
            }
        """)
        self.search_input.setFixedWidth(400)
        self.search_input.textChanged.connect(self.perform_search)
        layout.addWidget(self.search_input)
        
        layout.addSpacing(20)
        
        # search results
        self.results_label = QLabel("Search for songs, artists, or albums")
        self.results_label.setStyleSheet("color: #b3b3b3; font-size: 16px;")
        layout.addWidget(self.results_label)
        
        # scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
            QScrollBar:vertical {
                background-color: #121212;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #282828;
                border-radius: 6px;
            }
        """)
        
        self.results_widget = QWidget()
        self.results_layout = QHBoxLayout()
        self.results_layout.setSpacing(20)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.results_widget.setLayout(self.results_layout)
        
        scroll.setWidget(self.results_widget)
        layout.addWidget(scroll)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def perform_search(self, query):
        # clear previous results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not query or not self.main_window.music_library:
            self.results_label.setText("Search for songs, artists, or albums")
            return
        
        query = query.lower()
        results = []
        
        for song_info in self.main_window.music_library:
            if (query in song_info['title'].lower() or 
                query in song_info['artist'].lower()):
                results.append(song_info)
        
        if results:
            self.results_label.setText(f"Found {len(results)} result(s)")
            for song in results[:10]:  # Limit to 10 results
                card = MusicCard(song['title'], song['artist'], 
                               song['path'], song['album_art'], self.main_window)
                self.results_layout.addWidget(card)
        else:
            self.results_label.setText("No results found")

class NowPlayingBar(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.main_window = parent
        self.setFixedHeight(90)
        self.setStyleSheet("""
            background-color: transparent;
        """)
        
        # main player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        
        # playlist tracking
        self.current_index = -1
        
        # connect signals
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # top row
        top_layout = QHBoxLayout()
        
        # left: Song info
        song_info_layout = QHBoxLayout()
        song_info_layout.setSpacing(15)
        
        self.album_thumb = QLabel("🎵")
        self.album_thumb.setFixedSize(56, 56)
        self.album_thumb.setStyleSheet("""
            background-color: #282828;
            border-radius: 4px;
            font-size: 24px;
        """)
        self.album_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        song_details = QWidget()
        song_details_layout = QVBoxLayout()
        song_details_layout.setSpacing(2)
        song_details_layout.setContentsMargins(0, 8, 0, 0)
        
        self.song_title = QLabel("No Song Playing")
        self.song_title.setStyleSheet("color: white; font-size: 14px; font-weight: 500; background-color: transparent")
        
        self.song_artist = QLabel("Select a song to play")
        self.song_artist.setStyleSheet("color: #b3b3b3; font-size: 12px;")
        
        song_details_layout.addWidget(self.song_title)
        song_details_layout.addWidget(self.song_artist)
        song_details.setLayout(song_details_layout)
        
        song_info_layout.addWidget(self.album_thumb)
        song_info_layout.addWidget(song_details)
        
        # center: Controls
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        shuffle_btn = self.create_control_button("🔀", 30)
        self.prev_btn = self.create_control_button("⏮", 30)
        self.prev_btn.clicked.connect(self.play_previous)
        self.play_btn = self.create_control_button("▶", 36)
        self.play_btn.clicked.connect(self.toggle_play)
        self.next_btn = self.create_control_button("⏭", 30)
        self.next_btn.clicked.connect(self.play_next)
        repeat_btn = self.create_control_button("🔁", 30)
        
        buttons_layout.addStretch()
        # buttons_layout.addWidget(shuffle_btn)
        buttons_layout.addWidget(self.prev_btn)
        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.next_btn)
        # buttons_layout.addWidget(repeat_btn)
        buttons_layout.addStretch()
        
        controls_layout.addLayout(buttons_layout)
        
        # right: Volume
        volume_layout = QHBoxLayout()
        volume_icon = QLabel("🔊")
        volume_icon.setStyleSheet("color: #b3b3b3;")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setStyleSheet(self.slider_style())
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        volume_layout.addStretch()
        volume_layout.addWidget(volume_icon)
        volume_layout.addWidget(self.volume_slider)
        
        top_layout.addLayout(song_info_layout)
        top_layout.addStretch()
        top_layout.addLayout(controls_layout)
        top_layout.addStretch()
        top_layout.addLayout(volume_layout)
        
        # bottom: Progress bar
        progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("0:00")
        self.time_label.setStyleSheet("color: #b3b3b3; font-size: 11px;")
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet(self.slider_style())
        self.progress_slider.sliderMoved.connect(self.seek_position)
        
        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("color: #b3b3b3; font-size: 11px;")
        
        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.duration_label)
        
        layout.addLayout(top_layout)
        layout.addLayout(progress_layout)
        
        self.setLayout(layout)
    
    def create_control_button(self, icon, size):
        btn = QPushButton(icon)
        btn.setFixedSize(size, size)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: #b3b3b3;
                font-size: {size-8}px;
                border-radius: {size//2}px;
            }}
            QPushButton:hover {{
                color: white;
                background-color: rgba(255,255,255,0.1);
            }}
        """)
        return btn
    
    def slider_style(self):
        return """
            QSlider::groove:horizontal {
                background: #4d4d4d;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #1db954;
                border-radius: 2px;
            }
        """
    
    def load_song(self, file_path, title, artist, album_art):
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.song_title.setText(title)
        self.song_artist.setText(artist)
        
        if album_art:
            pixmap = QPixmap()
            pixmap.loadFromData(album_art)
            scaled_pixmap = pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                         Qt.TransformationMode.SmoothTransformation)
            self.album_thumb.setPixmap(scaled_pixmap)
        else:
            self.album_thumb.setText("🎵")
        
        self.player.play()
        self.play_btn.setText("⏸")
    
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("▶")
        else:
            self.player.play()
            self.play_btn.setText("⏸")
    
    def play_next(self):
        if self.main_window.music_library and self.current_index >= 0:
            self.current_index = (self.current_index + 1) % len(self.main_window.music_library)
            song_info = self.main_window.music_library[self.current_index]
            self.load_song(
                song_info['path'],
                song_info['title'],
                song_info['artist'],
                song_info['album_art']
            )
    
    def play_previous(self):
        if self.main_window.music_library and self.current_index >= 0:
            self.current_index = (self.current_index - 1) % len(self.main_window.music_library)
            song_info = self.main_window.music_library[self.current_index]
            self.load_song(
                song_info['path'],
                song_info['title'],
                song_info['artist'],
                song_info['album_art']
            )
    
    def on_playback_state_changed(self, state):
        # auto play next song
        if state == QMediaPlayer.PlaybackState.StoppedState and self.player.position() > 0:
            self.play_next()
    
    def update_position(self, position):
        self.progress_slider.blockSignals(True)
        self.progress_slider.setValue(position)
        self.progress_slider.blockSignals(False)
        mins = position // 60000
        secs = (position % 60000) // 1000
        self.time_label.setText(f"{mins}:{secs:02d}")
    
    def update_duration(self, duration):
        self.progress_slider.setMaximum(duration)
        mins = duration // 60000
        secs = (duration % 60000) // 1000
        self.duration_label.setText(f"{mins}:{secs:02d}")
    
    def seek_position(self, position):
        self.player.setPosition(position)
    
    def change_volume(self, value):
        self.audio_output.setVolume(value / 100)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyMusic Player")
        self.resize(1200, 700)
        self.setStyleSheet("background-color: #121212;")
        
        self.music_library = []
        
        # main container
        container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        container.setLayout(main_layout)
        
        # top
        content_row = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_row.setLayout(content_layout)
        
        # sidebar
        sidebar = Sidebar(self)
        content_layout.addWidget(sidebar)
        
        # right section with pages
        right_section = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_section.setLayout(right_layout)
        
        topbar = TopBar()
        right_layout.addWidget(topbar)
        
        # stacked widget for pages
        self.pages = QStackedWidget()
        self.home_page = HomePage(self)
        self.search_page = SearchPage(self)
        
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.search_page)
        
        right_layout.addWidget(self.pages)
        content_layout.addWidget(right_section)
        
        main_layout.addWidget(content_row)
        
        # Now playing bar
        self.now_playing = NowPlayingBar(self)
        main_layout.addWidget(self.now_playing)
        
        self.setCentralWidget(container)
    
    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
    
    def load_music_folder(self, folder_path):
        self.music_library.clear()
        
        # cleaer existing cards
        while self.home_page.cards_layout.count():
            child = self.home_page.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        #  formats
        audio_extensions = ['.mp3', '.flac', '.m4a', '.ogg', '.wav']
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    file_path = os.path.join(root, file)
                    song_info = self.extract_metadata(file_path)
                    if song_info:
                        self.music_library.append(song_info)
                        self.home_page.add_song_card(
                            song_info['title'],
                            song_info['artist'],
                            song_info['path'],
                            song_info['album_art']
                        )
        
        self.home_page.title.setText(f"Your Music Library ({len(self.music_library)} songs)")
    
    def extract_metadata(self, file_path):
        try:
            audio = MutagenFile(file_path)
            if audio is None:
                return None
            
            title = "Unknown Title"
            artist = "Unknown Artist"
            album_art = None
            
            # extract title and artist
            if hasattr(audio, 'tags') and audio.tags:
                title = str(audio.tags.get('TIT2', audio.tags.get('title', [Path(file_path).stem]))[0])
                artist = str(audio.tags.get('TPE1', audio.tags.get('artist', ['Unknown Artist']))[0])
                
                # extract album art
                if isinstance(audio.tags, ID3):
                    for tag in audio.tags.values():
                        if isinstance(tag, APIC):
                            album_art = tag.data
                            break
            elif isinstance(audio, MP4):
                title = audio.tags.get('\xa9nam', [Path(file_path).stem])[0]
                artist = audio.tags.get('\xa9ART', ['Unknown Artist'])[0]
                if 'covr' in audio.tags:
                    album_art = bytes(audio.tags['covr'][0])
            elif isinstance(audio, FLAC):
                title = audio.get('title', [Path(file_path).stem])[0]
                artist = audio.get('artist', ['Unknown Artist'])[0]
                if audio.pictures:
                    album_art = audio.pictures[0].data
            else:
                title = Path(file_path).stem
            
            return {
                'title': title,
                'artist': artist,
                'path': file_path,
                'album_art': album_art
            }
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def play_song(self, file_path):
        # find song info and index
        for idx, song_info in enumerate(self.music_library):
            if song_info['path'] == file_path:
                self.now_playing.current_index = idx
                self.now_playing.load_song(
                    file_path,
                    song_info['title'],
                    song_info['artist'],
                    song_info['album_art']
                )
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
