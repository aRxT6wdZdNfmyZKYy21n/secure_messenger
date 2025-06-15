#!/bin/bash

pyside6-android-deploy \
    --wheel-pyside=/home/debian-12-client/Repositories/pyside-setup/dist/PySide6-6.8.3-6.8.3-cp311-cp311-android_aarch64.whl \
    --wheel-shiboken=/home/debian-12-client/Repositories/pyside-setup/dist/shiboken6-6.8.3-6.8.3-cp311-cp311-android_aarch64.whl \
    --name=secure_messenger \
    --ndk-path="$ANDROID_NDK_ROOT" \
    --sdk-path="$ANDROID_SDK_ROOT"
