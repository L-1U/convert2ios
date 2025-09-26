import subprocess
import shutil
import sys


def check_nvenc():
    """ตรวจสอบว่า ffmpeg รองรับ NVENC หรือไม่"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-encoders"],
            capture_output=True,
            text=True,
            check=True
        )
        encoders = result.stdout
        return ("h264_nvenc" in encoders) or ("hevc_nvenc" in encoders)
    except Exception as e:
        print("❌ ไม่สามารถตรวจสอบ ffmpeg ได้:", e)
        return False


def convert_video(input_file, output_file, use_gpu=True, codec="h264"):
    """แปลงวิดีโอด้วย GPU (NVENC) ถ้ามี, ถ้าไม่มี fallback ไป CPU"""

    if use_gpu and check_nvenc():
        print("✅ ใช้ GPU (NVENC) สำหรับการเข้ารหัส")
        if codec == "h264":
            vcodec = "h264_nvenc"
        elif codec == "h265":
            vcodec = "hevc_nvenc"
        else:
            print(f"⚠️ ไม่รู้จัก codec: {codec}, ใช้ h264 แทน")
            vcodec = "h264_nvenc"
    else:
        print("⚠️ ไม่พบ NVENC → ใช้ CPU (libx264)")
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
        output_file
    ]

    print("🚀 รันคำสั่ง:", " ".join(command))
    subprocess.run(command, check=True)
    print("🎉 แปลงไฟล์เสร็จแล้ว:", output_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "วิธีใช้: python convert.py <input_file> <output_file> [h264|h265]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    codec = sys.argv[3] if len(sys.argv) > 3 else "h264"

    convert_video(input_file, output_file, use_gpu=True, codec=codec)
