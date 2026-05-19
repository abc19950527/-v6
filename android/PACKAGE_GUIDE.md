# 药品进销存管理系统v6 - Android打包指南

## 环境要求

### 方法一：Windows + WSL（推荐）

1. 安装WSL2
```powershell
wsl --install -d Ubuntu-22.04
```

2. 在WSL中安装依赖
```bash
# 安装Python和编译工具
sudo apt update
sudo apt install -y python3 python3-pip python3-dev build-essential git zip openjdk-11-jdk

# 安装Android SDK
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
mv cmdline-tools latest

# 设置环境变量
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# 接受协议
yes | sdkmanager --licenses

# 安装必要的SDK组件
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
```

3. 安装Buildozer
```bash
pip3 install buildozer

# 安装Python-for-Android
pip3 install python-for-android
```

4. 打包应用
```bash
cd /mnt/d/药品进销存管理系统v6/android
buildozer android debug
# 或Release版本
buildozer android release
```

### 方法二：使用GitHub Actions（无需本地配置）

1. 创建GitHub仓库，上传代码
2. 创建 `.github/workflows/android.yml`:
```yaml
name: Build Android APK

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          pip install buildozer
          pip install kivy
          
      - name: Build APK
        run: buildozer android debug
```

3. 从Actions下载APK

### 方法三：Docker容器

```bash
# 使用Kivy官方的Docker镜像
docker run -v $(pwd):/home/user/project kivy/buildozer bash -c "
    cd /home/user/project/android
    buildozer android debug
"
```

## Windows本地打包（备用方案）

如果需要在Windows本地打包，可以使用PyInstaller生成可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 输出文件

打包成功后，APK文件位于：
- Debug版本: `android/bin/drugpos-0.1-debug.apk`
- Release版本: `android/bin/drugpos-0.1-release-unsigned.apk`

## 安装APK

1. 启用手机开发者选项中的"USB调试"
2. 使用adb安装：
```bash
adb install android/bin/drugpos-0.1-debug.apk
```

3. 或直接将APK文件传到手机，通过文件管理器安装

## 签名Release版本

```bash
# 生成密钥
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

# 签名APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore my-app.apk my-key-alias

# 对齐APK
zipalign -v 4 my-app.apk my-app-aligned.apk
```

## 常见问题

1. **Buildozer下载依赖超时**: 可以配置镜像源或使用代理
2. **SDK组件安装失败**: 确保网络通畅，尝试多次安装
3. **编译内存不足**: 建议至少8GB内存
4. **API级别不兼容**: 在buildozer.spec中调整android.api值
