import json, os

ETF_DIR = r"c:\Git-Repo\static-proj\etfbharat\etf"

def load_save(fn, transform_fn):
    path = os.path.join(ETF_DIR, fn)
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    count = 0
    for etf in data:
        if not etf.get('holdings'):
            transform_fn(etf)
            count += 1
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"{fn}: {count} ETFs processed")

# ─── MOMENTUM TEMPLATES ────────────────────────────────────────────────────────

MOMENTUM_30 = [
    {"name":"Zomato","ticker":"ZOMATO","weight":6.78,"sector":"Food Tech","color":"#E91E63",
     "description":"High-momentum food-tech leader. Blinkit quick-commerce driving re-rating. Consistent 12-month price momentum qualifies for Nifty 200 Momentum 30 index."},
    {"name":"Trent Ltd","ticker":"TRENT","weight":6.34,"sector":"Retail","color":"#7B1FA2",
     "description":"Zudio rapid store expansion driving exceptional earnings growth. One of India's best momentum stories across consumer discretionary."},
    {"name":"BSE Ltd","ticker":"BSE","weight":5.89,"sector":"Capital Markets","color":"#F57F17",
     "description":"Derivatives volume surge and GIFT City expansion creating multi-year price momentum. Consistent earnings upgrades."},
    {"name":"Indian Hotels","ticker":"INDHOTEL","weight":5.45,"sector":"Hospitality","color":"#00695C",
     "description":"Tata's Taj brand re-rating on leisure travel boom. New hotel openings and Qmin food delivery brand adding revenue streams."},
    {"name":"Torrent Power","ticker":"TORNTPOWER","weight":5.12,"sector":"Power","color":"#FF8F00",
     "description":"Regulated utility with merchant exposure. Ahmedabad and Surat distribution franchise. Renewable capacity addition driving 15-18% earnings CAGR."},
    {"name":"IRCTC","ticker":"IRCTC","weight":4.56,"sector":"Railway PSU","color":"#2196F3",
     "description":"Monopoly railway catering and internet ticketing. Convenience fee regime fully restored. Travel boom post-COVID driving sustained momentum."},
    {"name":"PB Fintech","ticker":"POLICYBZR","weight":4.23,"sector":"InsurTech","color":"#1976D2",
     "description":"India's largest insurance aggregator achieving path-to-profitability ahead of schedule. Institutional accumulation supporting price momentum."},
    {"name":"Persistent Systems","ticker":"PERSISTENT","weight":3.89,"sector":"IT Services","color":"#1565C0",
     "description":"Mid-cap IT with consistent above-peer revenue growth. GenAI positioning and US healthcare vertical driving multi-year earnings momentum."},
    {"name":"Dixon Technologies","ticker":"DIXON","weight":3.67,"sector":"Electronics Mfg","color":"#0D47A1",
     "description":"India's largest electronics manufacturer. PLI scheme beneficiary assembling Samsung, Motorola phones. Laptop and set-top-box expansion."},
    {"name":"Coforge","ticker":"COFORGE","weight":3.45,"sector":"IT Services","color":"#0277BD",
     "description":"BFSI-focused IT services with consistent deal wins. Revenue growth above tier-1 peers. Strong order book visibility across insurance and banking verticals."},
]

ALPHA_50 = [
    {"name":"Zomato","ticker":"ZOMATO","weight":7.23,"sector":"Food Tech","color":"#E91E63",
     "description":"Highest alpha generator among Nifty 200. Blinkit disruption and margin improvement driving excess returns above benchmark."},
    {"name":"Trent Ltd","ticker":"TRENT","weight":6.89,"sector":"Retail","color":"#7B1FA2",
     "description":"Alpha from Zudio expansion outpacing FMCG and retail sector peers by 3-4x. Consecutive earnings beats vs consensus estimates."},
    {"name":"BSE Ltd","ticker":"BSE","weight":6.45,"sector":"Capital Markets","color":"#F57F17",
     "description":"Capital markets alpha play. Derivatives volume and GIFT City exchanges creating earnings surprise vs sell-side estimates."},
    {"name":"Kaynes Technology","ticker":"KAYNES","weight":5.98,"sector":"Electronics","color":"#4A148C",
     "description":"Electronics manufacturing services with aerospace and defence contracts. Revenue compounding at 50%+ CAGR. Highest alpha in EMS segment."},
    {"name":"Cochin Shipyard","ticker":"COCHINSHIP","weight":5.56,"sector":"Defence Shipbuilding","color":"#1A237E",
     "description":"Naval GDP beneficiary. INS Vikrant domestic aircraft carrier. Massive order backlog generating alpha vs PSU peers."},
    {"name":"Varun Beverages","ticker":"VBL","weight":5.12,"sector":"Beverages","color":"#388E3C",
     "description":"PepsiCo bottler growing faster than parent. International franchise expansion (Africa, Nepal) generating excess returns vs consumer staples index."},
    {"name":"PB Fintech","ticker":"POLICYBZR","weight":4.78,"sector":"InsurTech","color":"#1976D2",
     "description":"Loss-to-profit inflection creating sustained alpha. Insurance penetration expansion creates decade-long earnings growth runway."},
    {"name":"Persistent Systems","ticker":"PERSISTENT","weight":4.34,"sector":"IT Services","color":"#1565C0",
     "description":"Consistent outperformer vs IT sector. Revenue growth 25-30% vs sector 8-12%. Healthcare IT and GenAI positioning drives ongoing alpha."},
    {"name":"Dixon Technologies","ticker":"DIXON","weight":3.89,"sector":"Electronics Mfg","color":"#0D47A1",
     "description":"PLI alpha play with smartphone and laptop assembly scaling. Contract wins from Samsung expansion creating earnings surprise."},
    {"name":"REC Ltd","ticker":"REC","weight":3.45,"sector":"Power Finance","color":"#00838F",
     "description":"Power sector financing PSU benefiting from infrastructure capex. Loan book growing 20%+ with improving asset quality."},
]

