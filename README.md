# Blender Real-Time Collaboration 🤝

A simple, effective Blender Add-on that allows multiple users to work on the same scene in real-time. Syncs object transformations (Location, Rotation, Scale) instantly across connected clients.

## Features
*   **Real-time Sync**: Move an object in one Blender instance, and watch it update in another.
*   **Host & Join**: Easily host a session or join an existing one using a Room Code.
*   **Network Capable**: Connect over Local LAN or the Internet (requires port forwarding or VPN).
*   **Minimal Setup**: Lightweight Relay Server included.

## Installation

1.  **Download the Code**: Clone this repository or download the ZIP.
2.  **Install Dependencies**:
    *   This add-on requires the `websockets` Python library.
    *   Since Blender uses its own Python, you must install it *inside* Blender's environment.
    *   Open Blender > Scripting > Console and run:
        ```python
        import sys, subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
        ```
3.  **Install Add-on**:
    *   Go to **Edit > Preferences > Add-ons > Install...**
    *   Select the `RealTimeCollaboration` folder (you may need to zip it first if you downloaded the source).
    *   Enable **Real-Time Collaboration**.

## How to Use

### 1. Start the Server
Before anyone can connect, the "Relay Server" must be running. This acts as the bridge between all Blender users.
*   Open a terminal/command prompt.
*   Navigate to the `Server` folder.
*   Run:
    ```bash
    python relay_server.py
    ```

### 2. Connect from Blender
**User A (Host):**
*   Open the 3D Viewport side panel (Press `N`).
*   Click the **Collaboration** tab.
*   Enter the Server URL (Default: `ws://localhost:8765`).
*   Click **Host Session**.
*   Share the **Room Code** shown in the system console with User B.

**User B (Joiner):**
*   Open the **Collaboration** tab.
*   Enter the Server URL (e.g., `ws://192.168.1.5:8765` if on a different machine).
*   Enter the **Room Code**.
*   Click **Join Session**.

### 3. Collaborate!
Select an object and move it. It will move for everyone else in the session! 🚀

## Requirements
*   Blender 2.80+
*   Python 3.7+
*   `websockets` library

## License
MIT License. Feel free to modify and improve!
