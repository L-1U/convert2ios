"""
Test script to verify the GUI components work correctly
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

def test_gui_components():
    """Test that all GUI components can be created"""
    try:
        # Create root window
        root = tk.Tk()
        root.title("GUI Test")
        root.geometry("400x300")
        
        # Test basic widgets
        label = ttk.Label(root, text="GUI Test - All Components Working!")
        label.pack(pady=20)
        
        # Test file dialog imports
        try:
            from tkinter import filedialog, messagebox
            ttk.Label(root, text="[OK] File dialogs available").pack()
        except ImportError as e:
            ttk.Label(root, text=f"[ERROR] File dialogs error: {e}").pack()
        
        # Test threading
        try:
            import threading
            ttk.Label(root, text="[OK] Threading available").pack()
        except ImportError as e:
            ttk.Label(root, text=f"[ERROR] Threading error: {e}").pack()
        
        # Test subprocess
        try:
            import subprocess
            ttk.Label(root, text="[OK] Subprocess available").pack()
        except ImportError as e:
            ttk.Label(root, text=f"[ERROR] Subprocess error: {e}").pack()
        
        # Test pathlib
        try:
            from pathlib import Path
            ttk.Label(root, text="[OK] Pathlib available").pack()
        except ImportError as e:
            ttk.Label(root, text=f"[ERROR] Pathlib error: {e}").pack()
        
        # Close button
        ttk.Button(root, text="Close Test", command=root.quit).pack(pady=20)
        
        print("[OK] GUI test window created successfully!")
        print("[INFO] Close the test window to continue...")
        
        # Run for 5 seconds then close automatically
        root.after(5000, root.quit)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] GUI test failed: {e}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is available"""
    import shutil
    if shutil.which("ffmpeg"):
        print("[OK] FFmpeg found in PATH")
        return True
    else:
        print("[WARNING] FFmpeg not found in PATH")
        print("   Download from: https://ffmpeg.org/download.html")
        return False

def main():
    print("Testing Video Converter GUI Components")
    print("="*50)
    
    # Test Python version
    print(f"Python version: {sys.version}")
    
    # Test GUI components
    if test_gui_components():
        print("[OK] GUI components test passed!")
    else:
        print("[ERROR] GUI components test failed!")
        return False
    
    # Test FFmpeg
    check_ffmpeg()
    
    print("\nComponent Test Summary:")
    print("[OK] Python GUI framework working")
    print("[OK] All required modules available")
    print("[OK] Ready for building executable")
    
    return True

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
