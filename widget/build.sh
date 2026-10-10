#!/bin/bash
# Builds widget/build/Mori.app (needs Xcode command line tools for swiftc).
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
APP=build/Mori.app

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
swiftc -O -swift-version 5 Pet.swift -o "$APP/Contents/MacOS/Mori" -framework Cocoa -framework WebKit
cp pet.html "$APP/Contents/Resources/"
cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Mori</string>
  <key>CFBundleIdentifier</key><string>so.monogamy.mori</string>
  <key>CFBundleExecutable</key><string>Mori</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSUIElement</key><true/>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>VowPath</key><string>$ROOT/bin/vow</string>
</dict>
</plist>
EOF
codesign --force --sign - "$APP" >/dev/null 2>&1 || true
echo "built $APP"
