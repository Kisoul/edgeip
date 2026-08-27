from pathlib import Path
import csv
import hashlib
import urllib.request


# ============================================================
# 基本配置
# ============================================================

SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "papapapapdelesia/Emilia/refs/heads/main/Data/alive.txt"
)

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "Data"
CACHE_DIR = ROOT / ".cache"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

NEW_ALIVE = CACHE_DIR / "alive_new.txt"
HASH_FILE = CACHE_DIR / "alive.sha256"

# GitHub Actions 用它判断本次是否需要提交
CHANGED_FILE = ROOT / "changed.txt"


# ============================================================
# 国家 / 地区代码映射
# ============================================================

COUNTRIES = {
    "AD": "安道尔",
    "AE": "阿联酋",
    "AF": "阿富汗",
    "AG": "安提瓜和巴布达",
    "AI": "安圭拉",
    "AL": "阿尔巴尼亚",
    "AM": "亚美尼亚",
    "AO": "安哥拉",
    "AQ": "南极洲",
    "AR": "阿根廷",
    "AS": "美属萨摩亚",
    "AT": "奥地利",
    "AU": "澳大利亚",
    "AW": "阿鲁巴",
    "AX": "奥兰群岛",
    "AZ": "阿塞拜疆",
    "BA": "波黑",
    "BB": "巴巴多斯",
    "BD": "孟加拉国",
    "BE": "比利时",
    "BF": "布基纳法索",
    "BG": "保加利亚",
    "BH": "巴林",
    "BI": "布隆迪",
    "BJ": "贝宁",
    "BL": "圣巴泰勒米",
    "BM": "百慕大",
    "BN": "文莱",
    "BO": "玻利维亚",
    "BQ": "荷兰加勒比区",
    "BR": "巴西",
    "BS": "巴哈马",
    "BT": "不丹",
    "BV": "布韦岛",
    "BW": "博茨瓦纳",
    "BY": "白俄罗斯",
    "BZ": "伯利兹",
    "CA": "加拿大",
    "CC": "科科斯群岛",
    "CD": "刚果（金）",
    "CF": "中非共和国",
    "CG": "刚果（布）",
    "CH": "瑞士",
    "CI": "科特迪瓦",
    "CK": "库克群岛",
    "CL": "智利",
    "CM": "喀麦隆",
    "CN": "中国",
    "CO": "哥伦比亚",
    "CR": "哥斯达黎加",
    "CU": "古巴",
    "CV": "佛得角",
    "CW": "库拉索",
    "CX": "圣诞岛",
    "CY": "塞浦路斯",
    "CZ": "捷克",
    "DE": "德国",
    "DJ": "吉布提",
    "DK": "丹麦",
    "DM": "多米尼克",
    "DO": "多米尼加",
    "DZ": "阿尔及利亚",
    "EC": "厄瓜多尔",
    "EE": "爱沙尼亚",
    "EG": "埃及",
    "EH": "西撒哈拉",
    "ER": "厄立特里亚",
    "ES": "西班牙",
    "ET": "埃塞俄比亚",
    "FI": "芬兰",
    "FJ": "斐济",
    "FK": "福克兰群岛",
    "FM": "密克罗尼西亚",
    "FO": "法罗群岛",
    "FR": "法国",
    "GA": "加蓬",
    "GB": "英国",
    "GD": "格林纳达",
    "GE": "格鲁吉亚",
    "GF": "法属圭亚那",
    "GG": "根西岛",
    "GH": "加纳",
    "GI": "直布罗陀",
    "GL": "格陵兰",
    "GM": "冈比亚",
    "GN": "几内亚",
    "GP": "瓜德罗普",
    "GQ": "赤道几内亚",
    "GR": "希腊",
    "GS": "南乔治亚和南桑威奇群岛",
    "GT": "危地马拉",
    "GU": "关岛",
    "GW": "几内亚比绍",
    "GY": "圭亚那",
    "HK": "香港",
    "HM": "赫德岛和麦克唐纳群岛",
    "HN": "洪都拉斯",
    "HR": "克罗地亚",
    "HT": "海地",
    "HU": "匈牙利",
    "ID": "印度尼西亚",
    "IE": "爱尔兰",
    "IL": "以色列",
    "IM": "马恩岛",
    "IN": "印度",
    "IO": "英属印度洋领地",
    "IQ": "伊拉克",
    "IR": "伊朗",
    "IS": "冰岛",
    "IT": "意大利",
    "JE": "泽西岛",
    "JM": "牙买加",
    "JO": "约旦",
    "JP": "日本",
    "KE": "肯尼亚",
    "KG": "吉尔吉斯斯坦",
    "KH": "柬埔寨",
    "KI": "基里巴斯",
    "KM": "科摩罗",
    "KN": "圣基茨和尼维斯",
    "KP": "朝鲜",
    "KR": "韩国",
    "KW": "科威特",
    "KY": "开曼群岛",
    "KZ": "哈萨克斯坦",
    "LA": "老挝",
    "LB": "黎巴嫩",
    "LC": "圣卢西亚",
    "LI": "列支敦士登",
    "LK": "斯里兰卡",
    "LR": "利比里亚",
    "LS": "莱索托",
    "LT": "立陶宛",
    "LU": "卢森堡",
    "LV": "拉脱维亚",
    "LY": "利比亚",
    "MA": "摩洛哥",
    "MC": "摩纳哥",
    "MD": "摩尔多瓦",
    "ME": "黑山",
    "MF": "法属圣马丁",
    "MG": "马达加斯加",
    "MH": "马绍尔群岛",
    "MK": "北马其顿",
    "ML": "马里",
    "MM": "缅甸",
    "MN": "蒙古",
    "MO": "澳门",
    "MP": "北马里亚纳群岛",
    "MQ": "马提尼克",
    "MR": "毛里塔尼亚",
    "MS": "蒙特塞拉特",
    "MT": "马耳他",
    "MU": "毛里求斯",
    "MV": "马尔代夫",
    "MW": "马拉维",
    "MX": "墨西哥",
    "MY": "马来西亚",
    "MZ": "莫桑比克",
    "NA": "纳米比亚",
    "NC": "新喀里多尼亚",
    "NE": "尼日尔",
    "NF": "诺福克岛",
    "NG": "尼日利亚",
    "NI": "尼加拉瓜",
    "NL": "荷兰",
    "NO": "挪威",
    "NP": "尼泊尔",
    "NR": "瑙鲁",
    "NU": "纽埃",
    "NZ": "新西兰",
    "OM": "阿曼",
    "PA": "巴拿马",
    "PE": "秘鲁",
    "PF": "法属波利尼西亚",
    "PG": "巴布亚新几内亚",
    "PH": "菲律宾",
    "PK": "巴基斯坦",
    "PL": "波兰",
    "PM": "圣皮埃尔和密克隆",
    "PN": "皮特凯恩群岛",
    "PR": "波多黎各",
    "PS": "巴勒斯坦",
    "PT": "葡萄牙",
    "PW": "帕劳",
    "PY": "巴拉圭",
    "QA": "卡塔尔",
    "RE": "留尼汪",
    "RO": "罗马尼亚",
    "RS": "塞尔维亚",
    "RU": "俄罗斯",
    "RW": "卢旺达",
    "SA": "沙特阿拉伯",
    "SB": "所罗门群岛",
    "SC": "塞舌尔",
    "SD": "苏丹",
    "SE": "瑞典",
    "SG": "新加坡",
    "SH": "圣赫勒拿",
    "SI": "斯洛文尼亚",
    "SJ": "斯瓦尔巴和扬马延",
    "SK": "斯洛伐克",
    "SL": "塞拉利昂",
    "SM": "圣马力诺",
    "SN": "塞内加尔",
    "SO": "索马里",
    "SR": "苏里南",
    "SS": "南苏丹",
    "ST": "圣多美和普林西比",
    "SV": "萨尔瓦多",
    "SX": "荷属圣马丁",
    "SY": "叙利亚",
    "SZ": "斯威士兰",
    "TC": "特克斯和凯科斯群岛",
    "TD": "乍得",
    "TF": "法属南部领地",
    "TG": "多哥",
    "TH": "泰国",
    "TJ": "塔吉克斯坦",
    "TK": "托克劳",
    "TL": "东帝汶",
    "TM": "土库曼斯坦",
    "TN": "突尼斯",
    "TO": "汤加",
    "TR": "土耳其",
    "TT": "特立尼达和多巴哥",
    "TV": "图瓦卢",
    "TW": "台湾",
    "TZ": "坦桑尼亚",
    "UA": "乌克兰",
    "UG": "乌干达",
    "UM": "美国本土外小岛屿",
    "US": "美国",
    "UY": "乌拉圭",
    "UZ": "乌兹别克斯坦",
    "VA": "梵蒂冈",
    "VC": "圣文森特和格林纳丁斯",
    "VE": "委内瑞拉",
    "VG": "英属维尔京群岛",
    "VI": "美属维尔京群岛",
    "VN": "越南",
    "VU": "瓦努阿图",
    "WF": "瓦利斯和富图纳",
    "WS": "萨摩亚",
    "YE": "也门",
    "YT": "马约特",
    "ZA": "南非",
    "ZM": "赞比亚",
    "ZW": "津巴布韦",

    # 上游偶尔可能出现非标准地区代码
    "T1": "未知地区",
}