LOW_VOL_ALPHA = [
    {"name":"HDFC Bank","ticker":"HDFCBANK","weight":9.87,"sector":"Banking","color":"#1565C0",
     "description":"Low-volatility anchor. Consistent 16-18% ROE, stable NIM, low NPA. Provides volatility dampening in alpha-low-vol composite index."},
    {"name":"Infosys","ticker":"INFY","weight":8.45,"sector":"IT Services","color":"#0277BD",
     "description":"Large-cap IT with consistent dividend yield (2%+) and low price volatility. GenAI deals providing alpha on stable base."},
    {"name":"HUL","ticker":"HINDUNILVR","weight":7.23,"sector":"FMCG","color":"#1E88E5",
     "description":"FMCG defensive with 50%+ ROCE. Low beta stock providing volatility shield. Premium to broader market justified by earnings consistency."},
    {"name":"TCS","ticker":"TCS","weight":6.89,"sector":"IT Services","color":"#283593",
     "description":"India's largest IT with highest earnings consistency and dividend yield in sector. Low volatility anchor in factor blend."},
    {"name":"Bajaj Finance","ticker":"BAJFINANCE","weight":6.34,"sector":"NBFC","color":"#4527A0",
     "description":"King of consumer lending with strong moat. Alpha from credit expansion at controlled risk providing composite factor exposure."},
    {"name":"Asian Paints","ticker":"ASIANPAINT","weight":5.78,"sector":"Paints","color":"#7B1FA2",
     "description":"Duopoly paints market leader. 60%+ gross margins, asset-light model, low earnings volatility. Stable re-decorating cycle."},
    {"name":"Zomato","ticker":"ZOMATO","weight":5.12,"sector":"Food Tech","color":"#E91E63",
     "description":"Alpha contributor from profitability milestone. Blinkit driving growth acceleration creating alpha in otherwise low-volatility composite."},
    {"name":"Trent Ltd","ticker":"TRENT","weight":4.78,"sector":"Retail","color":"#7B1FA2",
     "description":"Controlled alpha exposure from Zudio expansion. Higher alpha with relatively controlled fundamental risk profile."},
    {"name":"Titan Company","ticker":"TITAN","weight":4.45,"sector":"Consumer","color":"#E65100",
     "description":"Watches, jewellery, eyewear — premium consumer market. Stable earnings with aspirational consumption alpha. Tata Group backing."},
    {"name":"Nestle India","ticker":"NESTLEIND","weight":4.12,"sector":"FMCG","color":"#388E3C",
     "description":"Low-volatility consumer staple. Maggi monopoly with premium portfolio of Munch, KitKat, Nescafe. High ROCE with minimal capital requirement."},
]

MIDCAP_MOMENTUM = [
    {"name":"Cochin Shipyard","ticker":"COCHINSHIP","weight":7.45,"sector":"Defence Shipbuilding","color":"#1A237E",
     "description":"Defence and commercial shipbuilding. INS Vikrant manufacturing. Navy modernisation driving multi-year order book and price momentum."},
    {"name":"Kaynes Technology","ticker":"KAYNES","weight":6.89,"sector":"Electronics Mfg","color":"#4A148C",
     "description":"Electronics manufacturing services rapidly scaling. Aerospace, defence and industrial electronics. 50%+ revenue CAGR driving midcap momentum index inclusion."},
    {"name":"BSE Ltd","ticker":"BSE","weight":6.34,"sector":"Capital Markets","color":"#F57F17",
     "description":"Mid-cap capital markets re-rating. Derivatives and GIFT City revenues scaling rapidly. Consistent quarterly earnings upgrades sustaining price momentum."},
    {"name":"Indian Hotels","ticker":"INDHOTEL","weight":5.78,"sector":"Hospitality","color":"#00695C",
     "description":"Taj brand domestic and international expansion. Leisure and business travel recovery with new hotel pipeline adding visibility."},
    {"name":"Torrent Power","ticker":"TORNTPOWER","weight":5.35,"sector":"Power","color":"#FF8F00",
     "description":"Regulated utility with renewable optionality. Ahmedabad distribution franchise re-rating on energy transition theme."},
    {"name":"PB Fintech","ticker":"POLICYBZR","weight":4.89,"sector":"InsurTech","color":"#1976D2",
     "description":"Insurance aggregator at profitability inflection. Midcap momentum inclusion from loss-to-profit transition driving institutional accumulation."},
    {"name":"Persistent Systems","ticker":"PERSISTENT","weight":4.45,"sector":"IT Services","color":"#1565C0",
     "description":"IT mid-cap with highest revenue growth rate. GenAI positioning and US healthcare deals sustaining momentum."},
    {"name":"Varun Beverages","ticker":"VBL","weight":4.12,"sector":"Beverages","color":"#388E3C",
     "description":"PepsiCo franchise bottler growing into Africa and South Asia. Volume growth and margin expansion driving mid-cap consumer momentum."},
    {"name":"Dixon Technologies","ticker":"DIXON","weight":3.78,"sector":"Electronics Mfg","color":"#0D47A1",
     "description":"PLI scheme electronics manufacturing scaling rapidly. Samsung, Motorola smartphone assembly plus laptop and LED TV manufacturing."},
    {"name":"Carborundum Universal","ticker":"CARBORUNIV","weight":3.45,"sector":"Industrials","color":"#37474F",
     "description":"Abrasives and advanced ceramics leader. Industrial cycle recovery driving mid-cap industrial momentum. Export growth to Middle East and Europe."},
]

