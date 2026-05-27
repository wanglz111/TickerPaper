# Crypto E-Ink Dashboard 加密货币墨水屏价格看板

本项目是一个给 **Zectrix 墨水屏** 使用的加密货币价格看板。它会从 **Binance 公共行情接口** 获取价格，把你关注的 USDT 交易对渲染成一张 400 x 300 的黑白图片，并推送到墨水屏指定页面上。

它适合放在桌面上做一个低打扰、常亮、扫一眼就够的 crypto 行情状态牌：

- 显示 BTC、ETH、SOL、BNB、PENDLE 的 USDT 最新价格。
- 显示每个币的 24 小时涨跌百分比。
- 底部显示 Binance 数据状态和下一次刷新间隔。

本工具只读取公开行情，**不需要 Binance API Key**，不会连接交易账户、读取资产、下单或发出任何交易指令。

---

## 功能特点

- **单页价格看板**：主分支只保留第一页价格预览，信息更干净。
- **公开行情数据**：使用 Binance Spot 公共 ticker 接口，无需配置交易所密钥。
- **墨水屏友好排版**：固定 400 x 300 黑白图片，字体、行距、涨跌标签和底栏都按小屏可读性处理。
- **自动字体处理**：默认 `font_path` 为 `auto`，会优先使用本机字体；没有合适字体时会自动下载 Cascadia Code 到 `.cache/fonts/`。
- **安全上传 GitHub**：真实配置文件 `config.json` 默认被忽略，不会把 Zectrix API Key 提交到仓库。

> 需要“价格页 + 持仓页”的完整双页版本，请切换到 `two-page-dashboard` 分支。

---

## 面板信息与布局

标题为 `CRYPTO WATCH`，默认显示 5 个 USDT 交易对：

- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`
- `BNBUSDT`
- `PENDLEUSDT`

每一行包含：

- 币种简称
- Binance 交易对
- 最新价格
- 24 小时涨跌百分比

底部状态栏显示数据状态，例如：

```text
BINANCE OK 19:05        NEXT 60s
```

意思是行情来自 Binance，最近一次刷新时间是 `19:05`，下一轮刷新间隔为 60 秒。

---

## 安装准备

请先准备：

1. **Python 3**
2. **Zectrix 云平台账号**
3. **你的 Zectrix 设备 MAC 地址**
4. **Zectrix Open API Key**

在 Zectrix 云平台中获取：

- API Key：进入开放 API 页面创建。
- 设备 MAC：进入设备管理页面复制。
- 页面 ID：决定价格看板推送到墨水屏的第几页。

---

## 安装与配置

进入项目目录后运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json
```

然后编辑 `config.json`。

一个配置大概长这样：

```json
{
  "api_key": "YOUR_ZECTRIX_API_KEY",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "page_id": 1,
  "interval_seconds": 60,
  "font_path": "auto",
  "binance_base_url": "https://api.binance.com",
  "watchlist": [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "PENDLEUSDT"
  ]
}
```

### 关键配置说明

- `api_key`：Zectrix Open API Key。
- `mac_address`：你的 Zectrix 设备 MAC 地址。
- `page_id`：价格看板要推送到哪一页。
- `interval_seconds`：连续运行时的刷新间隔，建议和 Zectrix 设备轮询时间保持一致，例如 60 秒。
- `font_path`：建议保持 `auto`，程序会自动寻找或下载字体。
- `watchlist`：屏幕上显示的 Binance 交易对，最多显示前 5 个。

---

## 开始使用

### 生成本地预览

先确认排版和配置是否正常：

```bash
python main.py --preview
```

运行后会在项目目录生成：

```text
preview.png
```

如果你还没有填真实配置，也可以用内置示例数据预览：

```bash
python main.py --preview --sample
```

### 推送一次到墨水屏

```bash
python main.py --once
```

成功时会看到类似输出：

```text
Pushed page 1
```

### 持续运行

```bash
python main.py
```

程序会按照 `interval_seconds` 定时刷新 Binance 行情，并推送新的价格看板图片到 Zectrix。

---

## 使用建议

- 建议把 Zectrix 设备轮询时间设置为 1 分钟，同时把 `interval_seconds` 设为 `60`。
- 如果你只想临时看一下效果，先运行 `python main.py --preview`，确认图片没问题后再推送。
- `watchlist` 可以改成其他 Binance USDT 交易对，但小屏最多显示前 5 个。
- `config.json` 里有 API Key，请不要手动提交到 GitHub。

---

## 常见问题排查

**Q: 为什么不需要 Binance API Key？**
A: 本项目只读取 Binance 公共行情接口，不读取你的账户余额，也不会下单，所以不需要 Binance API Key。

**Q: 屏幕没有刷新怎么办？**
A: 先运行：

```bash
python main.py --preview
```

如果本地预览图生成失败，通常是 Python 依赖、网络或配置格式有问题。如果预览图正常，但墨水屏不刷新，请检查 Zectrix 的 `api_key`、`mac_address` 和 `page_id` 是否正确。

**Q: 字体文件为什么不放进仓库？**
A: 默认配置使用 `"font_path": "auto"`。程序会优先使用本机已有字体；没有合适字体时，会自动下载 Cascadia Code 到 `.cache/fonts/`。这样上传 GitHub 时不会依赖某个人电脑上的绝对路径。

**Q: 我想换成自己的字体可以吗？**
A: 可以。把字体文件放到项目目录，例如 `fonts/my-font.ttf`，然后设置：

```json
"font_path": "fonts/my-font.ttf"
```

也可以填写绝对路径，但如果要分享给别人，推荐使用相对路径或保持 `auto`。

**Q: 完整持仓页去哪了？**
A: 完整双页版本保存在 `two-page-dashboard` 分支。主分支只保留价格页，适合公开展示和最小化配置。

---

## 免责声明

本项目仅用于个人信息展示和桌面看板，不构成任何投资建议。价格可能受到网络、行情接口、配置填写等因素影响，请以交易所显示为准。
