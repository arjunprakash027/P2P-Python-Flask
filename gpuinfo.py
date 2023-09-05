import GPUtil

def get_gpu_info():
  """Gets the GPU information."""
  gpus = GPUtil.getGPUs()
  gpu_info = []
  if gpus:
    for gpu in gpus:
      gpu_info.append({
          "gpu_name": gpu.name,
          "memory_total": gpu.memoryTotal,
          "memory_used": gpu.memoryUsed,
          "temperature": gpu.temperature
      })
  else:

    gpu_info.append({
          "gpu_name": "No GPU",
          "memory_total": 0,
          "memory_used": 0,
          "temperature": 0
      })
    
  return gpu_info

if __name__ == "__main__":
  print("GPU Info:")
  print(get_gpu_info())