IPO_HOLDINGS = [
    {"name":"Zomato","ticker":"ZOMATO","weight":12.45,"sector":"Food Tech","color":"#E91E63",
     "description":"Listed 2021. BSE Select IPO largest weight. Profitability milestone achieved. Blinkit quick-commerce expanding nationally."},
    {"name":"LIC of India","ticker":"LICI","weight":10.89,"sector":"Life Insurance","color":"#1A237E",
     "description":"Listed 2022. India's largest insurer. IPO raised Rs 21,000 Cr — India's largest IPO. Government retains 96%+ stake."},
    {"name":"Mankind Pharma","ticker":"MANKIND","weight":9.34,"sector":"Pharmaceuticals","color":"#7B1FA2",
     "description":"Listed 2023. Branded generics across India. Pan-India distribution with 50,000+ outlets. Consumer healthcare brands — Prega News, AcneStar."},
    {"name":"PB Fintech","ticker":"POLICYBZR","weight":8.78,"sector":"InsurTech","color":"#1976D2",
     "description":"Listed 2021. Policybazaar and Paisabazaar platforms. Profitability achieved. India's largest online insurance aggregator."},
    {"name":"Nykaa","ticker":"NYKAA","weight":7.56,"sector":"Beauty Retail","color":"#E91E63",
     "description":"Listed 2021. India's largest beauty and personal care platform. House of brands — Kay Beauty, Nykd. Omnichannel physical + digital."},
    {"name":"JSW Infrastructure","ticker":"JSWINFRA","weight":6.89,"sector":"Port Infrastructure","color":"#0277BD",
     "description":"Listed 2023. India's second-largest private port operator. Mangalore, Goa and Paradip ports. Leveraging JSW Steel captive volumes."},
    {"name":"Honasa Consumer","ticker":"HONASA","weight":5.78,"sector":"D2C Beauty","color":"#558B2F",
     "description":"Listed 2023. Mamaearth, The Derma Co, Aqualogica brands. Direct-to-consumer personal care with digital marketing capabilities."},
    {"name":"SBFC Finance","ticker":"SBFC","weight":4.56,"sector":"NBFC","color":"#FF8F00",
     "description":"Listed 2023. MSME-focused secured lender. Small business loans with gold loan component. Growing rural and semi-urban credit book."},
    {"name":"Godigit Insurance","ticker":"GODIGIT","weight":3.89,"sector":"General Insurance","color":"#00897B",
     "description":"Listed 2024. India's fastest growing general insurer. Digital-first motor and health insurance platform."},
    {"name":"Ola Electric","ticker":"OLAELECTRIC","weight":3.45,"sector":"EV Mobility","color":"#FF6F00",
     "description":"Listed 2024. India's largest EV scooter maker. S1 platform with Ola Gig B2B electric scooter for delivery partners."},
]

MANUFACTURING = [
    {"name":"Larsen & Toubro","ticker":"LT","weight":12.34,"sector":"Engineering & Construction","color":"#1565C0",
     "description":"India's largest engineering and construction conglomerate. Defence, railways, nuclear, green hydrogen projects. Rs 5+ lakh Cr order backlog."},
    {"name":"Siemens India","ticker":"SIEMENS","weight":9.87,"sector":"Industrial Machinery","color":"#1E88E5",
     "description":"Digital industries, smart infrastructure and mobility. Power T&D, railway systems and building automation. Germany-parent technology transfer."},
    {"name":"ABB India","ticker":"ABB","weight":8.56,"sector":"Power & Automation","color":"#FF6F00",
     "description":"Power grids, industrial automation and robotics. Electrification products for India's transformer and motor market. High-margin short-cycle products."},
    {"name":"HAL","ticker":"HAL","weight":7.89,"sector":"Defence Aerospace","color":"#4A148C",
     "description":"India's sole military aircraft manufacturer. LCA Tejas, Dhruv helicopter, HTT-40 trainer. Rs 1.3 lakh Cr order book with export optionality."},
    {"name":"Bharat Electronics","ticker":"BEL","weight":7.23,"sector":"Defence Electronics","color":"#37474F",
     "description":"Radar, sonar, electronic warfare, communication systems for India's armed forces. Rs 65,000 Cr order book. Exports to 25+ countries."},
    {"name":"Bharat Forge","ticker":"BHARATFORG","weight":6.67,"sector":"Auto Components","color":"#880E4F",
     "description":"Global leader in forged components for trucks, cars and industrial applications. Defence vehicle components growing. European and North American supply chain."},
    {"name":"Kaynes Technology","ticker":"KAYNES","weight":5.89,"sector":"Electronics Mfg","color":"#7B1FA2",
     "description":"Aerospace, defence and medical electronics manufacturing services. ITAR-certified Indian EMS company for US defence contracts."},
    {"name":"Thermax","ticker":"THERMAX","weight":5.34,"sector":"Industrial Engineering","color":"#0D47A1",
     "description":"Energy and environment engineering. Boilers, heat exchangers, chillers. Green hydrogen equipment for industrial decarbonisation."},
    {"name":"Dixon Technologies","ticker":"DIXON","weight":4.78,"sector":"Electronics Mfg","color":"#283593",
     "description":"PLI scheme electronics manufacturer. Smartphones, LED TVs, washing machines, set-top boxes. India's largest CE contract manufacturer."},
    {"name":"CG Power","ticker":"CGPOWER","weight":4.23,"sector":"Power Equipment","color":"#00897B",
     "description":"Transformers, switchgear, motors and railway traction systems. Murugappa Group turnaround. Railway electrification boom driving order inflows."},
]