# ============================================================
# 下载 alive.txt
# ============================================================

def download_alive():
    print("正在下载上游 Emilia/Data/alive.txt ...")

    urllib.request.urlretrieve(
        SOURCE_URL,
        NEW_ALIVE,
    )

    print(f"下载完成：{NEW_ALIVE}")


# ============================================================
# 计算 SHA256
# ============================================================

def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


# ============================================================
# 判断上游是否变化
# ============================================================

def check_upstream_changed():
    new_hash = sha256_file(NEW_ALIVE)

    if not HASH_FILE.exists():
        print("首次运行：没有历史 SHA256。")
        return True, new_hash

    old_hash = HASH_FILE.read_text(
        encoding="utf-8"
    ).strip()

    print(f"旧 SHA256：{old_hash}")
    print(f"新 SHA256：{new_hash}")

    if old_hash == new_hash:
        return False, new_hash

    return True, new_hash


# ============================================================
# 端口合法性
# ============================================================

def valid_port(port):
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


# ============================================================
# 从旧 Data 文件中读取历史节点
# ============================================================

def load_old_data():
    """
    返回结构：
    {
        "HK": {
            "1.2.3.4:443": "1.2.3.4:443#HK香港,Cloudflare"
        },
        "TR": {
            ...
        }
    }

    以 IP:端口 为唯一键。
    """

    regions = {}

    if not DATA_DIR.exists():
        print("Data 目录不存在，视为首次生成。")
        return regions

    print("正在读取历史地区文件...")

    file_count = 0
    node_count = 0

    for path in sorted(DATA_DIR.glob("*.txt")):
        # ALL.txt 只是汇总，不重复读取
        if path.name.upper() == "ALL.TXT":
            continue

        code = path.stem.upper()
        regions.setdefault(code, {})
        file_count += 1

        try:
            lines = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()

            for line in lines:
                line = line.strip()

                if not line:
                    continue

                # 格式：
                # IP:PORT#地区代码中文名,运营商
                if "#" not in line:
                    continue

                address = line.split("#", 1)[0].strip()

                if not address:
                    continue

                regions[code][address] = line
                node_count += 1

        except Exception as e:
            print(f"读取历史文件 {path.name} 失败：{e}")

    print(
        f"历史文件：{file_count} 个，"
        f"历史节点：{node_count} 条"
    )

    return regions


