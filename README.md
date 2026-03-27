# Minecraft Server GUI

A modern, user-friendly graphical interface for managing Minecraft servers with integrated plugin installation from Modrinth.

## Features

### 🎮 Server Management
- **Run Server**: Start your Minecraft server with customizable memory allocation
- **Auto-Download**: Automatically download server JARs (Paper, Purpur, Fabric, etc.) if not found
- **Restart Server**: Gracefully restart the server without losing progress
- **Stop Server**: Safely shutdown the server
- **Real-time Console**: View server logs in real-time with a dark theme console
- **Command Input**: Send commands directly to the server from the GUI
- **Import Server Folder**: Automatically configure settings by importing an existing Minecraft server folder

### 🔌 Plugin Management
- **Installed Plugins Display**: View all currently installed plugins in your plugins folder
- **Search Modrinth**: Search for Minecraft plugins directly from Modrinth's extensive library
- **One-Click Install**: Download and install plugins with a single click
- **Compatibility Filtering**: Automatically filters plugins based on your server type and version
- **Delete Plugins**: Remove unwanted plugins directly from the GUI
- **Refresh Plugin List**: Update the installed plugins list with a single click
- **Download Statistics**: View plugin popularity and version information
- **Plugin Folder Access**: Quick access to your plugins directory

### ⚙️ Configuration
- **Server Type & Version**: Select from various server types (Paper, Fabric, Vanilla, etc.) and fetch available versions automatically
- **Server JAR Selection**: Choose your Minecraft server JAR file or let the app download it
- **Memory Allocation**: Set custom memory limits for your server
- **Directory Management**: Configure server and plugins directories
- **Persistent Settings**: Save and load your configuration automatically

## Requirements

- **Python**: 3.13 or higher
- **Java**: Required to run Minecraft server (Java 17+ recommended for modern versions)
- **Dependencies**:
  - `requests`: For Modrinth API integration
  - `psutil`: For process management

## Installation

### Using uv (Recommended)

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Clone or download this repository**

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Run the application**:
   ```bash
   uv run main.py
   ```

