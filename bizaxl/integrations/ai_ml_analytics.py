# Copyright (c) 2026, bizaxl Optimisations LLP and contributors
# For license information, please see license.txt

"""
AI / ML Analytics Engine — Stub-to-Live Integration

Portfolio risk analytics, tax-loss harvesting opportunities, rebalancing recommendations,
and intelligent investment insights powered by AI/ML models.

Supports:
1. Portfolio Risk Analytics — Sharpe, Alpha, Beta, VaR, stress testing
2. Tax-Loss Harvesting — Identify loss positions, FIFO/LIFO optimization
3. Rebalancing Recommendations — Target allocation vs current, drift analysis
4. Performance Attribution — TWRR/MWRR, Brinson attribution, sector analysis
5. Market Regime Detection — Trend classification (bull/bear/sideways)
6. NLP Sentiment Analysis — News/social sentiment for portfolio holdings

Stub mode: Algorithmic calculations with realistic test data
Live mode: Integrates with TensorFlow/PyTorch models or cloud ML services
"""

import frappe
import json
import math
import random
from datetime import datetime, timedelta, date
from frappe.utils import now_datetime, today, random_string, get_datetime, flt
from frappe import _

from bizaxl.bizaxl.integrations.base_connector import BaseConnector


class MLAnalyticsConnector(BaseConnector):
    """AI/ML Analytics Engine — risk, tax harvesting, rebalancing, insights."""

    connector_name = "ai_ml_analytics"
    label = "AI / ML Analytics Engine"
    settings_doctype = "Integration Settings"

    def _has_credentials(self):
        return bool(self._get_api_key() and self._get_api_secret())

    # =========================================================================
    # PUBLIC API: Risk Analytics
    # =========================================================================

    def calculate_risk_metrics(self, portfolio_returns, benchmark_returns, risk_free_rate=6.5, lookback_months=12):
        """Compute complete risk metrics: Sharpe, Sortino, Alpha, Beta, VaR, etc."""
        try:
            if self.is_stub:
                result = self._stub_risk_metrics(portfolio_returns, benchmark_returns, risk_free_rate, lookback_months)
            else:
                result = self._live_risk_metrics(portfolio_returns, benchmark_returns, risk_free_rate, lookback_months)
            self.log_request("calculate_risk_metrics",
                             {"lookback_months": lookback_months, "risk_free_rate": risk_free_rate}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    def run_stress_test(self, portfolio_holdings, scenarios=None):
        """Run stress tests against predefined scenarios (2008 crash, COVID, etc.)."""
        try:
            if self.is_stub:
                result = self._stub_stress_test(portfolio_holdings, scenarios)
            else:
                result = self._live_stress_test(portfolio_holdings, scenarios)
            self.log_request("run_stress_test", {"holdings_count": len(portfolio_holdings or [])}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Tax-Loss Harvesting
    # =========================================================================

    def find_tax_harvest_opportunities(self, holdings, portfolio_value, tax_slab="30%"):
        """Identify tax-loss harvesting opportunities across holdings."""
        try:
            if self.is_stub:
                result = self._stub_tax_harvest(holdings, portfolio_value, tax_slab)
            else:
                result = self._live_tax_harvest(holdings, portfolio_value, tax_slab)
            self.log_request("find_tax_harvest_opportunities",
                             {"holdings_count": len(holdings or []), "portfolio_value": portfolio_value}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Rebalancing
    # =========================================================================

    def recommend_rebalance(self, current_allocation, target_allocation, drift_threshold=5.0):
        """Generate portfolio rebalancing recommendations based on drift."""
        try:
            if self.is_stub:
                result = self._stub_rebalance(current_allocation, target_allocation, drift_threshold)
            else:
                result = self._live_rebalance(current_allocation, target_allocation, drift_threshold)
            self.log_request("recommend_rebalance",
                             {"target_asset_count": len(target_allocation or [])}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Performance Attribution
    # =========================================================================

    def calculate_performance_attribution(self, portfolio_returns, benchmark_returns, sectors):
        """Calculate Brinson-style performance attribution."""
        try:
            if self.is_stub:
                result = self._stub_attribution(portfolio_returns, benchmark_returns, sectors)
            else:
                result = self._live_attribution(portfolio_returns, benchmark_returns, sectors)
            self.log_request("calculate_performance_attribution",
                             {"sectors_count": len(sectors or [])}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: Market Regime Detection
    # =========================================================================

    def detect_market_regime(self, index_values, lookback_days=252):
        """Detect current market regime using trend/momentum analysis."""
        try:
            if self.is_stub:
                result = self._stub_market_regime(index_values, lookback_days)
            else:
                result = self._live_market_regime(index_values, lookback_days)
            self.log_request("detect_market_regime", {"lookback_days": lookback_days}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # PUBLIC API: NLP Sentiment
    # =========================================================================

    def analyze_sentiment(self, texts, entities=None):
        """Analyze sentiment of news/articles for portfolio holdings."""
        try:
            if self.is_stub:
                result = self._stub_sentiment(texts, entities)
            else:
                result = self._live_sentiment(texts, entities)
            self.log_request("analyze_sentiment", {"texts_count": len(texts or [])}, result)
            return result
        except Exception as e:
            return {"status": "Error", "error": str(e), "mode": self.mode}

    # =========================================================================
    # STUB IMPLEMENTATIONS
    # =========================================================================

    def _stub_risk_metrics(self, portfolio_returns, benchmark_returns, risk_free_rate, lookback_months):
        """Algorithmic risk metric computation (no ML model needed for stub)."""
        # Simulate realistic risk metrics
        port_return = random.uniform(8.0, 18.0)
        port_vol = random.uniform(10.0, 22.0)
        bench_return = random.uniform(9.0, 16.0)
        bench_vol = random.uniform(12.0, 20.0)

        beta = round(random.uniform(0.75, 1.25), 2)
        alpha = round(port_return - (risk_free_rate + beta * (bench_return - risk_free_rate)), 2)
        sharpe = round((port_return - risk_free_rate) / port_vol, 4) if port_vol > 0 else 0
        tracking_error = round(abs(port_vol - bench_vol) + random.uniform(0, 0.5), 2)
        info_ratio = round((port_return - bench_return) / tracking_error if tracking_error > 0 else 0, 4)
        sortino = round((port_return - risk_free_rate) / (port_vol * 0.65), 4)  # Approximate downside deviation
        var_95 = round(port_vol * 1.645 * -1, 2)
        var_99 = round(port_vol * 2.326 * -1, 2)
        max_dd = round(random.uniform(-25, -8), 2)
        r_squared = round(beta * beta * random.uniform(0.5, 1.0) * 100, 2)

        return {
            "status": "Success",
            "mode": "stub",
            "metrics": {
                "portfolio_return": port_return,
                "portfolio_volatility": port_vol,
                "benchmark_return": bench_return,
                "benchmark_volatility": bench_vol,
                "beta": beta,
                "alpha": alpha,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "information_ratio": info_ratio,
                "tracking_error": tracking_error,
                "r_squared": r_squared,
                "var_95": var_95,
                "var_99": var_99,
                "max_drawdown": max_dd,
                "risk_free_rate": risk_free_rate,
                "up_capture_ratio": round(random.uniform(80, 120), 2),
                "down_capture_ratio": round(random.uniform(60, 110), 2),
                "calmar_ratio": round(abs(port_return - risk_free_rate) / abs(max_dd) if max_dd != 0 else 0, 4),
            },
            "model_version": "ml-analytics-v2.4",
            "confidence_interval": "95%",
        }

    def _stub_stress_test(self, portfolio_holdings, scenarios):
        """Simulate stress test scenarios."""
        default_scenarios = scenarios or ["2008 Financial Crisis", "COVID-19 2020", "Rate Hike 2023",
                                          "Currency Crisis", "Geopolitical Tensions", "Custom Shock"]
        results = []
        base_value = random.uniform(1000000, 100000000)

        impacts = {
            "2008 Financial Crisis": {"impact": -0.42, "vol_increase": 2.5},
            "COVID-19 2020": {"impact": -0.32, "vol_increase": 2.0},
            "Rate Hike 2023": {"impact": -0.12, "vol_increase": 1.3},
            "Currency Crisis": {"impact": -0.18, "vol_increase": 1.6},
            "Geopolitical Tensions": {"impact": -0.25, "vol_increase": 1.8},
            "Custom Shock": {"impact": -0.15, "vol_increase": 1.4},
        }

        for sc in default_scenarios:
            imp = impacts.get(sc, {"impact": -0.20, "vol_increase": 1.5})
            projected_value = base_value * (1 + imp["impact"] + random.uniform(-0.03, 0.03))
            results.append({
                "scenario_name": sc,
                "impact_percentage": round(imp["impact"] * 100 + random.uniform(-3, 3), 2),
                "portfolio_value_before": round(base_value),
                "portfolio_value_after": round(projected_value),
                "loss_amount": round(base_value - projected_value),
                "volatility_multiplier": imp["vol_increase"],
                "recovery_estimate_months": random.randint(3, 18),
                "probability": round(random.uniform(5, 30), 1),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "scenarios_tested": len(results),
            "worst_case": min(results, key=lambda r: r["impact_percentage"]),
            "scenarios": results,
            "portfolio_value": round(base_value),
        }

    def _stub_tax_harvest(self, holdings, portfolio_value, tax_slab):
        """Simulate tax-loss harvesting opportunity identification."""
        opportunities = []
        total_loss = 0

        # Generate 0-3 harvest opportunities
        harvestable = holdings or []
        for i, h in enumerate(harvestable):
            if random.random() < 0.25:  # 25% chance of loss position
                loss_percent = random.uniform(-25, -3)
                loss_amount = (portfolio_value / len(harvestable)) * abs(loss_percent) / 100
                total_loss += loss_amount
                tax_savings = loss_amount * float(tax_slab.replace("%", "")) / 100
                opportunities.append({
                    "holding": h.get("name", h.get("holding", f"Holding-{i+1}")),
                    "unrealized_loss_percent": round(loss_percent, 2),
                    "unrealized_loss_amount": round(loss_amount, 2),
                    "holding_period_days": random.randint(30, 800),
                    "short_term": random.choice([True, False]),
                    "recommended_action": "Sell to harvest loss",
                    "suggested_replacement": random.choice([
                        "Nifty 50 ETF", "HDFC Bank", "ICICI Prudential", "Axis Bluechip Fund",
                        "SBI Equity Hybrid", "Kotak Standard Multicap",
                    ]),
                    "tax_savings": round(tax_savings, 2),
                    "wash_sale_applicable": False,
                    "strategy": "Short-term" if random.random() < 0.5 else "Long-term",
                })

        return {
            "status": "Success",
            "mode": "stub",
            "opportunities_found": len(opportunities),
            "total_harvestable_loss": round(total_loss, 2),
            "estimated_tax_savings": round(sum(o["tax_savings"] for o in opportunities), 2),
            "opportunities": opportunities,
            "recommendations": [
                "Consider harvesting losses before quarter end",
                "Review wash-sale rules for replacement securities",
                "Consider gold ETF as temporary substitute for equity exposure",
            ] if opportunities else ["No tax-loss harvesting opportunities identified at this time."],
        }

    def _stub_rebalance(self, current_allocation, target_allocation, drift_threshold):
        """Simulate rebalancing recommendations."""
        actions = []
        total_drift = 0
        max_drift = 0

        targets = target_allocation or [
            {"asset": "Equity", "target": 60},
            {"asset": "Debt", "target": 25},
            {"asset": "Gold", "target": 10},
            {"asset": "Cash", "target": 5},
        ]
        currents = current_allocation or [
            {"asset": "Equity", "current": random.uniform(55, 68)},
            {"asset": "Debt", "current": random.uniform(20, 30)},
            {"asset": "Gold", "current": random.uniform(7, 14)},
            {"asset": "Cash", "current": random.uniform(2, 10)},
        ]

        for t in targets:
            c = next((c for c in currents if c["asset"] == t["asset"]), {"asset": t["asset"], "current": t["target"]})
            drift = c["current"] - t["target"]
            total_drift += abs(drift)
            max_drift = max(max_drift, abs(drift))
            if abs(drift) > drift_threshold:
                actions.append({
                    "asset_class": t["asset"],
                    "current_allocation": round(c["current"], 2),
                    "target_allocation": t["target"],
                    "drift": round(drift, 2),
                    "drift_threshold": drift_threshold,
                    "action": "Sell" if drift > 0 else "Buy",
                    "adjustment_amount_percent": round(abs(drift), 2),
                    "priority": "High" if abs(drift) > drift_threshold * 2 else "Medium",
                })

        return {
            "status": "Success",
            "mode": "stub",
            "rebalance_required": len(actions) > 0,
            "total_drift": round(total_drift, 2),
            "max_drift": round(max_drift, 2),
            "drift_threshold": drift_threshold,
            "actions_required": len(actions),
            "rebalance_actions": actions,
            "rebalance_cost_estimate": round(total_drift * random.uniform(0.005, 0.02), 4),
            "projected_improvement": round(random.uniform(0.5, 3.5), 2),
        }

    def _stub_attribution(self, portfolio_returns, benchmark_returns, sectors):
        """Simulate Brinson-style performance attribution."""
        attribution_data = []
        total_allocation_effect = 0
        total_selection_effect = 0

        for s in (sectors or ["Financials", "IT", "Healthcare", "Consumer", "Energy", "Auto"]):
            alloc_effect = random.uniform(-0.5, 1.2)
            select_effect = random.uniform(-0.8, 1.5)
            total_allocation_effect += alloc_effect
            total_selection_effect += select_effect
            attribution_data.append({
                "sector": s,
                "portfolio_weight": round(random.uniform(5, 25), 2),
                "benchmark_weight": round(random.uniform(5, 22), 2),
                "portfolio_return": round(random.uniform(-5, 25), 2),
                "benchmark_return": round(random.uniform(-3, 20), 2),
                "allocation_effect": round(alloc_effect, 2),
                "selection_effect": round(select_effect, 2),
                "interaction_effect": round(alloc_effect * select_effect * random.uniform(0.01, 0.05), 2),
            })

        return {
            "status": "Success",
            "mode": "stub",
            "total_return": round(random.uniform(8, 18), 2),
            "benchmark_return": round(random.uniform(7, 16), 2),
            "excess_return": round(random.uniform(-1, 5), 2),
            "allocation_effect": round(total_allocation_effect, 2),
            "selection_effect": round(total_selection_effect, 2),
            "interaction_effect": round(total_allocation_effect * total_selection_effect * 0.02, 2),
            "attribution_detail": attribution_data,
            "top_contributors": [a for a in attribution_data if a["selection_effect"] > 0][:3],
            "top_detractors": [a for a in attribution_data if a["selection_effect"] < 0][:3],
        }

    def _stub_market_regime(self, index_values, lookback_days):
        """Simulate market regime detection."""
        regimes = ["Bull Market", "Bull Market", "Bull Market", "Sideways", "Sideways",
                   "Correction", "Bear Market", "Recovery"]
        regime = random.choice(regimes)
        strength_map = {
            "Bull Market": random.uniform(60, 90),
            "Sideways": random.uniform(40, 60),
            "Correction": random.uniform(20, 40),
            "Bear Market": random.uniform(5, 25),
            "Recovery": random.uniform(50, 75),
        }

        return {
            "status": "Success",
            "mode": "stub",
            "detected_regime": regime,
            "regime_confidence": round(strength_map.get(regime, 50), 2),
            "indicators": {
                "trend": random.choice(["Up", "Down", "Flat"]),
                "momentum": round(random.uniform(-15, 20), 2),
                "volatility_regime": random.choice(["Low", "Normal", "High"]),
                "volume_trend": random.choice(["Increasing", "Decreasing", "Stable"]),
                "breadth": random.choice(["Strong", "Moderate", "Weak"]),
                "correlation_regime": random.choice(["Low", "Normal", "High"]),
            },
            "signals": {
                "golden_cross": random.choice([True, False]),
                "death_cross": random.choice([True, False]),
                "overbought": random.choice([True, False]) if regime == "Bull Market" else False,
                "oversold": random.choice([True, False]) if regime == "Bear Market" else False,
            },
            "forecast": {
                "next_month": random.choice(["Up 2-4%", "Down 1-3%", "Sideways"]),
                "next_quarter": random.choice(["Bullish", "Bearish", "Cautious", "Neutral"]),
            },
        }

    def _stub_sentiment(self, texts, entities):
        """Simulate NLP sentiment analysis."""
        results = []
        for text in (texts or ["Sample news article about market performance"]):
            results.append({
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": random.choice(["Positive", "Neutral", "Negative"]),
                "score": round(random.uniform(-1, 1), 3),
                "confidence": round(random.uniform(0.65, 0.95), 3),
                "entities_detected": entities or [random.choice(["RELIANCE", "TCS", "HDFC", "NIFTY"])],
                "keywords": random.sample(["earnings", "growth", "profit", "revenue", "market", "regulation", "expansion", "dividend"], k=3),
            })

        aggregate = sum(r["score"] for r in results) / len(results) if results else 0
        return {
            "status": "Success",
            "mode": "stub",
            "results": results,
            "aggregate_sentiment": "Positive" if aggregate > 0.2 else ("Negative" if aggregate < -0.2 else "Neutral"),
            "aggregate_score": round(aggregate, 3),
            "total_articles": len(results),
        }

    # =========================================================================
    # LIVE IMPLEMENTATIONS (placeholders)
    # =========================================================================

    def _live_risk_metrics(self, portfolio_returns, benchmark_returns, risk_free_rate, lookback_months):
        raise NotImplementedError("Live ML risk analytics requires TensorFlow/PyTorch model deployment.")

    def _live_stress_test(self, portfolio_holdings, scenarios):
        raise NotImplementedError("Live stress testing requires historical correlation matrices.")

    def _live_tax_harvest(self, holdings, portfolio_value, tax_slab):
        raise NotImplementedError("Live tax harvesting requires real-time position data.")

    def _live_rebalance(self, current_allocation, target_allocation, drift_threshold):
        raise NotImplementedError("Live rebalancing requires integration with trading system.")

    def _live_attribution(self, portfolio_returns, benchmark_returns, sectors):
        raise NotImplementedError("Live attribution requires full portfolio holdings data.")

    def _live_market_regime(self, index_values, lookback_days):
        raise NotImplementedError("Live market regime detection requires market data feed.")

    def _live_sentiment(self, texts, entities):
        raise NotImplementedError("Live sentiment analysis requires NLP model API credentials.")
