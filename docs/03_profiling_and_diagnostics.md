# 03 - Diagnoză, Profiling Hardware și Log-uri

## 1. Raportul Profiler-ului Hardware `simpleperf`

Test executat la data de 2026-11-13 pe procesul activ `com.rockstargames.gtavc.de` (PID 22935) în timpul rulării jocului 3D:

```text
Cmdline: /system/bin/simpleperf record -p 22935 --duration 2 -o /data/local/tmp/perf.data
Arch: arm64
Samples: 22472
Event count: 3083080763 cycles

Overhead  Shared Object       Symbol
4.26%     [kernel.kallsyms]   _raw_spin_unlock_irqrestore
3.70%     libUE4.so           Audio::FMixerSourceManager::ComputeSourceBuffersForIdRange
1.91%     libc.so             __memmove_aarch64_simd
1.62%     libUE4.so           FVulkanCommandListContext::SetShaderUniformBuffer
1.57%     libUE4.so           Audio::FMixerSourceManager::ReadSourceFrame
1.37%     libUE4.so           VulkanRHI::FVulkanSubresourceAllocator::TryAllocate2
1.31%     libUE4.so           libUE4.so[+498d104]
1.15%     libUE4.so           FSubmixEffectSubmixEQ::OnProcessAudio
0.99%     libUE4.so           ViceCity::CCollision::TestSphereTriangle
0.97%     libUE4.so           FGPUBaseSkinVertexFactory::FShaderDataType::UpdateBoneData
0.75%     libUE4.so           FVulkanDescriptorSetCache::FCachedPool::FindDescriptorSets
0.52%     libUE4.so           UpdateRefToLocalMatricesInner
```

### Concluzie Analiză:
Unreal Engine 4 utilizează în mod exclusiv subsistemul **Vulkan RHI** pe GPU-ul ARM Mali-G615 pentru trimiterea geometriei (`FVulkanCommandListContext`, `UpdateBoneData` pentru animația scheletică 3D a personajului).

---

## 2. Firele de Execuție (Threads) ale Jocului

Identificarea principalelor thread-uri active din proces:

| TID | Nume Thread | Rol Tehnic |
|---|---|---|
| 22935 | `rgames.gtavc.de` | Bucla principală Android UI / Looper |
| 22960 | `RenderThread` | Bucla de randare a framework-ului Android |
| 23035 | `GameThread` | Bucla logică Unreal Engine (fizică, scripturi, logică misiune) |
| 23066 | `RHIThread` | Bucla Hardware Interface Unreal Engine (trimite comenzile către Vulkan) |
| 23085 | `RenderThread` | Bucla de randare 3D a scenariului Unreal Engine |
| 23354 | `1.raster` | Thread-ul de rasterizare al motorului Flutter |
| 23365 | `IplrVkFenceWait` | Impeller Vulkan Fence Synchronization |
| 23366 | `IplrVkResMgr` | Impeller Vulkan Resource Manager |
| 23367 | `mali-compiler` | Compilatorul de shadere JIT din driverul Mali |

---

## 3. Log-urile Critice RenderDoc din Dispozitiv

Extrase din `/sdcard/Android/media/com.rockstargames.gtavc.de/files/RenderDoc/`:

```log
RDOC 022935: [18:10:36] core.cpp( 719) - Log - RenderDoc v1.47 Android 64-bit Release capturing application
RDOC 022935: [18:10:36] egl_hooks.cpp(1079) - Log - EGL_ANDROID_GLES_layers detected, disabling EGL hooks - GLES layering in effect
RDOC 022935: [18:10:36] gl_hooks.cpp( 280) - Log - Not registering OpenGL hooks for Android
RDOC 022935: [18:10:36] vk_layer.cpp( 110) - Log - Registering Vulkan hooks
RDOC 022935: [18:10:36] android_hook.cpp( 753) - Log - Dummy-loaded .../libVkLayer_GLES_RenderDoc.so with dlopen to prevent library unload
RDOC 022935: [18:10:36] android_hook.cpp( 765) - Log - No library hooks registered, not doing any hooking
```

### De ce apare `API: None` în RenderDoc GUI?
În codul sursă RenderDoc (`core.cpp`):
```cpp
IFrameCapturer *RenderDoc::GetActiveCapturer()
{
  for(IFrameCapturer *cap : m_Capturers)
  {
    if(cap->HasActiveWindow())
      return cap;
  }
  return NULL;
}
```
1. `VK_LAYER_RENDERDOC_Capture` a fost interceptat la pornire de instanța Vulkan din **Flutter** (folosită pentru UI-ul de pornire).
2. Flutter a încetat să mai prezinte frame-uri pe ecran în momentul în care activitatea Unreal Engine 4 a trecut în prim-plan (`com.epicgames.ue4.GameActivity`).
3. Instanța Vulkan din Unreal Engine fie folosește o a doua instanță `VkInstance` care nu a înregistrat swapchain-ul ca fereastră activă primară, fie randează pe un offscreen surface / sub-suprafață `BLASTBufferQueue` pe care RenderDoc nu a marcat-o automat ca `ActiveWindow`.
4. Deoarece `HasActiveWindow()` returnează fals pentru capturatori, RenderDoc raportează `API: None` și ține butoanele dezactivate.
