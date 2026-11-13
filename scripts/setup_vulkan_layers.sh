#!/system/bin/sh
# Setup global Vulkan layers for RenderDoc on rooted Android
echo "[*] Setting up Vulkan debug directory..."
mkdir -p /data/local/debug/vulkan

APP_PKG="com.rockstargames.gtavc.de"
APP_LIB_DIR=$(ls -d /data/app/~~*/${APP_PKG}-*/lib/arm64 2>/dev/null | head -n 1)

if [ -n "$APP_LIB_DIR" ] && [ -f "$APP_LIB_DIR/libVkLayer_GLES_RenderDoc.so" ]; then
    echo "[+] Found RenderDoc layer in $APP_LIB_DIR"
    cp "$APP_LIB_DIR/libVkLayer_GLES_RenderDoc.so" /data/local/debug/vulkan/
    cp "$APP_LIB_DIR/VkLayer_RENDERDOC_Capture.json" /data/local/debug/vulkan/
    ln -sf /data/local/debug/vulkan/libVkLayer_GLES_RenderDoc.so /data/local/debug/vulkan/libVK_LAYER_RENDERDOC_Capture.so
    ln -sf /data/local/debug/vulkan/libVkLayer_GLES_RenderDoc.so /data/local/debug/vulkan/VK_LAYER_RENDERDOC_Capture.so
    chmod -R 777 /data/local/debug
    chcon -R u:object_r:system_file:s0 /data/local/debug/vulkan/*
    echo "[+] Layer files deployed successfully."
else
    echo "[-] RenderDoc library not found in app directory."
fi

echo "[*] Configuring system properties and global settings..."
resetprop -d debug.vulkan.layer.0
resetprop -d debug.vulkan.layer.1
resetprop debug.vulkan.layers VK_LAYER_RENDERDOC_Capture

settings put global enable_gpu_debug_layers 1
settings put global gpu_debug_app "$APP_PKG"
settings put global gpu_debug_layers VK_LAYER_RENDERDOC_Capture
settings put global gpu_debug_layer_app "$APP_PKG"
settings put global gpu_debug_layers_gles libVkLayer_GLES_RenderDoc.so

echo "[+] Vulkan debug configuration complete."
