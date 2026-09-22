#!/usr/bin/env python
# Copyright (C) 2026. All rights reserved.
"""设备管理器 CLI（本项目“设备”=浏览器 / HTTP 通道）。

子命令：

    acquire-browser   创建（或复用）Chrome 浏览器实例并缓存
    release-browser   释放浏览器实例
    acquire-api       创建（或复用）HTTP 客户端
    status            查看当前托管实例
    reset             释放全部实例

多实例通过字符串 key 隔离：``browser:<device_id>``、``api_client:<device_id>``。
"""
from __future__ import annotations

import argparse
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 无条件置顶：脚本直跑时脚本目录（tblocks/）会遮蔽项目根的同名顶层包
# （tblocks/tools 与项目根 tools/），项目根必须排在最前。
sys.path.insert(0, _PROJECT_ROOT)

from tblocks.utils.instance_manager import (  # noqa: E402
    clear_instance,
    initialize_instances,
    reset_instances,
)
from lib.common.framework import step_singletons  # noqa: E402
from lib.core import instance_manager  # noqa: E402


def cmd_acquire_browser(args) -> int:
    initialize_instances()
    driver = step_singletons.get_browser(args.device_id, headless=args.headless)
    print(f"浏览器实例已就绪: key={step_singletons.browser_key(args.device_id)}")
    if args.url:
        driver.get(args.url)
        print(f"已打开: {args.url}")
    return 0


def cmd_release_browser(args) -> int:
    step_singletons.clear_browser(args.device_id)
    print(f"浏览器实例已释放: {step_singletons.browser_key(args.device_id)}")
    return 0


def cmd_acquire_api(args) -> int:
    initialize_instances()
    client = step_singletons.get_api_client(args.device_id)
    print(f"HTTP 客户端已就绪: key={step_singletons.api_client_key(args.device_id)}, base={client.base_url}")
    return 0


def cmd_status(_args) -> int:
    keys = instance_manager.instance_manager.keys()
    if not keys:
        print("当前无托管实例")
        return 0
    print("当前托管实例：")
    for key in keys:
        print(f"  - {key}")
    return 0


def cmd_reset(_args) -> int:
    reset_instances()
    print("全部实例已释放")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="原子化框架设备管理器")
    parser.add_argument("--device-id", default=None, help="逻辑设备 ID（默认 default）")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("acquire-browser", help="创建/复用浏览器实例")
    p.add_argument("--headless", action="store_true", help="无头模式（或设置 TBLOCKS_HEADLESS=1）")
    p.add_argument("--url", default=None, help="创建后打开的 URL")
    p.set_defaults(func=cmd_acquire_browser)

    p = sub.add_parser("release-browser", help="释放浏览器实例")
    p.set_defaults(func=cmd_release_browser)

    p = sub.add_parser("acquire-api", help="创建/复用 HTTP 客户端")
    p.set_defaults(func=cmd_acquire_api)

    p = sub.add_parser("status", help="查看托管实例")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("reset", help="释放全部实例")
    p.set_defaults(func=cmd_reset)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.device_id:
        os.environ["TBLOCKS_DEVICE_ID"] = args.device_id
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
