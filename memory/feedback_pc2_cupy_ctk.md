---
name: feedback_pc2_cupy_ctk
description: "PC2 GA-GPU падал на старте eaSimple — cupy без CTK-хедеров; fix pip install cupy-cuda12x[ctk]"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d9ff9919-79aa-4ffe-9d6e-8c2ebfb813d9
---

PC2 (`borys@100.73.22.1`, `C:/Users/borys/ga_gpu`) для параллельных GA-прогонов: `cupy-cuda12x` видел RTX 3090, но GA жёстко крэшил без stderr ровно на `[ga] ... starting eaSimple` — первая компиляция CUDA-ядра падала `RuntimeError: Failed to find CUDA headers` (на PC1 toolkit стоит системно, на PC2 не было).

**Why:** cupy nvrtc нужны CUDA-заголовки; без них любой RawKernel/ufunc не компилится.
**How to apply:** на PC2 (и любой новой GPU-машине без системного CUDA toolkit) — `venv\Scripts\python.exe -m pip install "cupy-cuda12x[ctk]==<версия>"` (тянет nvidia-cuda-* wheels с хедерами). После этого E на PC2 проходит end-to-end: launch → прогресс-бар gen→29 → результат стянут поллером (`--host/--user/--dir`) в `data/ga_results_<tid>.json`. См. [[project_ga_regime_feature]], [[project_trader_model_10]].
