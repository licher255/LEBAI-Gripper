# view/gripper_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class GripperView:
    def __init__(self, root):
        self.root = root
        self.root.title("LEBAI LMG-90 夹爪控制器")
        self.root.geometry("500x600")

        # Callbacks (set by controller)
        self.on_connect = None
        self.on_disconnect = None
        self.on_position_change = None
        self.on_force_change = None
        self.on_speed_change = None
        self.on_start_homing = None
        self.on_save_speed = None
        self.on_stop_auto_homing = None 

        self._create_widgets()
        
    def _create_widgets(self):
        pad = {'padx': 11, 'pady': 5}

        # COM Port Selection
        com_frame = ttk.LabelFrame(self.root, text="串口设置")
        com_frame.pack(fill='x', **pad)

        ttk.Label(com_frame, text="COM Port:").grid(row=0, column=0, sticky='w', **pad)
        self.com_var = tk.StringVar()
        self.com_combo = ttk.Combobox(com_frame, textvariable=self.com_var, state='readonly')
        self.com_combo.grid(row=0, column=1, sticky='ew', **pad)

        self.connect_btn = ttk.Button(com_frame, text="连接", command=self._on_connect)
        self.connect_btn.grid(row=0, column=2, **pad)

        self.disconnect_btn = ttk.Button(com_frame, text="断开", command=self._on_disconnect, state='disabled')
        self.disconnect_btn.grid(row=0, column=3, **pad)

        com_frame.columnconfigure(1, weight=1)

        # Debug Checkbox
        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(com_frame, text="Debug 模式", variable=self.debug_var).grid(row=1, column=0, columnspan=2, sticky='w', **pad)

        # Control Sliders
        ctrl_frame = ttk.LabelFrame(self.root, text="控制")
        ctrl_frame.pack(fill='x', **pad)

        # Position
        ttk.Label(ctrl_frame, text="位置 (0-100):").grid(row=0, column=0, sticky='w', **pad)
        self.pos_var = tk.IntVar(value=50)
        self.pos_slider = ttk.Scale(ctrl_frame, from_=0, to=100, variable=self.pos_var, orient='horizontal', command=self._on_pos_slider)
        self.pos_slider.grid(row=0, column=1, sticky='ew', **pad)
        self.pos_label = ttk.Label(ctrl_frame, text="50")
        self.pos_label.grid(row=0, column=2, **pad)

        # Force
        ttk.Label(ctrl_frame, text="力度 (0-100):").grid(row=1, column=0, sticky='w', **pad)
        self.force_var = tk.IntVar(value=50)
        self.force_slider = ttk.Scale(ctrl_frame, from_=0, to=100, variable=self.force_var, orient='horizontal', command=self._on_force_slider)
        self.force_slider.grid(row=1, column=1, sticky='ew', **pad)
        self.force_label = ttk.Label(ctrl_frame, text="50")
        self.force_label.grid(row=1, column=2, **pad)

        # Speed
        ttk.Label(ctrl_frame, text="速度 (0-100):").grid(row=2, column=0, sticky='w', **pad)
        self.speed_var = tk.IntVar(value=50)
        self.speed_slider = ttk.Scale(ctrl_frame, from_=0, to=100, variable=self.speed_var, orient='horizontal', command=self._on_speed_slider)
        self.speed_slider.grid(row=2, column=1, sticky='ew', **pad)
        self.speed_label = ttk.Label(ctrl_frame, text="50")
        self.speed_label.grid(row=2, column=2, **pad)

        ctrl_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, **pad)

        ttk.Button(btn_frame, text="保存速度", command=self._on_save_speed).pack(side='left', **pad)
        ttk.Button(btn_frame, text="开始找行程", command=self._on_start_homing).pack(side='left', **pad)
        
        #Auto Home Control
        autoHome_frame = ttk.LabelFrame(self.root, text="自动找行程管理")
        autoHome_frame.pack(fill='x', **pad)
        # Buttons 自动找行程管理
        btn_frame = ttk.Frame(autoHome_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, **pad )
        ttk.Button(btn_frame, text="关闭自动找行程", command=self._on_stop_auto_homing(1)).pack(side='left', **pad)
        ttk.Button(btn_frame, text="关闭自动找行程并且保持", command=self._on_stop_auto_homing(2)).pack(side='left', **pad)
        ttk.Button(btn_frame, text="恢复自动找行程并且保存", command=self._on_stop_auto_homing(3)).pack(side='left', **pad)
        
        # Status Display
        status_frame = ttk.LabelFrame(self.root, text="状态")
        status_frame.pack(fill='both', expand=True, **pad)

        self.status_text = tk.Text(status_frame, height=8, state='disabled')
        self.status_text.pack(fill='both', expand=True, **pad)

        # Scrollbar (optional)
        # scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        # self.status_text.configure(yscrollcommand=scrollbar.set)
        # scrollbar.pack(side='right', fill='y')

    def _on_connect(self):
        if self.on_connect:
            self.on_connect()

    def _on_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()

    def _on_pos_slider(self, val):
        val = int(float(val))
        self.pos_label.config(text=str(val))
        if self.on_position_change:
            self.on_position_change(val)

    def _on_force_slider(self, val):
        val = int(float(val))
        self.force_label.config(text=str(val))
        if self.on_force_change:
            self.on_force_change(val)

    def _on_speed_slider(self, val):
        val = int(float(val))
        self.speed_label.config(text=str(val))
        if self.on_speed_change:
            self.on_speed_change(val)

    def _on_start_homing(self):
        if self.on_start_homing:
            self.on_start_homing()

    def _on_stop_auto_homing(self, val):
        if self.on_stop_auto_homing:
            self.on_stop_auto_homing(val)

    def _on_save_speed(self):
        if self.on_save_speed:
            self.on_save_speed()

    def update_com_list(self, ports):
        self.com_combo['values'] = ports
        if ports and not self.com_var.get():
            self.com_var.set(ports[0])

    def set_connected(self, connected: bool):
        state = 'disabled' if connected else '!disabled'
        self.com_combo.state([state])
        self.connect_btn.config(state='normal' if not connected else 'disabled')
        self.disconnect_btn.config(state='normal' if connected else 'disabled')

    def append_status(self, text):
        self.status_text.config(state='normal')
        self.status_text.insert('end', text + '\n')
        self.status_text.see('end')
        self.status_text.config(state='disabled')

    def clear_status(self):
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', 'end')
        self.status_text.config(state='disabled')

    def get_selected_com(self):
        return self.com_var.get()

    def is_debug_enabled(self):
        return self.debug_var.get()