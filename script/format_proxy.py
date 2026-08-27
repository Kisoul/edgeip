from pathlib import Path
import csv
import hashlib
import shutil
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "papapapapdelesia/Emilia/refs/heads/main/Data/alive.txt"
)

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "Data"
CACHE_DIR = ROOT / ".cache"

CACHE_DIR.mkdir(exist_ok=True)

NEW_ALIVE = CACHE_DIR / "alive_new.txt"
HASH_FILE = CACHE_DIR / "alive.sha256"

COUNTRIES = {
    "AD": "安道尔",
    "AE": "阿联酋",
    "AF": "阿富汗",
    "AL": "阿尔巴尼亚",
    "AM": "亚美尼亚",
    "AO": "安哥拉",
    "AR": "阿根廷",
    "AT": "奥地利",
    "AU": "澳大利亚",
    "AZ": "阿塞拜疆",
    "BA": "波黑",
    "BD": "孟加拉国",
    "BE": "比利时",
    "BG": "保加利亚",
    "BH": "巴林",
    "BR": "巴西",
    "BY": "白俄罗斯",
    "CA": "加拿大",
    "CH": "瑞士",
    "CL": "智利",
    "CN": "中国",
    "CO": "哥伦比亚",
    "CR": "哥斯达黎加",
    "CY": "塞浦路斯",
    "CZ": "捷克",
    "DE": "德国",
    "DK": "丹麦",
    "DO": "多米尼加",
    "EE": "爱沙尼亚",
    "EG": "埃及",
    "ES": "西班牙",
    "FI": "芬兰",
    "FR": "法国",
    "GB": "英国",
    "GE": "格鲁吉亚",
    "GR": "希腊",
    "HK": "香港",
    "HR": "克罗地亚",
    "HU": "匈牙利",
    "ID": "印度尼西亚",
    "IE": "爱尔兰",
    "IL": "以色列",
    "IN": "印度",
    "IQ": "伊拉克",
    "IR": "伊朗",
    "IS": "冰岛",
    "IT": "意大利",
    "JP": "日本",
    "KE": "肯尼亚",
    "KG": "吉尔吉斯斯坦",
    "KH": "柬埔寨",
    "KR": "韩国",
    "KW": "科威特",
    "KZ": "哈萨克斯坦",
    "LA": "老挝",
    "LI": "列支敦士登",
    "LK": "斯里兰卡",
    "LT": "立陶宛",
    "LU": "卢森堡",
    "LV": "拉脱维亚",
    "LY": "利比亚",
    "MA": "摩洛哥",
    "MD": "摩尔多瓦",
    "ME": "黑山",
    "MK": "北马其顿",
    "MM": "缅甸",
    "MN": "蒙古",
    "MO": "澳门",
    "MT": "马耳他",
    "MU": "毛里求斯",
    "MX": "墨西哥",
    "MY": "马来西亚",
    "NG": "尼日利亚",
    "NL": "荷兰",
    "NO": "挪威",
    "NP": "尼泊尔",
    "NZ": "新西兰",
    "OM": "阿曼",
    "PA": "巴拿马",
    "PE": "秘鲁",
    "PH": "菲律宾",
    "PK": "巴基斯坦",
    "PL": "波兰",
    "PR": "波多黎各",
    "PT": "葡萄牙",
    "QA": "卡塔尔",
    "RO": "罗马尼亚",
    "RS": "塞尔维亚",
    "RU": "俄罗斯",
    "SA": "沙特阿拉伯",
    "SE": "瑞典",
    "SG": "新加坡",
    "SI": "斯洛文尼亚",
    "SK": "斯洛伐克",
    "TH": "泰国",
    "TR": "土耳其",
    "TW": "台湾",
    "UA": "乌克兰",
    "US": "美国",
    "UZ": "乌兹别克斯坦",
    "VE": "委内瑞拉",
    "VN": "越南",
    "ZA": "南非",
}


def download_alive():
    print("正在下载上游 alive.txt ...")
    urllib.request.urlretrieve(SOURCE_URL, NEW_ALIVE)


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def changed():
    new_hash = sha256_file(NEW_ALIVE)

    if not HASH_FILE.exists():
        return True, new_hash

    old_hash = HASH_FILE.read_text(
        encoding="utf-8"
    ).strip()

    return new_hash != old_hash, new_hash


def valid_port(port):
    try:
        p = int(port)
        return 1 <= p <= 65535
    except ValueError:
        return False


def rebuild():
    print("开始完整重建地区文件...")

    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)

    DATA_DIR.mkdir(parents=True)

    regions = {}
    all_lines = []

    seen = set()

    with NEW_ALIVE.open(
        "r",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as f:

        reader = csv.reader(f)

        for row in reader:

            if len(row) < 3:
                continue

            ip = row[0].strip()
            port = row[1].strip()
            code = row[2].strip().upper()

            provider = ""

            if len(row) >= 4:
                provider = ",".join(
                    x.strip()
                    for x in row[3:]
                )

            if not ip:
                continue

            if not valid_port(port):
                continue

            if not code:
                continue

            address = f"{ip}:{port}"

            # 全局去重
            if address in seen:
                continue

            seen.add(address)

            country = COUNTRIES.get(
                code,
                "未知地区"
            )

            if provider:
                line = (
                    f"{address}"
                    f"#{code}{country},"
                    f"{provider}"
                )
            else:
                line = (
                    f"{address}"
                    f"#{code}{country}"
                )

            regions.setdefault(
                code,
                []
            ).append(line)

            all_lines.append(line)

    # 分地区写入
    for code in sorted(regions):

        path = DATA_DIR / f"{code}.txt"

        path.write_text(
            "\n".join(regions[code]) + "\n",
            encoding="utf-8"
        )

        print(
            f"{code}.txt："
            f"{len(regions[code])} 条"
        )

    # 汇总
    (DATA_DIR / "ALL.txt").write_text(
        "\n".join(all_lines) + "\n",
        encoding="utf-8"
    )

    print("----------------------------")
    print(f"地区数量：{len(regions)}")
    print(f"总节点数量：{len(all_lines)}")


def main():

    download_alive()

    is_changed, new_hash = changed()

    if not is_changed:

        print("上游内容没有变化。")

        Path("changed.txt").write_text(
            "false",
            encoding="utf-8"
        )

        return

    print("检测到上游变化。")

    rebuild()

    HASH_FILE.write_text(
        new_hash + "\n",
        encoding="utf-8"
    )

    Path("changed.txt").write_text(
        "true",
        encoding="utf-8"
    )

    print("更新完成。")


if __name__ == "__main__":
    main()
