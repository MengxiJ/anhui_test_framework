# Copyright (C) 2026. All rights reserved.
"""Lib 业务层（按业务域组织）。

分层对应实习公司原子化框架规范：

- ``lib/common/<domain>/*_step.py`` / ``*_check.py``：Lib 入口层，对外提供
  ``step_xxx`` / ``check_xxx`` 纯函数，**仅本层允许使用 instance_manager**；
- ``lib/common/<domain>/utils/*_manager.py``：Lib 核心层，普通业务类，
  类内不做单例，生命周期由入口层托管；
- ``tblocks/step_impl`` 与 ``tblocks/check_impl`` 仅做薄封装并调用本层。

本项目业务域：

- ``core``：不依赖外部资源的通用原子能力（等待、日志、数值/文本比对）；
- ``browser``：浏览器通用操作（打开 URL、输入、点击、切换 frame 等）；
- ``member``：安汇智投前台会员（登录、注册、开户、额度申请）；
- ``account``：资金账户接口域（基于 LoginRegisterAPI 的登录/实名/开户/充值/投资）；
- ``portal``：门户公共只读接口域（标的列表、平台统计、公告文章、债权转让、体验标、筛选枚举）；
- ``backend``：运营后台（管理员登录、额度审核）；
- ``framework``：跨步骤共享实例的集中封装（step_singletons）。
"""
