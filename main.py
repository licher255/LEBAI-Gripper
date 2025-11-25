# main.py
import tkinter as tk
from controller.gripper_app import GripperApp

if __name__ == "__main__":
    root = tk.Tk()
    app = GripperApp(root)
    root.mainloop()