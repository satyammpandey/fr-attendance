"""
AI-Based Face Recognition Attendance System - ULTRA ENHANCED Edition
Author: Satyam Pandey (BCA AI/ML)
Enhanced with: Real-time Preview, Analytics Dashboard, Database, Reports, and much more!
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
from tkinter import font as tkfont
import subprocess
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import json
import sqlite3
import hashlib
import shutil
from collections import Counter
import csv
import platform
import webbrowser
from pathlib import Path

# Optional imports with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ CONFIGURATION MANAGER ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class ConfigManager:
    """Manages application configuration with persistence"""
    
    DEFAULT_CONFIG = {
        "app_name": "AI Face Recognition Attendance System",
        "version": "2.0.0",
        "author": "Satyam Pandey",
        "theme": "dark",
        "language": "en",
        "camera_index": 0,
        "confidence_threshold": 0.6,
        "auto_backup": True,
        "backup_interval_hours": 24,
        "max_log_entries": 1000,
        "sound_enabled": True,
        "notification_enabled": True,
        "auto_export": False,
        "export_format": "csv",
        "date_format": "%Y-%m-%d",
        "time_format": "%H:%M:%S",
        "working_hours_start": "09:00",
        "working_hours_end": "17:00",
        "late_threshold_minutes": 15,
        "window_width": 1400,
        "window_height": 900,
        "remember_window_position": True,
        "last_window_x": None,
        "last_window_y": None,
        "recent_exports": [],
        "admin_password_hash": None,
        "first_run": True,
        "show_tooltips": True,
        "animation_enabled": True,
        "log_to_file": True,
        "debug_mode": False
    }
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**self.DEFAULT_CONFIG, **loaded}
            except:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Config save error: {e}")
            return False
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def reset_to_defaults(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ DATABASE MANAGER ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    """SQLite database manager for robust data storage"""
    
    def __init__(self, db_file="attendance_system.db"):
        self.db_file = db_file
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                department TEXT,
                batch TEXT,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                photo_path TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                name TEXT NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status TEXT DEFAULT 'Present',
                confidence REAL,
                late_minutes INTEGER DEFAULT 0,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, date)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                total_recognized INTEGER DEFAULT 0,
                total_unknown INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                message TEXT,
                user TEXT DEFAULT 'system'
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query, params=None):
        """Execute a query with optional parameters"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor
    
    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Fetch single result from a query"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    # ─── Student Operations ───────────────────────────────────────────────────
    
    def add_student(self, student_id, name, email=None, phone=None, 
                    department=None, batch=None, photo_path=None):
        """Add a new student"""
        try:
            self.execute('''
                INSERT INTO students (student_id, name, email, phone, department, batch, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, email, phone, department, batch, photo_path))
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_students(self):
        """Get all active students"""
        return self.fetch_all("SELECT * FROM students WHERE is_active = 1 ORDER BY name")
    
    def get_student(self, student_id):
        """Get student by ID"""
        return self.fetch_one("SELECT * FROM students WHERE student_id = ?", (student_id,))
    
    def update_student(self, student_id, **kwargs):
        """Update student information"""
        valid_fields = ['name', 'email', 'phone', 'department', 'batch', 'photo_path', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if updates:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [student_id]
            self.execute(f"UPDATE students SET {set_clause} WHERE student_id = ?", values)
    
    def delete_student(self, student_id):
        """Soft delete student"""
        self.execute("UPDATE students SET is_active = 0 WHERE student_id = ?", (student_id,))
    
    # ─── Attendance Operations ────────────────────────────────────────────────
    
    def record_attendance(self, student_id, name, confidence=None, session_id=None):
        """Record attendance for a student"""
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Check if already recorded today
        existing = self.fetch_one(
            "SELECT * FROM attendance WHERE student_id = ? AND date = ?",
            (student_id, date)
        )
        
        if existing:
            return False, "Already marked"
        
        # Calculate late minutes
        try:
            from datetime import datetime as dt
            check_time = dt.strptime(time_str, "%H:%M:%S").time()
            start_time = dt.strptime("09:00:00", "%H:%M:%S").time()
            
            if check_time > start_time:
                late_mins = (dt.combine(dt.today(), check_time) - 
                           dt.combine(dt.today(), start_time)).seconds // 60
            else:
                late_mins = 0
        except:
            late_mins = 0
        
        status = "Late" if late_mins > 15 else "Present"
        
        self.execute('''
            INSERT INTO attendance (student_id, name, date, time, status, confidence, late_minutes, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, date, time_str, status, confidence, late_mins, session_id))
        
        return True, status
    
    def get_attendance_by_date(self, date):
        """Get attendance for a specific date"""
        return self.fetch_all(
            "SELECT * FROM attendance WHERE date = ? ORDER BY time",
            (date,)
        )
    
    def get_attendance_range(self, start_date, end_date):
        """Get attendance for date range"""
        return self.fetch_all('''
            SELECT * FROM attendance 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, time DESC
        ''', (start_date, end_date))
    
    def get_student_attendance(self, student_id, limit=None):
        """Get attendance history for a student"""
        query = "SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC, time DESC"
        if limit:
            query += f" LIMIT {limit}"
        return self.fetch_all(query, (student_id,))
    
    def get_attendance_stats(self):
        """Get attendance statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        stats = {
            'today': self.fetch_one(
                "SELECT COUNT(*) as count FROM attendance WHERE date = ?", (today,)
            )['count'],
            'this_week': self.fetch_one(
                "SELECT COUNT(*) as count FROM attendance WHERE date >= ?", (week_ago,)
            )['count'],
            'this_month': self.fetch_one(
                "SELECT COUNT(*) as count FROM attendance WHERE date >= ?", (month_ago,)
            )['count'],
            'total': self.fetch_one(
                "SELECT COUNT(*) as count FROM attendance"
            )['count'],
            'late_today': self.fetch_one(
                "SELECT COUNT(*) as count FROM attendance WHERE date = ? AND status = 'Late'", (today,)
            )['count'],
            'unique_students': self.fetch_one(
                "SELECT COUNT(DISTINCT student_id) as count FROM attendance"
            )['count']
        }
        return stats
    
    def get_daily_counts(self, days=30):
        """Get daily attendance counts for chart"""
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.fetch_all('''
            SELECT date, COUNT(*) as count 
            FROM attendance 
            WHERE date >= ?
            GROUP BY date 
            ORDER BY date
        ''', (start_date,))
    
    # ─── Session Operations ───────────────────────────────────────────────────
    
    def create_session(self):
        """Create a new attendance session"""
        session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.execute('''
            INSERT INTO sessions (session_id, start_time)
            VALUES (?, ?)
        ''', (session_id, datetime.now()))
        return session_id
    
    def end_session(self, session_id, total_recognized=0, total_unknown=0, notes=None):
        """End an attendance session"""
        self.execute('''
            UPDATE sessions 
            SET end_time = ?, total_recognized = ?, total_unknown = ?, notes = ?
            WHERE session_id = ?
        ''', (datetime.now(), total_recognized, total_unknown, notes, session_id))
    
    def get_sessions(self, limit=50):
        """Get recent sessions"""
        return self.fetch_all(
            "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?",
            (limit,)
        )
    
    # ─── Log Operations ───────────────────────────────────────────────────────
    
    def add_log(self, message, level="INFO", user="system"):
        """Add activity log"""
        self.execute('''
            INSERT INTO activity_logs (level, message, user)
            VALUES (?, ?, ?)
        ''', (level, message, user))
    
    def get_logs(self, limit=100, level=None):
        """Get activity logs"""
        if level:
            return self.fetch_all(
                "SELECT * FROM activity_logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?",
                (level, limit)
            )
        return self.fetch_all(
            "SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
    
    def clear_old_logs(self, days=30):
        """Clear logs older than specified days"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        self.execute("DELETE FROM activity_logs WHERE timestamp < ?", (cutoff,))
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ CUSTOM WIDGETS ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class AnimatedButton(tk.Canvas):
    """Custom animated button with hover effects"""
    
    def __init__(self, parent, text, command=None, width=200, height=45,
                 bg_color="#4CAF50", hover_color="#45a049", fg_color="white",
                 font=("Segoe UI", 11, "bold"), icon=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.text = text
        self.font = font
        self.icon = icon
        self.width = width
        self.height = height
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
        
        self.configure(bg=parent.cget('bg'))
        self.draw_button()
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def draw_button(self, color=None):
        """Draw the button with rounded corners"""
        self.delete("all")
        
        if color is None:
            color = self.hover_color if self.is_hovered else self.bg_color
        
        if not self.enabled:
            color = "#666666"
        
        # Draw rounded rectangle
        radius = 8
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, radius, color)
        
        # Draw text
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(
            self.width // 2, self.height // 2,
            text=display_text,
            fill=self.fg_color if self.enabled else "#999999",
            font=self.font
        )
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        """Create a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        self.create_polygon(points, fill=color, smooth=True)
    
    def on_enter(self, event):
        if self.enabled:
            self.is_hovered = True
            self.draw_button()
    
    def on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self.draw_button()
    
    def on_press(self, event):
        if self.enabled:
            self.is_pressed = True
            self.draw_button(self.hover_color)
    
    def on_release(self, event):
        if self.enabled and self.is_pressed:
            self.is_pressed = False
            self.draw_button()
            if self.command:
                self.command()
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        self.draw_button()
    
    def configure_button(self, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'bg_color' in kwargs:
            self.bg_color = kwargs['bg_color']
        if 'state' in kwargs:
            self.enabled = kwargs['state'] != 'disabled'
        self.draw_button()


class GradientFrame(tk.Canvas):
    """Frame with gradient background"""
    
    def __init__(self, parent, color1="#1e1e2e", color2="#2a2a3e", 
                 direction="vertical", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.direction = direction
        
        self.bind("<Configure>", self.draw_gradient)
    
    def draw_gradient(self, event=None):
        """Draw gradient background"""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Parse colors
        r1, g1, b1 = self.winfo_rgb(self.color1)
        r2, g2, b2 = self.winfo_rgb(self.color2)
        
        # Normalize to 0-255
        r1, g1, b1 = r1//256, g1//256, b1//256
        r2, g2, b2 = r2//256, g2//256, b2//256
        
        if self.direction == "vertical":
            for i in range(height):
                ratio = i / height
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.create_line(0, i, width, i, fill=color, tags="gradient")
        else:
            for i in range(width):
                ratio = i / width
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.create_line(i, 0, i, height, fill=color, tags="gradient")


class ToolTip:
    """Tooltip for widgets"""
    
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.scheduled = None
        
        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<Button>", self.hide)
    
    def schedule(self, event=None):
        self.scheduled = self.widget.after(self.delay, self.show)
    
    def show(self):
        if self.tooltip:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4
        )
        label.pack()
    
    def hide(self, event=None):
        if self.scheduled:
            self.widget.after_cancel(self.scheduled)
            self.scheduled = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class CircularProgress(tk.Canvas):
    """Circular progress indicator"""
    
    def __init__(self, parent, size=100, thickness=10, 
                 bg_color="#333333", progress_color="#4CAF50", **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, **kwargs)
        
        self.size = size
        self.thickness = thickness
        self.bg_color_arc = bg_color
        self.progress_color = progress_color
        self.progress = 0
        
        self.draw()
    
    def draw(self):
        """Draw the progress circle"""
        self.delete("all")
        
        # Background arc
        self.create_arc(
            self.thickness, self.thickness,
            self.size - self.thickness, self.size - self.thickness,
            start=90, extent=-360,
            style="arc", outline=self.bg_color_arc,
            width=self.thickness
        )
        
        # Progress arc
        if self.progress > 0:
            extent = -360 * (self.progress / 100)
            self.create_arc(
                self.thickness, self.thickness,
                self.size - self.thickness, self.size - self.thickness,
                start=90, extent=extent,
                style="arc", outline=self.progress_color,
                width=self.thickness
            )
        
        # Center text
        self.create_text(
            self.size // 2, self.size // 2,
            text=f"{int(self.progress)}%",
            font=("Segoe UI", 14, "bold"),
            fill="white"
        )
    
    def set_progress(self, value):
        """Set progress value (0-100)"""
        self.progress = max(0, min(100, value))
        self.draw()


class ModernNotebook(ttk.Notebook):
    """Enhanced notebook with custom styling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        style = ttk.Style()
        style.configure(
            "Modern.TNotebook",
            background="#1e1e2e",
            borderwidth=0
        )
        style.configure(
            "Modern.TNotebook.Tab",
            background="#2a2a3e",
            foreground="white",
            padding=[20, 10],
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", "#4CAF50")],
            foreground=[("selected", "white")]
        )
        
        self.configure(style="Modern.TNotebook")


