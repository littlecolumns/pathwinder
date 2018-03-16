#!/bin/bash

pyinstaller \
	--log-level=DEBUG \
	--name "Pathwinder" \
	--windowed \
	--noconfirm \
	--onefile \
  --osx-bundle-identifier "com.littlecolumns.pathwinder" \
	-i icon/browser.icns \
	app/app.py

codesign -s "$CODESIGN_ID" "dist/Pathwinder.app"

cd dist && zip -r "../release/Pathwinder.zip" "Pathwinder.app"
