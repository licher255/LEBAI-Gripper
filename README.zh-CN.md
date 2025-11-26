# 乐白夹爪LMD-90 控制程序

中文说明（README）

English — ：[README.md](README.md)

---

## 概要
此仓库包含一个简单的 MVC 风格 Python 应用，用于控制 Lebai 夹持器。项目严格要求 **Python 3.10.0**。
参考文献为乐白官方提供的**v1.5**版本的通讯协议

---

## 文件结构
- main.py — 程序入口  
- controller/gripper_app.py — 控制器逻辑  
- model/lebai_gripper.py — 夹持器模型  
- view/gripper_view.py — 界面与交互  
- i18n
   -  __init__.py  — i18n 翻译逻辑
   - lang_extractor.py  — 翻译字符提取工具
   - en.json  —  English 支持
   - zh.json  —  中文支持
- LICENSE — 许可证

---

## 依赖
- Python 3.10.0（严格要求）  
- 建议使用虚拟环境

---

## 安装
1. 安装或切换到 Python 3.10.0。  
2. 创建并激活虚拟环境：
   $ python3.10 -m venv venv
   $ venv\Scripts\activate  # Windows
   $ source venv/bin/activate  # macOS / Linux
3. 若有依赖：
   $ python -m pip install -r requirements.txt

---

## 使用
运行主程序：
```
 $ python3.10 main.py
 ```
---
## Translation I18N
add $tr("")$ to the text or label that need to be translated.

specially if it is a tkinter widget, it need to be also resigned, for example:
```
   self.pos_text_label = ttk.Label(ctrl_frame, text=tr("位置 (0-100):"))
   self.pos_text_label.grid(row=0, column=0, sticky='w', **pad)
   
   def _register_translatable_widgets(self):
        self._register_widget(self.pos_text_label, "位置 (0-100):")
```

## 开发说明
遵循 MVC 分层：controller/, model/, view/。修改 main.py 更改程序启动行为。

---

## 常见问题
- 检查 Python 版本：`python3.10 --version` 应显示 3.10.0。  
- 在虚拟环境中安装依赖包。

---

## 许可证
查看 [LICENSE](LICENSE)
