#!/usr/bin/env node
/**
 * 双均线金叉策略回测引擎
 * — MA(Short) 上穿 MA(Long) → 买入
 * — MA(Short) 下穿 MA(Long) → 卖出
 * 数据源: Yahoo Finance (美股) / Sina Finance (A股)
 */

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");

// ─── 配置 ────────────────────────────────────────────────────────────
const CONFIG = {
  symbol: process.argv.find((a) => a.startsWith("--symbol="))?.split("=")[1] || "000300.SS",
  fast: parseInt(process.argv.find((a) => a.startsWith("--fast="))?.split("=")[1]) || 5,
  slow: parseInt(process.argv.find((a) => a.startsWith("--slow="))?.split("=")[1]) || 20,
  years: parseInt(process.argv.find((a) => a.startsWith("--years="))?.split("=")[1]) || 5,
  initialCash: 1000000,
};

// ─── 工具函数 ─────────────────────────────────────────────────────────
function msToDate(ms) {
  return new Date(ms);
}
function formatDate(d) {
  return d.toISOString().slice(0, 10);
}
function daysBetween(a, b) {
  return Math.abs(Math.floor((b - a) / 86400000));
}

/** HTTP GET 返回 Promise<string> */
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith("https") ? https : http;
    const headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "*/*",
      "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
      "Referer": "https://finance.sina.com.cn/",
    };
    mod.get(url, { headers }, (res) => {
      let data = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => resolve(data));
    }).on("error", reject);
  });
}

/** 计算简单移动平均 */
function sma(prices, period) {
  const result = [];
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      const slice = prices.slice(i - period + 1, i + 1);
      result.push(slice.reduce((s, v) => s + v, 0) / period);
    }
  }
  return result;
}

// ─── 数据获取 ─────────────────────────────────────────────────────────
/**
 * 从 Yahoo Finance 获取历史数据（支持A股: 000300.SS, NFLX, AAPL等）
 * 返回: [{ date: Date, open, high, low, close, adjClose, volume }]
 */
async function fetchYahoo(symbol, years) {
  const endTs = Math.floor(Date.now() / 1000);
  const startTs = endTs - years * 365 * 86400;
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(
    symbol
  )}?period1=${startTs}&period2=${endTs}&interval=1d`;
  const raw = await httpGet(url);
  const json = JSON.parse(raw);

  if (!json.chart?.result?.[0]) throw new Error(`Yahoo数据获取失败: ${symbol}`);
  const res = json.chart.result[0];
  const timestamps = res.timestamp; // Unix seconds
  const quotes = res.indicators.quote[0];
  const adjClose = res.indicators.adjclose?.[0]?.adjclose;

  const data = timestamps.map((ts, i) => ({
    date: new Date(ts * 1000),
    open: quotes.open[i],
    high: quotes.high[i],
    low: quotes.low[i],
    close: quotes.close[i],
    adjClose: adjClose ? adjClose[i] : quotes.close[i],
    volume: quotes.volume[i],
  })).filter((d) => d.close != null && !isNaN(d.close));

  return data;
}

/**
 * 从 Sina Finance 获取A股日线数据（沪深300指数）
 * symbol: 000300 代表沪深300指数
 */
async function fetchSinaIndex(symbol, years) {
  // 沪深300指数代码: sh000300
  const sinaCode = symbol === "000300.SS" ? "sh000300" : `sh${symbol.split(".")[0]}`;
  const url = `https://quotes.sina.cn/cn/api/jsonp.php/var%20_data=/CN_MarketDataService.getKLineData?symbol=${sinaCode}&scale=240&ma=no&datalen=2000`;

  const raw = await httpGet(url);
  // 解析 JSONP
  const match = raw.match(/\[.*\]/s);
  if (!match) throw new Error(`Sina数据解析失败: ${raw.slice(0,100)}`);
  const arr = JSON.parse(match[0]);

  const data = arr
    .map((r) => ({
      date: new Date(r.day),
      open: parseFloat(r.open),
      high: parseFloat(r.high),
      low: parseFloat(r.low),
      close: parseFloat(r.close),
      adjClose: parseFloat(r.close),
      volume: parseInt(r.volume) || 0,
    }))
    .filter((d) => !isNaN(d.date.getTime()));

  data.sort((a, b) => a.date - b.date);
  // 截取指定年份
  const cutoff = Date.now() - years * 365 * 86400000;
  return data.filter(d => d.date.getTime() >= cutoff);
}

