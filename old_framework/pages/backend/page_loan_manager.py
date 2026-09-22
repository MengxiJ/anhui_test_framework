import time
from selenium.webdriver.common.by import By
from base.page_base import BasePage


class LoanManagerPage(BasePage):
    """额度审核页面 - 管理员审核借款额度功能"""

    __wait_time = 1

    __loan = (By.LINK_TEXT, "借款管理")
    __limit = (By.XPATH, '//span[text()="额度管理"]')
    __app_review = (By.LINK_TEXT, "额度申请审核")
    __frame1 = (By.ID, "iframe_box")
    __username = (By.NAME, "member_name")
    __search_btn = (By.CSS_SELECTOR, '[value="搜索"]')
    __record = (By.XPATH, "//tbody/tr[1]/td[2]/span")
    __approve = (By.XPATH, '//span[text()="审核"]')
    __frame2 = (By.CSS_SELECTOR, "#xubox_iframe1")
    __radio = (By.CSS_SELECTOR, ".ace.ng-pristine.ng-untouched.ng-valid")
    __note = (By.CSS_SELECTOR, "tr:nth-child(6) > td:nth-child(2) > div > textarea")
    __img_code = (By.NAME, "valicode")
    __save = (By.CSS_SELECTOR, ".dybtn.dybtn-save")
    __app_rec = (By.LINK_TEXT, "额度申请记录")
    __app_status = (By.CSS_SELECTOR, "select[name='status']")
    __success_text = (By.XPATH, "//tbody/tr[1]/td[7]/span")
    __fail_text = (By.XPATH, "//*[@id='xubox_layer1']/div[1]/div/em")

    def __init__(self, driver):
        """初始化额度审核页面"""
        super().__init__(driver)

    def click_menu_manage(self):
        """点击管理菜单"""
        self.base_click(self.__loan)
        self.base_click(self.__limit)
        self.base_click(self.__app_review)

    def search_record(self, phone):
        """搜索申请记录"""
        self.base_switch_frame(self.__frame1)
        self.base_input(self.__username, phone)
        self.base_click(self.__search_btn)

    def click_record(self):
        """点击选中记录"""
        time.sleep(self.__wait_time)
        self.base_click(self.__record)
        self.base_click(self.__approve)

    def approve_loan(self, note="审核OK", img_code="8888"):
        """执行审核操作"""
        self.base_switch_frame(self.__frame2)
        self.base_click_special(self.__radio)
        self.base_input(self.__note, note)
        self.base_input(self.__img_code, img_code)
        self.base_click(self.__save)

    def click_app_rec(self, phone, status="通过"):
        """点击申请记录并搜索"""
        self.base_default_frame()
        self.base_click(self.__app_rec)
        self.base_switch_frame(self.__frame1)
        self.base_input(self.__username, phone)
        self.base_select_list(self.__app_status, status)
        self.base_click(self.__search_btn)

    def get_result_success_text(self):
        """获取审核成功结果文本"""
        time.sleep(self.__wait_time)
        return self.fd_element(self.__success_text).text

    def get_result_fail_text(self):
        """获取审核失败结果文本"""
        time.sleep(self.__wait_time)
        self.base_switch_frame(self.__frame2)
        return self.fd_element(self.__fail_text).text

    def credit_application_review(self, phone, note="审核OK", img_code="8888"):
        """执行额度申请审核操作"""
        self.click_menu_manage()
        self.search_record(phone)
        self.click_record()
        self.approve_loan(note, img_code)