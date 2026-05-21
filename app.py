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
        url = "https://finance.naver.com/item/sise_day.nhn?code=" + code + "&page=" + str(page)
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
    if n is None:
        return "-"
    return "{:,}".format(int(n))

def diff_str(d):
    if d is None:
        return "-"
    sign = "+" if d >= 0 else ""
    return sign + str(d) + "%"

KST = pytz.timezone("Asia/Seoul")
now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

st.title("ETF 이동평균 대시보드")
st.caption("네이버 금융 기준 · 업데이트: " + now + " (KST)")

if st.button("새로고침"):
    st.rerun()

st.divider()

with st.spinner("데이터 불러오는 중..."):
    for code, name in TICKERS.items():
        d = get_etf_data(code)
        if not d:
            st.error(code + " " + name + " 데이터 수신 실패")
            continue
        chg_color = "normal" if d["change"] >= 0 else "inverse"
        sign = "+" if d["change"] >= 0 else ""
        col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1.5, 1, 1, 1, 1])
        with col1:
            st.markdown("**" + name + "**")
            st.caption(code + " · " + d["date"])
        with col2:
            st.metric(
                label="현재가",
                value=fmt(d["current"]),
                delta=sign + str(round(d["change_pct"], 2)) + "%",
                delta_color=chg_color
            )
        with col3:
            color5 = "🟢" if (d["diff5"] or 0) >= 0 else "🔴"
            st.metric(label="5일 MA", value=fmt(d["ma5"]))
            st.caption(color5 + " " + diff_str(d["diff5"]))
        with col4:
            color20 = "🟢" if (d["diff20"] or 0) >= 0 else "🔴"
            st.metric(label="20일 MA", value=fmt(d["ma20"]))
            st.caption(color20 + " " + diff_str(d["diff20"]))
        with col5:
            color60 = "🟢" if (d["diff60"] or 0) >= 0 else "🔴"
            st.metric(label="60일 MA", value=fmt(d["ma60"]))
            st.caption(color60 + " " + diff_str(d["diff60"]))
        with col6:
            color120 = "🟢" if (d["diff120"] or 0) >= 0 else "🔴"
            st.metric(label="120일 MA", value=fmt(d["ma120"]))
            st.caption(color120 + " " + diff_str(d["diff120"]))
        st.divider()

st.caption("🟢 현재가가 이평선 위 · 🔴 현재가가 이평선 아래")
