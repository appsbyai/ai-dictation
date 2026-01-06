#!/usr/bin/env python3
"""
GTK Configuration Manager for AI Dictation System
A GUI tool to manage dictation settings with real-time validation and service control
"""

import sys
import os
import re
import subprocess
import ast
import configparser
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

class ConfigManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="AI Dictation Configuration")
        self.set_border_width(20)
        self.set_default_size(600, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Apply dark theme for modern look
        self.apply_dark_theme()
        
        # Config path
        self.config_path = Path.home() / ".local/share/ai-dictation/config.py"
        self.original_config = {}
        self.config = {}
        
        # Create main container
        self.create_ui()
        
        # Load current config
        self.load_config()
        
    def apply_dark_theme(self):
        """Apply dark theme if available"""
        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property("gtk-application-prefer-dark-theme", True)
    
    def create_ui(self):
        """Create the main UI with tabs"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        # Header
        header_box = self.create_header()
        main_box.pack_start(header_box, False, False, 0)
        
        # Notebook (tabs)
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_box.pack_start(notebook, True, True, 0)
        
        # Whisper Settings Tab
        whisper_tab = self.create_whisper_tab()
        notebook.append_page(whisper_tab, Gtk.Label(label="Whisper Settings"))
        
        # Audio & Processing Tab
        audio_tab = self.create_audio_tab()
        notebook.append_page(audio_tab, Gtk.Label(label="Audio & Processing"))
        
        # Text Injection Tab
        text_tab = self.create_text_tab()
        notebook.append_page(text_tab, Gtk.Label(label="Text Injection"))
        
        # Service Control Tab
        service_tab = self.create_service_tab()
        notebook.append_page(service_tab, Gtk.Label(label="Service Control"))
        
        # Button box
        button_box = self.create_button_box()
        main_box.pack_start(button_box, False, False, 0)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        main_box.pack_start(self.status_bar, False, False, 0)
        self.update_status("Ready")
    
    def create_header(self):
        """Create header with icon and title"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_bottom(10)
        
        # Icon (using emoji as placeholder)
        icon_label = Gtk.Label()
        icon_label.set_markup("<span size='24000'>🎤</span>")
        box.pack_start(icon_label, False, False, 0)
        
        # Title and subtitle
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>AI Dictation Configuration</span>")
        title.set_halign(Gtk.Align.START)
        title_box.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label()
        subtitle.set_text("Configure your voice dictation system")
        subtitle.set_halign(Gtk.Align.START)
        subtitle.get_style_context().add_class("dim-label")
        title_box.pack_start(subtitle, False, False, 0)
        
        box.pack_start(title_box, True, True, 0)
        return box
    
    def create_whisper_tab(self):
        """Create Whisper model configuration tab"""
        grid = self.create_grid()
        
        # Backend
        backend_store = Gtk.ListStore(str, str)
        backends = [("whisper.cpp (Fastest)", "whisper.cpp"), ("faster-whisper", "faster-whisper")]
        for label, value in backends:
            backend_store.append([label, value])
        
        self.append_combo_row(grid, 0, "Backend:", backend_store, "WHISPER_BACKEND")
        
        # Model size
        model_store = Gtk.ListStore(str, str)
        models = [
            ("Tiny (~75MB, Fastest)", "tiny"),
            ("Base (~145MB, Default)", "base"),
            ("Small (~466MB, Good)", "small"),
            ("Medium (~1.5GB, Better)", "medium"),
            ("Large (~3GB, Best)", "large"),
            ("Turbo (~1.5GB, Fast Mode)", "turbo")
        ]
        for label, value in models:
            model_store.append([label, value])
        
        self.append_combo_row(grid, 1, "Model:", model_store, "WHISPER_MODEL")
        
        # Language
        self.append_entry_row(grid, 2, "Language:", "WHISPER_LANGUAGE", 
                             placeholder="en, es, fr, de... (empty for auto-detect)")
        
        # GPU Settings
        gpu_frame = Gtk.Frame(label=" GPU Settings (faster-whisper only) ")
        gpu_frame.set_margin_top(10)
        gpu_grid = self.create_grid()
        gpu_frame.add(gpu_grid)
        grid.attach(gpu_frame, 0, 4, 2, 1)
        
        self.append_switch_row(gpu_grid, 0, "Use GPU:", "USE_GPU")
        
        compute_store = Gtk.ListStore(str, str)
        compute_types = [
            ("float16 (Fastest, more memory)", "float16"),
            ("int8_float16 (Balanced)", "int8_float16"),
            ("int8 (Lowest memory)", "int8")
        ]
        for label, value in compute_types:
            compute_store.append([label, value])
        
        self.append_combo_row(gpu_grid, 1, "Compute Type:", compute_store, "GPU_COMPUTE_TYPE")
        
        container = Gtk.ScrolledWindow()
        container.add(grid)
        return container
    
    def create_audio_tab(self):
        """Create Audio and Processing configuration tab"""
        grid = self.create_grid()
        
        # Sample Rate
        sample_store = Gtk.ListStore(str, int)
        sample_rates = [("16 kHz (Recommended)", 16000), ("8 kHz", 8000)]
        for label, value in sample_rates:
            sample_store.append([label, value])
        
        self.append_combo_row(grid, 0, "Sample Rate:", sample_store, "SAMPLE_RATE")
        
        # Channels
        self.append_spin_row(grid, 1, "Audio Channels:", "AUDIO_CHANNELS", 1, 2, 1)
        
        # Whisper.cpp threads
        cpu_count = os.cpu_count() or 4
        self.append_spin_row(grid, 2, "CPU Threads:", "WHISPER_CPP_THREADS", 1, cpu_count * 2, 1)
        
        # Processors
        self.append_spin_row(grid, 3, "Processors:", "WHISPER_CPP_PROCESSORS", 1, 4, 1)
        
        # VAD Settings
        vad_frame = Gtk.Frame(label=" Voice Activity Detection (VAD) ")
        vad_frame.set_margin_top(10)
        vad_grid = self.create_grid()
        vad_frame.add(vad_grid)
        grid.attach(vad_frame, 0, 5, 2, 1)
        
        self.append_switch_row(vad_grid, 0, "Enable VAD:", "USE_VAD")
        self.append_scale_row(vad_grid, 1, "VAD Threshold:", "VAD_THRESHOLD", 0.0, 1.0, 0.1)
        
        # Logging
        log_frame = Gtk.Frame(label=" Logging ")
        log_frame.set_margin_top(10)
        log_grid = self.create_grid()
        log_frame.add(log_grid)
        grid.attach(log_frame, 0, 6, 2, 1)
        
        log_store = Gtk.ListStore(str, str)
        log_levels = [("DEBUG", "DEBUG"), ("INFO", "INFO"), ("WARNING", "WARNING"), ("ERROR", "ERROR")]
        for label, value in log_levels:
            log_store.append([label, value])
        
        self.append_combo_row(log_grid, 0, "Log Level:", log_store, "LOG_LEVEL")
        
        container = Gtk.ScrolledWindow()
        container.add(grid)
        return container
    
    def create_text_tab(self):
        """Create Text Injection configuration tab"""
        grid = self.create_grid()
        
        # Delay
        self.append_spin_row(grid, 0, "Type Delay (ms):", "TYPE_DELAY_MS", 0, 1000, 50)
        
        # Switches
        self.append_switch_row(grid, 1, "Auto Capitalize:", "AUTO_CAPITALIZE")
        self.append_switch_row(grid, 2, "Auto Punctuate:", "AUTO_PUNCTUATE")
        self.append_switch_row(grid, 3, "Add Space Before:", "ADD_SPACE_BEFORE")
        
        # Help text
        help_label = Gtk.Label()
        help_label.set_markup(
            "<i>These settings control how transcribed text is formatted and injected.</i>\n\n"
            "<b>Type Delay:</b> Pause before typing (ms)\n"
            "<b>Auto Capitalize:</b> Capitalize first letter\n"
            "<b>Auto Punctuate:</b> Add period if missing\n"
            "<b>Add Space Before:</b> Insert space before text"
        )
        help_label.set_line_wrap(True)
        help_label.set_halign(Gtk.Align.START)
        help_label.set_margin_top(20)
        grid.attach(help_label, 0, 5, 2, 1)
        
        container = Gtk.ScrolledWindow()
        container.add(grid)
        return container
    
    def create_service_tab(self):
        """Create Service Control tab"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Service status
        status_frame = Gtk.Frame(label=" Service Status ")
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        status_box.set_margin_top(10)
        status_box.set_margin_bottom(10)
        status_box.set_margin_start(10)
        status_box.set_margin_end(10)
        status_frame.add(status_box)
        
        self.service_status_label = Gtk.Label()
        self.service_status_label.set_markup("<span size='large'>Checking...</span>")
        status_box.pack_start(self.service_status_label, False, False, 0)
        
        self.update_service_status()
        box.pack_start(status_frame, False, False, 0)
        
        # Control buttons
        control_frame = Gtk.Frame(label=" Service Control ")
        control_grid = Gtk.Grid()
        control_grid.set_column_spacing(10)
        control_grid.set_row_spacing(10)
        control_grid.set_margin_top(10)
        control_grid.set_margin_bottom(10)
        control_grid.set_margin_start(10)
        control_grid.set_margin_end(10)
        control_frame.add(control_grid)
        
        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self.on_start_service)
        control_grid.attach(self.start_button, 0, 0, 1, 1)
        
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self.on_stop_service)
        control_grid.attach(self.stop_button, 1, 0, 1, 1)
        
        self.restart_button = Gtk.Button(label="Restart")
        self.restart_button.connect("clicked", self.on_restart_service)
        self.restart_button.get_style_context().add_class("suggested-action")
        control_grid.attach(self.restart_button, 2, 0, 1, 1)
        
        self.enable_button = Gtk.Button(label="Enable")
        self.enable_button.connect("clicked", self.on_enable_service)
        control_grid.attach(self.enable_button, 0, 1, 1, 1)
        
        self.disable_button = Gtk.Button(label="Disable")
        self.disable_button.connect("clicked", self.on_disable_service)
        control_grid.attach(self.disable_button, 1, 1, 1, 1)
        
        box.pack_start(control_frame, False, False, 0)
        
        # Refresh button
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        refresh_button = Gtk.Button(label="Refresh Status")
        refresh_button.connect("clicked", lambda x: self.update_service_status())
        refresh_box.pack_end(refresh_button, False, False, 0)
        box.pack_start(refresh_box, False, False, 0)
        
        # Log viewer
        log_frame = Gtk.Frame(label=" Recent Logs ")
        log_scrolled = Gtk.ScrolledWindow()
        log_scrolled.set_min_content_height(200)
        log_scrolled.set_shadow_type(Gtk.ShadowType.IN)
        
        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_monospace(True)
        log_scrolled.add(self.log_textview)
        log_frame.add(log_scrolled)
        
        box.pack_start(log_frame, True, True, 0)
        self.update_log_view()
        
        return box
    
    def create_button_box(self):
        """Create save/cancel button box"""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_halign(Gtk.Align.END)
        box.set_margin_top(10)
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel)
        box.pack_start(cancel_button, False, False, 0)
        
        save_button = Gtk.Button(label="Save Configuration")
        save_button.connect("clicked", self.on_save)
        save_button.get_style_context().add_class("suggested-action")
        box.pack_start(save_button, False, False, 0)
        
        return box
    
    def create_grid(self):
        """Create a standardized grid for forms"""
        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        grid.set_row_spacing(10)
        grid.set_margin_top(10)
        return grid
    
    def append_combo_row(self, grid, row, label_text, store, config_key):
        """Append a combobox row to grid"""
        label = Gtk.Label(label_text)
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, row, 1, 1)
        
        combo = Gtk.ComboBox.new_with_model_and_entry(store)
        combo.set_entry_text_column(0)
        combo.connect("changed", self.on_config_changed, config_key)
        grid.attach(combo, 1, row, 1, 1)
        
        self.config[config_key] = combo
    
    def append_entry_row(self, grid, row, label_text, config_key, placeholder=None):
        """Append a text entry row to grid"""
        label = Gtk.Label(label_text)
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, row, 1, 1)
        
        entry = Gtk.Entry()
        if placeholder:
            entry.set_placeholder_text(placeholder)
        entry.connect("changed", self.on_config_changed, config_key)
        grid.attach(entry, 1, row, 1, 1)
        
        self.config[config_key] = entry
    
    def append_spin_row(self, grid, row, label_text, config_key, min_val, max_val, step):
        """Append spin button row to grid"""
        label = Gtk.Label(label_text)
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, row, 1, 1)
        
        adjustment = Gtk.Adjustment(min_val, min_val, max_val, step, step * 10, 0)
        spin = Gtk.SpinButton()
        spin.set_adjustment(adjustment)
        spin.set_numeric(True)
        spin.connect("value-changed", self.on_config_changed, config_key)
        grid.attach(spin, 1, row, 1, 1)
        
        self.config[config_key] = spin
    
    def append_switch_row(self, grid, row, label_text, config_key):
        """Append switch row to grid"""
        label = Gtk.Label(label_text)
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, row, 1, 1)
        
        switch = Gtk.Switch()
        switch.connect("state-set", self.on_config_changed_switch, config_key)
        grid.attach(switch, 1, row, 1, 1)
        
        self.config[config_key] = switch
    
    def append_scale_row(self, grid, row, label_text, config_key, min_val, max_val, step):
        """Append scale/slider row to grid"""
        label = Gtk.Label(label_text)
        label.set_halign(Gtk.Align.END)
        grid.attach(label, 0, row, 1, 1)
        
        adjustment = Gtk.Adjustment(min_val, min_val, max_val, step, step * 10, 0)
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        scale.set_digits(1)
        scale.set_hexpand(True)
        scale.set_draw_value(False)
        
        # Add value label
        value_label = Gtk.Label()
        value_label.set_width_chars(4)
        value_label.set_halign(Gtk.Align.START)
        
        def update_value_label(scale):
            value_label.set_text(f"{scale.get_value():.1f}")
        
        scale.connect("value-changed", self.on_config_changed_scale, config_key)
        scale.connect("value-changed", update_value_label)
        update_value_label(scale)
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.pack_start(scale, True, True, 0)
        box.pack_start(value_label, False, False, 0)
        
        grid.attach(box, 1, row, 1, 1)
        self.config[config_key] = scale
    
    def on_config_changed(self, widget, config_key):
        """Handle config value changes"""
        # Mark as modified (simple visual feedback)
        self.update_status("Configuration modified")
    
    def on_config_changed_switch(self, widget, state, config_key):
        """Handle switch changes"""
        self.on_config_changed(widget, config_key)
    
    def on_config_changed_scale(self, widget, config_key):
        """Handle scale changes"""
        self.on_config_changed(widget, config_key)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if not self.config_path.exists():
                self.update_status(f"Warning: Config file not found at {self.config_path}")
                return
            
            # Read config file
            with open(self.config_path, 'r') as f:
                content = f.read()
            
            # Parse config values using AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            key = target.id
                            if key in self.config:
                                try:
                                    value = ast.literal_eval(node.value)
                                    self.original_config[key] = value
                                    self.set_widget_value(key, value)
                                except:
                                    # Handle special cases like None
                                    if isinstance(node.value, ast.Constant) and node.value.value is None:
                                        self.original_config[key] = ''
                                        self.set_widget_value(key, '')
            
            self.update_status(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            self.update_status(f"Error loading config: {e}")
            self.show_error_dialog(f"Failed to load configuration: {e}")
    
    def set_widget_value(self, key, value):
        """Set widget value based on type"""
        widget = self.config[key]
        
        if isinstance(widget, Gtk.ComboBox):
            model = widget.get_model()
            for i, row in enumerate(model):
                if row[1] == value:
                    widget.set_active(i)
                    break
        elif isinstance(widget, Gtk.Entry):
            if value is None:
                value = ''
            widget.set_text(str(value).replace("'", "\"").strip())
        elif isinstance(widget, Gtk.SpinButton):
            widget.set_value(value)
        elif isinstance(widget, Gtk.Switch):
            widget.set_active(bool(value))
        elif isinstance(widget, Gtk.Scale):
            widget.set_value(value)
    
    def get_widget_value(self, key):
        """Get widget value"""
        widget = self.config[key]
        
        if isinstance(widget, Gtk.ComboBox):
            model = widget.get_model()
            active = widget.get_active()
            if active >= 0:
                return model[active][1]
            return None
        elif isinstance(widget, Gtk.Entry):
            text = widget.get_text().strip()
            return text if text else None
        elif isinstance(widget, Gtk.SpinButton):
            return int(widget.get_value())
        elif isinstance(widget, Gtk.Switch):
            return widget.get_active()
        elif isinstance(widget, Gtk.Scale):
            return widget.get_value()
        
        return None
    
    def on_save(self, button):
        """Save configuration to file"""
        try:
            # Generate new config content
            config_lines = [
                '"""',
                'Configuration file for AI Dictation System',
                'Modify these settings to customize the behavior',
                '"""',
                '',
            ]
            
            # Group settings
            whisper_settings = [
                ('WHISPER_BACKEND', 'Whisper Model Configuration'),
                ('WHISPER_MODEL', None),
                ('WHISPER_LANGUAGE', None),
            ]
            
            gpu_settings = [
                ('USE_GPU', 'GPU Configuration (faster-whisper only)'),
                ('GPU_COMPUTE_TYPE', None),
            ]
            
            audio_settings = [
                ('SAMPLE_RATE', 'Audio Configuration'),
                ('AUDIO_CHANNELS', None),
            ]
            
            text_settings = [
                ('TYPE_DELAY_MS', 'Text Injection Configuration'),
                ('AUTO_CAPITALIZE', None),
                ('AUTO_PUNCTUATE', None),
                ('ADD_SPACE_BEFORE', None),
            ]
            
            cpp_settings = [
                ('WHISPER_CPP_THREADS', 'Whisper.cpp Specific Settings'),
                ('WHISPER_CPP_PROCESSORS', None),
            ]
            
            vad_settings = [
                ('USE_VAD', 'Voice Activity Detection'),
                ('VAD_THRESHOLD', None),
            ]
            
            log_settings = [
                ('LOG_LEVEL', 'Logging'),
            ]
            
            def add_section(lines, settings):
                for key, comment in settings:
                    if comment:
                        lines.append(f'# {comment}')
                    value = self.get_widget_value(key)
                    
                    if isinstance(value, str) and value is not None:
                        # Quote string values
                        lines.append(f'{key} = "{value}"')
                    elif value is None:
                        # Handle None/empty
                        lines.append(f'{key} =   # Language code (en, es, fr, de, etc.) or None for auto-detect')
                    else:
                        # Numeric or boolean
                        lines.append(f'{key} = {value}')
                lines.append('')
            
            # Build config file
            add_section(config_lines, whisper_settings)
            add_section(config_lines, gpu_settings)
            add_section(config_lines, audio_settings)
            add_section(config_lines, text_settings)
            add_section(config_lines, cpp_settings)
            add_section(config_lines, vad_settings)
            add_section(config_lines, log_settings)
            
            # Write to file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                f.write('\n'.join(config_lines))
            
            self.update_status(f"Configuration saved to {self.config_path}")
            
            # Ask if user wants to restart service
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Restart Service?",
            )
            dialog.format_secondary_text(
                "Configuration saved successfully. Would you like to restart the AI Dictation service to apply changes?"
            )
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                self.restart_service()
            
        except Exception as e:
            self.update_status(f"Error saving config: {e}")
            self.show_error_dialog(f"Failed to save configuration: {e}")
    
    def on_cancel(self, button):
        """Cancel and quit"""
        self.check_unsaved_changes()
        Gtk.main_quit()
    
    def check_unsaved_changes(self):
        """Check for unsaved changes"""
        # Simple check - if user modified any widget
        # (In a real app, we'd track actual changes)
        pass
    
    def update_status(self, message):
        """Update status bar message"""
        context_id = self.status_bar.get_context_id("main")
        self.status_bar.push(context_id, message)
        GLib.timeout_add(3000, lambda: self.status_bar.pop(context_id))
    
    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def update_service_status(self):
        """Update service status display"""
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "ai-dictation.service"],
                capture_output=True, text=True
            )
            status = result.stdout.strip()
            
            if status == "active":
                self.service_status_label.set_markup("\n<span size='large' color='#4ade80'>● Active (Running)</span>")
            elif status == "inactive":
                self.service_status_label.set_markup("\n<span size='large' color='#9ca3af'>○ Inactive (Stopped)</span>")
            elif status == "failed":
                self.service_status_label.set_markup("\n<span size='large' color='#ef4444'>✕ Failed</span>")
            else:
                self.service_status_label.set_markup(f"\n<span size='large' color='#f59e0b'>? {status}</span>")
            
        except Exception as e:
            self.service_status_label.set_markup(f"\n<span size='large' color='#ef4444'>Error: {e}</span>")
    
    def on_start_service(self, button):
        """Start the service"""
        try:
            subprocess.run(["systemctl", "--user", "start", "ai-dictation.service"], check=True)
            GLib.timeout_add(500, self.update_service_status)
            self.update_status("Service started")
        except Exception as e:
            self.show_error_dialog(f"Failed to start service: {e}")
    
    def on_stop_service(self, button):
        """Stop the service"""
        try:
            subprocess.run(["systemctl", "--user", "stop", "ai-dictation.service"], check=True)
            GLib.timeout_add(500, self.update_service_status)
            self.update_status("Service stopped")
        except Exception as e:
            self.show_error_dialog(f"Failed to stop service: {e}")
    
    def on_restart_service(self, button):
        """Restart the service"""
        self.restart_service()
    
    def restart_service(self):
        """Restart the service"""
        try:
            subprocess.run(["systemctl", "--user", "restart", "ai-dictation.service"], check=True)
            GLib.timeout_add(500, self.update_service_status)
            self.update_status("Service restarted")
        except Exception as e:
            self.show_error_dialog(f"Failed to restart service: {e}")
    
    def on_enable_service(self, button):
        """Enable the service"""
        try:
            subprocess.run(["systemctl", "--user", "enable", "ai-dictation.service"], check=True)
            self.update_status("Service enabled (will start on boot)")
        except Exception as e:
            self.show_error_dialog(f"Failed to enable service: {e}")
    
    def on_disable_service(self, button):
        """Disable the service"""
        try:
            subprocess.run(["systemctl", "--user", "disable", "ai-dictation.service"], check=True)
            self.update_status("Service disabled (will not start on boot)")
        except Exception as e:
            self.show_error_dialog(f"Failed to disable service: {e}")
    
    def update_log_view(self):
        """Update log view with recent entries"""
        try:
            result = subprocess.run(
                ["journalctl", "--user", "-u", "ai-dictation.service", "-n", "50", "--no-pager"],
                capture_output=True, text=True
            )
            
            buffer = self.log_textview.get_buffer()
            buffer.set_text(result.stdout)
            
            # Auto-scroll to bottom
            end_iter = buffer.get_end_iter()
            self.log_textview.scroll_to_iter(end_iter, 0.0, False, 0, 0)
            
        except Exception as e:
            buffer = self.log_textview.get_buffer()
            buffer.set_text(f"Error reading logs: {e}")

def main():
    # Set up CSS styling
    screen = Gdk.Screen.get_default()
    if screen:
        css_provider = Gtk.CssProvider()
        css_data = """
        button.suggested-action {
            background-color: #4ade80;
            color: white;
            font-weight: bold;
        }
        button.suggested-action:hover {
            background-color: #22c55e;
        }
        """
        css_provider.load_from_data(css_data.encode())
        Gtk.StyleContext.add_provider_for_screen(
            screen, 
            css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    win = ConfigManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
