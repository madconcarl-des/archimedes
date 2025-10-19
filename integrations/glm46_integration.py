"""
Archimedes Project - GLM-4.6 Integration Module

This module integrates GLM-4.6 AI capabilities for:
- Natural language querying of economic data
- Enhanced AML transaction analysis
- Intelligent report generation
- Economic insights and forecasting explanations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GLM46Client:
    """Client for GLM-4.6 API integration"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize GLM-4.6 client

        Args:
            api_key: API key for authentication (defaults to env var GLM_API_KEY)
            base_url: Base URL for GLM-4.6 API (defaults to Zhipu official endpoint)
        """
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        self.base_url = base_url or os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')

        if not self.api_key:
            logger.warning("GLM_API_KEY not set. API calls will fail.")

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Model configuration
        self.model = 'glm-4.6'
        self.max_tokens = 4000
        self.temperature = 0.7

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to GLM-4.6

        Args:
            messages: List of message objects with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            tools: Optional tool definitions for function calling

        Returns:
            API response with completion
        """
        # Handle different endpoint formats
        if 'bigmodel.cn' in self.base_url:
            endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        else:
            endpoint = f"{self.base_url}/chat/completions"

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature or self.temperature,
            'max_tokens': max_tokens or self.max_tokens
        }

        if tools:
            payload['tools'] = tools

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GLM-4.6 API request failed: {e}")
            raise

    def extract_response_text(self, response: Dict) -> str:
        """Extract text content from API response"""
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract response text: {e}")
            return ""


class EconomicDataQueryAgent:
    """Agent for natural language querying of economic data"""

    def __init__(self, glm_client: GLM46Client):
        self.client = glm_client

    def query_to_api_params(self, natural_query: str, available_indicators: List[str]) -> Dict:
        """
        Convert natural language query to API parameters

        Args:
            natural_query: User's natural language question
            available_indicators: List of available indicator codes

        Returns:
            Dictionary with API endpoint and parameters
        """
        system_prompt = f"""You are an economic data API assistant. Convert natural language queries
into structured API parameters.

Available indicators: {', '.join(available_indicators[:20])}

Given a user query, extract:
- endpoint: one of ['timeseries', 'compare', 'data']
- country_code: ISO 3-letter code (e.g., USA, CHN, DEU)
- indicator_code: from available list
- start_year, end_year: if temporal range specified
- country_codes: list for comparison queries

Respond ONLY with valid JSON. Example:
{{"endpoint": "timeseries", "country_code": "USA", "indicator_code": "GDP_GROWTH", "start_year": 2020, "end_year": 2023}}
"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': natural_query}
        ]

        response = self.client.chat_completion(messages, temperature=0.3)
        response_text = self.client.extract_response_text(response)

        try:
            params = json.loads(response_text)
            logger.info(f"Converted query to params: {params}")
            return params
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from GLM response: {response_text}")
            return {}

    def explain_economic_data(self, data: Dict, context: str = "") -> str:
        """
        Generate human-readable explanation of economic data

        Args:
            data: Economic data (time series, comparison, etc.)
            context: Additional context about the query

        Returns:
            Natural language explanation
        """
        system_prompt = """You are an expert economist. Analyze economic data and provide
clear, insightful explanations suitable for policy makers and business leaders.

Focus on:
- Key trends and patterns
- Historical context
- Potential implications
- Notable outliers or anomalies

Be concise but comprehensive."""

        user_message = f"""Analyze this economic data:

{json.dumps(data, indent=2)}

Context: {context}

Provide a brief analysis (3-4 paragraphs)."""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]

        response = self.client.chat_completion(messages, temperature=0.5, max_tokens=1000)
        return self.client.extract_response_text(response)


class AMLAnalysisAgent:
    """Agent for enhanced AML transaction analysis using GLM-4.6"""

    def __init__(self, glm_client: GLM46Client):
        self.client = glm_client

    def analyze_suspicious_transaction(
        self,
        transaction: Dict,
        risk_scores: Dict,
        account_history: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Generate detailed analysis of suspicious transaction

        Args:
            transaction: Transaction details
            risk_scores: Risk scores from ML models
            account_history: Optional transaction history

        Returns:
            Dictionary with analysis, red flags, and recommendations
        """
        system_prompt = """You are an expert in anti-money laundering (AML) and financial crime detection.
Analyze transactions and provide detailed assessments following FATF guidelines.

Consider:
- Transaction patterns and anomalies
- Geographic risk factors
- Temporal patterns
- Amount structuring
- Velocity and volume
- Account behavior

Provide specific, actionable insights."""

        user_message = f"""Analyze this potentially suspicious transaction:

Transaction Details:
{json.dumps(transaction, indent=2)}

ML Model Risk Scores:
{json.dumps(risk_scores, indent=2)}

{"Account History: " + json.dumps(account_history[:5], indent=2) if account_history else ""}

Provide:
1. Summary of red flags (bullet points)
2. Risk assessment (2-3 sentences)
3. Recommended actions (bullet points)
"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]

        response = self.client.chat_completion(messages, temperature=0.4, max_tokens=1500)
        analysis = self.client.extract_response_text(response)

        # Parse structured response
        return {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'model_version': 'glm-4.6',
            'confidence': 'high' if risk_scores.get('ensemble_score', 0) > 70 else 'medium'
        }

    def generate_sar_narrative(self, transaction_cluster: List[Dict]) -> str:
        """
        Generate Suspicious Activity Report (SAR) narrative

        Args:
            transaction_cluster: Group of related suspicious transactions

        Returns:
            Professional SAR narrative text
        """
        system_prompt = """You are a compliance officer writing Suspicious Activity Reports (SARs)
