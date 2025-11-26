# view/gripper_view.py
import tkinter as tk
from tkinter import ttk
from i18n import tr, set_language, get_available_languages

LANG_DISPLAY_NAMES = {
    "zh": "中文",
    "en": "English",
    "fr": "Français",
    "es": "Español",
}

class GripperView:
    def __init__(self, root):
        self.root = root
        self.translatable_widgets = []
        self._create_widgets()
        self._register_translatable_widgets()
        self.root.title(tr("LEBAI LMG-90 夹爪控制器"))
        self.root.geometry("520x650")

        # 回调...
        self.on_connect = None
        self.on_disconnect = None
        self.on_position_change = None
        self.on_force_change = None
        self.on_speed_change = None
        self.on_start_homing = None
        self.on_save_speed = None
        self.on_stop_auto_homing = None

    def _create_translatable_label_frame(self, parent, text_key: str):
        """返回 (outer_container, content_frame)"""
        container = tk.Frame(parent, relief='groove', borderwidth=2)
        title_label = ttk.Label(container, text=tr(text_key), font=('TkDefaultFont', 9, 'bold'))
        title_label.pack(anchor='nw', padx=5, pady=(5, 0))
        content_frame = tk.Frame(container)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self._register_widget(title_label, text_key)
        return container, content_frame

    def _create_widgets(self):
        pad = {'padx': 11, 'pady': 5}

        # === 语言选择器 ===
        lang_container = tk.Frame(self.root)
        lang_container.pack(fill='x', **pad)
        lang_label = tk.Label(lang_container, text=tr("语言"))
        lang_label.pack(side='left')
        self.lang_var = tk.StringVar(value="zh")
        languages = get_available_languages()
        display_names = [LANG_DISPLAY_NAMES.get(code, code) for code in languages]
        self.lang_name_to_code = dict(zip(display_names, languages))
        lang_menu = tk.OptionMenu(lang_container, self.lang_var, *display_names, command=self._on_lang_change_by_name)
        lang_menu.pack(side='left', padx=(5, 0))
        self._register_widget(lang_label, "语言")

        # === 串口设置 ===
        com_outer, com_frame = self._create_translatable_label_frame(self.root, tr("串口设置"))
        com_outer.pack(fill='x', **pad)

        self.com_port_label = ttk.Label(com_frame, text=tr("COM Port:"))  # ← 保存引用
        self.com_port_label.grid(row=0, column=0, sticky='w', **pad)

        self.com_var = tk.StringVar()
        self.com_combo = ttk.Combobox(com_frame, textvariable=self.com_var, state='readonly')
        self.com_combo.grid(row=0, column=1, sticky='ew', **pad)
        self.connect_btn = ttk.Button(com_frame, text=tr("连接"), command=self._on_connect)
        self.connect_btn.grid(row=0, column=2, **pad)
        self.disconnect_btn = ttk.Button(com_frame, text=tr("断开"), command=self._on_disconnect, state='disabled')
        self.disconnect_btn.grid(row=0, column=3, **pad)
        com_frame.columnconfigure(1, weight=1)
        self.debug_var = tk.BooleanVar()
        self.debug_cb = ttk.Checkbutton(com_frame, text=tr("Debug 模式"), variable=self.debug_var)
        self.debug_cb.grid(row=1, column=0, columnspan=2, sticky='w', **pad)

        # === 控制 ===
        ctrl_outer, ctrl_frame = self._create_translatable_label_frame(self.root, tr("控制"))
        ctrl_outer.pack(fill='x', **pad)

        self.pos_text_label = ttk.Label(ctrl_frame, text=tr("位置 (0-100):"))
        self.pos_text_label.grid(row=0, column=0, sticky='w', **pad)
        self.pos_var = tk.IntVar(value=50)
        self.pos_slider = ttk.Scale(ctrl_frame, from_=0, to=100, variable=self.pos_var, orient='horizontal', command=self._on_pos_slider)
        self.pos_slider.grid(row=0, column=1, sticky='ew', **pad)
        self.pos_label = ttk.Label(ctrl_frame, text="50")
        self.pos_label.grid(row=0, column=2, **pad)

        self.force_text_label = ttk.Label(ctrl_frame, text=tr("力度 (0-100):"))
        self.force_text_label.grid(row=1, column=0, sticky='w', **pad)
        self.force_var = tk.IntVar(value=50)
        self.force_slider = ttk.Scale(ctrl_frame, from_=0, to=100, variable=self.force_var, orient='horizontal', command=self._on_force_slider)
        self.force_slider.grid(row=1, column=1, sticky='ew', **pad)
        self.force_label = ttk.Label(ctrl_frame, text="50")
        self.force_label.grid(row=1, column=2, **pad)

        self.speed_text_label = ttk.Label(ctrl_frame, text=tr("速度 (0-100):"))
        self.speed_text_label.grid(row=2, column=0, sticky='w', **pad)
        self.speed_var = tk.IntVar(value=50)
        self.speed_slider = ttk.Scale(ctrl_frame, from_=0, to=100, variable=self.speed_var, orient='horizontal', command=self._on_speed_slider)
        self.speed_slider.grid(row=2, column=1, sticky='ew', **pad)
        self.speed_label = ttk.Label(ctrl_frame, text="50")
        self.speed_label.grid(row=2, column=2, **pad)
        ctrl_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, **pad)
        self.save_speed_btn = ttk.Button(btn_frame, text=tr("保存速度"), command=self._on_save_speed)
        self.save_speed_btn.pack(side='left', **pad)
        self.start_homing_btn = ttk.Button(btn_frame, text=tr("开始找行程"), command=self._on_start_homing)
        self.start_homing_btn.pack(side='left', **pad)
        # === 自动找行程管理 ===
        auto_outer, auto_home_frame = self._create_translatable_label_frame(self.root, tr("自动找行程管理"))
        auto_outer.pack(fill='x', **pad)

        auto_btn_frame = ttk.Frame(auto_home_frame)
        auto_btn_frame.pack(**pad)
        self.stop_auto_homing_btn1 = ttk.Button(auto_btn_frame, text=tr("关闭&不保持"), command=lambda: self._on_stop_auto_homing(1))
        self.stop_auto_homing_btn1.pack(side='left', **pad)
        self.stop_auto_homing_btn2 = ttk.Button(auto_btn_frame, text=tr("关闭&保持EPPROM"), command=lambda: self._on_stop_auto_homing(2))
        self.stop_auto_homing_btn2.pack(side='left', **pad)
        self.stop_auto_homing_btn3 = ttk.Button(auto_btn_frame, text=tr("开启&存EPPROM"), command=lambda: self._on_stop_auto_homing(3))
        self.stop_auto_homing_btn3.pack(side='left', **pad)

        # === 状态 ===
        status_outer, status_frame = self._create_translatable_label_frame(self.root, tr("状态"))
        status_outer.pack(fill='both', expand=True, **pad)

        self.status_text = tk.Text(status_frame, height=8, state='disabled')
        self.status_text.pack(fill='both', expand=True, **pad)



    # --- 以下方法保持不变 ---
    def _register_widget(self, widget, key: str):
        self.translatable_widgets.append((widget, key))

    def _register_translatable_widgets(self):
        # 原有
        self._register_widget(self.connect_btn, "连接")
        self._register_widget(self.disconnect_btn, "断开")
        
        # 新增：串口设置区
        self._register_widget(self.com_port_label, "COM Port:")
        self._register_widget(self.debug_cb, "Debug 模式")
        
        # 新增：控制区
        self._register_widget(self.pos_text_label, "位置 (0-100):")
        self._register_widget(self.force_text_label, "力度 (0-100):")
        self._register_widget(self.speed_text_label, "速度 (0-100):")
        self._register_widget(self.save_speed_btn, "保存速度")
        self._register_widget(self.start_homing_btn, "开始找行程")
        
        # 新增：自动找行程管理区（你需要类似保存按钮引用）
        self._register_widget(self.stop_auto_homing_btn1, "关闭&不保持")
        self._register_widget(self.stop_auto_homing_btn2, "关闭&保持EPPROM")
        self._register_widget(self.stop_auto_homing_btn3, "开启&存EPPROM")

    def _on_lang_change_by_name(self, display_name: str):
        lang_code = self.lang_name_to_code[display_name]
        set_language(lang_code)
        self._refresh_all_texts()
        self.root.title(tr("LEBAI LMG-90 夹爪控制器"))

    def _refresh_all_texts(self):
        for widget, key in self.translatable_widgets:
            if key.isdigit():
                continue
            widget.config(text=tr(key))

    # --- 事件回调 ---
    def _on_connect(self):
        if self.on_connect: self.on_connect()
    def _on_disconnect(self):
        if self.on_disconnect: self.on_disconnect()
    def _on_pos_slider(self, val):
        val = int(float(val))
        self.pos_label.config(text=str(val))
        if self.on_position_change: self.on_position_change(val)
    def _on_force_slider(self, val):
        val = int(float(val))
        self.force_label.config(text=str(val))
        if self.on_force_change: self.on_force_change(val)
    def _on_speed_slider(self, val):
        val = int(float(val))
        self.speed_label.config(text=str(val))
        if self.on_speed_change: self.on_speed_change(val)
    def _on_start_homing(self):
        if self.on_start_homing: self.on_start_homing()
    def _on_stop_auto_homing(self, val):
        if self.on_stop_auto_homing: self.on_stop_auto_homing(val)
    def _on_save_speed(self):
        if self.on_save_speed: self.on_save_speed()

    # --- 公共 API ---
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