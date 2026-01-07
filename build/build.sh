#!/bin/bash

OS="$1"
ARCH="$2"
VERSION_TAG="$3"
APP_NAME="ImIn"
CWD="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$(dirname "$CWD")/download_assets_dist"
OUTPUT_DIR="${DIST_DIR}/${APP_NAME}_${OS}_${ARCH}_installer"

# 出力ディレクトリの作成
mkdir -p "$OUTPUT_DIR"

# 作業ディレクトリの移動 (アプリケーションのソースコードがある場所)
cd "${CWD}/../app"

# アプリケーションのビルド
if [[ "$OS" == "macos" ]]; then
    # Nuitkaを使用して, macOSアプリケーションバンドルを作成
    nuitka --standalone \
           --follow-imports \
           --enable-plugin=tk-inter \
           --output-dir="${OUTPUT_DIR}" \
           --output-filename="${APP_NAME}" \
           --include-data-file=./LICENSE=./LICENSE \
           --include-data-file=./pyproject.toml=./pyproject.toml \
           --include-data-file=./settings.json=./settings.json \
           --include-data-file=./color.json=./color.json \
           --include-data-dir=./assets=./assets \
           --include-data-dir=./db/sql=./db/sql \
           --macos-app-name="${APP_NAME}" \
           --macos-app-icon=./assets/icons/app/icon.icns \
           --macos-target-arch="${ARCH}" \
           --macos-create-app-bundle \
           ./main.py \

    # アプリケーションバンドルの名前を変更
    mv "${OUTPUT_DIR}/main.app/" "${OUTPUT_DIR}/${APP_NAME}.app/"

    # 不必要なビルドファイルの削除
    rm -rf "${OUTPUT_DIR}/main.build/"
    rm -rf "${OUTPUT_DIR}/main.dist/"

    # DMGファイルの作成
    DMG_PATH="${DIST_DIR}/${APP_NAME}_${VERSION_TAG}_${OS}_${ARCH}_installer.dmg"
    create-dmg --volname "${APP_NAME} Installer" \
               --volicon "${OUTPUT_DIR}/${APP_NAME}.app/Contents/Resources/icon.icns" \
               --background "${CWD}/assets/dmg/background.png" \
               --window-size 1024 720 \
               --icon-size 120 \
               --icon "${APP_NAME}.app" 324 360 \
               --app-drop-link 700 360 \
               --hide-extension "${APP_NAME}.app" \
               --no-internet-enable \
               "${DMG_PATH}" \
               "${OUTPUT_DIR}" \

elif [[ "$OS" == "linux" ]]; then
    # TODO: Linux用のビルド
    echo "Linux用のビルドはまだ実装されていません。"

fi

# ビルド後のクリーンアップ
rm -rf "$OUTPUT_DIR"

cd "$CWD"