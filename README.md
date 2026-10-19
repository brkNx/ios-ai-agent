# iOS AI Agent

An autonomous multimodal AI agent that operates an iPhone just like a human: perceiving the live screen, deciding actions with vision LLMs, tapping buttons, scrolling, and typing.

> **Zero Bloat:** Does not require a heavy 40 GB Xcode installation. Runs cleanly on any Mac using Sideloadly and lightweight Python tools.

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Enable Developer Mode on iPhone
1. On your iPhone, navigate to **Settings > Privacy & Security > Developer Mode**.
2. Toggle Developer Mode **ON** and reboot the device when prompted.

---

### Step 2: Install WebDriverAgent (WDA) via Sideloadly (No Xcode Needed)
1. Download **Sideloadly** (~50 MB) on your Mac: [https://sideloadly.io](https://sideloadly.io)
2. Obtain `WebDriverAgentRunner.ipa`:
   * The prebuilt IPA is included in this repository as `WebDriverAgentRunner.ipa` (or build from [Appium WebDriverAgent Releases](https://github.com/appium/WebDriverAgent/releases)).
3. Connect your iPhone to your Mac via USB cable.
4. Launch Sideloadly:
   * Drag & drop `WebDriverAgentRunner.ipa` onto the **IPA** box.
   * Enter your Apple ID (free personal account works).
   * Click **Start**. The app installs directly onto the iPhone.
5. On your iPhone:
   * Go to **Settings > General > VPN & Device Management**, tap your Apple ID, and tap **Trust**.
   * Tap the **WebDriverAgentRunner** icon on your home screen once to launch the background server.

---

### Step 3: Relay Device Port
Bridge the device's WDA port to your Mac via USB using `t3` (tidevice3) or `iproxy`:

```bash
# Activate virtual environment
source .venv/bin/activate

# Relay WDA port to localhost:8100
t3 relay 8100 8100
```

---

### Step 4: Configure & Test

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Setup `.env` configuration:
   ```bash
   cp .env.example .env
   ```
   Add your Gemini or OpenAI API key:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=AIzaSy...
   GEMINI_MODEL=gemini-3.5-flash
   ```

3. Test the connection:
   ```bash
   python3 main.py --test
   ```
   If it outputs `[✅] Connection successful!`, the agent is ready.

---

## 🚀 Usage

Run the agent from the terminal with any natural language command:

```bash
# Example 1: Send a message
python3 main.py "Open WhatsApp, find Mom, and send 'I will be there in 30 minutes'"

# Example 2: Check settings
python3 main.py "Open Settings and check Battery Health"

# Example 3: Browse Safari
python3 main.py "Open Safari, search for apple stock price on Google"
```

---

## 🧩 Architecture

```
[ User Prompt / Goal ]
          │
          ▼
   [ IOSAgent (agent.py) ] ◄────────┐
          │ (Screenshot capture)    │
          ▼                         │
 [ VisionBrain (brain.py) ]         │ (Perception Loop)
   (Gemini / OpenAI Vision)         │
          │ (Decision: Tap / Type)  │
          ▼                         │
 [ WDADriver (wda_driver.py) ] ─────┘
          │ (HTTP REST: /wda/tap)
          ▼
   [ iPhone Screen ] (Physical tap & typing execution)
```

---

## 📄 License
MIT License
