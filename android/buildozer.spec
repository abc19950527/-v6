# Buildozer specs for 药品进销存管理系统 v6 Android App
[app]

# App name
title = 药品进销存
package.name = drugpos
package.domain = com.pharmacy

# Directory for source code
source.dir = .

# Main module
mainmodule = main

# App version
version = 1.0.0

# Requirements
requirements = python3,kivy,sqlite3,android,pyjnius,pygments,requests

# Android permissions
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA

# Screen settings
orientation = portrait
fullscreen = 0

# Window settings
android.window_soft_input_mode = adjust_resize

# Build settings
build_mode = debug
android.release_artifact = apk

[buildozer]

# Log level
log_level = 2

# Show warning
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# App requirements
requirements = hostpython3,kivy,sqlite3,android,pyjnius,pygments,requests

# 使用系统SDK
android.sdk_path = /usr/local/lib/android/sdk

# Android API level
android.api = 33

# NDK API
android.ndk_api = 21

# 跳过 NDK 下载
android.ndk_download = False

# 跳过 SDK 更新
android.update_sdk = False

# Private storage
android.private_storage = 1
