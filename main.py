#!/usr/bin/env python3
"""
Minecraft Server GUI - A graphical interface for managing Minecraft servers
with plugin installation from Modrinth.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import requests
import json
import os
import sys
import psutil
from pathlib import Path
from typing import Optional


class MinecraftServerGUI:
    """Main GUI application for Minecraft Server management."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Minecraft Server GUI")
        self.root.geometry("900x700")
        
        # Server process management
        self.server_process: Optional[subprocess.Popen] = None
        self.server_thread: Optional[threading.Thread] = None
        self.server_running = False
        
        # Server configuration
        self.server_jar = tk.StringVar(value="server.jar")
        self.server_memory = tk.StringVar(value="2048")
        self.server_dir = tk.StringVar(value=os.getcwd())
        self.plugins_dir = tk.StringVar(value=os.path.join(os.getcwd(), "plugins"))
        self.server_type = tk.StringVar(value="paper")
        self.server_version = tk.StringVar(value="1.21.4")
        
        # Setup GUI
        self.setup_ui()
        
        # Check for existing server process
        self.check_existing_server()
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.server_tab = ttk.Frame(self.notebook)
        self.plugins_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.server_tab, text="Server Control")
        self.notebook.add(self.plugins_tab, text="Plugin Installer")
        self.notebook.add(self.config_tab, text="Configuration")
        
        # Setup each tab
        self.setup_server_tab()
        self.setup_plugins_tab()
        self.setup_config_tab()
    
    def setup_server_tab(self):
        """Setup the server control tab."""
        # Control buttons frame
        control_frame = ttk.LabelFrame(self.server_tab, text="Server Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status indicator
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.run_button = ttk.Button(
            button_frame, text="▶ Run Server", 
            command=self.run_server, style="Success.TButton"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.restart_button = ttk.Button(
            button_frame, text="⟲ Restart Server", 
            command=self.restart_server, state=tk.DISABLED
        )
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame, text="⬛ Stop Server", 
            command=self.stop_server, state=tk.DISABLED, style="Danger.TButton"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Console output frame
        console_frame = ttk.LabelFrame(self.server_tab, text="Server Console", padding=10)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Console text widget
        self.console_text = scrolledtext.ScrolledText(
            console_frame, wrap=tk.WORD, height=20,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white"
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
        
        # Command input frame
        command_frame = ttk.Frame(console_frame)
        command_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(command_frame, text="Command:").pack(side=tk.LEFT, padx=5)
        self.command_entry = ttk.Entry(command_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.command_entry.bind('<Return>', lambda e: self.send_command())
        
        ttk.Button(
            command_frame, text="Send", 
            command=self.send_command
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_plugins_tab(self):
        """Setup the plugin installer tab."""
        # Installed plugins frame (new feature)
        installed_frame = ttk.LabelFrame(self.plugins_tab, text="Installed Plugins", padding=10)
        installed_frame.pack(fill=tk.X, padx=10, pady=5)
        
        installed_inner_frame = ttk.Frame(installed_frame)
        installed_inner_frame.pack(fill=tk.X)
        
        # Listbox for installed plugins
        installed_list_frame = ttk.Frame(installed_inner_frame)
        installed_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.installed_plugins_listbox = tk.Listbox(
            installed_list_frame,
            height=4,
            bg="#f0f0f0",
            selectmode=tk.SINGLE
        )
        self.installed_plugins_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        installed_scrollbar = ttk.Scrollbar(
            installed_list_frame,
            orient=tk.VERTICAL,
            command=self.installed_plugins_listbox.yview
        )
        self.installed_plugins_listbox.configure(yscrollcommand=installed_scrollbar.set)
        installed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons for installed plugins
        installed_buttons_frame = ttk.Frame(installed_inner_frame)
        installed_buttons_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            installed_buttons_frame,
            text="🔄 Refresh",
            command=self.refresh_installed_plugins,
            width=12
        ).pack(pady=2)
        
        ttk.Button(
            installed_buttons_frame,
            text="🗑 Delete",
            command=self.delete_plugin,
            width=12
        ).pack(pady=2)
        
        ttk.Button(
            installed_buttons_frame,
            text="📂 Open Folder",
            command=self.open_plugins_folder,
            width=12
        ).pack(pady=2)
        
        # Search frame
        search_frame = ttk.LabelFrame(self.plugins_tab, text="Search Modrinth Plugins", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X)
        
        ttk.Label(search_input_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_input_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_plugins())
        
        ttk.Button(
            search_input_frame, text="🔍 Search",
            command=self.search_plugins
        ).pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.plugins_tab, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for results
        columns = ("Name", "Author", "Downloads", "Version")
        self.plugins_tree = ttk.Treeview(results_frame, columns=columns, show="tree headings")
        
        self.plugins_tree.heading("#0", text="")
        self.plugins_tree.column("#0", width=0, stretch=False)
        
        for col in columns:
            self.plugins_tree.heading(col, text=col)
            self.plugins_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.plugins_tree.yview)
        self.plugins_tree.configure(yscrollcommand=scrollbar.set)
        
        self.plugins_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Install button
        install_frame = ttk.Frame(self.plugins_tab)
        install_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.install_button = ttk.Button(
            install_frame, text="⬇ Install Selected Plugin",
            command=self.install_plugin, style="Success.TButton"
        )
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        # Store plugin data
        self.plugins_data = {}
        
        # Load installed plugins on startup
        self.root.after(100, self.refresh_installed_plugins)
    
    def setup_config_tab(self):
        """Setup the configuration tab."""
        # Import server frame (new feature)
        import_frame = ttk.LabelFrame(self.config_tab, text="Import Existing Server", padding=10)
        import_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(import_frame, text="Import a Minecraft server folder to automatically configure settings:").pack(anchor=tk.W, pady=5)
        
        import_button_frame = ttk.Frame(import_frame)
        import_button_frame.pack(fill=tk.X)
        
        ttk.Button(
            import_button_frame,
            text="📁 Import Server Folder",
            command=self.import_server_folder,
            style="Success.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        config_frame = ttk.LabelFrame(self.config_tab, text="Server Configuration", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Server Type and Version frame
        type_version_frame = ttk.Frame(config_frame)
        type_version_frame.pack(fill=tk.X, pady=5)
        
        # Server Type
        ttk.Label(type_version_frame, text="Server Type:").pack(side=tk.LEFT, padx=5)
        server_types = ["paper", "spigot", "bukkit", "purpur", "fabric", "forge", "vanilla"]
        server_type_combo = ttk.Combobox(
            type_version_frame,
            textvariable=self.server_type,
            values=server_types,
            state="readonly",
            width=15
        )
        server_type_combo.pack(side=tk.LEFT, padx=5)
        
        # Server Version
        ttk.Label(type_version_frame, text="Version:").pack(side=tk.LEFT, padx=(20, 5))
        common_versions = ["1.21.4", "1.21.3", "1.21.1", "1.21", "1.20.6", "1.20.4", "1.20.1", "1.19.4", "1.19.2", "1.18.2", "1.17.1", "1.16.5"]
        server_version_combo = ttk.Combobox(
            type_version_frame,
            textvariable=self.server_version,
            values=common_versions,
            width=10
        )
        server_version_combo.pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_label = ttk.Label(
            config_frame,
            text="ℹ️ Server type and version are used to filter compatible plugins",
            foreground="gray"
        )
        info_label.pack(fill=tk.X, pady=(0, 10))
        
        # Server JAR
        jar_frame = ttk.Frame(config_frame)
        jar_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(jar_frame, text="Server JAR:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(jar_frame, textvariable=self.server_jar).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(jar_frame, text="Browse", command=self.browse_jar).pack(side=tk.LEFT, padx=5)
        
        # Memory allocation
        memory_frame = ttk.Frame(config_frame)
        memory_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(memory_frame, text="Memory (MB):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(memory_frame, textvariable=self.server_memory, width=10).pack(side=tk.LEFT, padx=5)
        
        # Server directory
        dir_frame = ttk.Frame(config_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Server Directory:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(dir_frame, textvariable=self.server_dir, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_server_dir).pack(side=tk.LEFT, padx=5)
        
        # Plugins directory
        plugins_dir_frame = ttk.Frame(config_frame)
        plugins_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(plugins_dir_frame, text="Plugins Directory:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(plugins_dir_frame, textvariable=self.plugins_dir, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(plugins_dir_frame, text="Browse", command=self.browse_plugins_dir).pack(side=tk.LEFT, padx=5)
        
        # Save button
        ttk.Button(config_frame, text="💾 Save Configuration", command=self.save_config).pack(pady=10)
        
        # Info frame
        info_frame = ttk.LabelFrame(self.config_tab, text="Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """
Tips:
• Make sure you have Java installed to run the server
• Accept the EULA by editing eula.txt in the server directory
• Default server port is 25565
• Plugins must be compatible with your server version
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
    
    def check_existing_server(self):
        """Check if a Minecraft server is already running."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('minecraft' in str(arg).lower() or 'server.jar' in str(arg).lower() for arg in cmdline):
                        response = messagebox.askyesno(
                            "Server Detected",
                            "A Minecraft server appears to be running. Would you like to manage it?"
                        )
                        if response:
                            self.log_to_console("⚠ Warning: Existing server detected. You can stop it using this GUI.\n")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.log_to_console(f"Error checking for existing server: {e}\n")
    
    def run_server(self):
        """Start the Minecraft server."""
        if self.server_running:
            messagebox.showwarning("Warning", "Server is already running!")
            return
        
        jar_path = self.server_jar.get()
        if not os.path.isabs(jar_path):
            jar_path = os.path.join(self.server_dir.get(), jar_path)
        
        if not os.path.exists(jar_path):
            messagebox.showerror("Error", f"Server JAR not found: {jar_path}")
            return
        
        memory = self.server_memory.get()
        
        # Build Java command
        java_cmd = [
            "java",
            f"-Xmx{memory}M",
            f"-Xms{memory}M",
            "-jar",
            jar_path,
            "nogui"
        ]
        
        self.log_to_console(f"Starting server with command: {' '.join(java_cmd)}\n")
        self.log_to_console("=" * 60 + "\n")
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self._run_server_process, args=(java_cmd,))
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Update UI
        self.server_running = True
        self.update_server_status(True)
    
    def _run_server_process(self, cmd):
        """Run the server process in a separate thread."""
        try:
            self.server_process = subprocess.Popen(
                cmd,
                cwd=self.server_dir.get(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output
            if self.server_process.stdout:
                for line in iter(self.server_process.stdout.readline, ''):
                    if line:
                        self.log_to_console(line)
            
            self.server_process.wait()
            
        except Exception as e:
            self.log_to_console(f"\n❌ Error running server: {e}\n")
        finally:
            self.server_running = False
            self.root.after(0, lambda: self.update_server_status(False))
            self.log_to_console("\n" + "=" * 60 + "\n")
            self.log_to_console("Server stopped.\n")
    
    def stop_server(self):
        """Stop the Minecraft server."""
        if not self.server_running or not self.server_process:
            messagebox.showwarning("Warning", "Server is not running!")
            return
        
        try:
            self.log_to_console("\nSending stop command to server...\n")
            if self.server_process.stdin:
                self.server_process.stdin.write("stop\n")
                self.server_process.stdin.flush()
            
            # Wait for graceful shutdown (timeout after 30 seconds)
            self.server_process.wait(timeout=30)
            
        except subprocess.TimeoutExpired:
            self.log_to_console("Server did not stop gracefully. Terminating...\n")
            self.server_process.terminate()
            
        except Exception as e:
            self.log_to_console(f"Error stopping server: {e}\n")
            messagebox.showerror("Error", f"Failed to stop server: {e}")
    
    def restart_server(self):
        """Restart the Minecraft server."""
        if not self.server_running:
            messagebox.showwarning("Warning", "Server is not running!")
            return
        
        self.log_to_console("\n🔄 Restarting server...\n")
        self.stop_server()
        
        # Wait for server to stop, then restart
        def wait_and_restart():
            if self.server_thread:
                self.server_thread.join(timeout=35)
            self.root.after(2000, self.run_server)
        
        threading.Thread(target=wait_and_restart, daemon=True).start()
    
    def send_command(self):
        """Send a command to the running server."""
        if not self.server_running or not self.server_process:
            messagebox.showwarning("Warning", "Server is not running!")
            return
        
        command = self.command_entry.get().strip()
        if not command:
            return
        
        try:
            self.log_to_console(f"> {command}\n")
            if self.server_process.stdin:
                self.server_process.stdin.write(f"{command}\n")
                self.server_process.stdin.flush()
            self.command_entry.delete(0, tk.END)
        except Exception as e:
            self.log_to_console(f"Error sending command: {e}\n")
    
    def update_server_status(self, running: bool):
        """Update the server status UI."""
        if running:
            self.status_label.config(text="Running", foreground="green")
            self.run_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Stopped", foreground="red")
            self.run_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
    
    def log_to_console(self, text: str):
        """Log text to the console widget."""
        def _log():
            self.console_text.insert(tk.END, text)
            self.console_text.see(tk.END)
        
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, _log)
        else:
            _log()
    
    def search_plugins(self):
        """Search for plugins on Modrinth."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query!")
            return
        
        # Clear previous results
        for item in self.plugins_tree.get_children():
            self.plugins_tree.delete(item)
        
        self.plugins_data.clear()
        
        # Search in a separate thread to avoid freezing UI
        threading.Thread(target=self._search_plugins_thread, args=(query,), daemon=True).start()
    
    def _search_plugins_thread(self, query: str):
        """Search for plugins on Modrinth API."""
        try:
            server_type = self.server_type.get().lower()
            server_version = self.server_version.get()
            
            self.root.after(0, lambda: self.log_to_console(f"🔍 Searching for '{query}' (Type: {server_type}, Version: {server_version})...\n"))
            
            # Modrinth API search endpoint
            url = "https://api.modrinth.com/v2/search"
            
            # Build facets based on server type
            # Map server types to Modrinth categories/loaders
            facets = [["project_type:plugin"]]
            
            # Add loader facet based on server type
            loader_map = {
                "paper": "paper",
                "spigot": "spigot",
                "bukkit": "bukkit",
                "purpur": "purpur",
                "fabric": "fabric",
                "forge": "forge",
                "vanilla": "bukkit"  # Vanilla servers typically use bukkit plugins
            }
            
            loader = loader_map.get(server_type, "paper")
            
            # Note: Modrinth uses categories and loaders differently
            # For plugins, we'll search broadly and filter by game versions
            params = {
                "query": query,
                "facets": json.dumps(facets),
                "limit": 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hits = data.get("hits", [])
            
            if not hits:
                self.root.after(0, lambda: messagebox.showinfo("No Results", "No plugins found matching your search."))
                return
            
            # Filter results by version compatibility
            compatible_count = 0
            for hit in hits:
                project_id = hit.get("project_id", "")
                title = hit.get("title", "Unknown")
                author = hit.get("author", "Unknown")
                downloads = hit.get("downloads", 0)
                latest_version = hit.get("latest_version", "N/A")
                
                # Check version compatibility
                versions_list = hit.get("versions", [])
                game_versions = hit.get("game_versions", [])
                
                # Check if the plugin supports the selected version
                is_compatible = not server_version or server_version in game_versions or not game_versions
                
                # Store plugin data with compatibility info
                self.plugins_data[project_id] = {
                    "title": title,
                    "project_id": project_id,
                    "slug": hit.get("slug", ""),
                    "description": hit.get("description", ""),
                    "compatible": is_compatible,
                    "game_versions": game_versions
                }
                
                # Add compatibility indicator to title
                display_title = title
                if not is_compatible and game_versions:
                    display_title = f"⚠️ {title}"
                elif is_compatible:
                    display_title = f"✓ {title}"
                    compatible_count += 1
                
                # Add to treeview
                self.root.after(0, lambda t=display_title, a=author, d=downloads, v=latest_version, pid=project_id:
                    self.plugins_tree.insert("", tk.END, iid=pid, values=(t, a, f"{d:,}", v))
                )
            
            self.root.after(0, lambda: self.log_to_console(f"✓ Found {len(hits)} plugin(s) ({compatible_count} compatible with {server_version})\n"))
            
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Error", f"Failed to search plugins: {e}"))
            self.root.after(0, lambda e=e: self.log_to_console(f"❌ Search failed: {e}\n"))
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Error", f"Unexpected error: {e}"))
            self.root.after(0, lambda e=e: self.log_to_console(f"❌ Error: {e}\n"))
    
    def install_plugin(self):
        """Install the selected plugin."""
        selection = self.plugins_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a plugin to install!")
            return
        
        project_id = selection[0]
        plugin_data = self.plugins_data.get(project_id)
        
        if not plugin_data:
            messagebox.showerror("Error", "Plugin data not found!")
            return
        
        # Install in a separate thread
        threading.Thread(target=self._install_plugin_thread, args=(plugin_data,), daemon=True).start()
    
    def refresh_installed_plugins(self):
        """Refresh the list of installed plugins."""
        self.installed_plugins_listbox.delete(0, tk.END)
        
        plugins_path = Path(self.plugins_dir.get())
        
        if not plugins_path.exists():
            plugins_path.mkdir(parents=True, exist_ok=True)
            self.installed_plugins_listbox.insert(tk.END, "No plugins installed")
            return
        
        # Find all .jar files in the plugins directory
        jar_files = list(plugins_path.glob("*.jar"))
        
        if not jar_files:
            self.installed_plugins_listbox.insert(tk.END, "No plugins installed")
            return
        
        # Add each plugin to the listbox
        for jar_file in sorted(jar_files):
            self.installed_plugins_listbox.insert(tk.END, jar_file.name)
        
        self.log_to_console(f"✓ Found {len(jar_files)} installed plugin(s)\n")
    
    def delete_plugin(self):
        """Delete the selected installed plugin."""
        selection = self.installed_plugins_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a plugin to delete!")
            return
        
        plugin_name = self.installed_plugins_listbox.get(selection[0])
        
        if plugin_name == "No plugins installed":
            return
        
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{plugin_name}'?\n\nThis action cannot be undone."
        )
        
        if not response:
            return
        
        try:
            plugin_path = Path(self.plugins_dir.get()) / plugin_name
            plugin_path.unlink()
            self.log_to_console(f"🗑 Deleted plugin: {plugin_name}\n")
            messagebox.showinfo("Success", f"Plugin '{plugin_name}' deleted successfully!")
            self.refresh_installed_plugins()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete plugin: {e}")
            self.log_to_console(f"❌ Failed to delete {plugin_name}: {e}\n")
    
    def import_server_folder(self):
        """Import an existing Minecraft server folder."""
        directory = filedialog.askdirectory(
            title="Select Minecraft Server Folder"
        )
        
        if not directory:
            return
        
        server_path = Path(directory)
        
        # Look for server JAR files
        jar_files = list(server_path.glob("*.jar"))
        server_jars = [jar for jar in jar_files if 'server' in jar.name.lower() or 
                       'paper' in jar.name.lower() or 'spigot' in jar.name.lower() or
                       'bukkit' in jar.name.lower() or 'purpur' in jar.name.lower()]
        
        if not server_jars:
            response = messagebox.askyesno(
                "No Server JAR Found",
                "No server JAR file detected in this folder.\n\nDo you still want to import this folder?"
            )
            if not response:
                return
            server_jar_name = "server.jar"
        else:
            # Use the first found server JAR
            server_jar_name = server_jars[0].name
        
        # Check for plugins directory
        plugins_path = server_path / "plugins"
        
        # Update configuration
        self.server_dir.set(str(server_path))
        self.server_jar.set(str(server_path / server_jar_name))
        
        if plugins_path.exists() and plugins_path.is_dir():
            self.plugins_dir.set(str(plugins_path))
        else:
            # Create plugins directory if it doesn't exist
            plugins_path.mkdir(exist_ok=True)
            self.plugins_dir.set(str(plugins_path))
        
        # Refresh installed plugins list
        self.refresh_installed_plugins()
        
        # Log the import
        self.log_to_console(f"\n📁 Imported server from: {directory}\n")
        self.log_to_console(f"   Server JAR: {server_jar_name}\n")
        self.log_to_console(f"   Plugins directory: {self.plugins_dir.get()}\n")
        
        # Check for plugins
        jar_files_in_plugins = list(plugins_path.glob("*.jar")) if plugins_path.exists() else []
        if jar_files_in_plugins:
            self.log_to_console(f"   Found {len(jar_files_in_plugins)} plugin(s)\n")
        
        # Save configuration
        self.save_config()
        
        messagebox.showinfo(
            "Import Successful",
            f"Server imported successfully!\n\n"
            f"Server JAR: {server_jar_name}\n"
            f"Plugins found: {len(jar_files_in_plugins)}\n\n"
            f"Configuration has been saved."
        )
    
    def _install_plugin_thread(self, plugin_data: dict):
        """Download and install the plugin."""
        try:
            title = plugin_data.get("title", "Unknown")
            project_id = plugin_data.get("project_id", "")
            server_version = self.server_version.get()
            server_type = self.server_type.get().lower()
            
            self.root.after(0, lambda: self.log_to_console(f"\n📥 Installing plugin: {title}...\n"))
            
            # Get project versions
            url = f"https://api.modrinth.com/v2/project/{project_id}/version"
            params = {}
            
            # Filter by game version if specified
            if server_version:
                params["game_versions"] = f'["{server_version}"]'
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            versions = response.json()
            
            # If no versions found for specific version, try without filter
            if not versions and server_version:
                self.root.after(0, lambda: self.log_to_console(f"⚠️ No version found for {server_version}, trying latest...\n"))
                response = requests.get(f"https://api.modrinth.com/v2/project/{project_id}/version", timeout=10)
                response.raise_for_status()
                versions = response.json()
            
            if not versions:
                self.root.after(0, lambda: messagebox.showerror("Error", "No versions available for this plugin!"))
                return
            
            # Find the best matching version
            best_version = None
            for version in versions:
                version_game_versions = version.get("game_versions", [])
                version_loaders = version.get("loaders", [])
                
                # Check if version matches our server version and type
                version_matches = not server_version or server_version in version_game_versions
                loader_matches = not server_type or server_type in version_loaders or not version_loaders
                
                if version_matches:
                    best_version = version
                    break
            
            # If no matching version found, use the latest
            if not best_version:
                best_version = versions[0]
                version_info = best_version.get("game_versions", [])
                self.root.after(0, lambda v=version_info: self.log_to_console(f"⚠️ Using latest version (supports: {', '.join(v[:3]) if v else 'unknown'})\n"))
            else:
                version_info = best_version.get("game_versions", [])
                self.root.after(0, lambda v=version_info: self.log_to_console(f"✓ Found compatible version (supports: {', '.join(v[:3]) if v else 'unknown'})\n"))
            
            files = best_version.get("files", [])
            
            if not files:
                self.root.after(0, lambda: messagebox.showerror("Error", "No downloadable files found!"))
                return
            
            # Download the primary file
            file_data = files[0]
            download_url = file_data.get("url")
            filename = file_data.get("filename", f"{project_id}.jar")
            
            # Ensure plugins directory exists
            plugins_path = Path(self.plugins_dir.get())
            plugins_path.mkdir(parents=True, exist_ok=True)
            
            # Download file
            self.root.after(0, lambda: self.log_to_console(f"Downloading {filename}...\n"))
            
            file_response = requests.get(download_url, timeout=30)
            file_response.raise_for_status()
            
            # Save file
            output_path = plugins_path / filename
            with open(output_path, 'wb') as f:
                f.write(file_response.content)
            
            self.root.after(0, lambda: self.log_to_console(f"✓ Successfully installed {title} to {output_path}\n"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Plugin '{title}' installed successfully!\n\nLocation: {output_path}"))
            
            # Refresh the installed plugins list
            self.root.after(0, self.refresh_installed_plugins)
            
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Error", f"Failed to download plugin: {e}"))
            self.root.after(0, lambda e=e: self.log_to_console(f"❌ Installation failed: {e}\n"))
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Error", f"Unexpected error: {e}"))
            self.root.after(0, lambda e=e: self.log_to_console(f"❌ Error: {e}\n"))
    
    def open_plugins_folder(self):
        """Open the plugins folder in file explorer."""
        plugins_path = Path(self.plugins_dir.get())
        plugins_path.mkdir(parents=True, exist_ok=True)
        
        try:
            if sys.platform == 'win32':
                os.startfile(plugins_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', plugins_path])
            else:
                subprocess.run(['xdg-open', plugins_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")
    
    def browse_jar(self):
        """Browse for server JAR file."""
        filename = filedialog.askopenfilename(
            initialdir=self.server_dir.get(),
            title="Select Server JAR",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if filename:
            self.server_jar.set(filename)
    
    def browse_server_dir(self):
        """Browse for server directory."""
        directory = filedialog.askdirectory(
            initialdir=self.server_dir.get(),
            title="Select Server Directory"
        )
        if directory:
            self.server_dir.set(directory)
            self.plugins_dir.set(os.path.join(directory, "plugins"))
    
    def browse_plugins_dir(self):
        """Browse for plugins directory."""
        directory = filedialog.askdirectory(
            initialdir=self.plugins_dir.get(),
            title="Select Plugins Directory"
        )
        if directory:
            self.plugins_dir.set(directory)
    
    def save_config(self):
        """Save configuration to file."""
        config = {
            "server_jar": self.server_jar.get(),
            "server_memory": self.server_memory.get(),
            "server_dir": self.server_dir.get(),
            "plugins_dir": self.plugins_dir.get(),
            "server_type": self.server_type.get(),
            "server_version": self.server_version.get()
        }
        
        try:
            with open("server_config.json", "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists("server_config.json"):
                with open("server_config.json", "r") as f:
                    config = json.load(f)
                
                self.server_jar.set(config.get("server_jar", "server.jar"))
                self.server_memory.set(config.get("server_memory", "2048"))
                self.server_dir.set(config.get("server_dir", os.getcwd()))
                self.plugins_dir.set(config.get("plugins_dir", os.path.join(os.getcwd(), "plugins")))
                self.server_type.set(config.get("server_type", "paper"))
                self.server_version.set(config.get("server_version", "1.21.4"))
        except Exception as e:
            self.log_to_console(f"Warning: Could not load configuration: {e}\n")


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Setup custom styles
    style = ttk.Style()
    
    # Try to use a modern theme if available
    try:
        style.theme_use('clam')
    except:
        pass
    
    app = MinecraftServerGUI(root)
    app.load_config()
    
    # Handle window close
    def on_closing():
        if app.server_running:
            if messagebox.askokcancel("Quit", "Server is still running. Do you want to stop it and quit?"):
                app.stop_server()
                root.after(2000, root.destroy)
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()