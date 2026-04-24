# -*- coding: utf-8 -*-
import urllib.request

stocks = [
    ('sz300760', '300760', '\u90fd\u745e\u533b\u7597', 178.48, 164.20),
    ('sh601899', '601899', '\u7d2b\u91d1\u77ff\u4e1a', None, None),
    ('sh600309', '600309', '\u4e07\u534e\u5316\u5b66', 79.18, 72.85),
    ('sh515980', '515980', 'AI ETF', 1.01, None),
    ('sh562500', '562500', '\u673a\u5668\u4ebaETF', None, None),
    ('sh159998', '159998', '\u8ba1\u7b97\u673aETF', None, None),
]

for sym, code, name, cost, stop in stocks:
    try:
        url = 'https://hq.sinajs.cn/list=' + sym
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://finance.sina.com.cn'})
        with urllib.request.urlopen(req, timeout=5) as r:
            raw = r.read().decode('gbk', errors='replace')
        content = raw.split('"')[1]
        parts = content.split(',')
        price = float(parts[3])
        yclose = float(parts[2])
        high = float(parts[4])
        low = float(parts[5])
        pct = (price - yclose) / yclose * 100
        note = ''
        if cost is not None:
            pnl = (price - cost) / cost * 100
            note = ' ' + ('\u6d6e\u76c8%.2f%%' % pnl)
            if stop is not None:
                note += (' \u6b62\u635d%d' % stop)
        print('%s(%s): %.3f (%+.2f%%) H:%.3f L:%.3f%s' % (name, code, price, pct, high, low, note))
    except Exception as e:
        print('%s(%s): error %s' % (name, code, e))
