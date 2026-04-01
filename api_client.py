import requests
import hashlib
import time
import random
import string


class FormulaAPIClient:
    def __init__(self):
        pass

    def generate_random_string(self, length=16):
        """生成16位随机字符串"""
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def generate_signature(self, data, app_secret):
        """生成签名"""
        # 将data中的key按字母顺序排序
        sorted_keys = sorted(data.keys())
        # 构建待签名字符串
        sign_string = "&".join([f"{key}={data[key]}" for key in sorted_keys])
        # 添加secret
        sign_string += f"&secret={app_secret}"
        # MD5签名
        md5_hash = hashlib.md5(sign_string.encode("utf-8")).hexdigest()

        return md5_hash

    def recognize_formula_api(
        self, image_path, app_id, app_secret, endpoint_choice="standard"
    ):
        """调用公式识别API"""
        try:
            # 准备请求数据
            timestamp = str(int(time.time()))
            random_str = self.generate_random_string()

            # 表单数据（只包含业务参数）
            form_data = {"use_batch": "False"}

            # 用于签名的数据（包含所有参数：业务参数 + 鉴权参数）
            # 注意：这里必须包含所有要参与签名的参数
            sign_data = {
                "app-id": app_id,
                "random-str": random_str,
                "timestamp": timestamp,
                "use_batch": "False",
            }

            # 生成签名
            signature = self.generate_signature(sign_data, app_secret)

            # 准备headers
            headers = {
                "app-id": app_id,
                "random-str": random_str,
                "timestamp": timestamp,
                "sign": signature,
            }

            # 准备文件和表单数据
            with open(image_path, "rb") as f:
                files = {"file": f}
                # 根据选择的端口类型确定API URL
                if endpoint_choice == "turbo":
                    url = "https://server.simpletex.cn/api/latex_ocr_turbo"
                else:
                    url = "https://server.simpletex.cn/api/latex_ocr"
                response = requests.post(
                    url, headers=headers, data=form_data, files=files, timeout=30
                )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API请求失败，状态码: {response.status_code}",
                    "details": response.text,
                }

        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
