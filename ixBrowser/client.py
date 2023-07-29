import random
import time
import uuid
import winreg
from typing import Union, List

import requests
from ixBrowser.utils.use_logger import WrapperRichLogger


class IxBrowser:
    def __init__(self, api_port: int = 53200):
        self.ixbrowser_install_dir: str
        self.ixbrowser_exe_path: str
        self.ixbrowser_version: str
        self.ixbrowser_api_host = f"http://127.0.0.1:{api_port}/api/"
        self.logger = WrapperRichLogger()
        self.ses = requests.Session()
        self.headers = {
            "Content-Type": "application/json"
        }
        self.ses.headers.update(self.headers)
        self.init()

    def init(self):
        """
        初始化
        """

        self.__update_ixbrowser_info()
        if not self.ixbrowser_install_dir:
            raise Exception("未安裝ixBrowser")
        self.logger.bullet("ixBrowser資訊", [
            f"路徑: {self.ixbrowser_install_dir}",
            f"版本: {self.ixbrowser_version}"
        ])
        self.logger.h1("檢查ixBrowser是否在運行")
        self.launch_ixbrowser()
        self.logger.log("ixBrowser已啟動")

    @staticmethod
    def get_ixbrowser_info():
        """
        檢查是否安裝ixBrowser

        :return:    {
                        "name": "ixBrowser",
                        "version": "1.0.0",
                        "install_path": "C:\\Program Files\\ixBrowser\\"
                    }
        """
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
                num_sub_keys = winreg.QueryInfoKey(key)[0]
                for i in range(num_sub_keys):
                    sub_key_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub_key_name) as sub_key:
                        try:
                            name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                            if str(name).startswith("ixBrowser"):
                                version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                                uninstall_string = winreg.QueryValueEx(sub_key, "UninstallString")[0]
                                start_index = uninstall_string.find('"') + 1
                                end_index = uninstall_string.find('"', start_index)
                                install_path = uninstall_string[start_index:end_index].replace(
                                    "Uninstall ixBrowser.exe", "")

                                return {
                                    "name": name,
                                    "version": version,
                                    "install_path": install_path
                                }
                        except FileNotFoundError as e:
                            return {}
        except FileNotFoundError:
            pass

        return False

    def launch_ixbrowser(self):
        """
        啟動ixBrowser
        """
        import subprocess
        count = 0
        while True:
            count += 1
            if count > 5:
                self.logger.error("啟動ixBrowser超時")
                return False
            try:
                # 檢查ixBrowser主程式
                if not self.__check_ixbrowser_app_is_running():
                    subprocess.Popen(self.ixbrowser_exe_path)
                    time.sleep(3)

                # 檢查ixBrowser服務
                if not self.__check_ixbrowser_service_is_running():
                    if self.__check_ixbrowser_app_is_running():
                        self.logger.log("ixBrowser主程式已啟動，等待ixBrowser服務啟動...(可能是沒有登入)")
                        time.sleep(3)
                else:
                    return True

            except Exception:
                self.logger.exception("啟動ixBrowser失敗")
                return False

    @staticmethod
    def close_ixbrowser():
        """
        關閉ixBrowser
        """
        import psutil
        for proc in psutil.process_iter():
            try:
                if proc.name() == "ixBrowser.exe":
                    proc.kill()
            except psutil.NoSuchProcess:
                pass

    def __update_ixbrowser_info(self):
        """
        更新ixBrowser資訊
        """
        ixbrowser_info = self.get_ixbrowser_info()
        if ixbrowser_info:
            self.ixbrowser_install_dir = ixbrowser_info["install_path"]
            self.ixbrowser_version = ixbrowser_info["version"]
            self.ixbrowser_exe_path = self.ixbrowser_install_dir + "ixBrowser.exe"
        else:
            self.ixbrowser_install_dir = ""
            self.ixbrowser_version = ""
            self.ixbrowser_exe_path = ""

    @staticmethod
    def __check_ixbrowser_app_is_running():
        """
        檢查ixBrowser主程式是否正在執行

        :return:    True: ixbrowser正在執行
                    False: ixbrowser沒有執行
        """
        import psutil
        for proc in psutil.process_iter():
            try:
                if proc.name() == "ixBrowser.exe":
                    return True
            except psutil.NoSuchProcess:
                pass
        return False

    def __check_ixbrowser_service_is_running(self):
        """
        檢查ixBrowser服務是否正在執行，或是有沒有登入

        :return:    True: ixbrowser服務正在執行
                    False: ixbrowser服務沒有執行
        """
        res = self.api_browser_list()
        if res["result"]:
            return True
        return False

    def __api_response(self, response):
        """
        API響應處理函數

        :param response: API的響應數據
        :return: 處理後的結果字典
        """

        def get_deepest_data(data_obj):
            """
            遞歸查詢最底層的"data"，返回該"data"字典

            :param data_obj: 要查詢的數據對象，可以是字典或列表
            :return: 最底層的"data"字典或None
            """
            if isinstance(data_obj, dict):
                if "data" in data_obj:
                    # 如果是{"data": {"data": ...}}，則繼續遞歸
                    return get_deepest_data(data_obj["data"])
                else:
                    # 否則直接返回該字典
                    return data_obj
            elif isinstance(data_obj, list):
                # 如果是[{"data": ...}, {"data": ...}]
                return data_obj
            else:
                # 如果既不是字典也不是列表，則返回None
                return None

        # self.logger.log(response)
        result = {}

        # 檢查是否有"error"和"data"鍵
        if "error" in response and "data" in response:
            # 檢查error code是否為0
            if response["error"]["code"] == 0:
                result["result"] = True
            else:
                result["result"] = False
                result["error"] = response["error"]
                return result

            # 將原始的"data"內容放入新的"data"字典中
            result["data"] = response["data"]

            # 遞歸處理"data"，如果有更底層的"data"，則覆蓋之前的"data"
            deepest_data = get_deepest_data(response["data"])
            if deepest_data is not None:
                result["data"] = deepest_data

        return result

    def api_browser_list(self, page: int = 1, limit: int = 1000, group_id: int = 0, name: str = "",
                         include_fields: List[str] = None, exclude_fields: List[str] = None):
        """
        獲取ixBrowser的瀏覽器列表
        :param page:            頁碼
        :param limit:           每頁顯示的數量
        :param group_id:        組ID
        :param name:            瀏覽器名稱
        :param include_fields:  只回傳想要的瀏覽器配置
        :param exclude_fields:  排除不想回傳的瀏覽器配置
        :return:
        """
        params = {
            "page": page,
            "limit": limit,
            "group_id": group_id,
            "name": name
        }

        response = self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-list", json=params).json())

        # 如果有指定的欄位，則將其餘不包含的欄位刪除
        if include_fields is not None:
            for browser in response["data"]:
                for key in list(browser.keys()):
                    if key not in include_fields:
                        del browser[key]

        # 如果有指定要排除的欄位，則將其餘欄位刪除
        if exclude_fields is not None:
            for browser in response["data"]:
                for key in list(browser.keys()):
                    if key in exclude_fields:
                        del browser[key]

        return response

    def api_browser_open(self, profile_id: int, args: list = None, load_extensions: bool = False,
                         load_default_page: bool = False):
        """
        開啟ixBrowser

        :param profile_id:          Profile的ID
        :param args:                開啟ixBrowser的參數
        :param load_extensions:     是否載入ixBrowser的擴充套件
        :param load_default_page:   是否載入ixBrowser的預設頁面
        :return:
        """
        if profile_id < 1:
            raise ValueError("Profile ID 必須大於 0")

        if args is None:
            args = []
        params = {
            "profile_id": profile_id,
            "args": args,
            "load_extensions": load_extensions,
            "load_default_page": load_default_page
        }
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-open", json=params).json())

    def api_browser_close(self, profile_id: Union[int, List[int]]):
        """
        關閉ixBrowser

        profile_id 是int也可以是一個list，關閉多個ixBrowser

        :param profile_id:  profile_id的ID
        :return:
        """
        if isinstance(profile_id, int):
            profile_id = [profile_id]
        params = {
            "profile_id": profile_id
        }
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-close-all", json=params).json())

    def api_browser_cache_clear(self, profile_id: Union[int, List[int]]):
        """
        清除ixBrowser快取

        profile_id 是int也可以是一個list，清除多個ixBrowser的快取

        :param profile_id:  profile_id的ID
        :return: {'result': Bool } 不必關注結果，因為沒有緩存也會回傳False

        """
        if isinstance(profile_id, int):
            profile_id = [profile_id]
        params = {
            "profile_id": profile_id
        }
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-cache-clear", json=params).json())

    def api_browser_create(self, config: dict = None, **kwargs):
        """
        建立ixBrowser

        :param config:
        :param random_config:  是否隨機產生ixBrowser的指紋設定
        :param kwargs:    建立ixBrowser的參數
                        {
                            "color": "#CC9966",
                            "site_url": "http://google.com/",
                            "name": "google",
                            "note": "",
                            "group_id": 1,
                            "username": "",
                            "password": "",
                            "proxy_mode": 2,
                            "proxy_type": "direct",
                            "proxy_ip": "",
                            "proxy_port": "",
                            "proxy_user": "",
                            "proxy_password": "",
                            "cookie": "",
                            "open_url": "",
                            "display_url": "",
                            "proxy_id": "",
                            "config": {
                                "hardware_concurrency": "4",
                                "device_memory": "8",
                                "is_cookies_cache": "1",
                                "is_tabs_cache": "0",
                                "is_proxy_check": "0",
                                "is_proxy_change": false,
                                "ua_type": 1,
                                "platform": "Windows",
                                "br_version": "",
                                "ua_info": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                                "language_type": "1",
                                "language": "cn",
                                "timezone_type": "1",
                                "timezone": "Asia/Shanghai",
                                "location": "1",
                                "location_type": "1",
                                "longitude": 25.7247,
                                "latitude": 119.3712,
                                "accuracy": 1000,
                                "resolving_power_type": "1",
                                "resolving_power": "1920,1080",
                                "fonts_type": "1",
                                "fonts": [],
                                "webrtc": "1",
                                "webgl_image": "1",
                                "canvas_type": "1",
                                "webgl_data_type": "1",
                                "webgl_factory": "Google Inc.",
                                "webgl_info": "ANGLE (AMD, ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0, atiumd64.dll-8.14.10.678)",
                                "audio_context": "1",
                                "media_equipment": "1",
                                "client_rects": "1",
                                "speech_voices": "1",
                                "product_type": "1",
                                "track": "1",
                                "allow_scan_ports": "0",
                                "allow_scan_ports_content": "",
                                "real_ip": "120.36.89.204"
                            }
                        }
        :return:
        """

        def random_color():
            return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        def random_ip_address():
            return ".".join([str(random.randint(0, 255)) for _ in range(4)])

        config = config or {}
        # 隨機顏色

        base_values = {
            "color": random_color(),
            "site_url": "https://google.com/",
            "name": uuid.uuid4().hex[:8], "note": "", "group_id": 1, "username": "", "password": "",
            "proxy_mode": 2, "proxy_type": "direct", "proxy_ip": "", "proxy_port": "", "proxy_user": "",
            "proxy_password": "", "cookie": "", "open_url": "", "display_url": "", "proxy_id": "",
            'config': {
                "hardware_concurrency": "4",
                "device_memory": "8",
                "is_cookies_cache": "1",
                "is_tabs_cache": "0",
                "is_proxy_check": "0",
                "is_proxy_change": False,
                "ua_type": 1,
                "platform": "Windows",
                "br_version": "",
                "ua_info": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                "language_type": "1",
                "language": "cn",
                "timezone_type": "1",
                "timezone": "Asia/Taipei",
                "location": "1",
                "location_type": "1",
                "longitude": 25.7247,
                "latitude": 119.3712,
                "accuracy": 1000,
                "resolving_power_type": "1",
                "resolving_power": "1920,1080",
                "fonts_type": "1",
                "fonts": [],
                "webrtc": "1",
                "webgl_image": "1",
                "canvas_type": "1",
                "webgl_data_type": "1",
                "webgl_factory": "Google Inc.",
                "webgl_info": "ANGLE (AMD, ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0, atiumd64.dll-8.14.10.678)",
                "audio_context": "1",
                "media_equipment": "1",
                "client_rects": "1",
                "speech_voices": "1",
                "product_type": "1",
                "track": "1",
                "allow_scan_ports": "0",
                "allow_scan_ports_content": "",
                "real_ip": random_ip_address()
            }}

        # 使用传入的kwargs参数更新默认值
        base_values.update(config)
        base_values.update(kwargs)
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-create", json=base_values).json())

    def api_browser_update(self, profile_id: int, config: dict = None, **kwargs):
        """
        更新ixBrowser信息

        # TODO 更新尚未完成

        :param profile_id:  ixBrowser的profile_id
        :param config:  Profile配置信息
        :return:
        """
        config = config or {}
        base_values = {
            "profile_id": profile_id,
            "color": "#CC9966",
            "site_url": "http://google.com/",
            "name": uuid.uuid4().hex[:8],
            "note": "",
            "group_id": 1,
            "username": "",
            "password": "",
            "proxy_mode": 2,
            "proxy_type": "direct",
            "proxy_ip": "",
            "proxy_port": "",
            "proxy_user": "",
            "proxy_password": "",
            "cookie": "",
            "open_url": "",
            "display_url": "",
            "proxy_id": "",
        }
        base_values['config'] = {
            "hardware_concurrency": "4",
            "device_memory": "8",
            "is_cookies_cache": "1",
            "is_tabs_cache": "0",
            "is_proxy_check": "0",
            "is_proxy_change": False,
            "ua_type": 1,
            "platform": "Windows",
            "br_version": "",
            "ua_info": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "language_type": "1",
            "language": "cn",
            "timezone_type": "1",
            "timezone": "Asia/Shanghai",
            "location": "1",
            "location_type": "1",
            "longitude": 25.7247,
            "latitude": 119.3712,
            "accuracy": 1000,
            "resolving_power_type": "1",
            "resolving_power": "1920,1080",
            "fonts_type": "1",
            "fonts": [],
            "webrtc": "1",
            "webgl_image": "1",
            "canvas_type": "1",
            "webgl_data_type": "1",
            "webgl_factory": "Google Inc.",
            "webgl_info": "ANGLE (AMD, ATI Radeon HD 4200 Direct3D9Ex vs_3_0 ps_3_0, atiumd64.dll-8.14.10.678)",
            "audio_context": "1",
            "media_equipment": "1",
            "client_rects": "1",
            "speech_voices": "1",
            "product_type": "1",
            "track": "1",
            "allow_scan_ports": "0",
            "allow_scan_ports_content": "",
            "real_ip": "120.36.89.204"
        }
        base_values.update(config)
        base_values.update(kwargs)
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-update", json=base_values).json())

    def api_browser_delete(self, profile_id: Union[int, List[int]]):
        """
        删除ixBrowser

        :param profile_id:  ixBrowser的profile_id
        :return:
        """
        if isinstance(profile_id, int):
            profile_id = [profile_id]
        params = {
            "profile_id": profile_id
        }
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-deleted", json=params).json())

    def api_browser_random_info(self, profile_id: int):
        """
        隨機ixBrowser信息

        :param profile_id:  ixProfile ID
        :return:
        """
        params = {
            "profile_id": profile_id
        }
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "random-browser-info", json=params).json())


if __name__ == '__main__':
    ixbrowser = IxBrowser()
    # print(ixbrowser.api_browser_create())
