# 01 - Arhitectură și Mediu Tehnic

## 1. Dispozitivul Mobil

- **Model:** Motorola Moto G86 Power 5G (nume de cod intern `nice_g_sysenp`, ID ADB: `ZY32LZZJVS`)
- **Procesor / Chipset:** MediaTek Dimensity MT6878 (Octa-core 64-bit ARMv8.2-A)
- **Procesor Grafic (GPU):** ARM Mali-G615 MC2 (Driver Mali CSF v14.0 r44p0)
- **Versiune Android:** Android 16 (API Level 36 precursor / QPR Preview)
- **Nivel de Securitate / Kernel:** Linux Kernel 6.6.x aarch64
- **Permisiuni de Sistem:**
  - Magisk 27.0 Root activ (`su` funcțional la `uid=0`)
  - SELinux configurat în mod `Permissive` (`setenforce 0`)
  - Magisk module la `/data/adb/modules/renderdoc_root/system.prop` setat cu:
    ```properties
    ro.debuggable=1
    ro.force.debuggable=1
    service.adb.root=1
    ```

---

## 2. Aplicația Țintă: GTA Vice City Definitive Edition

- **Pachet Android:** `com.rockstargames.gtavc.de`
- **Activitate Principală:** `com.epicgames.ue4.GameActivity`
- **Arhitectură Dual-Engine:**
  1. **Launcher & Autentificare:** Folosește **Flutter** cu backend de randare **Impeller** pe **Vulkan** (`[android_context_vk_impeller.cc] Using the Impeller rendering backend (Vulkan)`).
  2. **Motor 3D de Joc:** **Unreal Engine 4** modificat de Grove Street Games / Rockstar Games.
     - Fișier binar nativ: `libUE4.so` (dimensiune ~120 MB).
     - RHI activ: **Vulkan RHI** (`FVulkanCommandListContext`, `VulkanRHI::FVulkanSubresourceAllocator`).
     - Caching Shadere: `/sdcard/Android/data/com.rockstargames.gtavc.de/files/VulkanProgramBinaryCache/VulkanPSO_*.b8a31030`.
     - Suprafață de randare: `BLASTBufferQueue` pe un `SurfaceView` nativ administrat de `SurfaceFlinger`.

---

## 3. Stația PC de Lucru

- **Sistem:** Windows 10/11 x64 cu GPU NVIDIA GeForce RTX 4060 Ti
- **RenderDoc:** v1.47 64-bit Portable (`C:\Users\S77\RenderDoc\RenderDoc_1.47_64`)
  - Binar GUI: `qrenderdoc.exe`
  - Binar CLI: `renderdoccmd.exe`
  - Binar Replay Core: `renderdoc.dll`
- **Software 3D:** Blender 4.3 (`C:\Program Files\Blender Foundation\Blender 4.3`)
- **Conectivitate ADB:** Porturi forwardate activ:
  - `tcp:38969 -> localabstract:renderdoc_39920` (Serverul de replay RenderDoc pe telefon)
  - `tcp:38960 -> localabstract:renderdoc_38920` (Socket-ul Target Control al jocului)
