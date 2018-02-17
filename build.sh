#!/bin/bash

pyinstaller \
	--log-level=DEBUG \
	--name "Easy Bash PATH Editor" \
	--windowed \
	--noconfirm \
	--onefile \
  --osx-bundle-identifier "com.jonathansoma.ebpe" \
	-i icon/browser.icns \
	app/app.py

codesign -s "$CODESIGN_ID" "dist/Easy Bash PATH Editor.app"

cd dist && zip -r "../release/Easy Bash PATH Editor.zip" "Easy Bash PATH Editor.app"
