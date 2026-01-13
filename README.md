# MyMusic Player 🎵

A modern, cross-platform desktop music player built with PyQt6, featuring a Spotify-like interface with album art display and metadata support.

## ✨ Features

- **Modern UI**: Spotify-inspired dark theme interface
- **Music Library**: Browse and organize your music collection
- **Smart Search**: Real-time search through your music library
- **Album Art**: Automatic extraction and display of album artwork
- **Audio Formats**: Supports MP3, FLAC, M4A, OGG, WAV
- **Playback Controls**: Play, pause, next, previous, volume, and seek
- **Metadata Support**: Reads ID3 tags for title, artist, and album information
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/MusicPlay-python-MCA-project.git
cd MusicPlay-python-MCA-project
```

2. **Create a virtual environment (optional)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install PyQt6 mutagen
```

### Running the Application

```bash
python main.py
```

## 📁 Project Structure

```
mymusic-player/
├── main.py             
├── README.md           
├── requirements.txt    
└── .gitignore          
```

## 🎮 How to Use

### 1. Adding Music
- Launch the application
- Click the "📁 Select Music Folder" button in the sidebar
- Choose a folder containing your music files
- The app will automatically scan and display all supported audio files

### 2. Playing Music
- Browse your music library on the Home page
- Click any song card to start playback
- Use the controls in the Now Playing bar:
  - ⏮ Previous song
  - ▶/⏸ Play/Pause
  - ⏭ Next song
  - 🔊 Volume slider
  - ⏺ Progress slider

### 3. Searching
- Navigate to the Search page 
- Type in the search box to find songs by title or artist
- Click on search results to play

## 🔧 Supported Audio Formats

| Format | Metadata Support | Album Art |
|--------|-----------------|-----------|
| MP3    | ✅ ID3 Tags     | ✅ Embedded |
| FLAC   | ✅ Vorbis Comments | ✅ Embedded |
| M4A    | ✅ MP4 Atoms    | ✅ Embedded |
| OGG    | ✅ Vorbis Comments | ⚠️ Limited |
| WAV    | ⚠️ Limited      | ❌ Not supported |

## 🛠 Development

### Development Environment
- **OS**: Windows/macOS/Linux
- **Python**: 3.8+
- **IDE**: Visual Studio Code, Neovim
- **Version Control**: Git + GitHub
- **Package Manager**: pip
- **Testing**: Manual testing with various audio formats

### Dependencies
```txt
PyQt6>=6.5.0          # GUI
mutagen>=1.47.0       # Audio metadata parsing
```

### Common Issues

**Issue**: "No module named 'PyQt6'"
```bash
pip install PyQt6
```

**Issue**: Album art not displaying
- Ensure your audio files have embedded album art
- Supported formats: JPEG, PNG embedded in MP3/FLAC/M4A

**Issue**: Audio not playing
- Check if file format is supported
- Ensure file path doesn't contain special characters

**Issue**: Application crashes on launch
- Verify Python version
- Try reinstalling dependencies:
```bash
pip uninstall PyQt6 mutagen -y
pip install PyQt6 mutagen
```