### Using pip

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually:
   ```bash
   pip install requests psutil
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

## Setup Guide

### First Time Setup

#### Option 1: Import Existing Server (Quickest)

1. **Import Your Server**:
   - Go to the "Configuration" tab
   - Click "📁 Import Server Folder"
   - Select your existing Minecraft server folder
   - The application will automatically detect your server JAR and plugins
   - Configuration will be saved automatically

2. **Accept EULA** (if not already done):
   - Open `eula.txt` in your server directory
   - Change `eula=false` to `eula=true`
   - Save the file

3. **Start Your Server**:
   - Go to the "Server Control" tab
   - Click "▶ Run Server"

#### Option 2: Manual Setup & Auto-Download

1. **Configure the Application**:
   - Go to the "Configuration" tab
   - Select your **Server Type** (e.g., Paper, Purpur, Fabric, Vanilla)
   - Select your desired **Version** (the app will fetch available versions automatically)
   - Set your desired memory allocation (e.g., 2048 MB for 2GB)
   - Choose your server directory

2. **Download or Select JAR**:
   - **Auto-Download**: Click "▶ Run Server" in the "Server Control" tab. If the JAR is not found, the app will ask to download it for you.
   - **Manual**: Click "Browse" next to "Server JAR" and select your own JAR file.

3. **Accept EULA**:
   - Run the server once (it will stop automatically)
   - Open `eula.txt` in your server directory
   - Change `eula=false` to `eula=true`
   - Save the file

4. **Start Your Server**:
   - Go to the "Server Control" tab
   - Click "▶ Run Server"
   - Wait for the server to start (you'll see console output)

### Managing Plugins

#### Viewing Installed Plugins
- Go to the "Plugin Installer" tab
- The "Installed Plugins" section shows all .jar files in your plugins folder
- Click "🔄 Refresh" to update the list after manual changes

#### Installing New Plugins

1. **Search for Plugins**:
   - Enter a search term (e.g., "essentials", "worldedit") in the search box
   - Click "🔍 Search" or press Enter

2. **Install Plugin**:
   - Select a plugin from the search results
   - Click "⬇ Install Selected Plugin"
   - The plugin will be downloaded to your plugins folder
   - The installed plugins list will automatically refresh

#### Removing Plugins

1. **Select Plugin**:
   - In the "Installed Plugins" section, click on a plugin to select it

2. **Delete**:
   - Click "🗑 Delete"
   - Confirm the deletion when prompted
   - The plugin will be permanently removed

#### After Plugin Changes
- Restart the server for changes to take effect using the "⟲ Restart Server" button

## Usage Tips

### Server Management
- **Console Commands**: Use the command input at the bottom of the console to send commands
- **Graceful Shutdown**: Always use the "⬛ Stop Server" button instead of closing the application
- **Memory Settings**: Allocate at least 1GB (1024MB) for small servers, 2-4GB for medium servers

### Plugin Installation
- **Compatibility**: Ensure plugins are compatible with your server version
- **Dependencies**: Some plugins require other plugins to work (check plugin descriptions)
- **Testing**: Test new plugins on a backup server before using them on production

### Configuration
- **Auto-save**: Configuration is automatically saved when you click "💾 Save Configuration"
- **Backup**: Keep backups of your server directory before making major changes
- **Port**: Default Minecraft server port is 25565

## Troubleshooting

### "Server JAR not found"
- Ensure you've selected the correct server JAR file in the Configuration tab
- Verify the file exists in the specified directory

### "Java not found"
- Install Java Runtime Environment (JRE) or Java Development Kit (JDK)
- Ensure Java is added to your system PATH
- For modern Minecraft versions, use Java 17 or higher

### Server Won't Start
- Check the console for error messages
- Verify you've accepted the EULA
- Ensure no other server is running on port 25565
- Check file permissions in the server directory

### Plugins Not Loading
- Verify plugins are in the correct plugins folder
- Check plugin compatibility with your server version
- Look for error messages in the server console
- Some plugins require a server restart to load

### Search Not Working
- Check your internet connection
- Modrinth API may be temporarily unavailable
- Try searching with different keywords

## Advanced Features

### Background Server Management
The GUI can detect if a Minecraft server is already running on your system and warn you accordingly.

### Process Monitoring
Uses `psutil` to check for existing server processes and manage resources efficiently.

### Auto-detection
Automatically creates necessary directories (like the plugins folder) if they don't exist.

## Project Structure

```
ServerGUI/
├── main.py              # Main application file
├── pyproject.toml       # Project configuration and dependencies
├── README.md            # This file
├── AGENTS.md            # Agent instructions
├── .gitignore           # Git ignore rules
├── .python-version      # Python version specification
└── server_config.json   # Saved configuration (auto-generated)
```

## API Integration

This application uses the [Modrinth API v2](https://docs.modrinth.com/) for plugin search and download functionality. The API is free and requires no authentication for basic searches.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source and available for personal and educational use.

## Support

For issues and questions:
1. Check the Troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify Java is installed and accessible
4. Check the server console for error messages

## Changelog

### Version 0.2.0 (Current)
- ✅ **NEW**: Auto-download server JARs (Paper, Purpur, Fabric, etc.)
- ✅ **NEW**: Automatic version fetching for various server types
- ✅ **NEW**: Server folder import feature
- ✅ **NEW**: Installed plugins display with refresh functionality
- ✅ **NEW**: Delete plugins directly from GUI
- ✅ **IMPROVED**: Plugins are now visible immediately after installation
- ✅ **IMPROVED**: Better plugin management workflow
- ✅ All previous features from v0.1.0

### Version 0.1.0 (Initial Release)
- ✅ Server control (Run/Restart/Stop)
- ✅ Real-time console output
- ✅ Command input
- ✅ Modrinth plugin search
- ✅ One-click plugin installation
- ✅ Configuration management
- ✅ Process detection and management

## Future Enhancements

Potential features for future versions:
- Multiple server profiles
- Backup and restore functionality
- Scheduled restarts
- Player management
- Server performance monitoring
- Plugin update notifications
- Custom server properties editor
- World management tools

---

Made with ❤️ for Minecraft server administrators