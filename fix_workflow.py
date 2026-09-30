#!/usr/bin/env python3
from pathlib import Path

BASE = Path(__file__).resolve().parent
wf_dir = BASE / ".github" / "workflows"
wf_dir.mkdir(parents=True, exist_ok=True)

WORKFLOW = '''name: Build AL-KHALLAQI APK

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version name'
        required: false
        default: '1.0.0'
  push:
    branches: [main]
    paths:
      - 'mobile/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Java 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Accept Android SDK licenses
        run: |
          yes | sdkmanager --licenses || true
          sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" || true
        env:
          ANDROID_HOME: /usr/local/lib/android/sdk

      - name: Setup Android env
        run: |
          echo "ANDROID_HOME=/usr/local/lib/android/sdk" >> $GITHUB_ENV
          echo "ANDROID_SDK_ROOT=/usr/local/lib/android/sdk" >> $GITHUB_ENV
          echo "/usr/local/lib/android/sdk/platform-tools" >> $GITHUB_PATH
          echo "/usr/local/lib/android/sdk/cmdline-tools/latest/bin" >> $GITHUB_PATH

      - name: Install Capacitor CLI
        working-directory: mobile
        run: |
          npm install
          npx cap add android || true

      - name: Prepare Android
        working-directory: mobile
        run: |
          npx cap sync android

      - name: Set version
        working-directory: mobile/android
        run: |
          VERSION="${{ github.event.inputs.version }}"
          VERSION="${VERSION:-1.0.0}"
          sed -i "s/versionName \\".*\\"/versionName \\"$VERSION\\"/" app/build.gradle || true
          echo "Building version $VERSION"

      - name: Build Debug APK
        working-directory: mobile/android
        run: |
          chmod +x gradlew
          ./gradlew assembleDebug --no-daemon --stacktrace

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: al-khallaqi-apk
          path: mobile/android/app/build/outputs/apk/debug/*.apk
          retention-days: 30

      - name: Create Release
        if: github.event_name == 'workflow_dispatch'
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ github.event.inputs.version }}
          name: AL-KHALLAQI v${{ github.event.inputs.version }}
          files: mobile/android/app/build/outputs/apk/debug/*.apk
          draft: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''

(wf_dir / "build-apk.yml").write_text(WORKFLOW, encoding="utf-8")
print("[+] .github/workflows/build-apk.yml (fixed)")
print()
print("التغيير الأساسي: استبدلت android-actions/setup-android")
print("بأوامر مباشرة (sdkmanager) تتجنب حزمة 'tools' المحذوفة.")
print()
print("ارفع الآن:")
print("  git add -A")
print("  git commit -m 'Fix APK workflow: remove deprecated tools package'")
print("  git push origin main")
