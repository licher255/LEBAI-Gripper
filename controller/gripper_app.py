# controller/gripper_app.py
import threading
import time
import queue
from model.lebai_gripper import LEBAI_Gripper
from view.gripper_view import GripperView
import tkinter as tk

from i18n import tr, set_language, get_available_languages

class GripperApp:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.view = GripperView(root)
        self.running = False
        self.polling_thread = None

        # === 新增：命令队列与工作线程 ===
        self.command_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._command_worker, daemon=True)
        self.worker_thread.start()

        # Bind callbacks
        self.view.on_connect = self.connect
        self.view.on_disconnect = self.disconnect
        self.view.on_position_change = self.set_position
        self.view.on_force_change = self.set_force
        self.view.on_speed_change = self.set_speed
        self.view.on_start_homing = self.start_homing
        self.view.on_save_speed = self.save_speed

        self._refresh_com_ports()

        self._debounce_timers = {}  # 用于存储各控件的防抖定时器
        self._DEBOUNCE_DELAY = 0.15  # 150ms，可根据体验调整

    def _refresh_com_ports(self):
        ports = LEBAI_Gripper.list_ports()
        self.view.update_com_list(ports)

    def connect(self):
        com = self.view.get_selected_com()
        if not com:
            self.view.append_status(tr("请先选择 COM 口"))
            return
        debug = self.view.is_debug_enabled()
        self.model = LEBAI_Gripper(com=com, debug=debug)
        if self.model.connect():
            self.view.set_connected(True)
            self.view.append_status(tr("✅ 已连接到 {com}").format(com=com))
            self.running = True
            self.polling_thread = threading.Thread(target=self._poll_status, daemon=True)
            self.polling_thread.start()
        else:
            self.view.append_status(tr("❌ 连接失败: {com}").format(com=com))

    def disconnect(self):
        self.running = False

        # 停止轮询线程
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=1)

        # 清空并停止命令队列
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
        if self.model:
            self.model.disconnect()
        self.view.set_connected(False)
        self.view.append_status(tr("🔌 已断开连接"))

    def _poll_status(self):
        """后台线程：定期读取状态"""
        while self.running and self.model:
            try:
                pos = self.model.read_position()
                torque = self.model.read_torque()
                done = self.model.is_command_done()
                homing = self.model.is_homing_done()

                status_str = f"Pos: {pos} | Torque: {torque} | Moving: {not done if done is not None else '?'} | Homing: {homing}"
                self.root.after(0, lambda s=status_str: self.view.append_status(s))
                time.sleep(0.5)
            except Exception as e:
                if self.view.is_debug_enabled():
                    self.root.after(0, lambda: self.view.append_status(f"[Poll Error] {e}"))
                time.sleep(1)

    # === 命令提交方法：全部放入队列 ===
    # --- 防抖辅助方法 ---
    def _debounced_command(self, key: str, func, *args):
        """防抖执行：取消旧定时器，启动新定时器"""
        if key in self._debounce_timers:
            self._debounce_timers[key].cancel()
        
        timer = threading.Timer(self._DEBOUNCE_DELAY, func, args)
        self._debounce_timers[key] = timer
        timer.start()


    def set_position(self, value):
        if self.model and self.running:
            self._debounced_command('position', self.command_queue.put, ('set_position', value))

    def set_force(self, value):
        if self.model and self.running:
             self._debounced_command('force', self.command_queue.put, ('set_force', value))


    def set_speed(self, value):
        if self.model and self.running:
             self._debounced_command('speed', self.command_queue.put, ('set_speed', value))

    def start_homing(self):
        if self.model and self.running:
            self.command_queue.put(('start_homing', None))
            self.view.append_status(tr("🔍 开始找行程..."))

    def save_speed(self):
        if self.model and self.running:
            self.command_queue.put(('save_speed', None))

    def stop_auto_homing(self, value):
        if self.model and self.running:
            self.command_queue.put(('stop_auto_homing', value))
            self.view.append_status(tr("自动找行程状态码：{value}").format(value=value))

    # === 核心：单一工作线程处理所有命令 ===
    def _command_worker(self):
        """从队列中取出命令，顺序执行，确保 RS485 安全"""
        while True:
            try:
                cmd_name, arg = self.command_queue.get(timeout=1)
                
                if not self.running or not self.model:
                    self.command_queue.task_done()
                    continue

                success = False
                try:
                    if cmd_name == 'set_position':
                        success = self.model.set_position(arg)
                        if success:
                            self.root.after(0, lambda v=arg: self.view.append_status(tr("✅ 位置设为: {v}%").format(v=v)))
                    elif cmd_name == 'set_force':
                        success = self.model.set_force(arg)
                        if success:
                            self.root.after(0, lambda v=arg: self.view.append_status(tr("✅ 力度设为: {v}%").format(v=v)))
                    elif cmd_name == 'set_speed':
                        success = self.model.set_speed(arg)
                        if success:
                            self.root.after(0, lambda v=arg: self.view.append_status(tr("✅ 速度设为: {v}%").format(v=v)))
                    elif cmd_name == 'start_homing':
                        success = self.model.start_homing()
                        if not success:
                            self.root.after(0, lambda: self.view.append_status(tr("❌ 找行程启动失败")))
                    elif cmd_name == 'save_speed':
                        success = self.model.save_speed()
                        msg = tr("💾 速度已保存") if success else tr("❌ 保存速度失败")
                        self.root.after(0, lambda m=msg: self.view.append_status(m))
                    elif cmd_name == 'stop_auto_homing':
                        success = self.model.stop_auto_homing(arg)
                        self.root.after(0, lambda v=arg: self.view.append_status(tr("🛑 停止自动找行程: {v}").format(v=v)))

                except Exception as e:
                    if self.view.is_debug_enabled():
                        self.root.after(0, lambda err=e: self.view.append_status(tr("[Cmd Error] {err}").format(err=err)))

                # RS485 需要发送-接收切换时间
                time.sleep(0.03)  # 30ms，可根据设备调整（10~50ms）

                self.command_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                # 防止 worker 崩溃
                if self.view.is_debug_enabled():
                    print(f"[Worker Fatal] {e}")
                time.sleep(0.1)
