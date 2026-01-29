# 📈 Tick-by-Tick Option Chain Sentiment Analysis Engine  
*(Python | Live Market Microstructure | Options Analytics)*

A **real-time tick-by-tick option chain data analysis and visualization system** that captures **every market tick**, processes it into structured option metrics, and plots **live sentiment evolution** of the market using advanced option-chain–based indicators.

This project transforms raw option chain ticks into **actionable market sentiment insights**, using **dynamic ATM/OTM logic**, **OI & LTP pressure**, **IV behavior**, and **straddle-based analytics**.

> ⚠️ This project is for **market microstructure research & educational purposes only**.  
> It does **not** provide trading advice or signals.

---

## 🚀 Project Overview

- Tick-by-tick option chain data is **captured and stored**
- Each tick is **processed in real time**
- Metrics are **plotted live** to visualize:
  - Buying vs selling pressure
  - CE vs PE dominance
  - Volatility behavior
  - OI build-up & unwinding
  - Straddle decay / expansion
- Supports **NIFTY, BANKNIFTY, and SENSEX** simultaneously

---

## 🖥 Live Visualization Layout

### 🪟 Window 1 – Multi-Index Sentiment Dashboard

The main window consists of a **3 × 3 grid of subplots**:

| Column | Index |
|------|------|
| Column 1 | **NIFTY** |
| Column 2 | **BANKNIFTY** |
| Column 3 | **SENSEX** |

Each column contains **3 vertically stacked subplots**, performing different layers of sentiment analysis.

> Below explanation focuses on **Column 1 (NIFTY)**.  
> The same logic applies identically to BANKNIFTY and SENSEX.

---

## 📊 Subplot 1 (Row 1): OTM CE vs PE Pressure Analysis

### 🎯 What It Analyzes
- **Change in LTP (CE vs PE)** for **OTM strikes**
- **Change in OI (CE vs PE)** for **OTM strikes**
- Detects which side (Call or Put) is **building pressure**

### 🔄 Dynamic OTM Selection
- OTM strikes are **not fixed**
- As the market moves:
  - ATM shifts
  - OTM strikes are **reselected dynamically**
- Ensures relevance at all times

---

### 📌 Metrics Visualized
- CE OTM LTP change
- PE OTM LTP change
- CE OTM OI change
- PE OTM OI change

These collectively indicate:
- Aggressive buying
- Writing pressure
- Directional bias
- Sentiment imbalance

---

### 🧾 Textual Data Displayed
- Current Time
- Date
- Index Name
- Expiry Date
- DTE (Days to Expiry)
- India VIX
- IV Percentile (6M / 1Y / 2Y)
- CE OI Buildup (reference: previous day close)
- PE OI Buildup (reference: previous day close)
- PCR (OI-based)
- Today’s CE OI Change (reference: today’s open)
- Today’s PE OI Change (reference: today’s open)
- Intraday PCR (based on today’s OI change)

---

## 📊 Subplot 2 (Row 2): Dynamic ATM Straddle Analysis

### 🎯 What It Analyzes
- **Live ATM straddle** (ATM updates dynamically)
- Straddle price vs **Straddle VWAP**
- OBV (On-Balance Volume) of:
  - ATM CE
  - ATM PE

This subplot helps identify:
- Volatility expansion vs decay
- Institutional activity
- Directional conviction beneath straddle movement

---

### 📌 Metrics Visualized
- Live ATM Straddle Price
- Straddle VWAP
- CE OBV (ATM)
- PE OBV (ATM)

---

### 🧾 Textual Data Displayed
- Straddle price at market open (09:15)
- Current straddle price
- Net straddle decay / expansion
- Current ATM CE LTP
- Current ATM PE LTP
- CE OBV (ATM)
- PE OBV (ATM)
- Synthetic ATM strike

---

## 📊 Subplot 3 (Row 3): IV, Delta & Buying Pressure Analysis

### 🎯 What It Analyzes
- Average **OTM IV behavior**
- **Delta changes** (CE & PE)
- **Buying pressure** derived from:
  - Bid vs Ask quantity imbalance

This layer captures **volatility sentiment and order-flow bias**.

---

### 📌 Metrics Visualized
- CE Average OTM IV
- PE Average OTM IV
- CE Delta Change
- PE Delta Change
- CE Buying Pressure
- PE Buying Pressure

---

### 🧾 Textual Data Displayed
- Spot Price
- Synthetic ATM
- CE Avg OTM IV
- PE Avg OTM IV
- CE Buying Pressure (Ask–Bid based)
- PE Buying Pressure (Ask–Bid based)

---

## 🖼 Sample Output

### Live Tick-by-Tick Sentiment Visualization
![Live Option Chain Sentiment](./Images/all_screens.png)

*(All plots update tick-by-tick in real time)*

---

## 🧠 Core Concepts Used

- Tick-by-tick data processing
- Dynamic ATM & OTM selection
- Synthetic ATM calculation
- OI build-up vs unwinding logic
- Straddle VWAP analysis
- OBV-based option flow analysis
- Bid–Ask imbalance for pressure detection
- Multi-timeframe IV percentile context

---

## 🛠 Tech Stack

| Layer | Technology |
|-----|-----------|
| Language | Python 3.10+ |
| Data Feed | Broker WebSocket API |
| Processing | pandas, numpy |
| Plotting | matplotlib |
| Architecture | asyncio + threading |
| Data Storage | In-memory / CSV (optional) |

---

## 📦 Python Libraries Used

```text
pandas
numpy
matplotlib
asyncio
websockets
datetime