for FinCEN. Write clear, factual narratives following regulatory guidelines.

Include:
- Objective description of activities
- Dates, amounts, and parties involved
- Specific suspicious indicators
- Pattern analysis
- Professional, formal tone"""

        user_message = f"""Generate a SAR narrative for these related transactions:

{json.dumps(transaction_cluster, indent=2)}

Write a complete narrative section (200-300 words)."""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]

        response = self.client.chat_completion(messages, temperature=0.3, max_tokens=2000)
        return self.client.extract_response_text(response)


class EconomicForecastExplainer:
    """Agent for explaining economic forecasts and model predictions"""

    def __init__(self, glm_client: GLM46Client):
        self.client = glm_client

    def explain_forecast(
        self,
        indicator: str,
        forecast_values: List[float],
        historical_values: List[float],
        model_type: str = "LSTM",
        confidence_intervals: Optional[List[tuple]] = None
    ) -> str:
        """
        Generate explanation of economic forecast

        Args:
            indicator: Economic indicator being forecast
            forecast_values: Predicted future values
            historical_values: Historical data used for prediction
            model_type: Type of forecasting model used
            confidence_intervals: Optional confidence intervals

        Returns:
            Plain language explanation of forecast
        """
        system_prompt = """You are an economic forecasting expert. Explain model predictions
in clear language for non-technical stakeholders.

Cover:
- What the forecast indicates
- Key assumptions and limitations
- Confidence level
- Potential scenarios
- Actionable insights"""

        forecast_data = {
            'indicator': indicator,
            'model': model_type,
            'forecast': forecast_values,
            'historical_trend': historical_values[-10:],  # Last 10 points
            'confidence_intervals': confidence_intervals
        }

        user_message = f"""Explain this economic forecast:

{json.dumps(forecast_data, indent=2)}

Provide a clear explanation (2-3 paragraphs) for policy makers."""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]

        response = self.client.chat_completion(messages, temperature=0.5, max_tokens=1200)
        return self.client.extract_response_text(response)


class ArchimedesGLMIntegration:
    """Main integration class coordinating all GLM-4.6 capabilities"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Archimedes GLM-4.6 integration

        Args:
            api_key: GLM-4.6 API key (defaults to environment variable)
        """
        self.client = GLM46Client(api_key)
        self.query_agent = EconomicDataQueryAgent(self.client)
        self.aml_agent = AMLAnalysisAgent(self.client)
        self.forecast_explainer = EconomicForecastExplainer(self.client)

        logger.info("Archimedes GLM-4.6 integration initialized")

    def process_natural_language_query(self, query: str, available_indicators: List[str]) -> Dict:
        """
        Process natural language query and return structured API parameters

        Args:
            query: Natural language question about economic data
            available_indicators: List of available economic indicators

        Returns:
            API parameters dictionary
        """
        return self.query_agent.query_to_api_params(query, available_indicators)

    def explain_data(self, data: Dict, context: str = "") -> str:
        """Generate explanation of economic data"""
        return self.query_agent.explain_economic_data(data, context)

    def analyze_suspicious_transaction(
        self,
        transaction: Dict,
        risk_scores: Dict,
        account_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Analyze suspicious transaction with AI"""
        return self.aml_agent.analyze_suspicious_transaction(
            transaction, risk_scores, account_history
        )

    def generate_sar(self, transactions: List[Dict]) -> str:
        """Generate SAR narrative"""
        return self.aml_agent.generate_sar_narrative(transactions)

    def explain_forecast(
        self,
        indicator: str,
        forecast: List[float],
        historical: List[float],
        model: str = "LSTM"
    ) -> str:
        """Explain economic forecast"""
        return self.forecast_explainer.explain_forecast(
            indicator, forecast, historical, model
        )


# Example usage
if __name__ == "__main__":
    # Initialize integration
    integration = ArchimedesGLMIntegration()

    # Example 1: Natural language query
    print("\n=== Example 1: Natural Language Query ===")
    query = "What was China's GDP growth from 2020 to 2023?"
    indicators = ["GDP_GROWTH", "INFLATION", "UNEMPLOYMENT"]

    try:
        params = integration.process_natural_language_query(query, indicators)
        print(f"Query: {query}")
        print(f"Parsed Parameters: {json.dumps(params, indent=2)}")
    except Exception as e:
        print(f"Demo mode: {e}")

    # Example 2: AML Analysis
    print("\n=== Example 2: AML Transaction Analysis ===")
    sample_transaction = {
        'transaction_id': 'TX123456',
        'amount': 9950,
        'from_country': 'US',
        'to_country': 'PA',
        'timestamp': '2025-10-19T02:30:00Z'
    }

    sample_scores = {
        'ensemble_score': 85.3,
        'random_forest_score': 82.1,
        'xgboost_score': 88.5,
        'anomaly_score': 76.2
    }

    try:
        analysis = integration.analyze_suspicious_transaction(
            sample_transaction, sample_scores
        )
        print(f"Transaction: {sample_transaction['transaction_id']}")
        print(f"Risk Score: {sample_scores['ensemble_score']}")
        print(f"Analysis: {analysis.get('analysis', 'Demo mode - API key required')}")
    except Exception as e:
        print(f"Demo mode: Set GLM_API_KEY environment variable for full functionality")

    print("\n=== GLM-4.6 Integration Module Ready ===")
    print("Set environment variable GLM_API_KEY to enable API calls")
