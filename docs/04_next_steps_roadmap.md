# 04 - Ce Urmează să Încercăm (Roadmap & Soluții Imediate)

Având în vedere că Vulkan RHI rulează activ în joc și RenderDoc este conectat la socket-ul de control al procesului, iată opțiunile tehnice ce urmează să fie abordate pentru a declanșa captura salvată a fișierului `.rdc`:

---

## 🚀 Opțiunea 1: Forțarea Schimbării Ferestrei Active prin Protocolul TargetControl (`CycleActiveWindow`)

### Cauza:
În GTA Vice City DE există două suprafețe de randare:
1. Suprafața Flutter (Impeller Vulkan) - inactivă după încărcare.
2. Suprafața Unreal Engine (Vulkan RHI) - activă în jocul 3D.

### Soluția:
Chiar dacă butonul `Cycle Active Window` este gri în GUI când `API: None`, protocolul de rețea `ITargetControl` expune funcția:
```cpp
virtual void CycleActiveWindow() = 0;
virtual void TriggerCapture(uint32_t numFrames) = 0;
```
Trimiterea pachetului de rețea `CycleActiveWindow` direct prin socket-ul conectat la `127.0.0.1:38960` va forța RenderDoc să treacă de la swapchain-ul inactiv al Flutter la swapchain-ul activ al Unreal Engine, activând imediat `API: Vulkan`.

---

## 🚀 Opțiunea 2: Declanșarea Capturii Direct din Linia de Comandă (`renderdoccmd` / Script Python)

În loc să depindem de starea vizuală din GUI-ul Qt (`qrenderdoc.exe`), putem trimite comanda de captură la nivel de API direct către socket-ul `@renderdoc_38920`:
1. Prin apelul nativ `RENDERDOC_CreateTargetControl` cu structura `rdcstr` corect inițializată în memorie (evitând interpretarea greșită a string-urilor C standard).
2. Prin trimiterea directă pe socket a pachetului binar RenderDoc `TargetControlMessageType::CaptureNextFrame`.

---

## 🚀 Opțiunea 3: Setarea Parametrilor de Captură Automată prin `renderdoc.conf`

Putem configura fișierul de configurare RenderDoc al aplicației (`/sdcard/Android/media/com.rockstargames.gtavc.de/files/renderdoc.conf`):
- `queueCapture = 100` (captură automată programată la frame-ul 100 sau imediat ce swapchain-ul este apelat).
- `captureAllCmdLists = true` (înregistrarea tuturor buffer-elor de comenzi, chiar dacă nu sunt prezentate pe ecranul principal).
- `refAllResources = true` (capturarea tuturor texturilor și mesh-urilor din memorie).
- `captureCallstacks = true`.

Cu această opțiune, RenderDoc salvează automat fișierul `.rdc` pe stocarea telefonului (`/sdcard/Android/media/com.rockstargames.gtavc.de/files/RenderDoc/`) fără să fie necesară apăsarea manuală a butonului din interfață.

---

## 🚀 Opțiunea 4: Forțarea Pornirii Directe a Activității UE4 Fără Launcher-ul Flutter

În mod normal, aplicația pornește prin Flutter (`FlutterScreenHost`), care inițializează primul context Vulkan.
Dacă trimitem un intent explicit către `GameActivity` cu parametri care ocolesc launcher-ul de autentificare:
```bash
adb shell am start -n com.rockstargames.gtavc.de/com.epicgames.ue4.GameActivity --es "args" "-vulkan -game"
```
Unreal Engine va fi singurul motor care inițializează Vulkan, eliminând instanța concurentă a Flutter Impeller și făcând ca swapchain-ul 3D să fie cel primar încă din primul moment.

---

## 🚀 Opțiunea 5: Importul Geometriei 3D în Blender 4.3

Imediat ce este obținut fișierul de captură `.rdc`:
1. Copierea fișierului pe PC:
   ```bash
   adb pull /sdcard/Android/media/com.rockstargames.gtavc.de/files/RenderDoc/*.rdc c:\Users\S77\Desktop\BuildApps\3Cap\captures\
   ```
2. Deschiderea capturii în RenderDoc Desktop -> `Event Browser` -> Selectarea drawcall-urilor `vkCmdDrawIndexed` ale personajelor / clădirilor.
3. Exportul vertex buffer-ului în format `.OBJ` prin `Mesh Viewer -> Right Click -> Export to .OBJ`.
4. Sau utilizarea addon-ului **MapsModelsImporter** direct în Blender 4.3 pentru importul complet al scenei cu texturi și coordonate UV intacte.
