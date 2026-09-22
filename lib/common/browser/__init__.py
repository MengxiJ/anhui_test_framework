# Copyright (C) 2026. All rights reserved.
"""browser 域：浏览器通用操作。

把项目已有 ``base.page_base.BasePage`` 的等待/输入/点击/切 frame/下拉/截图
能力下沉为可复用的 ``BrowserManager``，供 member / backend 等业务域与
browser 域原子节点共用。
"""
