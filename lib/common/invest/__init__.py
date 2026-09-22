# Copyright (C) 2026. All rights reserved.
"""invest 域：安汇智投前台理财业务（风险测评、投资列表、标的投标、我的投资、理财巡检入口）。

页面对象：``RiskQuizPage`` / ``InvestListPage`` / ``LoanDetailPage`` / ``MyTenderPage`` /
``InvestPages``（收款计划 / 债权转让 / 自动投标入口）。

站点行为备注（实测）：

- 测评答题页打开时先弹「风险提示」xubox 模态框（内嵌只读 iframe），须先关闭再作答；
  提交成功后整页跳转 ``/risk/answer/introduce``。
- 标的详情页 ``/common/loan/loaninfoview#?id=xx`` 在数据加载后（约 1~2 秒）会被站点
  JS 重定向回投资列表，投标交互须在窗口期内完成并做降级双态判定。
"""
