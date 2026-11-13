# 3Cap - Android 3D Model Capture Pipeline

Pipeline de extragere și captură a modelelor 3D din jocuri Android (Unreal Engine / Vulkan / OpenGL ES) pe PC prin **RenderDoc**, **ADB** și instrumente de profiling hardware.

---

## 📌 Context și Specificații Hardware / Software

- **Dispozitiv Țintă:** Motorola Moto G86 Power 5G (`ZY32LZZJVS`)
- **Sistem de Operare:** Android 16 (Build `nice_g_sysenp`, Linux Kernel 6.6)
- **SoC / GPU:** MediaTek Dimensity MT6878 cu ARM Mali-G615 MC2
- **Nivel Acces Dispozitiv:** Root complet via Magisk 27.0 (`uid=0`), `SELinux: Permissive`, `ro.debuggable=1`
- **Aplicație Țintă:** *Grand Theft Auto: Vice City – The Definitive Edition* (`com.rockstargames.gtavc.de`)
- **Motor Joc:** Dual-engine — Launcher Flutter (`Impeller` Vulkan backend) + Motor 3D Unreal Engine 4 (`GameActivity` pe `BLASTBufferQueue` SurfaceView)
- **Stație de Lucru PC:** Windows 10/11 x64, RenderDoc v1.47 (64-bit portable la `C:\Users\S77\RenderDoc\RenderDoc_1.47_64`), Blender 4.3 (`C:\Program Files\Blender Foundation\Blender 4.3`)

---

## 📋 Cuprins Documentație Detaliată

1. [Arhitectură și Mediu Tehnic](docs/01_architecture_and_environment.md)
2. [Toate Variantele Încercate și Rezultate (Post-Mortem)](docs/02_methods_attempted.md)
3. [Diagnoză, Profiling Hardware și Log-uri](docs/03_profiling_and_diagnostics.md)
4. [Ce Urmează să Încercăm (Roadmap & Soluții Imediate)](docs/04_next_steps_roadmap.md)

---

## 🔬 Rezumat Executiv al Stadiului Actual

### Ce funcționează complet:
1. **Rooting & Modul Magisk**: Dispozitivul rulează cu `ro.debuggable=1`, `ro.force.debuggable=1` și `service.adb.root=1` la nivel de Zygote.
2. **Integrare RenderDoc Android**: Pachetul `org.renderdoc.renderdoccmd.arm64` este instalat și rulează ca server de replay pe portul `39920`.
3. **Injecție Strat Vulkan**: Stratul `VK_LAYER_RENDERDOC_Capture` este instalat în `/data/local/debug/vulkan/` și este detectat și încărcat nativ de către loader-ul Vulkan (`libvulkan.so`) din Android.
4. **Target Control Socket**: Socket-ul de control `@renderdoc_38920` din interiorul procesului `com.rockstargames.gtavc.de` este activ și acceptă conexiunea RenderDoc GUI de pe PC (`Connection Status: Established`).
5. **Jocul este în Gameplay 3D**: Tommy Vercetti este randat în timp real în lumea 3D pe telefon, iar profiling-ul `simpleperf` a confirmat apeluri masive către `FVulkanCommandListContext`, `VulkanRHI::FVulkanSubresourceAllocator` și `FVulkanDescriptorSetCache` în `libUE4.so`.

### Blocajul Curent (`API: None`):
În interfața RenderDoc de pe PC, deși conexiunea este stabilită cu procesul activ al jocului, câmpul `API` rămâne pe `None`, iar butonul `Capture Frame(s) Immediately` este dezactivat.
Acest lucru este cauzat de faptul că motorul Unreal Engine 4 folosește o suprafață nativă `ANativeWindow` compusă prin `SurfaceFlinger` / `BLASTBufferQueue` în loc de o prezentare standard pe swapchain-ul principal capturat de instanța internă inițială creată de Flutter Impeller.

---

## 🛠️ Scripturi Utilitare Incluse

- [`scripts/setup_vulkan_layers.sh`](scripts/setup_vulkan_layers.sh): Configurare completă pe Android a straturilor Vulkan globale și a proprietăților de sistem.
- [`scripts/dumpsys_wrapper.sh`](scripts/dumpsys_wrapper.sh): Interceptor `dumpsys` pentru păcălirea flag-urilor `DEBUGGABLE` cerute de GUI-ul RenderDoc.
- [`scripts/rdoc_gui_controller.py`](scripts/rdoc_gui_controller.py): Automatizare Python pentru interfața RenderDoc pe desktop și atașare la țintă.
- [`scripts/profile_game_rhi.py`](scripts/profile_game_rhi.py): Profiler direct prin `simpleperf` pentru verificarea activității Vulkan/UE4 pe telefon.
