# Lebai Gripper Controller

English — This file is the primary README.  
中文 — See the Chinese version: [README.zh-CN.md](README.zh-CN.md)

---

## Summary
This repository contains a simple MVC-style Python application to control a Lebai gripper. The project requires **Python 3.10.0**.
The reference is the communication protocol version **v1.5** provided by the official LeBai.
---

## Files
- main.py — application entry point  
- controller/gripper_app.py — controller logic  
- model/lebai_gripper.py — gripper model  
- view/gripper_view.py — view and UI  
- i18n
   -  __init__.py  — i18n logic
   - lang_extractor.py  — a tool for extracting tr("") string in program
   - en.json  —  English support
   - zh.json  —  Chinese support
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
```
python3.10 main.py
```
## Translation I18N
add $tr("")$ to the text or label that need to be translated.

specially if it is a tkinter widget, it need to be also resigned, for example:
```
   self.pos_text_label = ttk.Label(ctrl_frame, text=tr("位置 (0-100):"))
   self.pos_text_label.grid(row=0, column=0, sticky='w', **pad)

   def _register_translatable_widgets(self):
        self._register_widget(self.pos_text_label, "位置 (0-100):")
```
## Development notes
Follow MVC separation in controller/, model/, view/. Edit main.py to change start-up behavior.

---

## Troubleshooting
- Check Python version: `python3.10 --version` should show 3.10.0.  
- Activate venv before installing packages.

---

## License
See [LICENSE](LICENSE)
