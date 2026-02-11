# 📉 Market-Based Target Feasibility Simulator
**「前年比目標」の妥当性を、市場マクロデータに基づいて定量監査するシミュレーター**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://market-based-target-simulator-xxxx.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Type](https://img.shields.io/badge/Type-Financial_Audit-green)

## 📌 Executive Summary
**「市場が縮小しているのに、なぜ目標だけが増えるのか？」**

本ツールは、因習的な「前年比プラス目標（Year-Over-Year Target）」が、実際の市場容量（Market Capacity）とどれだけ乖離しているかを診断する**構造的監査ツール**です。

人口動態・購買力推移・競争環境係数から**「理論的な限界売上（Theoretical Potential）」**を算出し、会社目標とのギャップを**「組織疲弊コスト（Burnout Cost）」**として金額換算します。

---

## 🎯 Business Value
* **Prevent Burnout:** 達成不可能な目標による現場の疲弊・離職を未然に防ぐ。
* **Rationalize Budget:** 「気合い」ではなく「市場データ」に基づいた予算策定を支援。
* **Exit Strategy:** 構造的に成長が見込めない市場からの「戦略的撤退」のエビデンスを提供。

---

## 🛠 Model Logic (Market Capacity Logic)

$$TheoreticalTarget = Actual_{t-1} \times (1 + \Delta Pop) \times (1 + \Delta Income) \times K_{comp}$$

### Burnout Cost Calculation (Sigmoid Function)
組織の疲弊（Burnout）は線形ではなく、閾値を超えると非線形に加速すると仮定し、正規化ロジスティック関数を採用しています。

$$RiskRatio = \frac{1}{1 + e^{-k(Gap - Gap_{threshold})}}$$
*(k=20, Threshold=10% gap)*

---

## 💻 How to Run

```bash
# 1. Clone the repository
git clone [https://github.com/keisuke-data-lab/market-based-target-simulator.git](https://github.com/keisuke-data-lab/market-based-target-simulator.git)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Simulator
streamlit run app.py