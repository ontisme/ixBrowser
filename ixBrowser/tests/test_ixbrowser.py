import unittest

from ixBrowser.client import IxBrowser


class TestIxBrowser(unittest.TestCase):
    ixbrowser = IxBrowser()

    def test_9_api_browser_delete(self):
        profile_ids = [x["profile_id"] for x in self.ixbrowser.api_browser_list()["data"]]
        del_id = profile_ids[0] # 刪除最後一個 Profile
        info = self.ixbrowser.api_browser_delete(del_id)
        print("test_api_browser_delete", info)
        self.assertTrue(info["result"])

    def test_8_api_browser_update(self):
        # TODO 更新尚未完成
        info = self.ixbrowser.api_browser_update(1, name="test", config={
            "site_url": "https://www.google.com",
        })
        print("test_api_browser_update", info)
        self.assertTrue(info["result"])

    def test_7_api_browser_create(self):
        info = self.ixbrowser.api_browser_create()
        print("test_api_browser_create", info)
        self.assertTrue(info["result"])

    def test_6_api_browser_cache_clear(self):
        info = self.ixbrowser.api_browser_cache_clear(1)
        print("test_api_browser_cache_clear", info)
        self.assertTrue(info["result"])

    def test_5_api_browser_close(self):
        info = self.ixbrowser.api_browser_close(1)
        print("test_api_browser_close", info)
        self.assertTrue(info["result"])

    def test_4_api_browser_open(self):
        info = self.ixbrowser.api_browser_open(1)
        print("test_api_browser_open", info)
        self.assertTrue(info["result"])

    def test_3_api_browser_list(self):
        info = self.ixbrowser.api_browser_list()
        print("test_api_browser_list", info)
        self.assertTrue(info["result"])

    def test_2_launch_ixbrowser(self):
        info = self.ixbrowser.launch_ixbrowser()
        print("test_launch_ixbrowser", info)
        self.assertTrue(info)

    def test_1_get_ixbrowser_info(self):
        info = self.ixbrowser.get_ixbrowser_info()
        print("test_get_ixbrowser_info", info)

        # 檢查 `info` 字典中是否有 'name' 屬性
        self.assertIn("name", info)
        # 確保 'name' 屬性有值
        self.assertIsNotNone(info["name"])

        # 檢查 `info` 字典中是否有 'version' 屬性
        self.assertIn("version", info)
        # 確保 'version' 屬性有值
        self.assertIsNotNone(info["version"])

        # 檢查 `info` 字典中是否有 'install_path' 屬性
        self.assertIn("install_path", info)
        # 確保 'install_path' 屬性有值
        self.assertIsNotNone(info["install_path"])


if __name__ == '__main__':
    unittest.main()