# ─── PSU TEMPLATES ─────────────────────────────────────────────────────────────

PSU_HOLDINGS = [
    {"name":"NTPC Ltd","ticker":"NTPC","weight":18.45,"sector":"Power Generation","color":"#2196F3",
     "description":"India's largest power utility with 73 GW operational capacity. Government holds 51%. Transitioning to renewables with 60 GW RE target by 2032. Regulated tariff model."},
    {"name":"Coal India","ticker":"COALINDIA","weight":15.89,"sector":"Coal Mining","color":"#212121",
     "description":"World's largest coal miner producing 700+ MT annually. Government holds 63%. Dividend yield 6-8%. Essential for India's thermal power generation."},
    {"name":"ONGC","ticker":"ONGC","weight":13.34,"sector":"Oil & Gas","color":"#4CAF50",
     "description":"India's largest oil and gas explorer producing 70% of domestic crude. Government holds 58%. KG deepwater field adding production."},
    {"name":"Power Grid Corporation","ticker":"POWERGRID","weight":10.78,"sector":"Power Transmission","color":"#009688",
     "description":"India's monopoly inter-state power transmission PSU owning 175,000+ circuit km. Government holds 51%. Regulated 15.5% post-tax ROE."},
    {"name":"Indian Oil Corporation","ticker":"IOC","weight":8.56,"sector":"Oil Refining","color":"#F44336",
     "description":"India's largest oil company by revenue with 80 MMTPA refining capacity. 33,000+ fuel stations. Government holds 52%."},
    {"name":"BPCL","ticker":"BPCL","weight":7.23,"sector":"Oil Marketing","color":"#FF6F00",
     "description":"Third-largest PSU oil company. Kochi, Mumbai and Bina refineries. Gas, LNG and EV charging diversification. Privatisation narrative creates re-rating events."},
    {"name":"Bharat Electronics","ticker":"BEL","weight":6.45,"sector":"Defence Electronics","color":"#9C27B0",
     "description":"Defence electronics PSU with Rs 65,000+ Cr order backlog. Radar, sonar, electronic warfare systems. Government holds 51%."},
    {"name":"GAIL India","ticker":"GAIL","weight":5.67,"sector":"Gas Transmission","color":"#00897B",
     "description":"India's largest natural gas marketing and transmission company. 12,000+ km pipeline network. Government holds 51%."},
    {"name":"SAIL","ticker":"SAIL","weight":4.23,"sector":"Steel","color":"#37474F",
     "description":"India's largest integrated steel producer with 19+ MT capacity. Government holds 65%. Five integrated plants across Eastern India."},
    {"name":"HAL","ticker":"HAL","weight":3.45,"sector":"Defence Aerospace","color":"#4A148C",
     "description":"India's sole military aircraft manufacturer. LCA Tejas, Dhruv helicopter. Rs 1.3 lakh Cr order book. Government holds 71%."},
]