/**
 * 从腾讯财经获取A股日线数据
 * 沪深300指数代码: sh000300
 */
async function fetchTencent(symbol, years) {
  const tencentCode = symbol === "000300.SS" ? "sh000300" : `sh${symbol.split(".")[0]}`;
  // 腾讯日K数据接口，返回 qqt-data 格式
  const url = `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=${tencentCode},day,,,3000,qfq`;

  const raw = await httpGet(url);
  // 解析腾讯数据格式: v_sh000300="~...~日期1~开~高~低~收~量~...~"
  const match = raw.match(/"([^"]*?)"/s);
  if (!match) throw new Error(`腾讯数据解析失败: ${raw.slice(0,200)}`);

  const parts = match[1].split("~");
  if (parts.length < 6) throw new Error(`腾讯数据格式异常: ${match[1].slice(0,100)}`);

  // 腾讯返回的是拼接字符串，每7段为一天
  const data = [];
  for (let i = 1; i < parts.length; i += 7) {
    const dateStr = parts[i];
    const open = parseFloat(parts[i + 1]);
    const close = parseFloat(parts[i + 2]);
    const high = parseFloat(parts[i + 3]);
    const low = parseFloat(parts[i + 4]);
    const volume = parseInt(parts[i + 5]) || 0;
    if (!dateStr || isNaN(open)) continue;
    data.push({
      date: new Date(dateStr),
      open, high, low, close,
      adjClose: close,
      volume,
    });
  }

  data.sort((a, b) => a.date - b.date);
  const cutoff = Date.now() - years * 365 * 86400000;
  return data.filter(d => d.date.getTime() >= cutoff);
}

/**
 * 使用 EastMoney 接口获取沪深300指数历史数据
 */
async function fetchEastMoney(symbol, years) {
  // 沪深300指数: 000300，secid=1.000300 (1=上证)
  const secid = symbol.includes("000300") ? "1.000300" : `1.${symbol.split(".")[0]}`;
  const end = formatDate(new Date()).replace(/-/g, "");
  const start = formatDate(new Date(Date.now() - years * 365 * 86400000)).replace(/-/g, "");

  // 东方财富日K接口
  const url = `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=${secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=${start}&end=${end}&ut=fa5fd1943c7b386f172d6893dbfba10b`;

  const raw = await httpGet(url);
  let json;
  try {
    json = JSON.parse(raw);
  } catch (e) {
    throw new Error(`东方财富数据解析失败: ${raw.slice(0,200)}`);
  }

  if (!json.data?.klines) throw new Error(`东方财富无数据: ${raw.slice(0,200)}`);

  const data = json.data.klines.map((line) => {
    const [date, open, close, high, low, volume, amount, amplitude, pctChange, change, turnover] = line.split(",");
    return {
      date: new Date(date),
      open: parseFloat(open),
      high: parseFloat(high),
      low: parseFloat(low),
      close: parseFloat(close),
      adjClose: parseFloat(close),
      volume: parseInt(volume) || 0,
    };
  });

  data.sort((a, b) => a.date - b.date);
  return data;
}

async function fetchData(symbol, years) {
  // 优先使用东方财富（稳定性最好）
  try {
    return await fetchEastMoney(symbol, years);
  } catch (e) {
    console.error("东方财富接口失败:", e.message);
  }

  // 备选：腾讯
  try {
    return await fetchTencent(symbol, years);
  } catch (e) {
    console.error("腾讯接口失败:", e.message);
  }

  throw new Error("无法获取历史数据，请检查网络连接");
}

// ─── 策略逻辑 ─────────────────────────────────────────────────────────
/**
 * 双均线金叉/死叉策略回测
 * 返回交易记录和持仓序列
 */
