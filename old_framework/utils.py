import json
import logging
import os
import re
from logging import handlers


def _get_project_path():
    return os.path.dirname(os.path.abspath(__file__))


OUTPUT_DIR = os.path.join(_get_project_path(), "output")


def read_json(file_name):
    """
    读取JSON文件并转换为格式为 [(), (), ...] 的列表
    支持变量替换：{{VAR_NAME}} -> config.VAR_NAME
    :param file_name: json文件名
    :return: 列表
    """
    import config

    data = []
    file_path = os.path.join(_get_project_path(), "data", file_name)
    with open(file_path, mode="r", encoding="utf-8") as f:
        tmp = json.load(f)
        for i in tmp:
            processed_data = {}
            for key, value in i.items():
                if isinstance(value, str):
                    value = _replace_template_vars(value, config)
                processed_data[key] = value
            a = tuple(processed_data.values())
            data.append(a)
        return data


def _replace_template_vars(value, config):
    """通用模板变量替换：{{VAR_NAME}} -> config.VAR_NAME"""
    def replacer(match):
        var_name = match.group(1)
        attr = getattr(config, var_name, None)
        if attr is not None:
            return str(attr)
        return match.group(0)
    return re.sub(r'\{\{(\w+)\}\}', replacer, value)


class GetLog:
    __log = None

    @classmethod
    def get_log(cls):
        if cls.__log is None:
            cls.__log = logging.getLogger()
            cls.__log.setLevel(logging.INFO)
            log_dir = os.path.join(OUTPUT_DIR, "log")
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, "web.log")
            tf = logging.handlers.TimedRotatingFileHandler(
                filename=filename,
                when="midnight",
                interval=1,
                backupCount=3,
                encoding="utf-8",
            )
            fmt = "%(asctime)s %(levelname)s [%(filename)s(%(funcName)s:%(lineno)d)] - %(message)s"
            fm = logging.Formatter(fmt)
            tf.setFormatter(fm)
            cls.__log.addHandler(tf)
        return cls.__log