MANUFACTURING_PSU = [
    {"name":"Larsen & Toubro","ticker":"LT","weight":15.45,"sector":"Engineering & Construction","color":"#1565C0",
     "description":"India's largest engineering conglomerate. Defence, nuclear, railways, semiconductor fab projects. Nifty India Manufacturing anchor."},
    {"name":"HAL","ticker":"HAL","weight":12.89,"sector":"Defence Aerospace","color":"#4A148C",
     "description":"India's sole military aircraft manufacturer. LCA Tejas and Dhruv helicopter production. Government holds 71%. Rs 1.3 lakh Cr order book."},
    {"name":"Siemens India","ticker":"SIEMENS","weight":9.34,"sector":"Industrial Machinery","color":"#1E88E5",
     "description":"Digital industries, smart infrastructure and mobility. Power T&D and railway systems. Germany-parent technology transfer."},
    {"name":"ABB India","ticker":"ABB","weight":8.78,"sector":"Power & Automation","color":"#FF6F00",
     "description":"Power grids, industrial automation and robotics. Electrification products — transformers, motors, drives for infrastructure build-out."},
    {"name":"BEL","ticker":"BEL","weight":7.56,"sector":"Defence Electronics","color":"#9C27B0",
     "description":"Radar, sonar, electronic warfare manufacturing PSU. Rs 65,000 Cr backlog. Exports to 25+ countries. Government holds 51%."},
    {"name":"Bharat Forge","ticker":"BHARATFORG","weight":6.89,"sector":"Auto Components","color":"#880E4F",
     "description":"Global forged components leader for trucks, passenger cars and defence vehicles. European and North American supply chain."},
    {"name":"Kaynes Technology","ticker":"KAYNES","weight":5.78,"sector":"Electronics Mfg","color":"#7B1FA2",
     "description":"Aerospace, defence and medical EMS. ITAR-certified for US defence contracts. Highest growth EMS play in Indian manufacturing."},
    {"name":"Dixon Technologies","ticker":"DIXON","weight":5.23,"sector":"Electronics Mfg","color":"#283593",
     "description":"PLI electronics manufacturer — smartphones, LED TVs, washing machines. India's largest CE contract manufacturer."},
    {"name":"Thermax","ticker":"THERMAX","weight":4.67,"sector":"Industrial Engineering","color":"#0D47A1",
     "description":"Energy and environment solutions — boilers, heat exchangers, green hydrogen equipment. Industrial decarbonisation and export growth."},
    {"name":"CG Power","ticker":"CGPOWER","weight":3.89,"sector":"Power Equipment","color":"#00897B",
     "description":"Transformers, switchgear, motors and railway traction. Murugappa Group turnaround. Railway electrification driving order wins."},
]

# ─── VALUE / QUALITY / DIVIDEND TEMPLATES ─────────────────────────────────────

NV20_HOLDINGS = [
    {"name":"ITC Ltd","ticker":"ITC","weight":11.45,"sector":"FMCG & Conglomerates","color":"#558B2F",
     "description":"Value index anchor — cigarettes generate Rs 16,000 Cr+ EBIT at 65%+ margins. Trading at 25x PE vs global FMCG at 35-40x. 3%+ dividend yield. Hotels demerger unlocking NAV."},
    {"name":"Coal India","ticker":"COALINDIA","weight":9.87,"sector":"Energy - Mining","color":"#37474F",
     "description":"World's largest coal miner. Dividend yield 5%+ with government-mandated payouts. ROCE above 50% on minimal reinvestment. Classic Graham-style value."},
    {"name":"ONGC","ticker":"ONGC","weight":8.95,"sector":"Oil & Gas","color":"#F57F17",
     "description":"India's largest oil producer. P/B below 1x. KG-DWN deepwater project adding 40,000+ bopd. Perpetually undervalued with high yield."},
    {"name":"Power Grid Corporation","ticker":"POWERGRID","weight":8.12,"sector":"Utilities","color":"#01579B",
     "description":"Monopoly transmission PSU. Regulated 15.5% ROE. Dividend yield 4-5%. RE push adding green energy corridors doubling capex."},
    {"name":"NTPC Ltd","ticker":"NTPC","weight":7.85,"sector":"Utilities","color":"#1A237E",
     "description":"India's power backbone. Regulated tariff guarantees ROE. 60 GW renewable target. Trades below replacement cost. 45%+ dividend payout ratio."},
    {"name":"Vedanta Ltd","ticker":"VEDL","weight":7.23,"sector":"Metals & Mining","color":"#880E4F",
     "description":"Diversified natural resources — zinc, aluminium, iron ore, oil and silver. Dividend yield touches 15-20% in upcycles. India's only primary zinc producer."},
    {"name":"SBI","ticker":"SBIN","weight":6.98,"sector":"Banking - PSU","color":"#1565C0",
     "description":"India's largest bank. P/B ratio 1.2-1.5x vs private peers at 2.5-4x despite comparable ROE (15%+). Subsidiary value creation ongoing."},
    {"name":"HPCL","ticker":"HINDPETRO","weight":4.56,"sector":"Oil & Gas - Refining","color":"#F44336",
     "description":"PSU oil marketing company. Discount to replacement cost. Earnings highly cyclical with marketing margins — value opportunity deepens in downcycles."},
    {"name":"BPCL","ticker":"BPCL","weight":3.87,"sector":"Oil & Gas - Refining","color":"#FF6F00",
     "description":"Third PSU oil company with privatisation narrative. Kochi, Mumbai, Bina refineries. Free cash flow robust in positive marketing margin environments."},
    {"name":"GAIL India","ticker":"GAIL","weight":3.42,"sector":"Gas Distribution","color":"#00897B",
     "description":"Natural gas transmission monopoly. 16,000+ km pipeline. Trading at 10x PE with 3% dividend yield — quintessential value play."},
]

