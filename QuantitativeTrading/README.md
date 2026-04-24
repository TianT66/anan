# 量化交易系统

> 基于 Python 的自动化量化交易系统

## 📋 功能规划

- [ ] 数据采集模块（股票、期货、数字货币）
- [ ] 策略回测引擎
- [ ] 技术指标计算
- [ ] 交易信号生成
- [ ] 模拟交易执行
- [ ] 风险管理系统
- [ ] 业绩归因分析
- [ ] Web 可视化界面

## 🛠️ 技术栈

- Python 3.10+
- Pandas / NumPy - 数据处理
- TuShare / AKShare - 行情数据
- Backtrader - 策略回测
- Flask / FastAPI - Web 服务
- MySQL / SQLite - 数据存储

## 🚀 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## 📁 项目结构

```
QuantitativeTrading/
├── config/          # 配置文件
├── data/            # 数据存储
├── strategies/      # 交易策略
├── backtest/       # 回测引擎
├── trading/         # 实盘交易
├── utils/          # 工具函数
└── main.py         # 主程序入口
```
