# 02 - Toate Variantele Încercate și Rezultate (Post-Mortem)

În cadrul efortului de a realiza captura 3D a geometriei cu RenderDoc pe Motorola Moto G86 Power 5G, au fost testate metodic 10 variante și abordări tehnice distincte:

---

### Varianta 1: Lansarea Standard din RenderDoc GUI (PC)
- **Metoda:** Deschiderea `Launch Application` din RenderDoc GUI pe PC cu `com.rockstargames.gtavc.de/com.epicgames.ue4.GameActivity` și apăsarea butonului `Launch`.
- **Eroare 1:** RenderDoc a afișat dialogul *"Application is not debuggable"*.
- **Eroare 2:** La fiecare apăsare pe `Launch`, RenderDoc GUI executa automat comenzi ADB care ștergeau setările globale ale straturilor grafice (`settings delete global enable_gpu_debug_layers`).
- **Rezultat:** Eșec.

---

### Varianta 2: Interceptarea și Falsificarea Flags cu `dumpsys_wrapper`
- **Metoda:** RenderDoc verifică dacă pachetul este debuggable executând `dumpsys package com.rockstargames.gtavc.de` și căutând textul `DEBUGGABLE` în `pkgFlags`. Am creat un wrapper script la `/data/local/tmp/dumpsys_wrapper` și l-am montat bind peste `/system/bin/dumpsys`.
- **Rezultat:** **Succes parțial.** RenderDoc a crezut că jocul este debuggable și a trecut de verificare fără avertismente.

---

### Varianta 3: Injecție prin scriptul `wrap.sh` în APK
- **Metoda:** Crearea scriptului standard Android `wrap.sh` în `/data/app/.../lib/arm64/wrap.sh` pentru a pre-încărca biblioteca `libVkLayer_GLES_RenderDoc.so` cu `LD_PRELOAD`.
- **Eroare Critică:** Pe firmware-ul Motorola Android 16 (`nice_g_sysenp`), prezența `wrap.sh` forțează sistemul să pornească prin `WrapperInit.main`. Acest proces inițializează serviciul Motorola `MotoCarrierConfigManager` -> `AssetManager` -> `createIdmap` -> `setgid(144)`.
- Filtrele SECCOMP ale kernelului Android 16 au interceptat apelul de sistem `setgid` și au trimis `signal 31 (SIGSYS)` la zygote, generând crash instantaneu (`tombstone_03`).
- **Rezultat:** Abandonat. `wrap.sh` a fost șters complet pentru a elimina crash-ul SECCOMP.

---

### Varianta 4: Deplasarea bibliotecilor RenderDoc în directorul privat al jocului
- **Metoda:** Copierea `libVkLayer_GLES_RenderDoc.so`, `libVK_LAYER_RENDERDOC_Capture.so`, `VK_LAYER_RENDERDOC_Capture.so` și `VkLayer_RENDERDOC_Capture.json` în `/data/app/.../com.rockstargames.gtavc.de.../lib/arm64/`.
- **Rezultat:** **Succes.** Loader-ul Vulkan al sistemului a putut găsi stratul în logcat:
  `added global layer 'VK_LAYER_RENDERDOC_Capture' from library '.../libVkLayer_GLES_RenderDoc.so'`.

---

### Varianta 5: Activarea straturilor globale de GPU Debug prin `settings global`
- **Metoda:**
  ```bash
  settings put global enable_gpu_debug_layers 1
  settings put global gpu_debug_app com.rockstargames.gtavc.de
  settings put global gpu_debug_layers VK_LAYER_RENDERDOC_Capture
  settings put global gpu_debug_layer_app com.rockstargames.gtavc.de
  settings put global gpu_debug_layers_gles libVkLayer_GLES_RenderDoc.so
  ```
- **Observație:** Când `gpu_debug_layer_app` a fost setat din greșeală pe `org.renderdoc.renderdoccmd.arm64`, Unreal Engine a returnat *"No Vulkan driver found"*. După corectarea pe pachetul jocului, driverul Vulkan a pornit normal.

---

### Varianta 6: Crearea Căii Globale de Sistem `/data/local/debug/vulkan/`
- **Metoda:** Analiza binarului `/system/lib64/libvulkan.so` a demonstrat că Android are hardcodată calea `/data/local/debug/vulkan` pentru descoperirea straturilor de depanare la nivel de sistem. Am creat acest director pe root (`chmod 777`) și am copiat fișierele stratului și fișierul `.json`.
- **Rezultat:** **Succes.** Stratul devine accesibil global fără a depinde exclusiv de structura din `base.apk`.

---

### Varianta 7: Setarea Proprietăților de Sistem Vulkan (`debug.vulkan.layers`)
- **Metoda:**
  ```bash
  setprop debug.vulkan.layers VK_LAYER_RENDERDOC_Capture
  ```
- **Problemă Identificată & Rezolvată:** La un moment dat au fost setate simultan `debug.vulkan.layer.0`, `debug.vulkan.layer.1` și `debug.vulkan.layers`. Logcat a arătat:
  `Loaded layer VK_LAYER_RENDERDOC_Capture` de 3 ori consecutiv, cauzând un deadlock/ANR.
- **Fix:** Am folosit `resetprop -d` din Magisk pentru a elimina duplicatele și am lăsat o singură înregistrare curată.

---

### Varianta 8: Conectarea RenderDoc GUI prin "Attach to Running Instance"
- **Metoda:** Pentru a evita ca RenderDoc GUI să șteargă setările Vulkan la apăsarea butonului `Launch`, am folosit `File -> Attach to Running Instance` (Remote Host Manager).
- **Constatare:** Am realizat că în capturile anterioare de ecran, GUI-ul era conectat la PID-uri vechi/închise (27400, 29399, 31320, 9134).
- Prin automatizare am selectat procesul viu activ (`com.rockstargames.gtavc.de [PID 22935]`).
- **Rezultat:** Statusul s-a schimbat în `Connection Status: Established`, dar `API` a rămas `None`.

---

### Varianta 9: Depășirea Blocajelor de Interfață și Standby (Lockscreen & Skip Sign-In)
- **Metoda:** Prin capturi video/screencap trimise de pe telefon, am constatat că:
  1. Telefonul intra în sleep / lockscreen (ecranul devenea negru din punct de vedere hardware, `mState=1`).
  2. Jocul se oprea în ecranul 2D Flutter de autentificare Rockstar Games Social Club ("Sign in / Skip Sign in").
  3. Am automatizat trimiterea evenimentelor de deblocare (`input swipe`), menținerea ecranului pornit (`svc power stayon true`) și apăsarea butonului "Skip Sign In", apoi "RESUME GAME".
- **Rezultat:** **Succes deplin.** Jocul a intrat în randarea 3D a lumii de joc cu Tommy Vercetti pe ecran.

---

### Varianta 10: Profiling Hardware de Nivel Jos prin `simpleperf`
- **Metoda:** Rularea unui sampling de 2 secunde direct pe CPU/GPU cu `simpleperf record -p 22935`.
- **Rezultat:** **Confirmare absolută că Vulkan este activ în motorul Unreal:**
  - `FVulkanCommandListContext::SetShaderUniformBuffer` (1.62% CPU)
  - `VulkanRHI::FVulkanSubresourceAllocator::TryAllocate2` (1.37% CPU)
  - `FVulkanDescriptorSetCache::FCachedPool::FindDescriptorSets` (0.75% CPU)
  - `UpdateBoneData` și schelet 3D activ.