function runBacktest(data, fastPeriod, slowPeriod, initialCash) {
  const closes = data.map((d) => d.adjClose);
  const fastMA = sma(closes, fastPeriod);
  const slowMA = sma(closes, slowPeriod);

  let cash = initialCash;
  let shares = 0;
  let position = 0; // 0=空仓, 1=持仓
  const trades = [];
  const equityCurve = [];

  for (let i = 0; i < data.length; i++) {
    const price = closes[i];
    const f = fastMA[i];
    const s = slowMA[i];
    const date = data[i].date;

    // 跳过没有足够数据计算均线的日子
    if (f == null || s == null) {
      equityCurve.push({ date, equity: cash + shares * price, cash, shares });
      continue;
    }

    const prevFast = fastMA[i - 1];
    const prevSlow = slowMA[i - 1];

    if (prevFast != null && prevSlow != null) {
      // 金叉: 快线从下穿上
      if (prevFast <= prevSlow && f > s && position === 0) {
        shares = Math.floor(cash / price);
        const cost = shares * price;
        cash -= cost;
        position = 1;
        trades.push({ date, type: "BUY", price, shares, value: cost, reason: "金叉" });
      }
      // 死叉: 快线从上穿下
      else if (prevFast >= prevSlow && f < s && position === 1) {
        const proceeds = shares * price;
        cash += proceeds;
        trades.push({ date, type: "SELL", price, shares, value: proceeds, reason: "死叉" });
        shares = 0;
        position = 0;
      }
    }

    equityCurve.push({ date, equity: cash + shares * price, cash, shares });
  }

  // 最后若仍持仓，按最后收盘价计算
  const finalPrice = closes[closes.length - 1];
  const finalEquity = cash + shares * finalPrice;

  return { trades, equityCurve, finalEquity, initialCash };
}

// ─── 绩效计算 ─────────────────────────────────────────────────────────
function calcMetrics(data, equityCurve, trades, initialCash) {
  if (equityCurve.length === 0) throw new Error("无有效数据");

  const finalEq = equityCurve[equityCurve.length - 1].equity;
  const totalReturn = (finalEq - initialCash) / initialCash;

  const startDate = data[0].date;
  const endDate = data[data.length - 1].date;
  const years = daysBetween(startDate, endDate) / 365;
  const annualized = years > 0 ? (Math.pow(finalEq / initialCash, 1 / years) - 1) : 0;

  // 最大回撤
  let peak = -Infinity;
  let maxDrawdown = 0;
  let maxDrawdownPct = 0;
  let ddStart = null, ddEnd = null, peakDate = null;
  for (const pt of equityCurve) {
    if (pt.equity > peak) {
      peak = pt.equity;
      peakDate = pt.date;
    }
    const dd = (peak - pt.equity) / peak;
    if (dd > maxDrawdown) {
      maxDrawdown = dd;
      maxDrawdownPct = dd * 100;
      ddStart = peakDate;
      ddEnd = pt.date;
    }
  }

  // 年化波动率 (日收益标准差 * sqrt(252))
  const dailyReturns = [];
  for (let i = 1; i < equityCurve.length; i++) {
    const r = (equityCurve[i].equity - equityCurve[i - 1].equity) / equityCurve[i - 1].equity;
    dailyReturns.push(r);
  }
  const meanR = dailyReturns.reduce((s, v) => s + v, 0) / dailyReturns.length;
  const variance = dailyReturns.reduce((s, v) => s + (v - meanR) ** 2, 0) / dailyReturns.length;
  const annualVol = Math.sqrt(variance * 252);

  // 夏普比率 (假设无风险利率 3%)
  const riskFree = 0.03;
  const sharpe = annualVol > 0 ? (annualized - riskFree) / annualVol : 0;

  // 胜率
  let wins = 0, losses = 0;
  let profit = 0, loss = 0;
  let winStreak = 0, lossStreak = 0, maxWinStreak = 0, maxLossStreak = 0;
  let lastType = null;

  for (const t of trades) {
    if (t.type === "SELL") {
      const buyCost = trades[trades.indexOf(t) - 1]?.value || 0;
      const ret = t.value > 0 && buyCost > 0 ? (t.value - buyCost) / buyCost : 0;
      if (ret > 0) { wins++; profit += ret; winStreak++; lossStreak = 0; }
      else { losses++; loss += Math.abs(ret); lossStreak++; winStreak = 0; }
      if (winStreak > maxWinStreak) maxWinStreak = winStreak;
      if (lossStreak > maxLossStreak) maxLossStreak = lossStreak;
    }
  }
  const winRate = (wins + losses) > 0 ? wins / (wins + losses) : 0;
  const avgWin = wins > 0 ? profit / wins : 0;
  const avgLoss = losses > 0 ? loss / losses : 0;
  const profitFactor = loss > 0 ? profit / loss : 0;

  // 交易次数 & 持仓天数
  const tradesLong = trades.filter((t) => t.type === "BUY");
  const avgHoldingDays = trades.length >= 2
    ? trades.filter((t) => t.type === "SELL").reduce((s, sel, i) => {
        const buy = trades.find((t2, j) => t2.type === "BUY" && j < trades.indexOf(sel));
        if (buy) {
          const buyDate = buy.date, selDate = sel.date;
          return s + daysBetween(buyDate, selDate);
        }
        return s;
      }, 0) / Math.max(1, trades.filter((t) => t.type === "SELL").length)
    : 0;

  return {
    totalReturn, annualized, annualVol, sharpe,
    maxDrawdown: maxDrawdownPct,
    ddStart: ddStart ? formatDate(ddStart) : null,
    ddEnd: ddEnd ? formatDate(ddEnd) : null,
    winRate, profitFactor, avgWin, avgLoss,
    totalTrades: trades.length, buyCount: trades.filter(t=>t.type==="BUY").length,
    sellCount: trades.filter(t=>t.type==="SELL").length,
    maxWinStreak, maxLossStreak,
    avgHoldingDays: Math.round(avgHoldingDays),
    finalEquity: Math.round(finalEq),
    initialCash,
    startDate: formatDate(startDate),
    endDate: formatDate(endDate),
    years: years.toFixed(2),
    equityCurve,
    maxEquity: Math.max(...equityCurve.map(e=>e.equity)),
    minEquity: Math.min(...equityCurve.map(e=>e.equity)),
  };
}

