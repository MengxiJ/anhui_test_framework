import os
import subprocess


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


if __name__ == "__main__":
    serve_report()
