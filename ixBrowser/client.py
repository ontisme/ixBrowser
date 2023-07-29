import time
import winreg
from typing import Union

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
                # 如果是[{"data": ...}, {"data": ...}]，則遞歸處理每個元素，只返回最後一個
                return get_deepest_data(data_obj[-1])
            else:
                # 如果既不是字典也不是列表，則返回None
                return None

        result = {}

        # 檢查是否有"error"和"data"鍵
        if "error" in response and "data" in response:
            # 檢查error code是否為0
            if response["error"]["code"] == 0:
                result["result"] = True

            # 將原始的"data"內容放入新的"data"字典中
            result["data"] = response["data"]

            # 遞歸處理"data"，如果有更底層的"data"，則覆蓋之前的"data"
            deepest_data = get_deepest_data(response["data"])
            if deepest_data is not None:
                result["data"] = deepest_data

        return result

    def api_browser_list(self, page: int = 1, limit: int = 1000, group_id: int = 0, name: str = ""):
        """
        取得ixBrowser的瀏覽器列表
        """
        params = {
            "page": page,
            "limit": limit,
            "group_id": group_id,
            "name": name
        }
        return self.__api_response(self.ses.post(self.ixbrowser_api_host + "browser-list", json=params).json())

    def api_browser_open(self, profile_id: int, args: list = None, load_extensions: bool = False,
                         load_default_page: bool = False):
        """
        開啟ixBrowser

        :param profile_id:  Profile的ID
        :param args:    開啟ixBrowser的參數
        :param load_extensions: 是否載入ixBrowser的擴充套件
        :param load_default_page: 是否載入ixBrowser的預設頁面
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

    def api_browser_close(self, profile_id: Union[int, list]):
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


if __name__ == '__main__':
    ixbrowser = IxBrowser()
    ixbrowser.get_ixbrowser_info()