# ============================================================
# 解析上游 alive.txt
# ============================================================

def load_new_data():
    """
    读取新的 alive.txt。

    返回：
    {
        "HK": {
            "1.2.3.4:443": "1.2.3.4:443#HK香港,Cloudflare"
        }
    }
    """

    regions = {}

    raw_count = 0
    valid_count = 0
    invalid_count = 0

    print("正在解析新的 alive.txt ...")

    with NEW_ALIVE.open(
        "r",
        encoding="utf-8",
        errors="ignore",
        newline="",
    ) as f:
        reader = csv.reader(f)

        for row in reader:
            raw_count += 1

            if len(row) < 3:
                invalid_count += 1
                continue

            ip = row[0].strip()
            port = row[1].strip()
            code = row[2].strip().upper()

            # 第 4 列开始全部视为运营商信息，
            # 防止运营商名称中本身存在逗号。
            provider = ""

            if len(row) >= 4:
                provider = ",".join(
                    item.strip()
                    for item in row[3:]
                    if item.strip()
                )

            if not ip:
                invalid_count += 1
                continue

            if not valid_port(port):
                invalid_count += 1
                continue

            if not code:
                invalid_count += 1
                continue

            address = f"{ip}:{port}"

            country_name = COUNTRIES.get(
                code,
                "未知地区",
            )

            if provider:
                line = (
                    f"{address}"
                    f"#{code}{country_name},"
                    f"{provider}"
                )
            else:
                line = (
                    f"{address}"
                    f"#{code}{country_name}"
                )

            regions.setdefault(code, {})

            # 同一次上游内如果重复，自动去重
            regions[code][address] = line

            valid_count += 1

    print("----------------------------")
    print(f"上游原始行数：{raw_count}")
    print(f"有效行数：{valid_count}")
    print(f"无效行数：{invalid_count}")

    return regions


