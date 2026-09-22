# Copyright (C) 2026. All rights reserved.
"""account 域：资金账户接口业务。

复用项目已有 ``api.login_register_api.LoginRegisterAPI``（继承
``BaseRequest``，自带 Session/重试/超时），覆盖登录、注册、实名认证、
托管开户、充值、投资等接口。业务约定：响应 JSON ``code==200`` 为成功，
``code==100`` 为业务失败。
"""
