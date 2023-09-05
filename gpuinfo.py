import GPUtil

def get_gpu_info():
  """Gets the GPU information."""
  gpus = GPUtil.getGPUs()
  gpu_info = []
  for gpu in gpus:
    gpu_info.append({
        "gpu_name": gpu.name,
        "memory_total": gpu.memoryTotal,
        "memory_used": gpu.memoryUsed,
        "temperature": gpu.temperature
    })
  return gpu_info

