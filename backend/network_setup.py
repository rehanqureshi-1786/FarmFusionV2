"""
Network Setup Helper for FarmFusion

This script helps diagnose and configure network settings for connecting
Android app to the backend server via mobile hotspot.

Usage:
    python network_setup.py
"""
import socket
import subprocess
import platform
import os


def get_ip_addresses():
    """Get all local IP addresses"""
    ips = []
    try:
        # Get hostname
        hostname = socket.gethostname()

        # Get all IP addresses
        try:
            # Windows
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            output = result.stdout

            for line in output.split('\n'):
                if 'IPv4' in line and ':' in line:
                    ip = line.split(':')[-1].strip()
                    if ip and ip not in ips:
                        ips.append(ip)
        except:
            pass

        # Fallback - try to get IP from socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip not in ips:
                ips.append(ip)
            s.close()
        except:
            pass

    except Exception as e:
        print(f"Error getting IPs: {e}")

    return ips


def find_hotspot_ip(ips):
    """Find the hotspot IP (usually 192.168.137.x)"""
    for ip in ips:
        if ip.startswith('192.168.137.'):
            return ip
    return None


def update_android_config(ip_address):
    """Update the Android Constants.kt file with the correct IP"""
    constants_path = os.path.join(
        '..', 'frontend', 'app', 'src', 'main', 'java',
        'com', 'example', 'farmfusionapp', 'utils', 'Constants.kt'
    )

    # Also try absolute path
    if not os.path.exists(constants_path):
        constants_path = r'C:\Users\pf4es\Downloads\FarmFusion\frontend\app\src\main\java\com\example\farmfusionapp\utils\Constants.kt'

    if not os.path.exists(constants_path):
        print(f"[X] Could not find Constants.kt file")
        return False

    try:
        with open(constants_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the IP address
        import re
        new_content = re.sub(
            r'const val FARMFUSION_BASE_URL = "http://[^/]+:\d+/"',
            f'const val FARMFUSION_BASE_URL = "http://{ip_address}:8000/"',
            content
        )

        if new_content != content:
            with open(constants_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[OK] Updated Constants.kt with IP: {ip_address}")
            return True
        else:
            print(f"[i] Constants.kt already has correct IP")
            return True

    except Exception as e:
        print(f"[X] Error updating Constants.kt: {e}")
        return False


def check_server_running():
    """Check if the server is running on port 8000"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        return result == 0
    except:
        return False


def main():
    print("=" * 70)
    print("  FarmFusion Network Setup Helper")
    print("=" * 70)
    print()

    # Get IP addresses
    print("Detected IP addresses:")
    ips = get_ip_addresses()
    for ip in ips:
        print(f"   - {ip}")

    if not ips:
        print("   [X] No IP addresses found")
        return

    # Find hotspot IP
    hotspot_ip = find_hotspot_ip(ips)

    if hotspot_ip:
        print()
        print(f"[+] Hotspot IP detected: {hotspot_ip}")
        print()

        # Update Android config
        if update_android_config(hotspot_ip):
            print()
            print("[OK] Android configuration updated!")
        else:
            print()
            print("[!] Could not automatically update Android config.")
            print(f"   Please manually update Constants.kt with: http://{hotspot_ip}:8000/")
    else:
        print()
        print("[!] No hotspot IP (192.168.137.x) detected.")
        print("   Make sure your mobile hotspot is enabled.")
        print()

        # Use first available IP
        if ips:
            update_android_config(ips[0])

    # Check server status
    print()
    print("Checking server status:")
    if check_server_running():
        print("   [OK] Server is running on port 8000")
    else:
        print("   [X] Server is NOT running")
        print()
        print("   To start the server, run:")
        print("      python main.py")
        print()
        print("   Make sure to restart Android Studio after starting the server!")

    print()
    print("=" * 70)
    print("  Troubleshooting Tips:")
    print("=" * 70)
    print("""
1. Make sure your PC hotspot is ON:
   - Windows: Settings > Network & Internet > Mobile hotspot
   - Connect your phone to this hotspot

2. Windows Firewall:
   - Allow Python through Windows Firewall
   - Allow port 8000

3. After making changes:
   - Restart the backend server (Ctrl+C, then python main.py)
   - Clean build in Android Studio (Build > Clean Project)
   - Rebuild and run the Android app

4. Test connection:
   - From your phone's browser, visit: http://[PC_IP]:8000/
   - You should see "Welcome to FarmFusion API!"
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()
