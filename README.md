# Flet-Poke

## 実行コマンド

```
uv init . --lib

uv add 'flet[all]'
uv add requests

uv run src/main.py
```

## Android 環境構築

モバイルのときは、 watch_dog が使えないので、除外する必要がある。

```
brew install openjdk@17

echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc

sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk

brew install --cask android-commandlinetools

echo 'export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools' >> ~/.zshrc

echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools' >> ~/.zshrc

source ~/.zshrc

yes | sdkmanager --licenses

sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

source ~/.zshrc && uv run flet build apk --project "Pokemon Type Filter" --org "com.goda" --description "Pokemon type filter app built with Flet"


cd src
uv run flet build apk

adb install build/apk/app-arm64-v8a-release.apk

```

## Static Web

```
cd src && uv run flet build web --module-name main
```