// ─── Markdown 报告 ─────────────────────────────────────────────────────
function formatReport(metrics, fastPeriod, slowPeriod, symbol) {
  const { totalReturn, annualized, annualVol, sharpe, maxDrawdown, ddStart, ddEnd,
    winRate, profitFactor, avgWin, avgLoss,
    totalTrades, buyCount, sellCount, maxWinStreak, maxLossStreak, avgHoldingDays,
    finalEquity, initialCash, startDate, endDate, years } = metrics;

  const retSign = totalReturn >= 0 ? "+" : "";
  const annSign = annualized >= 0 ? "+" : "";
  const sharpeSign = sharpe >= 0 ? "+" : "";

  const retStars = totalReturn > 1 ? "⭐⭐⭐⭐⭐" : totalReturn > 0.5 ? "⭐⭐⭐⭐" : totalReturn > 0 ? "⭐⭐⭐" : "⭐";
  const sharpeStars = sharpe > 1.5 ? "⭐⭐⭐⭐" : sharpe > 1 ? "⭐⭐⭐" : sharpe > 0 ? "⭐⭐" : "⭐";
  const ddStars = maxDrawdown < 10 ? "⭐⭐⭐⭐" : maxDrawdown < 20 ? "⭐⭐⭐" : maxDrawdown < 30 ? "⭐⭐" : "⭐";

  const trend = annualized > 0.2 ? "📈 强势" : annualized > 0 ? "📊 稳健" : "📉 弱势";

  const equityRows = buildEquityTable(metrics.equityCurve);

  return `# 📊 双均线金叉策略 — 回测报告

**生成时间**: ${formatDate(new Date())}  
**标的**: ${symbol}  
**策略**: MA${fastPeriod} × MA${slowPeriod} 金叉/死叉  
**回测区间**: ${startDate} → ${endDate} (${years}年)  
**初始资金**: ¥${(initialCash/10000).toFixed(0)}万

---

## 🎯 核心发现

1. **双均线(${fastPeriod}/${slowPeriod})策略在 ${symbol} 过去${years}年的回测中${totalReturn >= 0 ? "实现正收益" : "未能覆盖成本"}**
2. 年化收益 ${annSign}${(annualized*100).toFixed(2)}% ${trend}，${sharpe > 0 ? `夏普比率 ${sharpeSign}${sharpe.toFixed(2)}（风险调整后收益${sharpe > 1 ? "良好" : "一般"}）` : "夏普比率为负，策略风险收益比欠佳"}
3. 最大回撤 ${maxDrawdown.toFixed(2)}%，发生在 ${ddStart} → ${ddEnd}

---

## 📋 绩效概览

| 指标 | 数值 | 趋势 | 评级 |
|------|------|------|------|
| 总收益率 | ${retSign}${(totalReturn*100).toFixed(2)}% | ${totalReturn>=0?"↑":"↓"} | ${retStars} |
| 年化收益率 | ${annSign}${(annualized*100).toFixed(2)}% | ${annualized>=0?"↑":"↓"} | ${retStars} |
| 夏普比率 | ${sharpeSign}${sharpe.toFixed(2)} | ${sharpe>=0?"↑":"↓"} | ${sharpeStars} |
| 最大回撤 | -${maxDrawdown.toFixed(2)}% | ↓ | ${ddStars} |
| 年化波动率 | ${(annualVol*100).toFixed(2)}% | ${annualVol<0.15?"→":"↑"} | ${annualVol<0.15?"⭐⭐⭐":"⭐⭐"} |
| 最终资产 | ¥${(finalEquity/10000).toFixed(2)}万 | ${finalEquity>=initialCash?"↑":"↓"} | ${finalEquity>=initialCash?"⭐⭐⭐":"⭐"} |
| 盈利次数 | ${buyCount}次 | — | — |
| 亏损次数 | ${sellCount}次 | — | — |

---

## 📈 交易分析

| 指标 | 数值 |
|------|------|
| 总交易次数 | ${totalTrades} 次 |
| 买入信号 | ${buyCount} 次 |
| 卖出信号 | ${sellCount} 次 |
| 胜率 | ${(winRate*100).toFixed(1)}% |
| 盈亏比 | ${profitFactor.toFixed(2)} |
| 平均单次盈利 | ${(avgWin*100).toFixed(2)}% |
| 平均单次亏损 | ${(avgLoss*100).toFixed(2)}% |
| 最大连续盈利 | ${maxWinStreak} 次 |
| 最大连续亏损 | ${maxLossStreak} 次 |
| 平均持仓周期 | ${avgHoldingDays} 个交易日 |

---

## 🐂 最大赢家 & 🐻 最大输家

${buildTradeTable(metrics.equityCurve, metrics.initialCash)}

---

## 📉 权益曲线（年度汇总）

| 期间 | 资产 | 收益 |
|------|------|------|
${equityRows}

---

## ⚙️ 策略信号图

\`\`\`
信号解读（金叉买入，死叉卖出）：
  ↑ MA${fastPeriod} 上穿 MA${slowPeriod} → 买入 ✅
  ↓ MA${fastPeriod} 下穿 MA${slowPeriod} → 卖出 🔴
\`\`\`

---

## 💡 行动建议

| 优先级 | 建议 | 预期效果 |
|--------|------|----------|
| ${sharpe < 0.5 ? "🔴 高" : "🟡 中"} | ${sharpe < 0.5 ? "夏普比率偏低，建议优化参数" : "策略基础收益尚可，考虑加入止损"} | ${sharpe < 0.5 ? "提升风险收益比" : "降低最大回撤"} |
| ${maxDrawdown > 20 ? "🔴 高" : "🟡 中"} | ${maxDrawdown > 20 ? "最大回撤过高，加入移动止损保护" : "回撤可控，可适当加仓"} | ${maxDrawdown > 20 ? "控制回撤在20%以内" : "提升绝对收益"} |
| 🟢 低 | 增加 filters（如放量确认、金叉距死叉>5日） | 减少假信号，提升胜率 |

---

> ⚠️ **风险提示**: 回测结果不代表未来表现。策略未含交易手续费、滑点及流动性风险，实际结果可能低于回测。数据来源于Yahoo Finance/Sina Finance，仅供参考。
`;
}

