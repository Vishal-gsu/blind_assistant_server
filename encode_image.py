import base64

with open("yolov8n.pt", "rb") as f:
    encoded_string = base64.b64encode(f.read()).decode("utf-8")
    print(encoded_string)
