[app]
title = Pro Custom Art Tarot
package.name = propictarotapp
package.domain = org.example
version = 1.0
requirements = hostpython3, libffi, openssl, sdl2_image, sdl2_mixer, sdl2_ttf, sqlite3, python3, sdl2, setuptools, six, pyjnius, android, kivy, urllib3, idna, certifi, chardet, requests
source.dir = .
source.include_exts = py,png,kv,atlas
fullscreen = 0
icon.filename = images/AppIcons/playstore.png
orientation = portrait

[buildozer]
log_level = 2
android.skip_update = True
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.ndk = 25b
android.api = 33
android.minapi = 21
android.build_tools = 33.0.2
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.extract_native_libs = False
android.accept_sdk_license = True
android.orientation = portrait
p4a.branch = develop