VALUE_30 = [
    {"name":"ITC Ltd","ticker":"ITC","weight":10.23,"sector":"FMCG & Conglomerates","color":"#558B2F",
     "description":"Value index core — cigarettes fund FMCG brands. 25x PE vs global FMCG peers at 35-40x. Hotels demerger unlocking NAV. Consistent 3%+ dividend yield."},
    {"name":"Coal India","ticker":"COALINDIA","weight":9.12,"sector":"Energy - Mining","color":"#37474F",
     "description":"5%+ dividend yield with government-mandated payouts. 50%+ ROCE on minimal capex. Classic value with long-term energy transition risk."},
    {"name":"ONGC","ticker":"ONGC","weight":8.34,"sector":"Oil & Gas","color":"#F57F17",
     "description":"Perpetually undervalued oil producer. P/B below 1x. Value-composite score driven by high dividend yield, low PE and high ROCE."},
    {"name":"Power Grid Corporation","ticker":"POWERGRID","weight":7.89,"sector":"Utilities","color":"#01579B",
     "description":"Regulated monopoly transmission with 4-5% dividend yield. Value inclusion from high dividend yield and low P/B relative to peers."},
    {"name":"NTPC Ltd","ticker":"NTPC","weight":7.23,"sector":"Utilities","color":"#1A237E",
     "description":"Regulated power generator. Trades below replacement cost. High-quality value with 45%+ dividend payout and renewable growth optionality."},
    {"name":"SBI","ticker":"SBIN","weight":6.78,"sector":"Banking - PSU","color":"#1565C0",
     "description":"India's largest bank at 1.2-1.5x P/B vs private peers at 2.5-4x. Value factor inclusion from high ROE-to-P/B spread. Subsidiary value ongoing."},
    {"name":"Vedanta Ltd","ticker":"VEDL","weight":6.23,"sector":"Metals & Mining","color":"#880E4F",
     "description":"Diversified metals giant. Ultra-high dividend yield in commodity upcycles. Broad value-index inclusion on composite scoring."},
    {"name":"Indian Oil Corporation","ticker":"IOC","weight":5.45,"sector":"Oil Refining","color":"#F44336",
     "description":"India's largest oil company by revenue. Trades at 6-8x PE with 4-5% dividend yield. Value inclusion from earnings yield vs book value spread."},
    {"name":"BPCL","ticker":"BPCL","weight":4.78,"sector":"Oil Marketing","color":"#FF6F00",
     "description":"PSU oil company with privatisation optionality. Value-factor inclusion from low P/BV, high earnings yield and above-average dividend payout."},
    {"name":"HPCL","ticker":"HINDPETRO","weight":4.12,"sector":"Oil Refining","color":"#E53935",
     "description":"Upstream refiner and fuel retailer. Cyclical value opportunity — earnings yield attractive against low P/B ratio."},
]

QUALITY_30 = [
    {"name":"TCS","ticker":"TCS","weight":12.45,"sector":"IT Services","color":"#283593",
     "description":"India's quality flagship. 40%+ EBITDA margin, 55%+ ROCE, near-zero debt. Consistent dividend payer with buyback track record. Quality factor anchor."},
    {"name":"Infosys","ticker":"INFY","weight":10.89,"sector":"IT Services","color":"#0277BD",
     "description":"Second-largest IT quality blue chip. 30%+ EBITDA margins, 35%+ ROCE. Consistent earnings and dividend. GenAI via Infosys Topaz platform."},
    {"name":"HUL","ticker":"HINDUNILVR","weight":9.34,"sector":"FMCG","color":"#1E88E5",
     "description":"Consumer quality benchmark. 50%+ ROCE, 20%+ net margin, 5%+ dividend yield. Low earnings variability across economic cycles."},
    {"name":"Nestle India","ticker":"NESTLEIND","weight":8.12,"sector":"FMCG","color":"#388E3C",
     "description":"Maggi monopoly with zero long-term debt. 60%+ ROCE. Premium portfolio of Munch, KitKat, Nescafe. Consistent quality scoring."},
    {"name":"Asian Paints","ticker":"ASIANPAINT","weight":7.56,"sector":"Paints","color":"#7B1FA2",
     "description":"Duopoly paints market leader. 60%+ gross margins, asset-light distribution. B2C brand moat. Quality perennial inclusion."},
    {"name":"Bajaj Finance","ticker":"BAJFINANCE","weight":6.89,"sector":"NBFC","color":"#4527A0",
     "description":"India's highest-quality NBFC. 20%+ ROE, 400M+ customer data asset. Consumer lending with proprietary credit models."},
    {"name":"Titan Company","ticker":"TITAN","weight":6.23,"sector":"Consumer","color":"#E65100",
     "description":"Watches, jewellery, eyewear — premium aspirational consumer. 25%+ ROCE, consistent cash generation. Tata Group quality governance."},
    {"name":"HDFC Bank","ticker":"HDFCBANK","weight":5.67,"sector":"Banking","color":"#1565C0",
     "description":"Quality banking franchise. 16-18% ROE, 1.1-1.2% RoA, lowest NPA among peers. Consistent dividend. Largest private bank by market cap."},
    {"name":"Wipro","ticker":"WIPRO","weight":5.12,"sector":"IT Services","color":"#006064",
     "description":"IT services with consistent quality metrics. Capital allocation discipline — recurring buybacks. Diversified BFSI, healthcare and energy verticals."},
    {"name":"Pidilite Industries","ticker":"PIDILITIND","weight":4.45,"sector":"Adhesives","color":"#FF8F00",
     "description":"Fevicol monopoly in wood adhesives. Consumer and construction segments. 35%+ ROCE with low debt. Massive distribution network."},
]

