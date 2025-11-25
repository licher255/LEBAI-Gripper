# Lebai Gripper Controller

English — This file is the primary README.  
中文 — See the Chinese version: [README.zh-CN.md](README.zh-CN.md)

---

## Summary
This repository contains a simple MVC-style Python application to control a Lebai gripper. The project requires **Python 3.10.0**.

---

## Files
- main.py — application entry point  
- controller/gripper_app.py — controller logic  
- model/lebai_gripper.py — gripper model  
- view/gripper_view.py — view and UI  
- LICENSE — license

---

## Requirements
- Python 3.10.0 (strict requirement)  
- Optional: use a virtual environment

---

## Installation
1. Install or switch to Python 3.10.0.  
2. Create and activate a venv:
   $ python3.10 -m venv venv
   $ venv\Scripts\activate     # Windows
   $ source venv/bin/activate  # macOS / Linux
3. Install dependencies if any:
   $ python -m pip install -r requirements.txt

---

## Usage
Run the main application:

$ python3.10 main.py

---

## Development notes
Follow MVC separation in controller/, model/, view/. Edit main.py to change start-up behavior.

---

## Troubleshooting
- Check Python version: `python3.10 --version` should show 3.10.0.  
- Activate venv before installing packages.

---

## License
See [LICENSE](LICENSE)
