# 药品进销存管理系统 v6 - Android APK

## 打包说明

本项目使用 Buildozer 进行 Android APK 打包。

### 环境要求

1. Python 3.8+
2. Java JDK 11
3. Android SDK
4. Android NDK

### 安装 Buildozer

```bash
pip install buildozer
```

### 打包步骤

1. **初始化项目**（如果还没有 buildozer.spec）
```bash
buildozer init
```

2. **编译 Debug APK**
```bash
buildozer debug
```

3. **编译 Release APK**
```bash
buildozer release
```

4. **安装到设备**
```bash
# Debug 版本
buildozer debug install

# Release 版本需要签名
```

### 输出文件

- Debug APK: `bin/drugpos-0.1-debug.apk`
- Release APK: `bin/drugpos-0.1-release-unsigned.apk`

### 签名 Release APK

```bash
# 创建密钥
keytool -genkey -v -keystore my-release-key.keystore -alias drugpos -keyalg RSA -keysize 2048 -validity 10000

# 签名
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/drugpos-0.1-release-unsigned.apk drugpos

# 验证签名
jarsigner -verify -verbose -certs bin/drugpos-0.1-release-unsigned.apk
```

### 常见问题

1. **编译失败**: 确保已安装所有依赖
2. **SDK/NDK 错误**: Buildozer 会自动下载，但可能需要代理
3. **权限问题**: 确保用户有写入权限

### 更多信息

请参考 Buildozer 官方文档: https://buildozer.readthedocs.io/