DIVIDEND_HOLDINGS = [
    {"name":"Coal India","ticker":"COALINDIA","weight":14.56,"sector":"Energy - Mining","color":"#37474F",
     "description":"Highest dividend yielder in Nifty 500 at 5-8% annually. Government mandated dividend payouts — 50%+ of profits distributed. Minimal capex requirement."},
    {"name":"ONGC","ticker":"ONGC","weight":12.89,"sector":"Oil & Gas","color":"#F57F17",
     "description":"Consistent 4-5% dividend yield. Government-owned oil company with mandatory dividend policy. ONGC Videsh cash flows supporting dividend capacity."},
    {"name":"IOC","ticker":"IOC","weight":11.34,"sector":"Oil Refining","color":"#F44336",
     "description":"India's largest oil company by revenue. 4-5% dividend yield with consistent payout. Dividend Opportunities 50 inclusion from high trailing yield."},
    {"name":"Power Grid Corporation","ticker":"POWERGRID","weight":10.12,"sector":"Utilities","color":"#01579B",
     "description":"Regulated utility mandated to distribute dividends. 4-5% yield. Inflation-indexed tariff escalation ensures growing dividend capacity."},
    {"name":"ITC Ltd","ticker":"ITC","weight":9.45,"sector":"FMCG & Conglomerates","color":"#558B2F",
     "description":"Highest dividend yield among Nifty 50 FMCG at 3%+. Cigarettes generative Rs 16,000 Cr+ EBIT funding generous dividend payouts."},
    {"name":"Infosys","ticker":"INFY","weight":8.23,"sector":"IT Services","color":"#0277BD",
     "description":"Consistent 2%+ dividend yield plus special dividends. Buyback programme supplementing regular payout. IT sector's most consistent dividend track record."},
    {"name":"NTPC","ticker":"NTPC","weight":7.67,"sector":"Utilities","color":"#1A237E",
     "description":"45%+ profit distributed as dividend. Government holds 51% requiring consistent payouts. Regulated ROE ensures dividend sustainability."},
    {"name":"GAIL India","ticker":"GAIL","weight":6.89,"sector":"Gas Distribution","color":"#00897B",
     "description":"3% dividend yield at current market price. Government-owned gas transmission monopoly with stable cash flows."},
    {"name":"HPCL","ticker":"HINDPETRO","weight":5.34,"sector":"Oil Marketing","color":"#E53935",
     "description":"High but volatile dividend yield (3-6%) tied to marketing margins. Deep value dividend play when crude prices stabilise."},
    {"name":"SBI","ticker":"SBIN","weight":4.78,"sector":"Banking - PSU","color":"#1565C0",
     "description":"Growing dividend from rising profits. Government holds 57% requiring mandatory annual dividends. PSU bank profitability normalising post-NPA cycle."},
]

MIDCAP_QUALITY = [
    {"name":"Persistent Systems","ticker":"PERSISTENT","weight":8.45,"sector":"IT Services","color":"#1565C0",
     "description":"Mid-cap quality IT leader. 30%+ revenue growth with 20%+ ROE. Consistent earnings beats. High ROCE, low debt and earnings consistency."},
    {"name":"Coforge","ticker":"COFORGE","weight":7.89,"sector":"IT Services","color":"#0277BD",
     "description":"BFSI IT services with quality metrics — consistent deal wins, improving margins, low leverage. Mid-cap quality inclusion from earnings consistency."},
    {"name":"Varun Beverages","ticker":"VBL","weight":7.34,"sector":"Beverages","color":"#388E3C",
     "description":"PepsiCo bottler with highest quality mid-cap profile. 25%+ ROCE, expanding geographic franchise. Earnings consistency from PepsiCo partnership."},
    {"name":"Kaynes Technology","ticker":"KAYNES","weight":6.78,"sector":"Electronics Mfg","color":"#4A148C",
     "description":"High-ROCE EMS company with aerospace and defence contracts providing revenue visibility. 50%+ revenue CAGR with consistent margin expansion."},
    {"name":"Indian Hotels","ticker":"INDHOTEL","weight":6.23,"sector":"Hospitality","color":"#00695C",
     "description":"Tata's Taj brand with consistent ROCE improvement post-COVID. Quality hospitality stock with expanding footprint and improving asset turn."},
    {"name":"Torrent Pharmaceuticals","ticker":"TORNTPHARM","weight":5.67,"sector":"Pharmaceuticals","color":"#9C27B0",
     "description":"Mid-cap pharma quality play. Germany, Brazil and emerging markets branded generics. Low debt, high margins, consistent FCF generation."},
    {"name":"Voltas","ticker":"VOLTAS","weight":5.12,"sector":"Consumer Durables","color":"#0D47A1",
     "description":"Tata's AC and cooling equipment maker. Unitary cooling market leader. Quality mid-cap consumer brand leveraging India's heat-wave driven AC penetration boom."},
    {"name":"Mphasis","ticker":"MPHASIS","weight":4.67,"sector":"IT Services","color":"#283593",
     "description":"BFSI-focused IT services with Blackstone ownership. BPS+IT convergence model. Consistent mid-teen revenue growth with quality factor driven by return metrics."},
    {"name":"Blue Star","ticker":"BLUESTAR","weight":4.23,"sector":"Consumer Durables","color":"#1976D2",
     "description":"Commercial refrigeration and AC player. B2B and B2C mix. Growing channel distribution. Quality mid-cap industrial consumer play."},
    {"name":"Schaeffler India","ticker":"SCHAEFFLER","weight":3.89,"sector":"Auto Components","color":"#FF8F00",
     "description":"German-parent bearing manufacturer for auto and industrial applications. High ROCE in import-substitute precision engineering. Mid-cap industrial quality anchor."},
]

