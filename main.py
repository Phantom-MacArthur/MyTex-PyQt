import os
import sys
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog, QWidget, QHBoxLayout,
    QPushButton
)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QTimer
import pyperclip

try:
    from pynput.keyboard import Controller, Key
except ImportError:
    Controller = None
    Key = None

# 禁用Python字节码缓存
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

from main_window import MainWindow
from api_client import FormulaAPIClient
from image_handler import ImageHandler
from image_display_panel import ImageDisplayPanel  # 更新导入
from api_and_recognition_panel import APIAndRecognitionPanel
from api_config import TEST_CONFIG  # 测试配置 - 提交前记得删除！


class FormulaRecognizer(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置窗口标题和初始大小 - 更小的默认高度
        self.setWindowTitle("公式识别软件")
        self.resize(800, 400)  # 减小默认高度到400px
        
        # 创建中心部件
        central_widget = MainWindow()
        self.setCentralWidget(central_widget)
        
        # 初始化各个模块
        self.api_client = FormulaAPIClient()
        self.image_handler = ImageHandler(self)
        self.ui = central_widget
        
        # 连接信号
        self.ui.left_panel.input_panel.original_view  # 确保左侧面板可用
        self.ui.right_panel.select_image_requested.connect(self.select_image)
        self.ui.right_panel.take_screenshot_requested.connect(self.take_screenshot)
        self.ui.right_panel.retry_recognition_requested.connect(self.retry_recognition)
        self.ui.right_panel.screenshot_shortcut_changed.connect(self.on_screenshot_shortcut_changed)
        self.ui.right_panel.compact_mode_toggled.connect(self.toggle_compact_mode)
        
        # 状态变量
        self.selected_image_path = None
        self.is_waiting_for_screenshot = False
        self.success_count = 0
        self.fail_count = 0
        self.ui.right_panel.update_record_count(self.success_count, self.fail_count)
        self.is_compact_mode = False
        self.normal_window_size = self.size()  # 保存初始正常窗口大小
        
        # 绑定快捷键
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.paste_image_from_clipboard)
        
        # 加载测试配置（仅用于开发调试）
        if TEST_CONFIG.app_id and TEST_CONFIG.app_secret:
            self.ui.right_panel.set_app_config(TEST_CONFIG.app_id, TEST_CONFIG.app_secret)
        
        # 定时器用于检测超时
        self.timeout_timer = None
        
    def _set_test_config(self):
        """设置测试配置 - 提交前记得删除！"""
        if TEST_CONFIG.app_id and TEST_CONFIG.app_secret:
            self.ui.right_panel.set_app_config(TEST_CONFIG.app_id, TEST_CONFIG.app_secret)
            if TEST_CONFIG.endpoint_choice == "turbo":
                self.ui.right_panel.turbo_radio.setChecked(True)
            else:
                self.ui.right_panel.standard_radio.setChecked(True)
        
    def on_screenshot_shortcut_changed(self, shortcut):
        """截图快捷键变化处理"""
        self.current_screenshot_method = shortcut
        
    def toggle_compact_mode(self, checked):
        """切换精简模式 - 只显示图片识别框"""
        self.is_compact_mode = checked
        if self.is_compact_mode:
            # 保存当前正常窗口大小
            self.normal_window_size = self.size()
            
            self.ui.right_panel.compact_mode_btn.setText("完整模式")
            # 隐藏左侧面板和API配置区域，只显示图片识别框
            self.ui.left_panel.hide()
            self.ui.right_panel.config_panel.hide()
            self.ui.right_panel.latex_panel.hide()
            
            # 强制重新计算图片识别框的尺寸
            self.ui.right_panel.buttons_panel.setVisible(True)
            self.ui.right_panel.buttons_panel.adjustSize()
            
            # 获取图片识别框的实际尺寸
            buttons_rect = self.ui.right_panel.buttons_panel.rect()
            buttons_width = self.ui.right_panel.buttons_panel.sizeHint().width()
            buttons_height = self.ui.right_panel.buttons_panel.sizeHint().height()
            
            # 设置窗口大小为刚好包含图片识别框，添加少量边距
            window_width = max(buttons_width + 40, 300)  # 最小宽度300
            window_height = buttons_height + 80  # 添加标题栏和边距
            
            self.resize(window_width, window_height)
            self.adjustSize()
            
        else:
            self.ui.right_panel.compact_mode_btn.setText("精简模式")
            # 显示所有面板
            self.ui.left_panel.show()
            self.ui.right_panel.config_panel.show()
            self.ui.right_panel.latex_panel.show()
            # 恢复之前保存的窗口大小
            self.resize(self.normal_window_size)
        
    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;所有文件 (*.*)"
        )

        if file_path:
            self.selected_image_path = file_path
            # 显示原图在上方区域
            self.image_handler.display_original_image(file_path, self.ui.left_panel)
            self.ui.right_panel.clear_result_text()
            self.ui.right_panel.show_processing_message()
            
            # 自动执行识别
            self.auto_recognize_formula()

    def paste_image_from_clipboard(self):
        """从剪贴板粘贴图片"""
        from PIL import ImageGrab
        
        try:
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.image_handler.display_original_image(temp_path, self.ui.left_panel)
                self.ui.right_panel.clear_result_text()
                self.ui.right_panel.show_processing_message()
                self.auto_recognize_formula()
            else:
                # 根据项目规范，剪贴板无图片时静默返回，不弹窗警告
                return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"从剪贴板读取图片失败: {str(e)}")

    def start_clipboard_monitoring(self):
        """启动剪贴板变化监听 - 立即开始检查"""
        # 记录当前剪贴板的图片内容（不仅仅是是否有图片）
        try:
            from PIL import ImageGrab
            current_image = ImageGrab.grabclipboard()
            if current_image is not None:
                # 将图片转换为可比较的形式（使用临时文件路径或哈希）
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                current_image.save(temp_path, 'PNG')
                self.clipboard_baseline_path = temp_path
                self.clipboard_has_baseline = True
            else:
                self.clipboard_baseline_path = None
                self.clipboard_has_baseline = False
        except:
            self.clipboard_baseline_path = None
            self.clipboard_has_baseline = False
            
        self.is_waiting_for_screenshot = True
        # 立即开始检查（不等待）
        self.check_clipboard_for_changes()
        
    def check_clipboard_for_changes(self):
        """检查剪贴板是否发生变化 - 改进的比较逻辑"""
        if not self.is_waiting_for_screenshot:
            return
            
        try:
            from PIL import ImageGrab
            current_image = ImageGrab.grabclipboard()
            
            # 检查是否有新图片
            if current_image is not None:
                # 有图片，检查是否与基准不同
                if not self.clipboard_has_baseline:
                    # 之前没有图片，现在有图片 -> 新截图
                    self.process_new_screenshot(current_image)
                    return
                else:
                    # 之前有图片，需要比较是否相同
                    # 简单方案：直接处理（因为区域截图通常会产生新内容）
                    self.process_new_screenshot(current_image)
                    return
            else:
                # 当前没有图片
                if self.clipboard_has_baseline:
                    # 之前有图片，现在没有 -> 剪贴板被清空
                    # 更新基准状态
                    self.clipboard_has_baseline = False
                    if hasattr(self, 'clipboard_baseline_path') and self.clipboard_baseline_path:
                        try:
                            os.remove(self.clipboard_baseline_path)
                        except:
                            pass
                        self.clipboard_baseline_path = None
                
            # 继续监听（延长到30秒，每100ms检查一次，共300次）
            if not hasattr(self, 'clipboard_check_count'):
                self.clipboard_check_count = 0
                
            self.clipboard_check_count += 1
            
            # 监听30秒（300次检查，每次100ms）
            if self.clipboard_check_count <= 300:
                QTimer.singleShot(100, self.check_clipboard_for_changes)
            else:
                # 超时，停止监听
                self.cleanup_clipboard_monitoring()
                
        except Exception as e:
            # 只在真正出错时才显示错误
            self.cleanup_clipboard_monitoring()
            self.fail_count += 1
            self.ui.right_panel.update_record_count(self.success_count, self.fail_count)
            self.ui.right_panel.show_error("截图处理失败", str(e))
            
    def process_new_screenshot(self, image):
        """处理新的截图"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
            image.save(temp_path, 'PNG')
            self.selected_image_path = temp_path
            self.image_handler.display_original_image(temp_path, self.ui.left_panel)
            self.ui.right_panel.clear_result_text()
            self.ui.right_panel.show_processing_message()
            self.auto_recognize_formula()
            
            # 更新基准状态为当前图片
            self.clipboard_has_baseline = True
            self.clipboard_baseline_path = temp_path
            
        except Exception as e:
            self.ui.right_panel.show_error("处理截图失败", str(e))
            
    def cleanup_clipboard_monitoring(self):
        """清理剪贴板监听资源"""
        self.is_waiting_for_screenshot = False
        if hasattr(self, 'clipboard_check_count'):
            delattr(self, 'clipboard_check_count')
        # 清理临时文件
        if hasattr(self, 'clipboard_baseline_path') and self.clipboard_baseline_path:
            try:
                os.remove(self.clipboard_baseline_path)
            except:
                pass
            self.clipboard_baseline_path = None
            
    def check_clipboard_for_screenshot(self):
        """保留原有方法以避免引用错误"""
        self.check_clipboard_for_changes()
        
    def take_screenshot(self):
        """截图功能 - 触发系统区域截图快捷键"""
        screenshot_method = self.ui.right_panel.get_current_screenshot_shortcut()
        
        if screenshot_method == "printscreen":
            # 对于PrintScreen，触发Win+Shift+S（Windows区域截图）
            self.trigger_win_shift_s()
        elif screenshot_method == "ctrl+c":
            self.trigger_ctrl_c_keys()
        else:
            # 自定义快捷键
            self.trigger_custom_shortcut(screenshot_method)
            
    def trigger_win_shift_s(self):
        """触发 Windows 区域截图快捷键 Win+Shift+S"""
        try:
            keyboard = Controller()
            # 按下 Win+Shift+S
            keyboard.press(Key.cmd)
            keyboard.press(Key.shift)
            keyboard.press('s')
            keyboard.release('s')
            keyboard.release(Key.shift)
            keyboard.release(Key.cmd)
            
            # 启动剪贴板监听
            self.start_clipboard_monitoring()
            
        except ImportError:
            # 如果没有 pynput，提示用户手动截图
            self.is_waiting_for_screenshot = True
            QMessageBox.information(self, "区域截图", "请按 Win+Shift+S 进行区域截图")
            QTimer.singleShot(100, self.check_clipboard_for_screenshot)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发区域截图失败：{str(e)}")
            
    def trigger_ctrl_c_keys(self):
        """触发 Ctrl+C 组合键 - 仍然使用剪贴板方式"""
        try:
            keyboard = Controller()
            keyboard.press(Key.ctrl)
            keyboard.press('c')
            keyboard.release('c')
            keyboard.release(Key.ctrl)
            # 对于Ctrl+C，仍然需要监听剪贴板
            self.paste_image_from_clipboard()
        except ImportError:
            # 如果没有 pynput，回退到原来的逻辑
            self.fallback_ctrl_c_logic()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发 Ctrl+C 失败：{str(e)}")
            
    def trigger_custom_shortcut(self, shortcut_str):
        """触发自定义快捷键"""
        if Controller is None or Key is None:
            QMessageBox.warning(self, "警告", "缺少 pynput 库，无法触发自定义快捷键。\n请安装：pip install pynput")
            return
            
        try:
            keyboard = Controller()
            keys = shortcut_str.split('+')
            pressed_keys = []
            
            # 按下所有键
            for key in keys:
                key_lower = key.lower()
                if key_lower == 'ctrl':
                    keyboard.press(Key.ctrl)
                    pressed_keys.append(Key.ctrl)
                elif key_lower == 'alt':
                    keyboard.press(Key.alt)
                    pressed_keys.append(Key.alt)
                elif key_lower == 'shift':
                    keyboard.press(Key.shift)
                    pressed_keys.append(Key.shift)
                elif key_lower == 'meta':
                    keyboard.press(Key.cmd)
                    pressed_keys.append(Key.cmd)
                else:
                    # 普通字符键
                    keyboard.press(key.lower())
                    pressed_keys.append(key.lower())
                    
            # 释放所有键（反向顺序）
            for key in reversed(pressed_keys):
                keyboard.release(key)
                
            # 触发后启动剪贴板监听
            self.start_clipboard_monitoring()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发自定义快捷键失败：{str(e)}")
            
    def stop_timeout_timer(self):
        """停止超时定时器 - 现在为空方法"""
        pass
        
    def start_timeout_timer(self):
        """启动超时定时器 - 现在为空方法"""
        pass
        
    def on_timeout(self):
        """超时处理"""
        self.is_waiting_for_screenshot = False
        self.timeout_timer = None
        self.fail_count += 1
        self.ui.right_panel.update_record_count(self.success_count, self.fail_count)
        self.ui.right_panel.show_error("截图超时", "5秒内未检测到剪贴板中的图片")
        
    def retry_recognition(self):
        """重试识别功能 - 永远激活，无提示"""
        if not self.selected_image_path:
            # 没有图片时直接返回，不显示任何提示
            return
            
        self.ui.right_panel.clear_result_text()
        self.ui.right_panel.show_processing_message()
        self.auto_recognize_formula()

    def auto_recognize_formula(self):
        """自动执行公式识别"""
        if not self.selected_image_path:
            return

        # 获取API配置
        app_id = self.ui.right_panel.get_app_id()
        app_secret = self.ui.right_panel.get_app_secret()

        if not app_id or not app_secret:
            self.ui.right_panel.clear_result_text()
            self.ui.right_panel.show_config_prompt()
            return

        try:
            # 调用API
            result = self.api_client.recognize_formula_api(
                self.selected_image_path, app_id, app_secret, self.ui.right_panel.get_endpoint_choice()
            )

            if "error" in result:
                self.ui.right_panel.clear_result_text()
                self.ui.right_panel.show_error(result['error'], result.get('details', ''))
                self.fail_count += 1
                self.ui.right_panel.update_record_count(self.success_count, self.fail_count)
            else:
                # 成功识别，显示结果
                self.ui.right_panel.clear_result_text()
                self.ui.right_panel.show_success_result(result)
                
                # 在下方区域显示识别结果
                if "res" in result and "latex" in result["res"]:
                    latex_formula = result["res"]["latex"]
                    self.image_handler.display_result_visualization(latex_formula, self.ui.left_panel)
                    
                    # 提取置信度并设置
                    confidence = 0.0
                    # 检查所有可能的置信度字段，包括SimpleTex API的实际字段名
                    res_data = result["res"]
                    if "conf" in res_data:  # SimpleTex API 使用 conf 字段
                        confidence = float(res_data["conf"])
                    elif "confidence" in res_data:
                        confidence = float(res_data["confidence"])
                    elif "score" in res_data:
                        confidence = float(res_data["score"])
                    elif "prob" in res_data:
                        confidence = float(res_data["prob"])
                    elif "accuracy" in res_data:
                        confidence = float(res_data["accuracy"])
                    # 确保置信度在0-1范围内
                    confidence = max(0.0, min(1.0, confidence))
                    
                    # 设置置信度显示
                    self.ui.right_panel.set_confidence(confidence)
                    
                    # 自动复制到剪贴板
                    pyperclip.copy(latex_formula)
                    
                    # 增加成功计数
                    self.success_count += 1
                    self.ui.right_panel.update_record_count(self.success_count, self.fail_count)

        except Exception as e:
            self.ui.right_panel.clear_result_text()
            self.ui.right_panel.show_error(f"识别过程中发生错误: {str(e)}", "")
            self.fail_count += 1
            self.ui.right_panel.update_record_count(self.success_count, self.fail_count)


def main():
    """主函数"""
    # 根据项目规范，启动时严禁在控制台打印任何使用说明或状态信息
    # 所有启动提示已在 GUI 界面中显示
    
    try:
        app = QApplication(sys.argv)
        window = FormulaRecognizer()
        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        # 依赖错误仍然需要在控制台显示，因为此时 GUI 可能无法启动
        print(f"缺少必要的依赖包: {e}")
        print("请安装以下依赖:")
        print("pip install PyQt6 requests pillow pyperclip")
        sys.stdout.flush()
    except Exception as e:
        import traceback
        print(f"程序启动失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        sys.stdout.flush()


if __name__ == "__main__":
    main()