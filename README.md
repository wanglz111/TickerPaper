# Crypto E-Ink Dashboard 加密货币墨水屏看板

本项目是一个给 **Zectrix 墨水屏** 使用的加密货币桌面看板。它会从 **Binance 公共行情接口** 获取价格，把你的关注币种和本地配置的持仓状态渲染成两张 400 x 300 的黑白图片，并推送到墨水屏的两个页面上。

它适合放在桌面上做一个低打扰、常亮、扫一眼就够的 crypto 状态牌：

- 第 1 页看行情：BTC、ETH、SOL、BNB、PENDLE 的 USDT 价格和 24 小时涨跌。
- 第 2 页看持仓：当前总价值、未实现盈亏、成本、币种数量，以及每个币的仓位盈亏。

本工具只读取公开行情和你本地填写的持仓配置，**不需要 Binance API Key**，也不会连接交易账户、下单或读取真实账户资产。

---

## 功能特点

- **双页面看板**：价格预览和持仓预览分开显示，不把所有信息挤在一张屏里。
- **公开行情数据**：使用 Binance Spot 公共 ticker 接口，无需配置交易所密钥。
- **本地持仓配置**：你只需要在 `config.json` 里填币种数量和平均成本，就能看到仓位盈亏。
- **墨水屏友好排版**：固定 400 x 300 黑白图片，字体、行距、底栏都按小屏可读性处理。
- **自动字体处理**：默认 `font_path` 为 `auto`，会优先使用本机字体；没有合适字体时会自动下载 Cascadia Code 到 `.cache/fonts/`。
- **安全上传 GitHub**：真实配置文件 `config.json` 默认被忽略，不会把 Zectrix API Key 提交到仓库。

---

## 面板信息与布局

### 第 1 页：价格预览

标题为 `CRYPTO WATCH`，显示 5 个 USDT 交易对：

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

### 第 2 页：持仓预览

标题为 `CRYPTO PORTFOLIO`，左侧是仓位列表，右侧是组合摘要。

左侧每个币显示：

- `COIN`：币种
- `VALUE`：当前仓位价值
- `UPNL`：未实现盈亏
- `%`：未实现盈亏百分比

右侧摘要显示：

- `CURRENT VALUE`：组合当前总价值
- `UNREALIZED`：组合未实现盈亏
- `UPNL%`：组合未实现盈亏百分比
- `Cost`：总成本
- `Coins`：持仓币种数量

底部状态栏显示持仓里表现最好和最差的币，例如：

```text
BEST BTC +31%           WORST PENDLE -58%
```

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
- 页面 ID：决定价格页和持仓页分别推送到墨水屏的第几页。

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
  "price_page_id": 1,
  "portfolio_page_id": 2,
  "interval_seconds": 60,
  "font_path": "auto",
  "binance_base_url": "https://api.binance.com",
  "watchlist": [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "PENDLEUSDT"
  ],
  "positions": [
    {
      "asset": "BTC",
      "symbol": "BTCUSDT",
      "quantity": 0.75,
      "avg_cost": 58000
    }
  ]
}
```

### 关键配置说明

- `api_key`：Zectrix Open API Key。
- `mac_address`：你的 Zectrix 设备 MAC 地址。
- `price_page_id`：价格预览页要推送到哪一页。
- `portfolio_page_id`：持仓预览页要推送到哪一页。
- `interval_seconds`：连续运行时的刷新间隔，建议和 Zectrix 设备轮询时间保持一致，例如 60 秒。
- `font_path`：建议保持 `auto`，程序会自动寻找或下载字体。
- `watchlist`：第 1 页显示的 Binance 交易对。
- `positions`：第 2 页用于计算持仓的本地数据。

### 持仓字段说明

每一条 `positions` 表示一个币的持仓：

- `asset`：屏幕上显示的币种简称，例如 `BTC`。
- `symbol`：对应 Binance 交易对，例如 `BTCUSDT`。
- `quantity`：当前持有数量。
- `avg_cost`：平均持仓成本，单位按 USDT 计算。

程序会用 Binance 最新价格自动计算：

```text
当前价值 = quantity * 最新价格
成本 = quantity * avg_cost
未实现盈亏 = 当前价值 - 成本
未实现盈亏百分比 = 未实现盈亏 / 成本
```

---

## 开始使用

### 生成本地预览

先确认排版和配置是否正常：

```bash
python main.py --preview
```

运行后会在项目目录生成：

- `preview-price.png`
- `preview-portfolio.png`

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
Pushed pages 1 and 2
```

### 持续运行

```bash
python main.py
```

程序会按照 `interval_seconds` 定时刷新 Binance 行情、重新计算持仓，并推送两张新图片到 Zectrix。

---

## 使用建议

- 建议把 Zectrix 设备轮询时间设置为 1 分钟，同时把 `interval_seconds` 设为 `60`。
- `price_page_id` 和 `portfolio_page_id` 请设置成两个不同页面，避免互相覆盖。
- 如果你只想临时看一下效果，先运行 `python main.py --preview`，确认图片没问题后再推送。
- `config.json` 里有 API Key 和你的真实持仓信息，请不要手动提交到 GitHub。

---

## 常见问题排查

**Q: 为什么不需要 Binance API Key？**
A: 本项目只读取 Binance 公共行情接口，不读取你的账户余额，也不会下单，所以不需要 Binance API Key。

**Q: 屏幕没有刷新怎么办？**
A: 先运行：

```bash
python main.py --preview
```

如果本地预览图生成失败，通常是 Python 依赖、网络或配置格式有问题。如果预览图正常，但墨水屏不刷新，请检查 Zectrix 的 `api_key`、`mac_address` 和页面 ID 是否正确。

**Q: 字体文件为什么不放进仓库？**
A: 默认配置使用 `"font_path": "auto"`。程序会优先使用本机已有字体；没有合适字体时，会自动下载 Cascadia Code 到 `.cache/fonts/`。这样上传 GitHub 时不会依赖某个人电脑上的绝对路径。

**Q: 我想换成自己的字体可以吗？**
A: 可以。把字体文件放到项目目录，例如 `fonts/my-font.ttf`，然后设置：

```json
"font_path": "fonts/my-font.ttf"
```

也可以填写绝对路径，但如果要分享给别人，推荐使用相对路径或保持 `auto`。

**Q: 持仓数据会自动从交易所同步吗？**
A: 不会。当前版本的持仓来自本地 `config.json`，这样最简单，也最安全。你需要手动维护 `quantity` 和 `avg_cost`。

**Q: 这个工具会交易或发出买卖指令吗？**
A: 不会。它只是一个显示看板，只负责获取公开价格、渲染图片、推送到墨水屏。

---

## 免责声明

本项目仅用于个人信息展示和桌面看板，不构成任何投资建议。价格和盈亏计算可能受到网络、行情接口、配置填写等因素影响，请以交易所和你自己的账户记录为准。