# ============================================================
# 合并历史 + 新数据
# ============================================================

def merge_data(old_regions, new_regions):
    """
    方案2：

    历史数据永久保留。

    新数据：
    - 不存在 → 新增
    - IP:端口 已存在，但信息变化 → 更新成上游新信息
    - 上游本次没有出现 → 旧数据仍保留
    """

    merged = {}

    # 复制历史数据
    for code, nodes in old_regions.items():
        merged.setdefault(code, {})
        merged[code].update(nodes)

    added_count = 0
    updated_count = 0
    duplicate_count = 0

    # 合并新数据
    for code, nodes in new_regions.items():
        merged.setdefault(code, {})

        for address, new_line in nodes.items():
            if address not in merged[code]:
                merged[code][address] = new_line
                added_count += 1
            else:
                old_line = merged[code][address]

                if old_line != new_line:
                    # 相同 IP:端口信息变化：
                    # 以本次上游信息为准
                    merged[code][address] = new_line
                    updated_count += 1
                else:
                    duplicate_count += 1

    print("----------------------------")
    print(f"新增节点：{added_count}")
    print(f"更新节点：{updated_count}")
    print(f"重复节点：{duplicate_count}")

    return merged


# ============================================================
# 写入所有地区文件
# ============================================================

def write_data(regions):
    """
    不删除历史地区。

    根据合并后的完整数据重新写入每个地区文件。

    最后重新生成 ALL.txt。
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_lines = []
    region_count = 0

    print("----------------------------")
    print("正在生成地区文件...")

    for code in sorted(regions.keys()):
        nodes = regions[code]

        if not nodes:
            continue

        # 按 address 字符排序
        sorted_items = sorted(
            nodes.items(),
            key=lambda item: item[0],
        )

        lines = [
            line
            for _, line in sorted_items
        ]

        output_file = DATA_DIR / f"{code}.txt"

        output_file.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        all_lines.extend(lines)

        region_count += 1

        print(
            f"{code}.txt："
            f"{len(lines)} 条"
        )

    # ========================================================
    # 重新生成 ALL.txt
    # ========================================================

    all_file = DATA_DIR / "ALL.txt"

    all_file.write_text(
        "\n".join(all_lines) + "\n",
        encoding="utf-8",
    )

    print("============================")
    print(f"地区数量：{region_count}")
    print(f"累计节点：{len(all_lines)}")
    print(f"汇总文件：{all_file}")


# ============================================================
# 保存新 SHA256
# ============================================================

def save_hash(new_hash):
    HASH_FILE.write_text(
        new_hash + "\n",
        encoding="utf-8",
    )


# ============================================================
# 写 GitHub Actions 状态
# ============================================================

def set_changed(value):
    CHANGED_FILE.write_text(
        "true" if value else "false",
        encoding="utf-8",
    )


# ============================================================
# 主程序
# ============================================================

def main():
    print("======================================")
    print("Proxy IP 自动同步整理")
    print("======================================")

    # 1. 下载上游
    download_alive()

    # 2. 检查上游是否有变化
    is_changed, new_hash = check_upstream_changed()

    if not is_changed:
        print("----------------------------")
        print("上游 alive.txt 没有变化。")
        print("本次不重新生成 Data 文件。")

        set_changed(False)
        return

    print("----------------------------")
    print("检测到上游 alive.txt 已变化。")

    # 3. 读取历史节点
    old_regions = load_old_data()

    # 4. 读取本次上游节点
    new_regions = load_new_data()

    # 5. 合并历史 + 新节点
    merged_regions = merge_data(
        old_regions,
        new_regions,
    )

    # 6. 重新写地区文件 + ALL
    write_data(merged_regions)

    # 7. 更新 SHA256
    save_hash(new_hash)

    # 8. 通知 GitHub Actions
    set_changed(True)

    print("============================")
    print("本次同步整理完成。")
    print("============================")


if __name__ == "__main__":
    main()
