#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能测试运行脚本
使用JMeter进行API性能测试
"""
import os
import sys
import subprocess
import argparse
import time
from datetime import datetime


def find_jmeter():
    """查找JMeter可执行文件"""
    common_paths = [
        r"D:\Program_Files\Jmeter\apache-jmeter-5.6.3\bin\jmeter.bat",
        r"D:\Program_Files\Jmeter\apache-jmeter-5.6.3\bin\jmeter",
        "jmeter.bat",
        "jmeter",
        r"C:\Program Files\Apache Software Foundation\jmeter\bin\jmeter.bat",
        r"C:\Program Files\apache-jmeter-5.6.3\bin\jmeter.bat",
        r"C:\apache-jmeter-5.6.3\bin\jmeter.bat",
        os.path.join(os.getcwd(), "jmeter.bat"),
        os.path.join(os.getcwd(), "jmeter"),
    ]

    if "PATH" in os.environ:
        for path in os.environ["PATH"].split(os.pathsep):
            if path:
                jmeter_path = os.path.join(path, "jmeter.bat")
                if os.path.exists(jmeter_path):
                    return jmeter_path
                jmeter_path = os.path.join(path, "jmeter")
                if os.path.exists(jmeter_path):
                    return jmeter_path

    for path in common_paths:
        if os.path.exists(path):
            return path

    return "jmeter"


def check_jmeter():
    """检查JMeter是否安装"""
    jmeter_cmd = find_jmeter()
    try:
        result = subprocess.run([jmeter_cmd, "--version"], capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
        print("[OK] JMeter检测到")
        print(f"命令: {jmeter_cmd}")
        print(output)
        return True
    except Exception as e:
        print(f"[WARN] JMeter检查失败: {e}")
        print("请确保JMeter已正确安装并配置到环境变量PATH中")
        print("或者直接使用 jmeter 命令手动运行测试")
        return False


def run_performance_test(jmx_file, output_dir="output/performance"):
    """运行性能测试"""
    if not os.path.exists(jmx_file):
        print(f"❌ 测试计划文件不存在: {jmx_file}")
        return 1

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(output_dir, f"result_{timestamp}.jtl")
    report_dir = os.path.join(output_dir, f"report_{timestamp}")

    jmeter_cmd = find_jmeter()

    print(f"\n{'='*60}")
    print(f"开始性能测试")
    print(f"测试计划: {jmx_file}")
    print(f"JMeter命令: {jmeter_cmd}")
    print(f"结果文件: {result_file}")
    print(f"报告目录: {report_dir}")
    print(f"{'='*60}\n")

    cmd = [
        jmeter_cmd,
        "-n",
        "-t",
        jmx_file,
        "-l",
        result_file,
        "-e",
        "-o",
        report_dir,
    ]

    start_time = time.time()
    result = subprocess.run(cmd)
    end_time = time.time()

    if result.returncode == 0:
        print(f"\n[OK] 性能测试完成！")
        print(f"执行时间: {end_time - start_time:.2f}秒")
        report_html = os.path.join(report_dir, "index.html")
        print(f"测试报告: {report_html}")
        
        # 自动打开报告
        print(f"正在打开报告...")
        if sys.platform == "win32":
            os.startfile(report_html)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", report_html])
        else:  # Linux
            subprocess.run(["xdg-open", report_html])
            
        return 0
    else:
        print(f"\n[FAIL] 性能测试失败！")
        return 1


def find_latest_result(output_dir="output/performance"):
    """查找最新的结果文件"""
    if not os.path.exists(output_dir):
        return None
    
    jtl_files = []
    for file in os.listdir(output_dir):
        if file.startswith("result_") and file.endswith(".jtl"):
            file_path = os.path.join(output_dir, file)
            jtl_files.append((os.path.getmtime(file_path), file_path))
    
    if not jtl_files:
        return None
    
    jtl_files.sort(reverse=True, key=lambda x: x[0])
    return jtl_files[0][1]


def generate_report(result_file, report_dir):
    """生成性能测试报告"""
    if not os.path.exists(result_file):
        print(f"[FAIL] 结果文件不存在: {result_file}")
        return 1

    os.makedirs(report_dir, exist_ok=True)

    jmeter_cmd = find_jmeter()

    print(f"\n生成性能测试报告...")
    print(f"结果文件: {result_file}")
    print(f"报告目录: {report_dir}")
    cmd = [jmeter_cmd, "-g", result_file, "-o", report_dir]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        report_html = os.path.join(report_dir, "index.html")
        print(f"[OK] 报告生成成功: {report_html}")
        
        # 自动打开报告
        print(f"正在打开报告...")
        if sys.platform == "win32":
            os.startfile(report_html)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", report_html])
        else:  # Linux
            subprocess.run(["xdg-open", report_html])
            
        return 0
    else:
        print(f"[FAIL] 报告生成失败！")
        return 1


def main():
    parser = argparse.ArgumentParser(description="性能测试运行脚本")
    parser.add_argument("--check", action="store_true", help="检查JMeter是否安装")
    parser.add_argument("--run", action="store_true", help="运行性能测试")
    parser.add_argument(
        "--jmx", type=str, default="performance/performance_test.jmx", help="JMeter测试计划文件路径"
    )
    parser.add_argument("--output", type=str, default="output/performance", help="结果输出目录")
    parser.add_argument("--report", type=str, nargs="?", const="latest", help="从结果文件生成报告（不传参数则使用最新结果）")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        print("\n示例:")
        print("  python tools/run_performance.py --check              # 检查JMeter安装")
        print("  python tools/run_performance.py --run                # 运行性能测试")
        print("  python tools/run_performance.py --run --jmx test.jmx # 指定测试计划")
        print("  python tools/run_performance.py --report             # 生成最新结果的报告")
        print("  python tools/run_performance.py --report result.jtl  # 生成指定结果的报告")
        return 0

    if args.check:
        check_jmeter()
        return 0

    if args.run:
        return run_performance_test(args.jmx, args.output)

    if args.report:
        if args.report == "latest":
            result_file = find_latest_result(args.output)
            if not result_file:
                print("[FAIL] 找不到结果文件，请先运行测试: python tools/run_performance.py --run")
                return 1
            print(f"[OK] 找到最新结果文件: {result_file}")
        else:
            result_file = args.report
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = f"output/performance/report_{timestamp}"
        return generate_report(result_file, report_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
