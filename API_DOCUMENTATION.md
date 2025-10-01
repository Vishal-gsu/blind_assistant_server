
# Professor API Documentation

## 1. Introduction

This document provides the technical specification for interacting with the "Professor" server, the AI backend for the Scout assistive application. The server exposes a single, powerful endpoint to process visual and textual data.

**Contact:** Taylor, Senior Backend & AI Engineer

## 2. Base URL

The server runs locally. Once started, the base URL for all API calls is:

`http://localhost:8000`

## 3. Authentication

There is currently no authentication required to access the API.

## 4. The Universal Endpoint: `POST /process_data`

All functionality is accessed through a single endpoint. The action the server performs is determined by the `task` field in the JSON request body.

- **URL:** `/process_data`
- **Method:** `POST`
- **Content-Type:** `application/json`

### Request Body

The request body must be a JSON object with the following structure:

```json
{
  "task": "string",
  "image_data": "string",
  "query_text": "string, optional",
  "conversation_history": "array, optional"
}
```

**Field Descriptions:**

- `task` (string, required): The specific task for the server to perform. Must be one of the following values:
    - `describe_scene`: Provides a general description of the image.
    - `read_text`: Performs Optical Character Recognition (OCR) on the image.
    - `find_object`: Searches for a specific object in the image.
    - `answer_question`: Answers a direct question about the image.
- `image_data` (string, required): A Base64 encoded string of the JPEG image to be processed.
- `query_text` (string, optional): Required for `find_object` and `answer_question` tasks. For `find_object`, this is the name of the object to find (e.g., "my keys"). For `answer_question`, this is the question itself (e.g., "what color is the car?").
- `conversation_history` (array, optional): A list of previous conversation turns. While the server is stateless, including this allows for more context-aware responses in future versions. (Currently not implemented in the server logic).

### Response Body

A successful request will receive a `200 OK` status code and a JSON response body with the following structure:

```json
{
  "result_text": "string",
  "structured_data": "object, optional"
}
```

**Field Descriptions:**

- `result_text` (string): The primary result of the task, designed to be spoken directly to the user by the Scout application.
- `structured_data` (object, optional): Contains supplementary, non-verbal data. For the `find_object` task, this will include the bounding box of the found object (e.g., `{"box": {"xmin": 10, "ymin": 20, "xmax": 100, "ymax": 120}, "score": 0.95}`).

## 5. Error Handling

If a request is invalid (e.g., missing a required field, invalid `task` value, malformed image data), the server will respond with a `400 Bad Request` status code and a JSON body containing a `detail` key with an error message.

```json
{
  "detail": "Invalid image data: Incorrect padding"
}
```

## 6. Example Requests

Here are `curl` examples for each task. You will need to replace `[BASE64_ENCODED_IMAGE_STRING]` with your actual base64 image data.

### Describe Scene

```bash
curl -X POST http://localhost:8000/process_data \
-H "Content-Type: application/json" \
-d '{
  "task": "describe_scene",
  "image_data": "[BASE64_ENCODED_IMAGE_STRING]"
}'
```

### Read Text

```bash
curl -X POST http://localhost:8000/process_data \
-H "Content-Type: application/json" \
-d '{
  "task": "read_text",
  "image_data": "[BASE64_ENCODED_IMAGE_STRING]"
}'
```

### Find Object

```bash
curl -X POST http://localhost:8000/process_data \
-H "Content-Type: application/json" \
-d '{
  "task": "find_object",
  "image_data": "[BASE64_ENCODED_IMAGE_STRING]",
  "query_text": "a water bottle"
}'
```

### Answer Question

```bash
curl -X POST http://localhost:8000/process_data \
-H "Content-Type: application/json" \
-d '{
  "task": "answer_question",
  "image_data": "[BASE64_ENCODED_IMAGE_STRING]",
  "query_text": "how many chairs are in the room?"
}'
```
