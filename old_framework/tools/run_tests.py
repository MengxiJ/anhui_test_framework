#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化测试运行脚本
支持运行API测试、UI测试、生成报告
"""
import os
import sys
import subprocess
import argparse
import glob


def run_command(cmd, description):
    """运行命令并打印输出"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, shell=False)
    return result.returncode


def run_api_tests(parallel=False):
    """运行API测试"""
    cmd = ["pytest", "-v", "--alluredir=output/allure/results", "--clean-alluredir"]
    api_files = glob.glob(os.path.join("scripts", "test_api_*.py"))
    if not api_files:
        print("未找到API测试文件")
        return 1
    cmd.extend(api_files)
    if parallel:
        cmd.extend(["-n", "auto"])
    return run_command(cmd, "API自动化测试")


def run_ui_tests():
    """运行UI测试"""
    cmd = ["pytest", "-v", "--alluredir=output/allure/results-ui", "--clean-alluredir"]
    ui_files = glob.glob(os.path.join("scripts", "test_0*.py"))
    if not ui_files:
        print("未找到UI测试文件")
        return 1
    cmd.extend(ui_files)
    return run_command(cmd, "UI自动化测试")


def run_all_tests(parallel=False):
    """运行所有测试"""
    cmd = ["pytest", "scripts/", "-v", "--alluredir=output/allure/results", "--clean-alluredir"]
    if parallel:
        cmd.extend(["-n", "auto"])
    return run_command(cmd, "所有自动化测试")


def get_allure_cmd():
    """获取正确的Allure命令（Windows上用allure.bat）"""
    import platform
    if platform.system() == "Windows":
        possible_cmds = ["allure.bat", "allure"]
    else:
        possible_cmds = ["allure"]

    for cmd in possible_cmds:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


def serve_report(results_dir="output/allure/results"):
    """自动生成并打开Allure报告（allure serve）"""
    allure_cmd = get_allure_cmd()
    if not allure_cmd:
        print("Allure未安装或未添加到PATH")
        print("\n安装步骤:")
        print("1. 下载: https://github.com/allure-framework/allure2/releases")
        print("2. 解压到某个目录（如: C:\\Program Files\\allure-2.20.0）")
        print("3. 将 bin 目录添加到系统 PATH 环境变量")
        print("4. 重启终端/IDE")
        return 1

    if not os.path.exists(results_dir):
        print(f"测试结果目录不存在: {results_dir}")
        return 1

    print(f"正在生成并打开Allure报告...")
    print(f"结果目录: {results_dir}")
    print("按 Ctrl+C 可关闭服务器\n")
    cmd = [allure_cmd, "serve", results_dir]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n报告服务器已关闭")
    return 0


def main():
    parser = argparse.ArgumentParser(description="自动化测试运行脚本")
    parser.add_argument("--api", action="store_true", help="只运行API测试")
    parser.add_argument("--ui", action="store_true", help="只运行UI测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--serve", action="store_true", help="自动生成并打开Allure报告")
    parser.add_argument("--parallel", action="store_true", help="并行运行测试")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        print("\n示例:")
        print("  python tools/run_tests.py --api             # 运行API测试")
        print("  python tools/run_tests.py --ui              # 运行UI测试")
        print("  python tools/run_tests.py --all             # 运行所有测试")
        print("  python tools/run_tests.py --serve           # 自动生成并打开报告")
        print("  python tools/run_tests.py --api --serve     # 运行API测试并打开报告")
        print("  python tools/run_tests.py --all --parallel  # 并行运行所有测试")
        return 0

    exit_code = 0

    # 运行测试
    if args.api:
        exit_code = run_api_tests(args.parallel)
    elif args.ui:
        exit_code = run_ui_tests()
    elif args.all:
        exit_code = run_all_tests(args.parallel)

    # 生成报告
    if args.serve:
        results_dir = "output/allure/results" if not args.ui else "output/allure/results-ui"
        exit_code = serve_report(results_dir)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