function buildEquityTable(equityCurve) {
  if (!equityCurve || equityCurve.length === 0) return "| 无数据 | — | — |";
  const byYear = {};
  for (const pt of equityCurve) {
    const y = new Date(pt.date).getFullYear();
    if (!byYear[y]) byYear[y] = { equity: [], dates: [] };
    byYear[y].equity.push(pt.equity);
    byYear[y].dates.push(new Date(pt.date));
  }
  let rows = "";
  const years = Object.keys(byYear).sort();
  for (const y of years) {
    const pts = byYear[y];
    const yearEndDate = new Date(Math.max(...pts.dates.map(d => d.getTime())));
    const yearEndEquity = pts.equity[pts.dates.findIndex(d => d.getTime() === yearEndDate.getTime())];
    const yearStartEquity = pts.equity[0];
    const ret = yearStartEquity > 0 ? ((yearEndEquity - yearStartEquity) / yearStartEquity * 100).toFixed(1) : "—";
    const bar = buildBar(parseFloat(ret));
    const sign = parseFloat(ret) >= 0 ? "+" : "";
    rows += `| ${y}年 | ¥${(yearEndEquity/10000).toFixed(1)}万 | ${sign}${ret}% ${bar} |\n`;
  }
  return rows;
}

function buildTradeTable(equityCurve, initialCash) {
  if (!equityCurve || equityCurve.length < 2) return "| 无交易记录 | — |";
  // 按年度找最大最小权益点
  const byYear = {};
  for (const pt of equityCurve) {
    const y = new Date(pt.date).getFullYear();
    if (!byYear[y]) byYear[y] = [];
    byYear[y].push(pt);
  }
  let rows = [];
  for (const [y, pts] of Object.entries(byYear).sort((a,b)=>a[0]-b[0])) {
    const maxPt = pts.reduce((m, p) => p.equity > m.equity ? p : m, pts[0]);
    const minPt = pts.reduce((m, p) => p.equity < m.equity ? p : m, pts[0]);
    const yRet = ((maxPt.equity - initialCash) / initialCash * 100).toFixed(1);
    rows.push({ year: y, type: "最高", date: formatDate(new Date(maxPt.date)), equity: (maxPt.equity/10000).toFixed(2), ret: yRet });
    rows.push({ year: y, type: "最低", date: formatDate(new Date(minPt.date)), equity: (minPt.equity/10000).toFixed(2), ret: yRet });
  }
  return rows.slice(0, 10).map(r => `| ${r.year}年${r.type} | ${r.date} | ¥${r.equity}万 | ${r.ret >= 0 ? "+" : ""}${r.ret}% |`).join("\n");
}

