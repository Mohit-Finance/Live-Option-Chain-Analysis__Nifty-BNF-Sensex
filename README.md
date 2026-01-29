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

### 🧾 Textual Data Displayed
- Straddle price at market open (09:15)
- Current straddle price
- Net straddle decay / expansion
- Current ATM CE OBV
- Current ATM PE OBV
- Synthetic ATM strike

---

## 📊 Subplot 3 (Row 3): IV, Delta & Buying Pressure Analysis

### 🎯 What It Analyzes
- Average **OTM IV behavior**
- **Delta changes** (CE & PE)
- **Buying pressure** derived from bid–ask quantity imbalance

---

### 🧾 Textual Data Displayed
- Spot Price
- Synthetic ATM
- CE Avg OTM IV
- PE Avg OTM IV
- CE Buying Pressure
- PE Buying Pressure

---

## 🪟 Window 2 – Tick-by-Tick Strike-Level Pressure Dashboard

This window provides a **high-resolution, strike-specific view** of **immediate price and pressure behavior** using **LTP vs VWAP** comparisons.

- Layout: **3 × 3 grid**
- Index selection:
  - NIFTY
  - BANKNIFTY
  - SENSEX
- When an index is selected (e.g., NIFTY), **the entire window focuses on that index only**

---

### 🎯 Central Focus: ATM Straddle (2 × 2 Block)

- The **center 2 × 2 area** plots:
  - **ATM Straddle LTP vs VWAP**
- Represents the **core volatility and sentiment zone**
- ATM strike can be:
  - Selected **automatically** (current ATM)
  - Selected **manually** (user-defined strike)

---

### 📉 Left Side: ATM Put & OTM Put Analysis

- Immediate **left of the 2 × 2 center**:
  - ATM **PE LTP vs VWAP**
- **Top row** plots:
  - **OTM PE strikes above ATM**
  - PE LTP vs VWAP
- Total coverage:
  - **ATM PE**
  - **Up to 4 OTM PE strikes**

This reveals **downside pressure buildup** and defensive positioning.

---

### 📈 Right & Bottom Side: ATM Call & OTM Call Analysis

- Immediate **right of the 2 × 2 center**:
  - ATM **CE LTP vs VWAP**
- **Bottom row** plots:
  - **OTM CE strikes above ATM**
  - CE LTP vs VWAP
- Total coverage:
  - **ATM CE**
  - **Up to 4 OTM CE strikes**

This highlights **upside aggression and call-side dominance**.

---

### 🧠 What Window 2 Reveals

- Instant **price vs VWAP divergence**
- Tick-level **pressure buildup**
- Early **sentiment shifts**
- Real-time **volatility expansion or contraction**
- CE vs PE dominance at and around ATM

This window acts as a **microscope**, while Window 1 acts as a **macro sentiment scanner**.

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
- Straddle VWAP behavior
- OBV-based option flow
- Bid–ask imbalance analysis
- Strike-level VWAP interaction

---

## 🛠 Tech Stack

| Layer | Technology |
|-----|-----------|
| Language | Python 3.10+ |
| Data Feed | Broker WebSocket API |
| Processing | pandas, numpy |
| Visualization | pyqtgraph |
| Architecture | Event-driven (tick-based) |
| Data Storage | In-memory / CSV (optional) |

---

## 📦 Python Libraries Used

```text
pandas
numpy
pyqtgraph
websockets
datetime
