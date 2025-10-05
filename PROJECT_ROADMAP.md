#  Blind Assistive System: Project Roadmap & Issues

This document outlines the future direction, planned features, and current issues for the Blind Assistive System project. It serves as an internal issue tracker and a guide for future development.

---

## 🎯 High-Level Goals

- **Personalization**: Train models on user-specific data to provide a faster and more tailored experience.
- **Performance**: Optimize models for both speed and accuracy to ensure real-time feedback.
- **Robustness**: Improve code quality, error handling, and configuration management.
- **Scalability**: Ensure the system can handle more features and potentially more users in the future.

---

## 📝 Current Issues & Refactoring Tasks

This section lists existing issues that need to be addressed to improve the stability and maintainability of the project.

- [ ] **Security: Remove Hardcoded Path in `face.py`**
  - **Issue**: The path to `known_faces.pkl` is hardcoded. This is not portable and will break if the app is run from a different directory.
  - **Solution**: Use a relative path based on the current file's location or define the path in a configuration file (`.env`).

- [ ] **Configuration: Improve `.env` Handling**
  - **Issue**: Environment variables from `.env` are not being loaded into the application. The convention is to use `.env.example` instead of `env_template.txt`.
  - **Solution**: Use `python-dotenv` in `start_server.py` to load variables. Rename `env_template.txt` to `.env.example`.

- [ ] **Dependencies: Add Missing `face_recognition` to `requirements.txt`**
  - **Issue**: The `face_recognition` library is a critical dependency for face detection but is missing from `requirements.txt`.
  - **Solution**: Add `face_recognition` to the `requirements.txt` file.

- [ ] **Project Cleanup: Remove Duplicated and Unused Files**
  - **Issue**: The project contains duplicate model files (`yolov8n.pt`) and potentially unused CLI scripts (`mic.py`, `scout_cli.py`).
  - **Solution**: Consolidate to a single model file and remove unused scripts to simplify the codebase.

- [ ] **Git: Untrack `__pycache__` Directories**
  - **Issue**: `__pycache__` directories are currently tracked by Git, which is not standard practice.
  - **Solution**: Run `git rm -r --cached __pycache__` and `git rm -r --cached modules/__pycache__` and commit the change. The `.gitignore` file will prevent them from being tracked in the future.

- [ ] **Error Handling: Improve API Error Specificity**
  - **Issue**: The API returns generic 500 errors for model-related issues.
  - **Solution**: Implement custom exception classes (e.g., `ModelInferenceError`) to provide more descriptive error messages to the client.

---

## ✨ Planned Feature: Personalized Object Detection

**Goal**: Make object detection faster and more personalized by training a lightweight model on user-provided data.

- [ ] **Phase 1: Data Collection API**
  - **Description**: Create a new API endpoint (e.g., `/learn_object`) that allows the mobile app to send an image and a label.
  - **Implementation**:
    - The endpoint will save the image to a structured directory like `user_data/{label}/{timestamp}.jpg`.
    - **Privacy consideration**: This data is user-specific and potentially sensitive. We must ensure it's handled securely and consider adding a user authentication layer in the future.

- [ ] **Phase 2: Model Fine-Tuning Pipeline**
  - **Description**: Create a script (`train_personal_model.py`) to fine-tune a lightweight object detection model on the collected user data.
  - **Model Choice**: Use a fast model like **YOLOv8-Nano** or a **MobileNetV2-SSD**. These are designed for edge devices and are quick to train.
  - **Implementation**: The script will load a pre-trained version of the model and fine-tune it on the images in the `user_data` directory. This can be run manually or triggered periodically.

-  [ ] **Phase 3: Integration with `find_object`**
  - **Description**: Update the `find_object` task to use the personalized model.
  - **Implementation**:
    1.  When a request comes in, first check if a personalized model exists.
    2.  If it does, use the personalized model to detect the object. This will be very fast for known objects.
    3.  If the personalized model doesn't recognize the object or doesn't exist, fall back to the more powerful but slower general-purpose model (OWL-ViT).

---

## 🚀 Strategy: Fine-Tuning for Speed and Accuracy

**Challenge**: Large models are accurate but slow. Small models are fast but less accurate. How do we get the best of both worlds?

**Solution**: A combination of **Model Quantization**, **Knowledge Distillation**, and **Hardware-Specific Optimization**.

- [ ] **1. Model Quantization**
  - **What it is**: A technique to reduce the precision of a model's weights (e.g., from 32-bit floating-point to 8-bit integer). This makes the model smaller and significantly faster with only a minor drop in accuracy.
  - **How to implement**: PyTorch has built-in tools for quantization (`torch.quantization`). We can apply this to the larger models like the BLIP captioning model after fine-tuning.

- [ ] **2. Knowledge Distillation**
  - **What it is**: A "teacher-student" training method. We use a large, accurate "teacher" model (like GPT-4 for text or a large vision model) to train a smaller, faster "student" model (like DistilBERT or a MobileNet). The student model learns to mimic the teacher's outputs, capturing its complex patterns in a much smaller architecture.
  - **How to implement**:
    1.  Pass a large dataset of images/questions through the big "teacher" model and save its predictions.
    2.  Train the small "student" model to match the teacher's predictions, not just the ground-truth labels.

- [ ] **3. Use of Specialized Runtimes**
  - **What it is**: Instead of running models directly in PyTorch, we can convert them to a format optimized for inference, like **ONNX (Open Neural Network Exchange)**.
  - **How to implement**: Convert the PyTorch models to ONNX format. Then, use a runtime like **ONNX Runtime**, which is highly optimized for CPU and GPU and can deliver significant speedups.

### Proposed Workflow for a "Good and Fast" Model:

1.  **Fine-tune** a large, accurate model on a specific task (e.g., fine-tune BLIP on a medical VQA dataset).
2.  **Quantize** the fine-tuned model to reduce its size and speed up inference.
3.  **(Optional) Distill** the knowledge from this model into a smaller, faster architecture if more speed is needed.
4.  **Convert** the final model to ONNX format and serve it using ONNX Runtime.

---

## 💡 GitHub Issues Integration

You mentioned posting these issues on GitHub. That is an excellent idea and the standard practice for managing open-source projects.

- **Suggestion**: I can help you create these issues in your GitHub repository. This would allow for better tracking, assignment, and community contributions. For now, this `PROJECT_ROADMAP.md` file will serve as our planning document.
