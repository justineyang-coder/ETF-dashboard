import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

st.set_page_config(page_title="ETF 대시보드", layout="wide")

TICKERS = {
    "360750": "TIGER 미국S&P500",
    "379810": "KODEX 미국나스닥100",
    "458730": "TIGER 미국배당다우존스",
    "315960": "RISE 대형고배당10TR",
    "329200": "TIGER 리츠부동산인프라",
    "481430": "RISE 국고채10년액티브",
    "136340": "RISE 중기우량회사채",
    "433980": "KODEX TDF2040액티브",
}

def get_etf_data(code):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    closes, dates = [], []
    for page in range(1, 8):
        url = f"https://finance.naver.com/item/sise_day.nhn?code={code}&page={page}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.encoding = "euc-kr"
            soup = BeautifulSoup(r.text, "html.parser")
            for row in soup.select("table.type2 tr"):
                tds = row.select("td")
                if len(tds) < 2:
                    continue
                date_text = tds[0].get_text(strip=True)
                close_text = tds[1].get_text(strip=True).replace(",", "")
                if not date_text or not close_text:
                    continue
                try:
                    closes.append(float(close_text))
                    dates.append(date_text)
                except:
                    pass
        except:
            pass
    if len(closes) < 5:
        return None
    current = closes[0]
    prev = closes[1] if len(closes) > 1 else current
    change = current - prev
    change_pct = (change / prev * 100) if prev else 0
    def ma(n):
        if len(closes) < n:
            return None
        return round(sum(closes[:n]) / n, 0)
    def diff(v):
        if not v:
            return None
        return round((current - v) / v * 100, 2)
    m5, m20, m60, m120 = ma(5), ma(20), ma(60), ma(120)
    return {
        "current": current, "change": change, "change_pct": change_pct,
        "ma5": m5, "ma20": m20, "ma60": m60, "ma120": m120,
        "diff5": diff(m5), "diff20": diff(m20),
        "diff60": diff(m60), "diff120": diff(m120),
        "date": dates[0] if dates else "-",
    }

def fmt(n):
    if n is None: return "-"
    return f"{in