FLEXICAP_QUALITY = [
    {"name":"TCS","ticker":"TCS","weight":10.23,"sector":"IT Services","color":"#283593",
     "description":"Large-cap quality anchor. 40%+ EBITDA margin, zero debt, consistent dividend. Quality factor cornerstone across flexicap universe."},
    {"name":"Infosys","ticker":"INFY","weight":8.67,"sector":"IT Services","color":"#0277BD",
     "description":"Large-cap quality. 30%+ EBITDA margins, GenAI positioning. Consistent dividend and buyback programme."},
    {"name":"HUL","ticker":"HINDUNILVR","weight":7.89,"sector":"FMCG","color":"#1E88E5",
     "description":"Consumer quality across market caps. 50%+ ROCE. Unilever-parent global playbook localised for India. Low earnings variability."},
    {"name":"Bajaj Finance","ticker":"BAJFINANCE","weight":7.23,"sector":"NBFC","color":"#4527A0",
     "description":"Mid-large NBFC with quality profile — 20%+ ROE, proprietary credit models, 400M+ customer dataset."},
    {"name":"Asian Paints","ticker":"ASIANPAINT","weight":6.56,"sector":"Paints","color":"#7B1FA2",
     "description":"Duopoly paints quality. 60%+ gross margins, asset-light distribution. Quality-factor perennial inclusion across flexicap universe."},
    {"name":"Persistent Systems","ticker":"PERSISTENT","weight":5.89,"sector":"IT Services","color":"#1565C0",
     "description":"Mid-cap quality IT. Highest revenue growth in sector with consistent ROCE improvement. Flexicap bridge from mid to large quality."},
    {"name":"Varun Beverages","ticker":"VBL","weight":5.34,"sector":"Beverages","color":"#388E3C",
     "description":"PepsiCo bottler with highest-quality mid-cap composite score. Geographic franchise expansion driving earnings with high ROCE."},
    {"name":"Titan Company","ticker":"TITAN","weight":4.78,"sector":"Consumer","color":"#E65100",
     "description":"Premium consumer brands — watches, jewellery, eyewear. 25%+ ROCE, Tata Group governance. Quality perennial across market cap bands."},
    {"name":"Nestle India","ticker":"NESTLEIND","weight":4.23,"sector":"FMCG","color":"#388E3C",
     "description":"Large-cap quality FMCG. Maggi duopoly, 60%+ ROCE, zero debt. Most quality-consistent brand in Nifty 500 universe."},
    {"name":"Coforge","ticker":"COFORGE","weight":3.67,"sector":"IT Services","color":"#006064",
     "description":"Mid-cap IT quality. BFSI-focused deal wins, low leverage, improving margins. Flexicap quality bridge."},
]

# ─── ROUTING LOGIC ─────────────────────────────────────────────────────────────

def route_momentum(etf):
    idx = etf['index']['name'].lower()
    ticker = etf['ticker'].upper()
    if 'alpha low' in idx or 'low-vol' in idx or 'alpl30' in ticker:
        etf['holdings'] = LOW_VOL_ALPHA
    elif 'alpha' in idx:
        etf['holdings'] = ALPHA_50
    elif 'midcap' in idx or 'midsmall' in idx or 'mid small' in idx:
        etf['holdings'] = MIDCAP_MOMENTUM
    elif 'ipo' in idx:
        etf['holdings'] = IPO_HOLDINGS
    elif 'manufacturing' in idx:
        etf['holdings'] = MANUFACTURING
    else:
        etf['holdings'] = MOMENTUM_30

def route_psu(etf):
    idx = etf['index']['name'].lower()
    if 'manufacturing' in idx:
        etf['holdings'] = MANUFACTURING_PSU
    else:
        etf['holdings'] = PSU_HOLDINGS

def route_value(etf):
    idx = etf['index']['name'].lower()
    ticker = etf['ticker'].upper()
    if 'dividend' in idx:
        etf['holdings'] = DIVIDEND_HOLDINGS
    elif 'quality' in idx or 'qual' in ticker.lower() or 'qlty' in ticker.lower():
        if 'midcap' in idx or 'mid cap' in idx or 'midq' in ticker.lower():
            etf['holdings'] = MIDCAP_QUALITY
        elif 'flexicap' in idx or 'flexi' in idx:
            etf['holdings'] = FLEXICAP_QUALITY
        else:
            etf['holdings'] = QUALITY_30
    elif 'value 30' in idx or 'value 50' in idx or 'nifty200' in idx or 'nifty500' in idx:
        etf['holdings'] = VALUE_30
    else:
        etf['holdings'] = NV20_HOLDINGS

# ─── RUN ──────────────────────────────────────────────────────────────────────

load_save("thematic---momentum.json", route_momentum)
load_save("thematic---psu.json", route_psu)
load_save("thematic---value.json", route_value)

print("\nBatch 6 complete!")
