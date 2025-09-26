import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import shutil
import sys
import os
import threading
from pathlib import Path


class VideoConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Converter - GPU Accelerated")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.codec_var = tk.StringVar(value="h265")
        self.use_gpu_var = tk.BooleanVar(value=True)
        
        # Process tracking
        self.current_process = None
        self.conversion_thread = None
        
        # Setup cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Video Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        input_btn_frame = ttk.Frame(main_frame)
        input_btn_frame.grid(row=1, column=2, pady=5)
        ttk.Button(input_btn_frame, text="Browse", 
                  command=self.browse_input_file).pack(side=tk.LEFT)
        ttk.Button(input_btn_frame, text="Clear", 
                  command=self.clear_input_file, width=6).pack(side=tk.LEFT, padx=(2, 0))
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        # Codec selection
        codec_frame = ttk.LabelFrame(main_frame, text="Encoding Options", padding="10")
        codec_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        codec_frame.columnconfigure(0, weight=1)
        
        ttk.Label(codec_frame, text="Codec:").grid(row=0, column=0, sticky=tk.W)
        codec_combo = ttk.Combobox(codec_frame, textvariable=self.codec_var, 
                                  values=["h264", "h265"], state="readonly", width=10)
        codec_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # GPU acceleration checkbox
        ttk.Checkbutton(codec_frame, text="Use GPU Acceleration (NVENC)", 
                       variable=self.use_gpu_var).grid(row=1, column=0, columnspan=2, 
                                                      sticky=tk.W, pady=(10, 0))
        
        # Convert and Stop buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.convert_btn = ttk.Button(button_frame, text="Convert Video", 
                                     command=self.start_conversion, style="Accent.TButton")
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Conversion", 
                                  command=self.stop_conversion, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Release Locks", 
                  command=self.release_all_locks).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status text
        self.status_text = tk.Text(main_frame, height=8, width=70, wrap=tk.WORD)
        self.status_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=6, column=3, sticky=(tk.N, tk.S), pady=10)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure row weight for text area
        main_frame.rowconfigure(6, weight=1)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.ts *.m4v"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Ensure proper UTF-8 handling for paths
            try:
                # Normalize the path to handle UTF-8 characters properly
                normalized_path = os.path.normpath(filename)
                self.input_file.set(normalized_path)
                
                # Auto-suggest output filename with UTF-8 support
                if not self.output_file.get():
                    input_path = Path(normalized_path)
                    output_path = input_path.with_suffix('.mp4')
                    # If same extension, add _converted
                    if input_path.suffix.lower() == '.mp4':
                        output_path = input_path.with_stem(input_path.stem + '_converted')
                    self.output_file.set(str(output_path))
                    
                self.log_message(f"📁 เลือกไฟล์: {normalized_path}")
                
                # Important: Don't keep any file handles open
                # Just store the path, don't open or probe the file
                
            except Exception as e:
                self.log_message(f"⚠️ ข้อผิดพลาดในการเลือกไฟล์: {e}")
                messagebox.showerror("Error", f"ไม่สามารถเลือกไฟล์ได้: {e}")
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save Output Video As",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("MKV files", "*.mkv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            try:
                # Normalize the path to handle UTF-8 characters properly
                normalized_path = os.path.normpath(filename)
                self.output_file.set(normalized_path)
                self.log_message(f"💾 เลือกไฟล์เอาต์พุต: {normalized_path}")
            except Exception as e:
                self.log_message(f"⚠️ ข้อผิดพลาดในการเลือกไฟล์เอาต์พุต: {e}")
                messagebox.showerror("Error", f"ไม่สามารถเลือกไฟล์เอาต์พุตได้: {e}")
    
    def clear_input_file(self):
        """Clear input file selection and release any locks"""
        self.input_file.set("")
        self.log_message("🗑️ ล้างการเลือกไฟล์ input")
        # Force garbage collection to release any file handles
        import gc
        gc.collect()
    
    def clear_output_file(self):
        """Clear output file selection"""
        self.output_file.set("")
        self.log_message("🗑️ ล้างการเลือกไฟล์ output")
    
    def log_message(self, message):
        """Add message to status text area"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_nvenc(self):
        """ตรวจสอบว่า ffmpeg รองรับ NVENC หรือไม่"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            encoders = result.stdout
            return ("h264_nvenc" in encoders) or ("hevc_nvenc" in encoders)
        except Exception as e:
            self.log_message(f"❌ ไม่สามารถตรวจสอบ ffmpeg ได้: {e}")
            return False
    
    def convert_video(self, input_file, output_file, use_gpu=True, codec="h264"):
        """แปลงวิดีโอด้วย GPU (NVENC) ถ้ามี, ถ้าไม่มี fallback ไป CPU"""
        
        if use_gpu and self.check_nvenc():
            self.log_message("✅ ใช้ GPU (NVENC) สำหรับการเข้ารหัส")
            if codec == "h264":
                vcodec = "h264_nvenc"
            elif codec == "h265":
                vcodec = "hevc_nvenc"
            else:
                self.log_message(f"⚠️ ไม่รู้จัก codec: {codec}, ใช้ h264 แทน")
                vcodec = "h264_nvenc"
        else:
            self.log_message("⚠️ ไม่พบ NVENC → ใช้ CPU (libx264)")
            vcodec = "libx264"
        
        command = [
            "ffmpeg",
            "-hwaccel", "cuda",   # ใช้ GPU decode ถ้ามี
            "-i", input_file,
            "-c:v", vcodec,
            "-preset", "p3" if "nvenc" in vcodec else "medium",
            "-b:v", "5M",         # Bitrate วิดีโอ
            "-c:a", "aac",
            "-b:a", "192k",
            "-y",  # Overwrite output file
            output_file
        ]
        
        self.log_message("🚀 รันคำสั่ง: " + " ".join(command))
        
        try:
            # Run ffmpeg with real-time output and UTF-8 encoding
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'  # Replace invalid characters instead of crashing
            )
            
            # Read output in real-time
            for line in self.current_process.stdout:
                if line.strip():
                    self.log_message(line.strip())
                # Check if process was terminated
                if self.current_process.poll() is not None:
                    break
            
            self.current_process.wait()
            
            if self.current_process.returncode == 0:
                self.log_message("🎉 แปลงไฟล์เสร็จแล้ว: " + output_file)
                return True
            else:
                self.log_message(f"❌ การแปลงไฟล์ล้มเหลว (exit code: {self.current_process.returncode})")
                return False
                
        except Exception as e:
            self.log_message(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def start_conversion(self):
        """Start conversion in a separate thread"""
        input_file = self.input_file.get().strip()
        output_file = self.output_file.get().strip()
        
        # Validation
        if not input_file:
            messagebox.showerror("Error", "กรุณาเลือกไฟล์ input")
            return
        
        if not output_file:
            messagebox.showerror("Error", "กรุณาระบุไฟล์ output")
            return
        
        # Check if input file exists with proper UTF-8 handling
        try:
            if not os.path.exists(input_file):
                messagebox.showerror("Error", f"ไฟล์ input ไม่พบ: {input_file}")
                return
        except UnicodeError as e:
            messagebox.showerror("Error", f"ข้อผิดพลาดในการอ่านชื่อไฟล์: {e}")
            return
        
        # Validate output directory exists and is writable
        try:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.log_message(f"📁 สร้างโฟลเดอร์: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถสร้างโฟลเดอร์เอาต์พุตได้: {e}")
            return
        
        # Check if ffmpeg is available
        if not shutil.which("ffmpeg"):
            messagebox.showerror("Error", "ไม่พบ ffmpeg ในระบบ\nกรุณาติดตั้ง ffmpeg ก่อน")
            return
        
        # Clear status text
        self.status_text.delete(1.0, tk.END)
        
        # Disable convert button, enable stop button, and start progress
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.stop_btn.configure(state="normal")
        self.progress.start()
        
        # Start conversion in thread
        self.conversion_thread = threading.Thread(target=self.conversion_worker)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
    
    def conversion_worker(self):
        """Run conversion in separate thread"""
        try:
            success = self.convert_video(
                self.input_file.get(),
                self.output_file.get(),
                self.use_gpu_var.get(),
                self.codec_var.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self.conversion_finished, success)
            
        except Exception as e:
            self.root.after(0, self.conversion_error, str(e))
        finally:
            # Clear process reference when done
            self.current_process = None
    
    def conversion_finished(self, success):
        """Called when conversion is finished"""
        self.progress.stop()
        self.convert_btn.configure(state="normal", text="Convert Video")
        self.stop_btn.configure(state="disabled")
        
        if success:
            messagebox.showinfo("Success", "แปลงไฟล์เสร็จแล้ว!")
        else:
            messagebox.showerror("Error", "การแปลงไฟล์ล้มเหลว")
    
    def conversion_error(self, error_msg):
        """Called when conversion encounters an error"""
        self.progress.stop()
        self.convert_btn.configure(state="normal", text="Convert Video")
        self.stop_btn.configure(state="disabled")
        self.log_message(f"❌ เกิดข้อผิดพลาด: {error_msg}")
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {error_msg}")
    
    def stop_conversion(self):
        """Stop the current conversion process"""
        if self.current_process and self.current_process.poll() is None:
            try:
                self.log_message("🛑 หยุดการแปลงไฟล์...")
                self.current_process.terminate()
                # Wait a bit for graceful termination
                try:
                    self.current_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    self.current_process.kill()
                    self.current_process.wait()
                self.log_message("✅ หยุดการแปลงไฟล์แล้ว")
                
                # Reset UI
                self.progress.stop()
                self.convert_btn.configure(state="normal", text="Convert Video")
                self.stop_btn.configure(state="disabled")
                
            except Exception as e:
                self.log_message(f"⚠️ ข้อผิดพลาดในการหยุดกระบวนการ: {e}")
        else:
            # No process running, just reset UI
            self.progress.stop()
            self.convert_btn.configure(state="normal", text="Convert Video")
            self.stop_btn.configure(state="disabled")
    
    def kill_all_ffmpeg_processes(self):
        """Kill all ffmpeg processes that might be locking files"""
        try:
            import psutil
            killed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'ffmpeg' in proc.info['name'].lower():
                        proc.kill()
                        killed_count += 1
                        self.log_message(f"🔫 ฆ่ากระบวนการ ffmpeg PID: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed_count > 0:
                self.log_message(f"✅ ฆ่ากระบวนการ ffmpeg จำนวน {killed_count} กระบวนการ")
            else:
                self.log_message("ℹ️ ไม่พบกระบวนการ ffmpeg ที่ทำงานอยู่")
                
        except ImportError:
            # Fallback to taskkill if psutil not available
            try:
                subprocess.run(["taskkill", "/f", "/im", "ffmpeg.exe"], 
                             capture_output=True, check=False)
                self.log_message("🔫 ใช้ taskkill ฆ่ากระบวนการ ffmpeg")
            except Exception as e:
                self.log_message(f"⚠️ ไม่สามารถฆ่ากระบวนการ ffmpeg ได้: {e}")
        except Exception as e:
            self.log_message(f"⚠️ ข้อผิดพลาดในการฆ่ากระบวนการ: {e}")

    def release_all_locks(self):
        """Release all file locks and handles"""
        try:
            # First kill any remaining ffmpeg processes
            self.kill_all_ffmpeg_processes()
            
            # Clear file selections
            self.input_file.set("")
            self.output_file.set("")
            
            # Force garbage collection to release file handles
            import gc
            gc.collect()
            
            # Clear any cached file information
            if hasattr(self, '_file_cache'):
                delattr(self, '_file_cache')
            
            # Wait a moment for system to release locks
            import time
            time.sleep(0.5)
                
            self.log_message("🔓 ปล่อยการล็อกไฟล์ทั้งหมด")
        except Exception as e:
            self.log_message(f"⚠️ ข้อผิดพลาดในการปล่อยล็อก: {e}")
    
    def on_closing(self):
        """Handle window closing event"""
        if self.current_process and self.current_process.poll() is None:
            # Ask user if they want to stop the conversion
            result = messagebox.askyesno(
                "Conversion in Progress", 
                "การแปลงไฟล์กำลังดำเนินการอยู่\nคุณต้องการหยุดและปิดโปรแกรมหรือไม่?"
            )
            if result:
                self.stop_conversion()
                self.release_all_locks()
                self.root.destroy()
        else:
            # Always release locks when closing
            self.release_all_locks()
            self.root.destroy()


def main():
    root = tk.Tk()
    app = VideoConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
