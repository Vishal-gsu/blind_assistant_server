#!/usr/bin/env python3
"""
Startup script for Blind Assistive System with optimized memory management.
"""

import os
import sys

def setup_environment():
    """Set up environment variables for optimal performance."""
    # Set CUDA memory allocation configuration
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
    
    # Set OMP threads for better CPU performance
    os.environ['OMP_NUM_THREADS'] = '4'
    
    # Reduce memory fragmentation
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
    
    print("Environment configured for optimal memory usage.")

def check_gpu_memory():
    """Check available GPU memory."""
    try:
        import torch
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**3
            print(f"GPU detected: {torch.cuda.get_device_name(device)}")
            print(f"Total GPU Memory: {total_memory:.2f}GB")
            
            if total_memory < 4.0:
                print("⚠️  Warning: Limited GPU memory detected. Some features may use CPU fallback.")
            elif total_memory < 6.0:
                print("ℹ️  Note: Medium GPU memory. OCR will use CPU for stability.")
            else:
                print("✅ Sufficient GPU memory available.")
        else:
            print("No GPU detected. Running in CPU mode.")
    except ImportError:
        print("PyTorch not installed. Please install PyTorch first.")
        sys.exit(1)

def main():
    """Main startup function."""
    print("🦯 Starting Blind Assistive System...")
    
    # Setup environment
    setup_environment()
    
    # Check GPU
    check_gpu_memory()
    
    # Import and start the main application
    try:
        print("Loading application...")
        import uvicorn
        from main import app
        
        print("✅ Application loaded successfully!")
        print("🚀 Starting server on http://localhost:8000")
        print("📡 API documentation available at http://localhost:8000/docs")
        
        # Start the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            reload=False,  # Disable reload to prevent memory issues
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()