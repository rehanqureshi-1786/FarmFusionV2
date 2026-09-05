#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

APK_PATH="$REPO_ROOT/frontend/app/build/outputs/apk/debug/app-debug.apk"

if [ ! -f "$APK_PATH" ]; then
    echo "APK not found. Running Gradle assembleDebug..."
    ./gradlew assembleDebug
fi

echo "Checking for connected Android devices via ADB..."
DEVICE_COUNT=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l)

if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo "No device currently attached. Please plug in your phone or enable USB debugging."
    echo "Waiting for device..."
    adb wait-for-device
fi

DEVICE_ID=$(adb devices | grep -v "List of devices" | grep "device$" | head -n 1 | awk '{print $1}')
echo "Device connected: $DEVICE_ID"

echo "Installing debug APK: $APK_PATH..."
adb -s "$DEVICE_ID" install -r "$APK_PATH"

echo "Configuring ADB reverse proxy (port 8000 -> 8000)..."
adb -s "$DEVICE_ID" reverse tcp:8000 tcp:8000 || true

echo "Launching FarmFusion..."
adb -s "$DEVICE_ID" shell am start -n com.example.farmfusionapp/.MainActivity

echo "FarmFusion app is now running on device: $DEVICE_ID"
