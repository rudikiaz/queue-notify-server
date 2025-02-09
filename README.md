# Flask Telegram Notification Service

This project is a Flask-based web service designed to integrate with a Telegram bot. It provides two endpoints to register a chat based on a specific identifier and to notify that chat when required. This Dockerized application now uses the PyPy runtime to leverage JIT optimizations for improved performance.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Setup and Running](#setup-and-running)
  - [Using Docker](#using-docker)
  - [Running Locally](#running-locally)
- [Endpoints](#endpoints)
  - [/register (POST)](#register-post)
  - [/notify (POST)](#notify-post)
- [Configuration Files](#configuration-files)
- [Additional Information](#additional-information)
- [License](#license)

---

## Overview

This service:
- Uses AES encryption (with a fixed IV) to securely encode chat IDs.
- Retrieves Telegram updates to match a provided ID with a corresponding chat.
- Sends notifications via Telegram using the bot's sendMessage API.

It is packaged in a Docker container using the PyPy runtime, offering potential performance improvements over traditional CPython.

---

## Project Structure

- `Dockerfile`: Defines how to build the Docker image using the PyPy runtime.
- `app.py`: Contains the Flask application with the business logic.
- `requirements.txt`: Lists the Python dependencies.
- `encryption.key`: (Optional) File containing your encryption key (if missing, a default key is used, which is insecure).
- `bot.token`: (Optional) File containing your Telegram bot token.

---

## Dependencies

The application depends on:
- **cryptography==42.0.7:** For AES encryption/decryption.
- **Flask==3.1.0:** The web framework.
- **Requests==2.32.3:** For making HTTP requests to Telegram's API.
- **Gunicorn:** Installed via the Dockerfile for running the application in production.

All these libraries are compatible with the PyPy runtime.

---

## Setup and Running

### Using Docker

1. **Build the Docker Image:**

   ```bash
   docker build -t telegram-app .
   ```

2. **Run the Container:**

   ```bash
   docker run -p 8000:8000 telegram-app
   ```

   The application will be available at [http://localhost:8000](http://localhost:8000).

### Running Locally

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install gunicorn
   ```

2. **Run the Application:**

   - For development, you can run:

     ```bash
     python app.py
     ```

   - For production, run with Gunicorn:

     ```bash
     gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
     ```

---

## Endpoints

### /register (POST)

- **Description:**  
  Matches a provided identifier with the text of a Telegram message, retrieves the corresponding chat ID, then encrypts the chat ID using AES encryption before returning it.

- **Request Body:**  
  ```json
  {
    "id": "UniqueIdentifier"
  }
  ```
  - `id`: The identifier you're registering (e.g., a message text in Telegram).

- **Response:**  
  If successful:
  ```json
  {
    "encodedID": "encrypted_chat_id"
  }
  ```
  Otherwise, returns an error with a descriptive message.

---

### /notify (POST)

- **Description:**  
  Accepts an encrypted chat ID and sends a notification message ("Your Solo Shuffle is ready.") to that chat via Telegram. You can specify how many times to send the notification using the `notifyRetries` field.

- **Request Body:**  
  ```json
  {
    "encodedID": "encrypted_chat_id",
    "notifyRetries": 2
  }
  ```
  - `encodedID`: The AES-encrypted chat ID returned from the `/register` endpoint.
  - `notifyRetries`: The number of times the notification should be sent (default is 1).

- **Response:**  
  ```json
  {
    "status": "notifications sent"
  }
  ```

---

## Configuration Files

- **`encryption.key`**:  
  Create this file in the root directory if you want to use a custom encryption key. The service will use its content as the AES key. Without this file, a default key (`b'test'`) is used, which is insecure.

- **`bot.token`**:  
  Create this file in the root directory to store your Telegram bot token. If not present, the application will use a default (`default_token`), so be sure to replace this with your actual token for proper Telegram integration.

---

## Additional Information

- **PyPy Runtime:**  
  The Dockerfile now specifies the `pypy:3-slim` image, which can lead to enhanced performance for CPU-intensive operations thanks to PyPy's JIT compilation.

- **Encryption Details:**  
  The service uses AES encryption in CBC mode with a fixed IV (all zeros) and PKCS7 padding. Although using a fixed IV is generally not recommended for strong security guarantees, it is used here to maintain a consistent decryption format.

- **Telegram Integration:**  
  The `/register` endpoint uses Telegram's `getUpdates` API to retrieve messages, and the `/notify` endpoint uses the `sendMessage` API to dispatch notifications.

---

## License

This project is provided "as is" with no warranties. Please consult the terms of any libraries used for more detailed licensing information. 