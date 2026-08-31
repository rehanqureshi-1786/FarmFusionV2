# FarmFusion — Best Practical Mandi Mathematical Ranking Specification

**Status**: Active Production Specification  
**Version**: 1.0.0  
**Scope**: Mandi Price Intelligence Agent & Android UI  

---

## 1. Overview & Problem Definition

Traditional agricultural apps often rank mandis solely by **highest recorded modal price**. However, for a rural farmer with small-to-medium harvests, travelling an extra 60–100 km for a marginal ₹30/Quintal price increase is impractical and risks cargo spoilage.

FarmFusion introduces the **Best Practical Mandi** ranking algorithm. It deterministically computes a multi-attribute utility score combining:
1. **Normalized Current Modal Price** ($S_{price}$)
2. **Geodesic Distance Proximity** ($S_{dist}$)
3. **Data Freshness Reliability** ($S_{fresh}$)

> [!IMPORTANT]
> **Strict Non-Fabrication Rule**: FarmFusion does **NOT** estimate fuel costs, road toll charges, or claim "net profit". The practical ranking reflects multi-criteria decision convenience based strictly on verified Agmarknet data.

---

## 2. Deterministic Scoring Formula

For a requested commodity $C$ and candidate mandis $M = \{m_1, m_2, \dots, m_n\}$ within radius $D_{max} = 300\text{ km}$:

$$\text{Practical Score}(m_i) = 0.50 \cdot S_{price}(m_i) + 0.35 \cdot S_{dist}(m_i) + 0.15 \cdot S_{fresh}(m_i)$$

Where:

### A. Price Component ($S_{price} \in [0.0, 1.0]$)
Let $P_i$ be the modal price of candidate $m_i$, $P_{min} = \min_{j} P_j$, and $P_{max} = \max_{j} P_j$:

$$S_{price}(m_i) = \begin{cases} \frac{P_i - P_{min}}{P_{max} - P_{min}} & \text{if } P_{max} > P_{min} \\ 1.0 & \text{otherwise} \end{cases}$$

### B. Distance Component ($S_{dist} \in [0.0, 1.0]$)
Geodesic distance $d_i$ is calculated using the Haversine formula from the farmer's GPS coordinates:

$$S_{dist}(m_i) = \begin{cases} \max\left(0.0, 1.0 - \frac{d_i}{D_{max}}\right) & \text{if } d_i \text{ is known} \\ 0.50 & \text{if coordinates are unresolved} \end{cases}$$

### C. Freshness Component ($S_{fresh} \in [0.0, 1.0]$)
Based on elapsed calendar days $\Delta t = \text{Current Date} - \text{Arrival Date}$:

$$S_{fresh}(m_i) = \begin{cases} 1.00 & \text{if } \Delta t \le 3\text{ days (FRESH)} \\ 0.70 & \text{if } 4 \le \Delta t \le 14\text{ days (RECENT)} \\ 0.40 & \text{if } \Delta t > 14\text{ days (STALE)} \end{cases}$$

---

## 3. Practical Example

Consider a farmer near Udaipur looking to sell **Wheat**:

| Market | Modal Price | Distance | Freshness | $S_{price}$ | $S_{dist}$ | $S_{fresh}$ | $\text{Practical Score}$ | Classification |
|---|---|---|---|---|---|---|---|---|
| **Udaipur Mandi** | ₹2,580/Q | 8.4 km | FRESH | $0.00$ | $0.97$ | $1.00$ | **$0.49$** | ⭐ **Best Practical** (Lowest logistics barrier) |
| **Mavli Mandi** | ₹2,620/Q | 34.0 km | FRESH | $0.44$ | $0.89$ | $1.00$ | **$0.68$** | Nearby Alternative |
| **Salumber Mandi** | ₹2,670/Q | 62.0 km | FRESH | $1.00$ | $0.79$ | $1.00$ | **$0.93$** | 🏆 **Highest Price** |

*Note*: Depending on the candidate pool and relative price spread, the algorithm highlights both the **Best Practical Option** and the **Highest Recorded Price**, enabling the farmer to make an informed trade-off.

---

## 4. Verbalization & Safe Wording

- **Highest Recorded Price**: `"सबसे अधिक दर्ज भाव"`
- **Best Practical Option**: `"सबसे व्यावहारिक विकल्प (भाव + दूरी)"`
- **Voice Response**: *"उपलब्ध भाव और दूरी को देखते हुए उदयपुर (8.4 किमी, ₹2580/Q) सबसे व्यावहारिक विकल्प दिख रही है। सबसे अधिक दर्ज भाव सलूंबर (62 किमी, ₹2670/Q) में है।"*
