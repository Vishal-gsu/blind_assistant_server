import torch
import time

# Check if CUDA is available
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using GPU: {torch.cuda.get_device_name(device)}")
else:
    device = torch.device("cpu")
    print("Using CPU only")

# Create a large tensor
size = 5000
a = torch.randn(size, size, device=device)
b = torch.randn(size, size, device=device)

# Time the matrix multiplication
start = time.time()
c = torch.matmul(a, b)
torch.cuda.synchronize()  # Wait for GPU to finish
end = time.time()

print(f"Matrix multiplication completed in {end - start:.4f} seconds on {device}")