function buildBar(pct) {
  const bars = Math.min(Math.abs(pct) / 5, 10) | 0;
  return pct >= 0 ? "📈".repeat(Math.max(1, bars)) : "📉".repeat(Math.max(1, bars));
}

// ─── 主程序 ───────────────────────────────────────────────────────────
async function main() {
  console.error(`\n🔧 双均线回测引擎 | ${CONFIG.symbol} | MA${CONFIG.fast}×MA${CONFIG.slow} | 近${CONFIG.years}年\n`);
  console.error("📡 正在获取数据...");

  const data = await fetchData(CONFIG.symbol, CONFIG.years);
  console.error(`✅ 获取到 ${data.length} 个交易日 (${formatDate(data[0].date)} → ${formatDate(data[data.length-1].date)})`);

  console.error("⚙️  运行策略回测...");
  const { trades, equityCurve, finalEquity } = runBacktest(data, CONFIG.fast, CONFIG.slow, CONFIG.initialCash);
  const metrics = calcMetrics(data, equityCurve, trades, CONFIG.initialCash);
  const report = formatReport(metrics, CONFIG.fast, CONFIG.slow, CONFIG.symbol);

  console.log(report);

  // 保存数据
  const outDir = path.join(__dirname, "..", "output");
  try {
    fs.mkdirSync(outDir, { recursive: true });
  } catch (e) {
    console.error("无法创建输出目录，跳过保存");
  }
  const outFile = path.join(outDir, `backtest_${CONFIG.symbol.replace(/\./g, "_")}_${CONFIG.fast}_${CONFIG.slow}.json`);
  try {
    fs.writeFileSync(outFile, JSON.stringify({ metrics, trades, equityCurve }, null, 2));
    console.error(`\n💾 数据已保存: ${outFile}`);
  } catch (e) {
    console.error("保存数据失败:", e.message);
  }
}

main().catch((err) => {
  console.error("❌ 错误:", err.message);
  process.exit(1);
});
