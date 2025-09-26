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
        self.root.title("Video Converter - iOS Compatible")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        # Default to h264 for better iOS compatibility
        self.codec_var = tk.StringVar(value="h264")
        self.use_gpu_var = tk.BooleanVar(value=True)
        self.format_var = tk.StringVar(value="mp4")  # Output format selection

        # Process tracking
        self.current_process = None
        self.conversion_thread = None

        # Progress tracking
        self.total_duration = 0
        self.current_time = 0
        self.conversion_speed = 0

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
        title_label = ttk.Label(main_frame, text="Video Converter - iOS Compatible",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # iOS compatibility note
        subtitle_label = ttk.Label(main_frame, text="✅ Optimized for iOS playback",
                                   font=("Arial", 10), foreground="green")
        subtitle_label.grid(row=0, column=0, columnspan=3, pady=(30, 10))

        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)

        input_btn_frame = ttk.Frame(main_frame)
        input_btn_frame.grid(row=2, column=2, pady=5)
        ttk.Button(input_btn_frame, text="Browse",
                   command=self.browse_input_file).pack(side=tk.LEFT)
        ttk.Button(input_btn_frame, text="Clear",
                   command=self.clear_input_file, width=6).pack(side=tk.LEFT, padx=(2, 0))

        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(
            row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(
            row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse",
                   command=self.browse_output_file).grid(row=3, column=2, pady=5)

        # Codec selection
        codec_frame = ttk.LabelFrame(
            main_frame, text="Encoding Options (IOS Compatible)", padding="10")
        codec_frame.grid(row=4, column=0, columnspan=3,
                         sticky=(tk.W, tk.E), pady=10)
        codec_frame.columnconfigure(0, weight=1)

        ttk.Label(codec_frame, text="Codec:").grid(
            row=0, column=0, sticky=tk.W)
        codec_combo = ttk.Combobox(codec_frame, textvariable=self.codec_var,
                                   values=["h264", "h265"], state="readonly", width=10)
        codec_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(codec_frame, text="Format:").grid(
            row=0, column=2, sticky=tk.W, padx=(20, 0))
        format_combo = ttk.Combobox(codec_frame, textvariable=self.format_var,
                                    values=["mp4", "mov", "m4v"], state="readonly", width=8)
        format_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))

        # GPU acceleration checkbox
        ttk.Checkbutton(codec_frame, text="Use GPU Acceleration (NVENC)",
                        variable=self.use_gpu_var).grid(row=1, column=0, columnspan=2,
                                                        sticky=tk.W, pady=(10, 0))

        # iOS compatibility note
        ttk.Label(codec_frame, text="📱 Baseline Profile + Level 3.1 = Maximum iOS Compatibility",
                  font=("Arial", 9), foreground="blue").grid(row=2, column=0, columnspan=4,
                                                             sticky=tk.W, pady=(5, 0))

        # Format recommendation
        ttk.Label(codec_frame, text="💡 Recommended: H.264 + MP4 for best iOS support",
                  font=("Arial", 8), foreground="green").grid(row=3, column=0, columnspan=4,
                                                              sticky=tk.W, pady=(2, 0))

        # Convert and Stop buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

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
        self.progress.grid(row=6, column=0, columnspan=3,
                           sticky=(tk.W, tk.E), pady=5)

        # Status text
        self.status_text = tk.Text(
            main_frame, height=8, width=70, wrap=tk.WORD)
        self.status_text.grid(row=7, column=0, columnspan=2,
                              sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Progress percentage display
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=7, column=2, sticky=(
            tk.N, tk.S), padx=(10, 0), pady=10)

        ttk.Label(progress_frame, text="Progress:", font=(
            "Arial", 9, "bold")).pack(anchor=tk.W)
        self.progress_percent_label = ttk.Label(
            progress_frame, text="0%", font=("Arial", 12, "bold"))
        self.progress_percent_label.pack(anchor=tk.W, pady=(5, 10))

        ttk.Label(progress_frame, text="Time:", font=(
            "Arial", 9, "bold")).pack(anchor=tk.W)
        self.time_progress_label = ttk.Label(
            progress_frame, text="00:00 / 00:00", font=("Arial", 10))
        self.time_progress_label.pack(anchor=tk.W, pady=(5, 10))

        ttk.Label(progress_frame, text="Speed:", font=(
            "Arial", 9, "bold")).pack(anchor=tk.W)
        self.speed_label = ttk.Label(
            progress_frame, text="0x", font=("Arial", 10))
        self.speed_label.pack(anchor=tk.W, pady=(5, 0))

        # Configure row weight for text area
        main_frame.rowconfigure(7, weight=1)

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
                    selected_format = self.format_var.get()
                    output_path = input_path.with_suffix(f'.{selected_format}')
                    # If same extension, add _converted
                    if input_path.suffix.lower() == f'.{selected_format}':
                        output_path = input_path.with_stem(
                            input_path.stem + '_converted')
                    self.output_file.set(str(output_path))

                self.log_message(f"📁 เลือกไฟล์: {normalized_path}")

                # Important: Don't keep any file handles open
                # Just store the path, don't open or probe the file

            except Exception as e:
                self.log_message(f"⚠️ ข้อผิดพลาดในการเลือกไฟล์: {e}")
                messagebox.showerror("Error", f"ไม่สามารถเลือกไฟล์ได้: {e}")

    def browse_output_file(self):
        selected_format = self.format_var.get()
        filename = filedialog.asksaveasfilename(
            title="Save Output Video As",
            defaultextension=f".{selected_format}",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("MOV files", "*.mov"),
                ("M4V files", "*.m4v"),
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
                messagebox.showerror(
                    "Error", f"ไม่สามารถเลือกไฟล์เอาต์พุตได้: {e}")

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

    def parse_duration(self, duration_str):
        """Parse duration string (HH:MM:SS.ms) to seconds"""
        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return 0

    def format_time(self, seconds):
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def update_progress_display(self, current_time=None, speed=None):
        """Update the progress percentage and time display"""
        if current_time is not None:
            self.current_time = current_time
        if speed is not None:
            self.conversion_speed = speed

        # Calculate percentage
        if self.total_duration > 0:
            percentage = min(
                100, (self.current_time / self.total_duration) * 100)
            self.progress_percent_label.configure(text=f"{percentage:.1f}%")

            # Update progress bar to determinate mode
            self.progress.configure(
                mode='determinate', maximum=100, value=percentage)
        else:
            self.progress_percent_label.configure(text="0%")

        # Update time display
        current_formatted = self.format_time(self.current_time)
        total_formatted = self.format_time(self.total_duration)
        self.time_progress_label.configure(
            text=f"{current_formatted} / {total_formatted}")

        # Update speed display
        if self.conversion_speed > 0:
            self.speed_label.configure(text=f"{self.conversion_speed:.1f}x")
        else:
            self.speed_label.configure(text="0x")

    def parse_ffmpeg_progress(self, line):
        """Parse FFmpeg output line for progress information"""
        import re

        # Parse duration from initial output
        if "Duration:" in line:
            duration_match = re.search(
                r'Duration: (\d{2}:\d{2}:\d{2}\.\d{2})', line)
            if duration_match:
                self.total_duration = self.parse_duration(
                    duration_match.group(1))
                self.update_progress_display()

        # Parse current time and speed from progress lines
        elif "time=" in line and "speed=" in line:
            time_match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
            speed_match = re.search(r'speed=\s*(\d+\.?\d*)x', line)

            current_time = 0
            speed = 0

            if time_match:
                current_time = self.parse_duration(time_match.group(1))

            if speed_match:
                speed = float(speed_match.group(1))

            self.update_progress_display(current_time, speed)

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

    def convert_video(self, input_file, output_file, use_gpu=True, codec="h264", output_format="mp4"):
        """แปลงวิดีโอด้วย GPU (NVENC) ถ้ามี, ถ้าไม่มี fallback ไป CPU - iOS Compatible"""

        if use_gpu and self.check_nvenc():
            self.log_message(
                "✅ ใช้ GPU (NVENC) สำหรับการเข้ารหัส (iOS Compatible)")
            if codec == "h264":
                vcodec = "h264_nvenc"
            elif codec == "h265":
                vcodec = "hevc_nvenc"
            else:
                self.log_message(f"⚠️ ไม่รู้จัก codec: {codec}, ใช้ h264 แทน")
                vcodec = "h264_nvenc"
        else:
            self.log_message(
                "⚠️ ไม่พบ NVENC → ใช้ CPU (libx264) - iOS Compatible")
            vcodec = "libx264"

        # Build iOS compatible command - Maximum Compatibility
        # Special handling for different input formats
        base_command = [
            "ffmpeg",
            "-fflags", "+genpts+discardcorrupt",  # Handle corrupted/problematic streams
            "-i", input_file,
            "-c:v", vcodec,
        ]

        # Add codec-specific settings
        if "nvenc" in vcodec:
            # NVENC settings - more flexible
            video_settings = [
                "-preset", "p4",      # NVENC preset
                "-profile:v", "main",  # NVENC supports main better than baseline
                "-level:v", "4.0",    # Higher level for NVENC
                "-rc", "cbr",         # Constant bitrate for NVENC
                "-b:v", "3M",         # Bitrate for NVENC
                "-maxrate", "3M",
                "-bufsize", "6M",
            ]
        else:
            # CPU libx264 settings - maximum compatibility
            video_settings = [
                "-preset", "medium",  # CPU preset
                "-profile:v", "baseline",  # Maximum iOS compatibility
                "-level", "3.1",      # Lower level for older devices
                "-b:v", "2M",         # Lower bitrate for CPU
                "-maxrate", "2M",
                "-bufsize", "4M",
            ]

        # Common video settings
        common_video = [
            "-pix_fmt", "yuv420p",  # Required by all iOS devices
            "-g", "60",           # GOP length
            "-keyint_min", "30",  # Minimum keyframe interval
            "-sc_threshold", "0",  # Disable scene change detection
        ]

        # Audio settings
        audio_settings = [
            "-c:a", "aac",        # iOS native audio codec
            "-b:a", "128k",       # Conservative audio bitrate
            "-ar", "44100",       # iOS standard sample rate
            "-ac", "2",           # Stereo audio
        ]

        # Container and compatibility settings
        container_settings = [
            "-movflags", "+faststart",  # Simplified movflags for better compatibility
            "-f", output_format,  # Use selected output format
            "-avoid_negative_ts", "make_zero",  # Fix timestamp issues
            "-max_muxing_queue_size", "1024",   # Handle complex streams
            "-y",                 # Overwrite output file
            output_file
        ]

        # Combine all settings
        command = base_command + video_settings + \
            common_video + audio_settings + container_settings

        # Log input file info
        self.log_message(f"📂 ไฟล์ต้นฉบับ: {input_file}")
        self.log_message(f"📁 ไฟล์เอาต์พุต: {output_file}")
        self.log_message(
            f"🎬 Codec: {codec} ({vcodec}) | Format: {output_format}")
        if "nvenc" in vcodec:
            self.log_message("🚀 ใช้ GPU NVENC - Main Profile, Level 4.0")
        else:
            self.log_message("🚀 ใช้ CPU libx264 - Baseline Profile, Level 3.1")
        self.log_message("🔧 คำสั่ง FFmpeg: " + " ".join(command))

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
                    # Parse progress information
                    self.parse_ffmpeg_progress(line.strip())

                    # Log important messages and errors
                    if any(keyword in line.lower() for keyword in
                           ['error', 'warning', 'duration:', 'video:', 'audio:', 'stream', 'invalid', 'failed', 'not found']):
                        self.log_message(line.strip())

                # Check if process was terminated
                if self.current_process.poll() is not None:
                    break

            self.current_process.wait()

            if self.current_process.returncode == 0:
                self.log_message("🎉 แปลงไฟล์เสร็จแล้ว: " + output_file)
                return True
            else:
                self.log_message(
                    f"❌ การแปลงไฟล์ล้มเหลว (exit code: {self.current_process.returncode})")

                # If NVENC failed, suggest CPU fallback
                if "nvenc" in vcodec and use_gpu:
                    self.log_message(
                        "💡 NVENC อาจมีปัญหา - ลองปิด GPU Acceleration")
                    return False

                self.log_message("💡 คำแนะนำ:")
                self.log_message("   - ลองปิด GPU Acceleration")
                self.log_message("   - ลองเปลี่ยนจาก MOV เป็น MP4")
                self.log_message("   - ตรวจสอบว่าไฟล์ต้นฉบับไม่เสียหาย")
                self.log_message("   - ลองใช้ H.264 แทน H.265")
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
                messagebox.showerror(
                    "Error", f"ไฟล์ input ไม่พบ: {input_file}")
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
            messagebox.showerror(
                "Error", f"ไม่สามารถสร้างโฟลเดอร์เอาต์พุตได้: {e}")
            return

        # Check if ffmpeg is available
        if not shutil.which("ffmpeg"):
            messagebox.showerror(
                "Error", "ไม่พบ ffmpeg ในระบบ\nกรุณาติดตั้ง ffmpeg ก่อน")
            return

        # Clear status text and reset progress
        self.status_text.delete(1.0, tk.END)
        self.total_duration = 0
        self.current_time = 0
        self.conversion_speed = 0
        self.update_progress_display()

        # Disable convert button, enable stop button, and start progress
        self.convert_btn.configure(state="disabled", text="Converting...")
        self.stop_btn.configure(state="normal")
        self.progress.configure(mode='indeterminate')
        self.progress.start()

        # Start conversion in thread
        self.conversion_thread = threading.Thread(
            target=self.conversion_worker)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def conversion_worker(self):
        """Run conversion in separate thread"""
        try:
            success = self.convert_video(
                self.input_file.get(),
                self.output_file.get(),
                self.use_gpu_var.get(),
                self.codec_var.get(),
                self.format_var.get()
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
            # Show 100% completion
            self.progress_percent_label.configure(text="100%")
            self.progress.configure(mode='determinate', maximum=100, value=100)
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
                self.convert_btn.configure(
                    state="normal", text="Convert Video")
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
                        self.log_message(
                            f"🔫 ฆ่ากระบวนการ ffmpeg PID: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if killed_count > 0:
                self.log_message(
                    f"✅ ฆ่ากระบวนการ ffmpeg จำนวน {killed_count} กระบวนการ")
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