class StatCard(tk.Frame):
    """Statistics display card"""
    
    def __init__(self, parent, title, value, icon="📊", 
                 color="#4CAF50", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(bg="#2a2a3e", padx=20, pady=15)
        
        # Icon and title
        header = tk.Frame(self, bg="#2a2a3e")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=icon,
            font=("Segoe UI", 20),
            bg="#2a2a3e",
            fg=color
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 10),
            bg="#2a2a3e",
            fg="#b4b4c8"
        ).pack(side=tk.LEFT, padx=10)
        
        # Value
        self.value_label = tk.Label(
            self,
            text=str(value),
            font=("Segoe UI", 28, "bold"),
            bg="#2a2a3e",
            fg="white"
        )
        self.value_label.pack(anchor=tk.W, pady=(10, 0))
    
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.config(text=str(value))


class SearchableTreeview(tk.Frame):
    """Treeview with search functionality"""
    
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(bg="#1e1e2e")
        self.all_items = []
        self.columns = columns
        
        # Search frame
        search_frame = tk.Frame(self, bg="#1e1e2e")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Segoe UI", 12),
            bg="#1e1e2e",
            fg="white"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_items)
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            bg="#2a2a3e",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Treeview frame
        tree_frame = tk.Frame(self, bg="#1e1e2e")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Configure treeview style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="#2a2a3e",
            foreground="white",
            fieldbackground="#2a2a3e",
            font=("Segoe UI", 10)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#363650",
            foreground="white",
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#4CAF50")],
            foreground=[("selected", "white")]
        )
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=120, anchor=tk.CENTER)
        
        # Pack
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def insert_items(self, items):
        """Insert items into treeview"""
        self.clear()
        self.all_items = items
        for item in items:
            self.tree.insert("", tk.END, values=item)
    
    def clear(self):
        """Clear all items"""
        self.all_items = []
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def filter_items(self, *args):
        """Filter items based on search"""
        search = self.search_var.get().lower()
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert matching items
        for item in self.all_items:
            if any(search in str(val).lower() for val in item):
                self.tree.insert("", tk.END, values=item)
    
    def sort_column(self, col, reverse):
        """Sort treeview by column"""
        items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        items.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(items):
            self.tree.move(child, '', index)
        
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def get_selected(self):
        """Get selected item"""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values']
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ CAMERA PREVIEW PANEL ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class CameraPreviewPanel(tk.Frame):
    """Real-time camera preview panel"""
    
    def __init__(self, parent, width=640, height=480, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.width = width
        self.height = height
        self.cap = None
        self.is_running = False
        self.preview_thread = None
        
        self.configure(bg="#1a1a2e")
        
        # Create canvas for preview
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg="#1a1a2e",
            highlightthickness=2,
            highlightbackground="#4CAF50"
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self,
            text="Camera not started",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#b4b4c8"
        )
        self.status_label.pack()
        
        # Control frame
        control_frame = tk.Frame(self, bg="#1a1a2e")
        control_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            control_frame,
            text="📷 Start Preview",
            command=self.start_preview,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ Stop",
            command=self.stop_preview,
            bg="#f44336",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Display placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder image"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text="📷\nCamera Preview",
            font=("Segoe UI", 16),
            fill="#4CAF50",
            justify=tk.CENTER
        )
    
    def start_preview(self):
        """Start camera preview"""
        if not CV2_AVAILABLE:
            messagebox.showerror("Error", "OpenCV not installed!")
            return
        
        if not PIL_AVAILABLE:
            messagebox.showerror("Error", "Pillow not installed!")
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot open camera!")
                return
            
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Camera active", fg="#4CAF50")
            
            self.preview_thread = threading.Thread(target=self.update_preview, daemon=True)
            self.preview_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def update_preview(self):
        """Update camera preview"""
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                
                # Convert to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                # Update canvas
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas.image = photo
            
            time.sleep(0.03)  # ~30 FPS
    
    def stop_preview(self):
        """Stop camera preview"""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Camera stopped", fg="#b4b4c8")
        self.show_placeholder()
    
    def destroy(self):
        """Clean up on destroy"""
        self.stop_preview()
        super().destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ ANALYTICS PANEL ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class AnalyticsPanel(tk.Frame):
    """Analytics and visualization panel"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.db = db_manager
        self.configure(bg="#1e1e2e")
        
        # Header
        header = tk.Frame(self, bg="#2a2a3e")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="📈 Analytics Dashboard",
            font=("Segoe UI", 16, "bold"),
            bg="#2a2a3e",
            fg="white"
        ).pack(pady=15)
        
        # Stats cards
        self.create_stats_section()
        
        # Charts section
        self.create_charts_section()
    
    def create_stats_section(self):
        """Create statistics cards"""
        stats_frame = tk.Frame(self, bg="#1e1e2e")
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        stats = self.db.get_attendance_stats()
        
        # Create stat cards
        cards_data = [
            ("Today", stats['today'], "📅", "#4CAF50"),
            ("This Week", stats['this_week'], "📆", "#2196F3"),
            ("This Month", stats['this_month'], "🗓️", "#ff9800"),
            ("Total Records", stats['total'], "📊", "#9c27b0"),
            ("Late Today", stats['late_today'], "⏰", "#f44336"),
            ("Unique Students", stats['unique_students'], "👥", "#00bcd4")
        ]
        
        self.stat_cards = []
        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(stats_frame, title, value, icon, color)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            self.stat_cards.append((title, card))
        
        # Configure grid weights
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)
    
    def create_charts_section(self):
        """Create charts section"""
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(
                self,
                text="Install matplotlib for charts: pip install matplotlib",
                font=("Segoe UI", 10),
                bg="#1e1e2e",
                fg="#ff9800"
            ).pack(pady=20)
            return
        
        charts_frame = tk.Frame(self, bg="#1e1e2e")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 4), facecolor="#1e1e2e")
        self.fig.subplots_adjust(bottom=0.2)
        
        # Daily attendance chart
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#2a2a3e")
        
        # Style the chart
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('#2a2a3e')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('#2a2a3e')
        
        # Get data and plot
        self.update_chart()
        
        # Add canvas
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        refresh_btn = tk.Button(
            charts_frame,
            text="🔄 Refresh Data",
            command=self.refresh_data,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            padx=20,
            pady=8
        )
        refresh_btn.pack(pady=10)
    
    def update_chart(self):
        """Update the attendance chart"""
        self.ax.clear()
        
        # Get daily counts
        data = self.db.get_daily_counts(30)
        
        if data:
            dates = [row['date'] for row in data]
            counts = [row['count'] for row in data]
            
            # Create bar chart
            bars = self.ax.bar(dates, counts, color="#4CAF50", alpha=0.8)
            
            # Customize
            self.ax.set_xlabel("Date", color='white', fontsize=10)
            self.ax.set_ylabel("Attendance Count", color='white', fontsize=10)
            self.ax.set_title("Daily Attendance (Last 30 Days)", color='white', fontsize=12, fontweight='bold')
            
            # Rotate x-axis labels
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
            
            # Set colors
            self.ax.tick_params(colors='white')
            self.ax.set_facecolor("#2a2a3e")
        else:
            self.ax.text(
                0.5, 0.5,
                "No data available",
                ha='center', va='center',
                color='white', fontsize=14,
                transform=self.ax.transAxes
            )
        
        self.fig.tight_layout()
    
    def refresh_data(self):
        """Refresh all data"""
        # Update stats
        stats = self.db.get_attendance_stats()
        
        stats_map = {
            "Today": stats['today'],
            "This Week": stats['this_week'],
            "This Month": stats['this_month'],
            "Total Records": stats['total'],
            "Late Today": stats['late_today'],
            "Unique Students": stats['unique_students']
        }
        
        for title, card in self.stat_cards:
            if title in stats_map:
                card.update_value(stats_map[title])
        
        # Update chart
        if MATPLOTLIB_AVAILABLE:
            self.update_chart()
            self.canvas.draw()


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ STUDENT MANAGEMENT PANEL ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class StudentManagementPanel(tk.Frame):
    """Student registration and management panel"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.db = db_manager
        self.configure(bg="#1e1e2e")
        
        # Header
        header = tk.Frame(self, bg="#2a2a3e")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="👥 Student Management",
            font=("Segoe UI", 16, "bold"),
            bg="#2a2a3e",
            fg="white"
        ).pack(pady=15)
        
        # Main content
        content = tk.Frame(self, bg="#1e1e2e")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Form
        self.create_form_panel(content)
        
        # Right panel - Student list
        self.create_list_panel(content)
        
        # Load students
        self.refresh_student_list()
    
    def create_form_panel(self, parent):
        """Create student registration form"""
        form_frame = tk.LabelFrame(
            parent,
            text="📝 Student Registration",
            font=("Segoe UI", 12, "bold"),
            bg="#2a2a3e",
            fg="white",
            padx=20,
            pady=20
        )
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Form fields
        fields = [
            ("Student ID:", "student_id"),
            ("Full Name:", "name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Department:", "department"),
            ("Batch:", "batch")
        ]
        
        self.form_vars = {}
        
        for label_text, field_name in fields:
            frame = tk.Frame(form_frame, bg="#2a2a3e")
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                frame,
                text=label_text,
                font=("Segoe UI", 10),
                bg="#2a2a3e",
                fg="#b4b4c8",
                width=12,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            var = tk.StringVar()
            entry = tk.Entry(
                frame,
                textvariable=var,
                font=("Segoe UI", 10),
                bg="#363650",
                fg="white",
                insertbackground="white",
                relief="flat",
                width=25
            )
            entry.pack(side=tk.LEFT, ipady=5, padx=(5, 0))
            
            self.form_vars[field_name] = var
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg="#2a2a3e")
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(
            btn_frame,
            text="➕ Add Student",
            command=self.add_student,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Clear Form",
            command=self.clear_form,
            bg="#ff9800",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Camera capture section
        if CV2_AVAILABLE and PIL_AVAILABLE:
            capture_frame = tk.LabelFrame(
                form_frame,
                text="📷 Capture Face",
                font=("Segoe UI", 10),
                bg="#2a2a3e",
                fg="white",
                padx=10,
                pady=10
            )
            capture_frame.pack(fill=tk.X, pady=(20, 0))
            
            tk.Button(
                capture_frame,
                text="📸 Capture & Register Face",
                command=self.capture_face,
                bg="#2196F3",
                fg="white",
                font=("Segoe UI", 10),
                relief="flat",
                padx=15,
                pady=8
            ).pack()
    
    def create_list_panel(self, parent):
        """Create student list panel"""
        list_frame = tk.LabelFrame(
            parent,
            text="📋 Registered Students",
            font=("Segoe UI", 12, "bold"),
            bg="#2a2a3e",
            fg="white",
            padx=10,
            pady=10
        )
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Searchable treeview
        columns = ("ID", "Name", "Department", "Batch", "Registered")
        self.student_tree = SearchableTreeview(list_frame, columns)
        self.student_tree.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = tk.Frame(list_frame, bg="#2a2a3e")
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            action_frame,
            text="🔄 Refresh",
            command=self.refresh_student_list,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="✏️ Edit Selected",
            command=self.edit_student,
            bg="#2196F3",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            command=self.delete_student,
            bg="#f44336",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def add_student(self):
        """Add new student"""
        student_id = self.form_vars['student_id'].get().strip()
        name = self.form_vars['name'].get().strip()
        
        if not student_id or not name:
            messagebox.showwarning("Validation Error", "Student ID and Name are required!")
            return
        
        success = self.db.add_student(
            student_id=student_id,
            name=name,
            email=self.form_vars['email'].get().strip(),
            phone=self.form_vars['phone'].get().strip(),
            department=self.form_vars['department'].get().strip(),
            batch=self.form_vars['batch'].get().strip()
        )
        
        if success:
            messagebox.showinfo("Success", f"Student '{name}' added successfully!")
            self.clear_form()
            self.refresh_student_list()
        else:
            messagebox.showerror("Error", "Student ID already exists!")
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            var.set("")
    
    def refresh_student_list(self):
        """Refresh the student list"""
        students = self.db.get_all_students()
        items = [
            (
                s['student_id'],
                s['name'],
                s['department'] or '-',
                s['batch'] or '-',
                s['registered_date'][:10] if s['registered_date'] else '-'
            )
            for s in students
        ]
        self.student_tree.insert_items(items)
    
    def edit_student(self):
        """Edit selected student"""
        selected = self.student_tree.get_selected()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student to edit!")
            return
        
        # Populate form with selected student data
        student = self.db.get_student(selected[0])
        if student:
            self.form_vars['student_id'].set(student['student_id'])
            self.form_vars['name'].set(student['name'])
            self.form_vars['email'].set(student['email'] or '')
            self.form_vars['phone'].set(student['phone'] or '')
            self.form_vars['department'].set(student['department'] or '')
            self.form_vars['batch'].set(student['batch'] or '')
    
    def delete_student(self):
        """Delete selected student"""
        selected = self.student_tree.get_selected()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student to delete!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete student '{selected[1]}'?"):
            self.db.delete_student(selected[0])
            self.refresh_student_list()
            messagebox.showinfo("Success", "Student deleted successfully!")
    
    def capture_face(self):
        """Capture face for registration"""
        student_id = self.form_vars['student_id'].get().strip()
        name = self.form_vars['name'].get().strip()
        
        if not student_id or not name:
            messagebox.showwarning("Required", "Enter Student ID and Name first!")
            return
        
        # This would integrate with face capture functionality
        messagebox.showinfo(
            "Face Capture",
            f"Face capture for {name} ({student_id})\n\n"
            "This feature would open the camera to capture face images "
            "for training the recognition model."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ SETTINGS PANEL ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class SettingsPanel(tk.Frame):
    """Application settings panel"""
    
    def __init__(self, parent, config_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.config = config_manager
        self.configure(bg="#1e1e2e")
        
        # Header
        header = tk.Frame(self, bg="#2a2a3e")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="⚙️ Settings",
            font=("Segoe UI", 16, "bold"),
            bg="#2a2a3e",
            fg="white"
        ).pack(pady=15)
        
        # Settings notebook
        self.notebook = ModernNotebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # General settings
        self.create_general_settings()
        
        # Recognition settings
        self.create_recognition_settings()
        
        # Notification settings
        self.create_notification_settings()
        
        # Backup settings
        self.create_backup_settings()
        
        # About section
        self.create_about_section()
        
        # Save button
        tk.Button(
            self,
            text="💾 Save Settings",
            command=self.save_settings,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=30,
            pady=10
        ).pack(pady=20)
    
    def create_general_settings(self):
        """Create general settings tab"""
        frame = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(frame, text="🏠 General")
        
        # Theme selection
        self.create_setting_row(
            frame,
            "Theme:",
            "theme",
            "combobox",
            ["dark", "light"],
            "Application color theme"
        )
        
        # Language
        self.create_setting_row(
            frame,
            "Language:",
            "language",
            "combobox",
            ["en", "es", "fr", "de", "hi"],
            "Application language"
        )
        
        # Date format
        self.create_setting_row(
            frame,
            "Date Format:",
            "date_format",
            "combobox",
            ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"],
            "Date display format"
        )
        
        # Time format
        self.create_setting_row(
            frame,
            "Time Format:",
            "time_format",
            "combobox",
            ["%H:%M:%S", "%I:%M:%S %p"],
            "Time display format"
        )
        
        # Animation toggle
        self.create_setting_row(
            frame,
            "Enable Animations:",
            "animation_enabled",
            "checkbox",
            tooltip="Enable/disable UI animations"
        )
        
        # Tooltips toggle
        self.create_setting_row(
            frame,
            "Show Tooltips:",
            "show_tooltips",
            "checkbox",
            tooltip="Show helpful tooltips on hover"
        )
    
    def create_recognition_settings(self):
        """Create recognition settings tab"""
        frame = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(frame, text="🎯 Recognition")
        
        # Camera index
        self.create_setting_row(
            frame,
            "Camera Index:",
            "camera_index",
            "spinbox",
            (0, 5),
            "Camera device index (usually 0)"
        )
        
        # Confidence threshold
        self.create_setting_row(
            frame,
            "Confidence Threshold:",
            "confidence_threshold",
            "scale",
            (0.3, 1.0),
            "Minimum confidence for recognition"
        )
        
        # Working hours
        self.create_setting_row(
            frame,
            "Working Hours Start:",
            "working_hours_start",
            "entry",
            tooltip="Start time for attendance (HH:MM)"
        )
        
        self.create_setting_row(
            frame,
            "Working Hours End:",
            "working_hours_end",
            "entry",
            tooltip="End time for attendance (HH:MM)"
        )
        
        # Late threshold
        self.create_setting_row(
            frame,
            "Late Threshold (mins):",
            "late_threshold_minutes",
            "spinbox",
            (0, 60),
            "Minutes after which marked as late"
        )
    
    def create_notification_settings(self):
        """Create notification settings tab"""
        frame = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(frame, text="🔔 Notifications")
        
        # Sound
        self.create_setting_row(
            frame,
            "Enable Sound:",
            "sound_enabled",
            "checkbox",
            tooltip="Play sound on recognition"
        )
        
        # Notifications
        self.create_setting_row(
            frame,
            "Enable Notifications:",
            "notification_enabled",
            "checkbox",
            tooltip="Show desktop notifications"
        )
    
    def create_backup_settings(self):
        """Create backup settings tab"""
        frame = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(frame, text="💾 Backup")
        
        # Auto backup
        self.create_setting_row(
            frame,
            "Auto Backup:",
            "auto_backup",
            "checkbox",
            tooltip="Automatically backup data"
        )
        
        # Backup interval
        self.create_setting_row(
            frame,
            "Backup Interval (hours):",
            "backup_interval_hours",
            "spinbox",
            (1, 168),
            "Hours between automatic backups"
        )
        
        # Auto export
        self.create_setting_row(
            frame,
            "Auto Export:",
            "auto_export",
            "checkbox",
            tooltip="Automatically export attendance"
        )
        
        # Export format
        self.create_setting_row(
            frame,
            "Export Format:",
            "export_format",
            "combobox",
            ["csv", "xlsx", "json"],
            "File format for exports"
        )
        
        # Manual backup button
        tk.Button(
            frame,
            text="🔄 Create Backup Now",
            command=self.create_backup,
            bg="#2196F3",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            padx=20,
            pady=8
        ).pack(pady=20)
    
    def create_about_section(self):
        """Create about tab"""
        frame = tk.Frame(self.notebook, bg="#1e1e2e")
        self.notebook.add(frame, text="ℹ️ About")
        
        # App info
        info_frame = tk.Frame(frame, bg="#2a2a3e")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            info_frame,
            text="🎯 AI Face Recognition Attendance System",
            font=("Segoe UI", 18, "bold"),
            bg="#2a2a3e",
            fg="#4CAF50"
        ).pack(pady=20)
        
        info_text = f"""
Version: {self.config.get('version', '2.0.0')}
Author: {self.config.get('author', 'Satyam Pandey')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This application uses advanced face recognition
technology for automated attendance tracking.

Features:
• Real-time face detection and recognition
• Student management system
• Comprehensive analytics dashboard
• Automated backup and export
• Multi-camera support
• Customizable settings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Built with Python, OpenCV, and Tkinter
Powered by Machine Learning

© 2024 All Rights Reserved
"""
        
        tk.Label(
            info_frame,
            text=info_text,
            font=("Consolas", 10),
            bg="#2a2a3e",
            fg="#b4b4c8",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Social links
        links_frame = tk.Frame(info_frame, bg="#2a2a3e")
        links_frame.pack(pady=20)
        
        tk.Button(
            links_frame,
            text="🌐 GitHub",
            command=lambda: webbrowser.open("https://github.com"),
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            links_frame,
            text="📧 Contact",
            command=lambda: webbrowser.open("mailto:contact@example.com"),
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def create_setting_row(self, parent, label, key, widget_type, 
                          options=None, tooltip=None):
        """Create a setting row"""
        row = tk.Frame(parent, bg="#1e1e2e")
        row.pack(fill=tk.X, padx=20, pady=10)
        
        # Label
        lbl = tk.Label(
            row,
            text=label,
            font=("Segoe UI", 10),
            bg="#1e1e2e",
            fg="#b4b4c8",
            width=25,
            anchor=tk.W
        )
        lbl.pack(side=tk.LEFT)
        
        # Widget
        current_value = self.config.get(key)
        
        if widget_type == "checkbox":
            var = tk.BooleanVar(value=current_value)
            widget = tk.Checkbutton(
                row,
                variable=var,
                bg="#1e1e2e",
                fg="white",
                selectcolor="#2a2a3e",
                activebackground="#1e1e2e"
            )
            widget.var = var
            
        elif widget_type == "combobox":
            var = tk.StringVar(value=current_value)
            widget = ttk.Combobox(
                row,
                textvariable=var,
                values=options,
                state="readonly",
                width=20
            )
            widget.var = var
            
        elif widget_type == "spinbox":
            var = tk.IntVar(value=current_value)
            widget = tk.Spinbox(
                row,
                from_=options[0],
                to=options[1],
                textvariable=var,
                width=10,
                bg="#2a2a3e",
                fg="white",
                buttonbackground="#363650"
            )
            widget.var = var
            
        elif widget_type == "scale":
            var = tk.DoubleVar(value=current_value)
            widget = tk.Scale(
                row,
                from_=options[0],
                to=options[1],
                resolution=0.05,
                orient=tk.HORIZONTAL,
                variable=var,
                bg="#1e1e2e",
                fg="white",
                troughcolor="#2a2a3e",
                highlightthickness=0,
                length=200
            )
            widget.var = var
            
        else:  # entry
            var = tk.StringVar(value=current_value)
            widget = tk.Entry(
                row,
                textvariable=var,
                font=("Segoe UI", 10),
                bg="#2a2a3e",
                fg="white",
                insertbackground="white",
                relief="flat",
                width=20
            )
            widget.var = var
        
        widget.pack(side=tk.LEFT, padx=10)
        
        # Store reference
        if not hasattr(self, 'setting_widgets'):
            self.setting_widgets = {}
        self.setting_widgets[key] = widget
        
        # Tooltip
        if tooltip:
            ToolTip(widget, tooltip)
    
    def save_settings(self):
        """Save all settings"""
        for key, widget in self.setting_widgets.items():
            self.config.set(key, widget.var.get())
        
        messagebox.showinfo("Settings Saved", "All settings have been saved successfully!")
    
    def create_backup(self):
        """Create manual backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backups/backup_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy database
            if os.path.exists("attendance_system.db"):
                shutil.copy("attendance_system.db", f"{backup_dir}/attendance_system.db")
            
            # Copy config
            if os.path.exists("config.json"):
                shutil.copy("config.json", f"{backup_dir}/config.json")
            
            # Copy model
            if os.path.exists("model.pkl"):
                shutil.copy("model.pkl", f"{backup_dir}/model.pkl")
            
            messagebox.showinfo("Backup Complete", f"Backup created at:\n{backup_dir}")
            
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Error creating backup:\n{str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ REPORTS PANEL ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class ReportsPanel(tk.Frame):
    """Reports generation panel"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.db = db_manager
        self.configure(bg="#1e1e2e")
        
        # Header
        header = tk.Frame(self, bg="#2a2a3e")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="📑 Reports & Export",
            font=("Segoe UI", 16, "bold"),
            bg="#2a2a3e",
            fg="white"
        ).pack(pady=15)
        
        # Content
        content = tk.Frame(self, bg="#1e1e2e")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Date range selector
        self.create_date_selector(content)
        
        # Report options
        self.create_report_options(content)
        
        # Preview area
        self.create_preview_area(content)
    
    def create_date_selector(self, parent):
        """Create date range selector"""
        frame = tk.LabelFrame(
            parent,
            text="📅 Date Range",
            font=("Segoe UI", 11, "bold"),
            bg="#2a2a3e",
            fg="white",
            padx=15,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 15))
        
        # Quick selectors
        quick_frame = tk.Frame(frame, bg="#2a2a3e")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        for text, days in [("Today", 0), ("This Week", 7), 
                          ("This Month", 30), ("All Time", -1)]:
            tk.Button(
                quick_frame,
                text=text,
                command=lambda d=days: self.set_date_range(d),
                bg="#363650",
                fg="white",
                font=("Segoe UI", 9),
                relief="flat",
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
        
        # Custom date range
        custom_frame = tk.Frame(frame, bg="#2a2a3e")
        custom_frame.pack(fill=tk.X)
        
        tk.Label(
            custom_frame,
            text="From:",
            bg="#2a2a3e",
            fg="white",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        self.start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(
            custom_frame,
            textvariable=self.start_date_var,
            font=("Segoe UI", 10),
            bg="#363650",
            fg="white",
            width=12,
            insertbackground="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            custom_frame,
            text="To:",
            bg="#2a2a3e",
            fg="white",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(
            custom_frame,
            textvariable=self.end_date_var,
            font=("Segoe UI", 10),
            bg="#363650",
            fg="white",
            width=12,
            insertbackground="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            custom_frame,
            text="🔄 Load",
            command=self.load_report_data,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=3
        ).pack(side=tk.LEFT, padx=15)
    
    def create_report_options(self, parent):
        """Create report options"""
        frame = tk.LabelFrame(
            parent,
            text="📊 Export Options",
            font=("Segoe UI", 11, "bold"),
            bg="#2a2a3e",
            fg="white",
            padx=15,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 15))
        
        btn_frame = tk.Frame(frame, bg="#2a2a3e")
        btn_frame.pack(fill=tk.X)
        
        export_options = [
            ("📄 Export CSV", self.export_csv, "#4CAF50"),
            ("📊 Export Excel", self.export_excel, "#217346"),
            ("📋 Export JSON", self.export_json, "#f39c12"),
            ("📑 Generate PDF Report", self.generate_pdf, "#e74c3c"),
            ("🖨️ Print Report", self.print_report, "#9b59b6")
        ]
        
        for text, command, color in export_options:
            tk.Button(
                btn_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Segoe UI", 10),
                relief="flat",
                padx=15,
                pady=8
            ).pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_preview_area(self, parent):
        """Create report preview area"""
        frame = tk.LabelFrame(
            parent,
            text="👁️ Preview",
            font=("Segoe UI", 11, "bold"),
            bg="#2a2a3e",
            fg="white",
            padx=10,
            pady=10
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Name", "Student ID", "Date", "Time", "Status")
        self.report_tree = SearchableTreeview(frame, columns)
        self.report_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load initial data
        self.load_report_data()
    
    def set_date_range(self, days):
        """Set date range based on quick selector"""
        end_date = datetime.now()
        
        if days == -1:  # All time
            start_date = datetime(2020, 1, 1)
        elif days == 0:  # Today
            start_date = end_date
        else:
            start_date = end_date - timedelta(days=days)
        
        self.start_date_var.set(start_date.strftime("%Y-%m-%d"))
        self.end_date_var.set(end_date.strftime("%Y-%m-%d"))
        
        self.load_report_data()
    
    def load_report_data(self):
        """Load report data for preview"""
        start = self.start_date_var.get()
        end = self.end_date_var.get()
        
        records = self.db.get_attendance_range(start, end)
        
        items = [
            (r['name'], r['student_id'], r['date'], r['time'], r['status'])
            for r in records
        ]
        
        self.report_tree.insert_items(items)
    
    def get_report_data(self):
        """Get data for export"""
        start = self.start_date_var.get()
        end = self.end_date_var.get()
        return self.db.get_attendance_range(start, end)
    
    def export_csv(self):
        """Export to CSV"""
        try:
            data = self.get_report_data()
            if not data:
                messagebox.showinfo("No Data", "No records to export!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if filename:
                df = pd.DataFrame([dict(row) for row in data])
                df.to_csv(filename, index=False)
                messagebox.showinfo("Export Complete", f"Exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def export_excel(self):
        """Export to Excel"""
        try:
            data = self.get_report_data()
            if not data:
                messagebox.showinfo("No Data", "No records to export!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            
            if filename:
                df = pd.DataFrame([dict(row) for row in data])
                df.to_excel(filename, index=False, engine='openpyxl')
                messagebox.showinfo("Export Complete", f"Exported to:\n{filename}")
                
        except ImportError:
            messagebox.showerror("Error", "Install openpyxl: pip install openpyxl")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def export_json(self):
        """Export to JSON"""
        try:
            data = self.get_report_data()
            if not data:
                messagebox.showinfo("No Data", "No records to export!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            if filename:
                records = [dict(row) for row in data]
                with open(filename, 'w') as f:
                    json.dump(records, f, indent=2, default=str)
                messagebox.showinfo("Export Complete", f"Exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def generate_pdf(self):
        """Generate PDF report"""
        messagebox.showinfo(
            "PDF Report",
            "PDF generation requires additional libraries.\n\n"
            "Install: pip install reportlab\n\n"
            "This feature would generate a formatted PDF report "
            "with attendance statistics, charts, and detailed records."
        )
    
    def print_report(self):
        """Print report"""
        messagebox.showinfo(
            "Print Report",
            "This feature would send the report to the default printer.\n\n"
            "Preview would be shown before printing."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ MAIN APPLICATION ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class AttendanceSystemGUI:
    """Main GUI class for Face Recognition Attendance System - ENHANCED"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize managers
        self.config = ConfigManager()
        self.db = DatabaseManager()
        
        # Window setup
        self.setup_window()
        
        # Process control
        self.recognition_process = None
        self.is_running = False
        self.start_time = None
        self.timer_running = False
        self.current_session_id = None
        self.recognized_count = 0
        self.unknown_count = 0
        
        # File paths
        self.model_file = "model.pkl"
        self.recognize_script = "recognize.py"
        
        # Initialize UI
        self.create_main_interface()
        self.check_dependencies()
        self.log_message("System initialized successfully", "SUCCESS")
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind_keyboard_shortcuts()
        
        # Auto-cleanup old logs
        self.db.clear_old_logs(30)
        
        # Check first run
        if self.config.get('first_run'):
            self.show_welcome_dialog()
            self.config.set('first_run', False)
    
    def setup_window(self):
        """Setup main window"""
        width = self.config.get('window_width', 1400)
        height = self.config.get('window_height', 900)
        
        self.root.title(f"{self.config.get('app_name')} v{self.config.get('version')}")
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(1200, 700)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        
        # Use saved position if available
        if self.config.get('remember_window_position'):
            saved_x = self.config.get('last_window_x')
            saved_y = self.config.get('last_window_y')
            if saved_x is not None and saved_y is not None:
                x, y = saved_x, saved_y
        
        self.root.geometry(f"+{x}+{y}")
        
        # Colors
        self.bg_primary = "#1e1e2e"
        self.bg_secondary = "#2a2a3e"
        self.bg_tertiary = "#363650"
        self.fg_primary = "#ffffff"
        self.fg_secondary = "#b4b4c8"
        self.accent_green = "#4CAF50"
        self.accent_red = "#f44336"
        self.accent_blue = "#2196F3"
        self.accent_orange = "#ff9800"
        
        self.root.configure(bg=self.bg_primary)
    
    def create_main_interface(self):
        """Create the main application interface"""
        
        # ═══════════════════════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════════════════════
        
        header_frame = tk.Frame(self.root, bg=self.bg_secondary, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg=self.bg_secondary)
        title_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            title_frame,
            text="🎯",
            font=("Segoe UI", 28),
            bg=self.bg_secondary
        ).pack(side=tk.LEFT)
        
        title_text = tk.Frame(title_frame, bg=self.bg_secondary)
        title_text.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            title_text,
            text=self.config.get('app_name'),
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_text,
            text=f"by {self.config.get('author')} | v{self.config.get('version')}",
            font=("Segoe UI", 9),
            bg=self.bg_secondary,
            fg=self.fg_secondary
        ).pack(anchor=tk.W)
        
        # Status in header
        status_frame = tk.Frame(header_frame, bg=self.bg_secondary)
        status_frame.pack(side=tk.RIGHT, padx=20)
        
        self.status_canvas = tk.Canvas(
            status_frame,
            width=15,
            height=15,
            bg=self.bg_secondary,
            highlightthickness=0
        )
        self.status_canvas.pack(side=tk.LEFT)
        self.status_canvas.create_oval(2, 2, 13, 13, fill="#666666", outline="")
        
        self.header_status_label = tk.Label(
            status_frame,
            text="IDLE",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_secondary,
            fg="#666666"
        )
        self.header_status_label.pack(side=tk.LEFT, padx=5)
        
        self.timer_label = tk.Label(
            status_frame,
            text="00:00:00",
            font=("Consolas", 14, "bold"),
            bg=self.bg_secondary,
            fg=self.accent_green
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        # ═══════════════════════════════════════════════════════════════════════
        # MAIN CONTENT AREA
        # ═══════════════════════════════════════════════════════════════════════
        
        main_container = tk.Frame(self.root, bg=self.bg_primary)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Content area with notebook
        content_frame = tk.Frame(main_container, bg=self.bg_primary)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.notebook = ModernNotebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_attendance_tab()
        self.create_students_tab()
        self.create_analytics_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        # ═══════════════════════════════════════════════════════════════════════
        # FOOTER / STATUS BAR
        # ═══════════════════════════════════════════════════════════════════════
        
        footer = tk.Frame(self.root, bg=self.bg_tertiary, height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Left info
        tk.Label(
            footer,
            text=f"📅 {datetime.now().strftime('%A, %B %d, %Y')}",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.fg_secondary
        ).pack(side=tk.LEFT, padx=10)
        
        # Right info
        self.footer_status = tk.Label(
            footer,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.bg_tertiary,
            fg=self.accent_green
        )
        self.footer_status.pack(side=tk.RIGHT, padx=10)
    
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = tk.Frame(parent, bg=self.bg_secondary, width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Quick actions section
        tk.Label(
            sidebar,
            text="⚡ Quick Actions",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary
        ).pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # Main control buttons
        self.start_btn = AnimatedButton(
            sidebar,
            text="START",
            icon="▶",
            command=self.start_attendance,
            bg_color=self.accent_green,
            hover_color="#45a049",
            width=190,
            height=50
        )
        self.start_btn.pack(padx=15, pady=5)
        
        self.stop_btn = AnimatedButton(
            sidebar,
            text="STOP",
            icon="⏹",
            command=self.stop_attendance,
            bg_color=self.accent_red,
            hover_color="#da190b",
            width=190,
            height=50
        )
        self.stop_btn.pack(padx=15, pady=5)
        self.stop_btn.set_enabled(False)
        
        # Separator
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=15, pady=15)
        
        # Navigation section
        tk.Label(
            sidebar,
            text="📍 Navigation",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        nav_items = [
            ("🏠 Dashboard", 0),
            ("📋 Attendance", 1),
            ("👥 Students", 2),
            ("📈 Analytics", 3),
            ("📑 Reports", 4),
            ("⚙️ Settings", 5)
        ]
        
        for text, tab_index in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                command=lambda idx=tab_index: self.notebook.select(idx),
                font=("Segoe UI", 10),
                bg=self.bg_tertiary,
                fg=self.fg_primary,
                activebackground=self.accent_blue,
                activeforeground="white",
                relief="flat",
                anchor=tk.W,
                padx=15,
                pady=8,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, padx=15, pady=2)
        
        # Separator
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=15, pady=15)
        
        # Live stats
        tk.Label(
            sidebar,
            text="📊 Session Stats",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        stats_frame = tk.Frame(sidebar, bg=self.bg_tertiary)
        stats_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.session_recognized = tk.Label(
            stats_frame,
            text="Recognized: 0",
            font=("Segoe UI", 10),
            bg=self.bg_tertiary,
            fg=self.accent_green
        )
        self.session_recognized.pack(anchor=tk.W, padx=10, pady=5)
        
        self.session_unknown = tk.Label(
            stats_frame,
            text="Unknown: 0",
            font=("Segoe UI", 10),
            bg=self.bg_tertiary,
            fg=self.accent_orange
        )
        self.session_unknown.pack(anchor=tk.W, padx=10, pady=5)
        
        # Exit button at bottom
        exit_btn = tk.Button(
            sidebar,
            text="🚪 Exit Application",
            command=self.on_closing,
            font=("Segoe UI", 10),
            bg="#333333",
            fg="white",
            activebackground=self.accent_red,
            relief="flat",
            pady=10
        )
        exit_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard = tk.Frame(self.notebook, bg=self.bg_primary)
        self.notebook.add(dashboard, text="🏠 Dashboard")
        
        # Welcome section
        welcome_frame = tk.Frame(dashboard, bg=self.bg_secondary)
        welcome_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            welcome_frame,
            text=f"👋 Welcome back!",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary
        ).pack(pady=15)
        
        tk.Label(
            welcome_frame,
            text=f"Today is {datetime.now().strftime('%A, %B %d, %Y')}",
            font=("Segoe UI", 12),
            bg=self.bg_secondary,
            fg=self.fg_secondary
        ).pack(pady=(0, 15))
        
        # Quick stats
        stats_frame = tk.Frame(dashboard, bg=self.bg_primary)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        stats = self.db.get_attendance_stats()
        
        cards_data = [
            ("Today's Attendance", stats['today'], "👥", self.accent_green),
            ("Weekly Total", stats['this_week'], "📅", self.accent_blue),
            ("Monthly Total", stats['this_month'], "🗓️", self.accent_orange),
            ("All Time", stats['total'], "📊", "#9c27b0")
        ]
        
        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(stats_frame, title, value, icon, color)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Two column layout
        columns = tk.Frame(dashboard, bg=self.bg_primary)
        columns.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - Activity log
        log_frame = tk.LabelFrame(
            columns,
            text="📋 Activity Log",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary,
            padx=10,
            pady=10
        )
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 9),
            bg="#1a1a2e",
            fg="#00ff00",
            insertbackground="white",
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Right column - Recent attendance
        recent_frame = tk.LabelFrame(
            columns,
            text="🕐 Recent Attendance",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_secondary,
            fg=self.fg_primary,
            padx=10,
            pady=10
        )
        recent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Recent attendance list
        recent_list = tk.Frame(recent_frame, bg=self.bg_secondary)
        recent_list.pack(fill=tk.BOTH, expand=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        recent_records = self.db.get_attendance_by_date(today)[:10]
        
        if recent_records:
            for record in recent_records:
                item_frame = tk.Frame(recent_list, bg=self.bg_tertiary)
                item_frame.pack(fill=tk.X, pady=2)
                
                tk.Label(
                    item_frame,
                    text=f"✓ {record['name']}",
                    font=("Segoe UI", 10),
                    bg=self.bg_tertiary,
                    fg=self.fg_primary,
                    anchor=tk.W
                ).pack(side=tk.LEFT, padx=10, pady=5)
                
                tk.Label(
                    item_frame,
                    text=record['time'],
                    font=("Segoe UI", 9),
                    bg=self.bg_tertiary,
                    fg=self.fg_secondary
                ).pack(side=tk.RIGHT, padx=10, pady=5)
        else:
            tk.Label(
                recent_list,
                text="No attendance recorded today",
                font=("Segoe UI", 10),
                bg=self.bg_secondary,
                fg=self.fg_secondary
            ).pack(pady=20)
    
    def create_attendance_tab(self):
        """Create attendance viewing tab"""
        attendance_frame = tk.Frame(self.notebook, bg=self.bg_primary)
        self.notebook.add(attendance_frame, text="📋 Attendance")
        
        # Header with filters
        filter_frame = tk.Frame(attendance_frame, bg=self.bg_secondary)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            filter_frame,
            text="📅 Filter by Date:",
            font=("Segoe UI", 10),
            bg=self.bg_secondary,
            fg=self.fg_primary
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        self.filter_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(
            filter_frame,
            textvariable=self.filter_date,
            font=("Segoe UI", 10),
            bg=self.bg_tertiary,
            fg=self.fg_primary,
            width=15,
            insertbackground="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="🔍 Filter",
            command=self.filter_attendance,
            bg=self.accent_blue,
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            filter_frame,
            text="📅 Today",
            command=lambda: self.quick_filter("today"),
            bg=self.accent_green,
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="📆 This Week",
            command=lambda: self.quick_filter("week"),
            bg=self.accent_orange,
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Attendance table
        table_frame = tk.Frame(attendance_frame, bg=self.bg_primary)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("ID", "Name", "Student ID", "Date", "Time", "Status", "Late (min)")
        self.attendance_tree = SearchableTreeview(table_frame, columns)
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load initial data
        self.filter_attendance()
    
    def create_students_tab(self):
        """Create students management tab"""
        students_panel = StudentManagementPanel(self.notebook, self.db)
        self.notebook.add(students_panel, text="👥 Students")
    
    def create_analytics_tab(self):
        """Create analytics tab"""
        analytics_panel = AnalyticsPanel(self.notebook, self.db)
        self.notebook.add(analytics_panel, text="📈 Analytics")
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_panel = ReportsPanel(self.notebook, self.db)
        self.notebook.add(reports_panel, text="📑 Reports")
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_panel = SettingsPanel(self.notebook, self.config)
        self.notebook.add(settings_panel, text="⚙️ Settings")
    
    def filter_attendance(self):
        """Filter attendance by date"""
        date = self.filter_date.get()
        records = self.db.get_attendance_by_date(date)
        
        items = [
            (
                r['id'],
                r['name'],
                r['student_id'],
                r['date'],
                r['time'],
                r['status'],
                r['late_minutes']
            )
            for r in records
        ]
        
        self.attendance_tree.insert_items(items)
    
    def quick_filter(self, period):
        """Quick filter by period"""
        today = datetime.now()
        
        if period == "today":
            self.filter_date.set(today.strftime("%Y-%m-%d"))
        elif period == "week":
            week_ago = today - timedelta(days=7)
            self.filter_date.set(week_ago.strftime("%Y-%m-%d"))
        
        self.filter_attendance()
    
    def log_message(self, message, level="INFO"):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "INFO": "#00bfff",
            "SUCCESS": "#00ff00",
            "WARNING": "#ffa500",
            "ERROR": "#ff4444"
        }
        
        # Update GUI log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Save to database
        self.db.add_log(message, level)
        
        # Log to file if enabled
        if self.config.get('log_to_file'):
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
            
            with open(log_file, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] [{level}] {message}\n")
    
    def update_status(self, status, color):
        """Update status indicators"""
        self.header_status_label.config(text=status, fg=color)
        self.status_canvas.delete("all")
        self.status_canvas.create_oval(2, 2, 13, 13, fill=color, outline="")
        self.footer_status.config(text=status, fg=color)
    
    def check_dependencies(self):
        """Check required files and dependencies"""
        issues = []
        
        if not os.path.exists(self.model_file):
            issues.append("⚠️ model.pkl not found")
            self.log_message("Model file missing - run train_model.py", "WARNING")
        
        if not os.path.exists(self.recognize_script):
            issues.append("⚠️ recognize.py not found")
            self.log_message("Recognition script missing", "ERROR")
        
        # Create required directories
        for dir_name in ["attendance", "logs", "backups", "exports"]:
            os.makedirs(dir_name, exist_ok=True)
        
        if issues:
            self.start_btn.set_enabled(False)
            messagebox.showwarning("Dependencies", "\n".join(issues))
        else:
            self.log_message("All dependencies verified", "SUCCESS")
    
    def start_attendance(self):
        """Start the attendance recognition system"""
        if self.is_running:
            messagebox.showinfo("Info", "Attendance system is already running!")
            return
        
        if not os.path.exists(self.model_file):
            messagebox.showerror("Error", "model.pkl not found!\nRun train_model.py first.")
            return
        
        # Create new session
        self.current_session_id = self.db.create_session()
        self.recognized_count = 0
        self.unknown_count = 0
        
        def run_recognition():
            try:
                self.log_message("Starting face recognition...", "INFO")
                
                self.recognition_process = subprocess.Popen(
                    [sys.executable, self.recognize_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                self.is_running = True
                self.start_time = time.time()
                
                # Update UI
                self.root.after(0, lambda: self.start_btn.set_enabled(False))
                self.root.after(0, lambda: self.stop_btn.set_enabled(True))
                self.root.after(0, lambda: self.update_status("RUNNING", self.accent_green))
                self.root.after(0, lambda: self.log_message("Recognition started", "SUCCESS"))
                
                # Start timer
                self.timer_running = True
                self.root.after(0, self.update_timer)
                
                # Monitor output
                for line in self.recognition_process.stdout:
                    line = line.strip()
                    if line:
                        self.root.after(0, lambda l=line: self.process_recognition_output(l))
                
                self.recognition_process.wait()
                self.cleanup_after_stop()
                
            except Exception as e:
                self.cleanup_after_stop()
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        thread = threading.Thread(target=run_recognition, daemon=True)
        thread.start()
    
    def process_recognition_output(self, line):
        """Process output from recognition script"""
        self.log_message(line, "INFO")
        
        # Parse recognition results
        if "Recognized:" in line or "Marked:" in line:
            self.recognized_count += 1
            self.session_recognized.config(text=f"Recognized: {self.recognized_count}")
        elif "Unknown" in line:
            self.unknown_count += 1
            self.session_unknown.config(text=f"Unknown: {self.unknown_count}")
    
    def stop_attendance(self):
        """Stop the running attendance system"""
        if not self.is_running or not self.recognition_process:
            return
        
        try:
            self.log_message("Stopping recognition...", "WARNING")
            self.recognition_process.terminate()
            
            try:
                self.recognition_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.recognition_process.kill()
            
            self.cleanup_after_stop()
            
        except Exception as e:
            self.log_message(f"Stop error: {e}", "ERROR")
    
    def cleanup_after_stop(self):
        """Cleanup after stopping recognition"""
        self.is_running = False
        self.timer_running = False
        
        # End session in database
        if self.current_session_id:
            self.db.end_session(
                self.current_session_id,
                self.recognized_count,
                self.unknown_count
            )
        
        self.root.after(0, lambda: self.start_btn.set_enabled(True))
        self.root.after(0, lambda: self.stop_btn.set_enabled(False))
        self.root.after(0, lambda: self.update_status("STOPPED", self.accent_orange))
        self.root.after(0, lambda: self.log_message("Recognition stopped", "INFO"))
    
    def update_timer(self):
        """Update session timer"""
        if self.timer_running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="00:00:00")
    
    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind("<F5>", lambda e: self.start_attendance())
        self.root.bind("<Escape>", lambda e: self.stop_attendance())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<Control-s>", lambda e: self.config.save_config())
    
    def show_welcome_dialog(self):
        """Show welcome dialog on first run"""
        welcome = tk.Toplevel(self.root)
        welcome.title("Welcome!")
        welcome.geometry("500x400")
        welcome.configure(bg=self.bg_primary)
        welcome.transient(self.root)
        welcome.grab_set()
        
        # Center the dialog
        welcome.update_idletasks()
        x = (welcome.winfo_screenwidth() - 500) // 2
        y = (welcome.winfo_screenheight() - 400) // 2
        welcome.geometry(f"+{x}+{y}")
        
        tk.Label(
            welcome,
            text="🎯",
            font=("Segoe UI", 48),
            bg=self.bg_primary
        ).pack(pady=20)
        
        tk.Label(
            welcome,
            text="Welcome to AI Face Recognition\nAttendance System!",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_primary,
            fg=self.fg_primary,
            justify=tk.CENTER
        ).pack(pady=10)
        
        tk.Label(
            welcome,
            text="Version 2.0 - Enhanced Edition\n\n"
                 "Features:\n"
                 "• Real-time face recognition\n"
                 "• Student management\n"
                 "• Analytics dashboard\n"
                 "• Report generation\n"
                 "• And much more!",
            font=("Segoe UI", 11),
            bg=self.bg_primary,
            fg=self.fg_secondary,
            justify=tk.CENTER
        ).pack(pady=10)
        
        tk.Button(
            welcome,
            text="Get Started →",
            command=welcome.destroy,
            bg=self.accent_green,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=30,
            pady=10
        ).pack(pady=20)
    
    def on_closing(self):
        """Handle application close"""
        if self.is_running:
            response = messagebox.askyesno(
                "Confirm Exit",
                "Recognition is running. Stop and exit?"
            )
            if response:
                self.stop_attendance()
                time.sleep(0.5)
            else:
                return
        
        # Save window position
        if self.config.get('remember_window_position'):
            self.config.set('last_window_x', self.root.winfo_x())
            self.config.set('last_window_y', self.root.winfo_y())
        
        self.db.close()
        self.log_message("Application closed", "INFO")
        self.root.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ SPLASH SCREEN ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

class SplashScreen:
    """Animated splash screen"""
    
    def __init__(self, root):
        self.root = root
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        
        # Size and position
        width, height = 500, 350
        x = (self.splash.winfo_screenwidth() - width) // 2
        y = (self.splash.winfo_screenheight() - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
        
        self.splash.configure(bg="#1e1e2e")
        
        # Content
        tk.Label(
            self.splash,
            text="🎯",
            font=("Segoe UI", 64),
            bg="#1e1e2e"
        ).pack(pady=(40, 20))
        
        tk.Label(
            self.splash,
            text="AI Face Recognition",
            font=("Segoe UI", 24, "bold"),
            bg="#1e1e2e",
            fg="white"
        ).pack()
        
        tk.Label(
            self.splash,
            text="Attendance System",
            font=("Segoe UI", 18),
            bg="#1e1e2e",
            fg="#4CAF50"
        ).pack()
        
        tk.Label(
            self.splash,
            text="v2.0 Enhanced Edition",
            font=("Segoe UI", 10),
            bg="#1e1e2e",
            fg="#b4b4c8"
        ).pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.splash,
            length=400,
            mode='determinate'
        )
        self.progress.pack(pady=30)
        
        self.status_label = tk.Label(
            self.splash,
            text="Loading...",
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#b4b4c8"
        )
        self.status_label.pack()
        
        tk.Label(
            self.splash,
            text="by Satyam Pandey",
            font=("Segoe UI", 9),
            bg="#1e1e2e",
            fg="#666666"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def update_progress(self, value, text=""):
        """Update progress bar"""
        self.progress['value'] = value
        if text:
            self.status_label.config(text=text)
        self.splash.update()
    
    def close(self):
        """Close splash screen"""
        self.splash.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗ MAIN EXECUTION ███████╗
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    root = tk.Tk()
    root.withdraw()  # Hide main window during splash
    
    # Show splash screen
    splash = SplashScreen(root)
    
    # Simulate loading
    loading_steps = [
        (10, "Initializing..."),
        (25, "Loading configuration..."),
        (40, "Connecting to database..."),
        (55, "Loading modules..."),
        (70, "Checking dependencies..."),
        (85, "Preparing interface..."),
        (100, "Ready!")
    ]
    
    for progress, text in loading_steps:
        splash.update_progress(progress, text)
        time.sleep(0.2)
    
    time.sleep(0.3)
    splash.close()
    
    # Show main application
    root.deiconify()
    app = AttendanceSystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()     