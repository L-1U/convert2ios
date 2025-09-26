"""
Standalone script to kill all ffmpeg processes and release file locks
Run this if files remain locked after closing the GUI
"""
import subprocess
import sys

def kill_ffmpeg_processes():
    """Kill all ffmpeg processes using Windows taskkill"""
    try:
        print("🔍 ค้นหากระบวนการ ffmpeg...")
        
        # Try to list ffmpeg processes first
        result = subprocess.run(
            ["tasklist", "/fi", "imagename eq ffmpeg.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if "ffmpeg.exe" in result.stdout:
            print("📋 พบกระบวนการ ffmpeg:")
            print(result.stdout)
            
            # Kill all ffmpeg processes
            kill_result = subprocess.run(
                ["taskkill", "/f", "/im", "ffmpeg.exe"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if kill_result.returncode == 0:
                print("✅ ฆ่ากระบวนการ ffmpeg สำเร็จ")
                print(kill_result.stdout)
            else:
                print("⚠️ ไม่สามารถฆ่ากระบวนการ ffmpeg ได้")
                print(kill_result.stderr)
        else:
            print("ℹ️ ไม่พบกระบวนการ ffmpeg ที่ทำงานอยู่")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def kill_with_psutil():
    """Kill ffmpeg processes using psutil (more reliable)"""
    try:
        import psutil
        killed_count = 0
        
        print("🔍 ค้นหากระบวนการ ffmpeg ด้วย psutil...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'ffmpeg' in proc.info['name'].lower():
                    print(f"🎯 พบ ffmpeg PID: {proc.info['pid']}")
                    if proc.info['cmdline']:
                        print(f"   คำสั่ง: {' '.join(proc.info['cmdline'][:3])}...")
                    
                    proc.kill()
                    killed_count += 1
                    print(f"🔫 ฆ่ากระบวนการ PID: {proc.info['pid']}")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            print(f"✅ ฆ่ากระบวนการ ffmpeg จำนวน {killed_count} กระบวนการ")
        else:
            print("ℹ️ ไม่พบกระบวนการ ffmpeg ที่ทำงานอยู่")
            
    except ImportError:
        print("⚠️ ไม่พบ psutil, ใช้ taskkill แทน")
        kill_ffmpeg_processes()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน psutil: {e}")
        print("🔄 ลองใช้ taskkill แทน...")
        kill_ffmpeg_processes()

def main():
    print("🚀 FFmpeg Process Killer")
    print("=" * 40)
    print("สคริปต์นี้จะฆ่ากระบวนการ ffmpeg ทั้งหมดเพื่อปลดล็อกไฟล์")
    print("=" * 40)
    
    # Try psutil first (more reliable), fallback to taskkill
    kill_with_psutil()
    
    print("\n🔓 การปลดล็อกไฟล์เสร็จสิ้น")
    print("💡 ตอนนี้คุณสามารถเปลี่ยนชื่อไฟล์ได้แล้ว")
    
    input("\nกด Enter เพื่อปิด...")

if __name__ == "__main__":
    main()
