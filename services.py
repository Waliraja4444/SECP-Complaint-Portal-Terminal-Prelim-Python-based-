import httpx
import json
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from .models import ClassificationResponse, Classification

load_dotenv()

class ClassificationService:
    def __init__(self):
        self.llm_url = os.getenv("LLM_URL")
        self.llm_key = os.getenv("LLM_KEY")
        
        # Mock classifications for fallback
        self.mock_classifications = [
            {
                'keywords': ['health', 'claim', 'pending', 'insurance', 'medical'],
                'classification': {
                    'category': 'Insurance Services',
                    'subcategory': 'Health Insurance Claims',
                    'nature_of_issue': 'Delayed Processing',
                    'confidence': 0.92
                }
            },
            {
                'keywords': ['broker', 'unauthorized', 'trading', 'account', 'fraud'],
                'classification': {
                    'category': 'Brokerage Services',
                    'subcategory': 'Unauthorized Trading',
                    'nature_of_issue': 'Account Manipulation',
                    'confidence': 0.88
                }
            },
            {
                'keywords': ['mutual', 'fund', 'returns', 'investment', 'loss'],
                'classification': {
                    'category': 'Investment Services',
                    'subcategory': 'Mutual Funds',
                    'nature_of_issue': 'Performance Issues',
                    'confidence': 0.85
                }
            },
            {
                'keywords': ['pension', 'retirement', 'withdrawal', 'pf'],
                'classification': {
                    'category': 'Pension Services',
                    'subcategory': 'Retirement Benefits',
                    'nature_of_issue': 'Withdrawal Process',
                    'confidence': 0.90
                }
            },
            {
                'keywords': ['bank', 'loan', 'interest', 'repayment'],
                'classification': {
                    'category': 'Banking Services',
                    'subcategory': 'Loan Services',
                    'nature_of_issue': 'Interest Rate Dispute',
                    'confidence': 0.87
                }
            }
        ]

    async def classify(self, complaint_text: str) -> ClassificationResponse:
        """Classify complaint using OpenAI API with fallback to mock classification"""
        
        # Try OpenAI API first
        if self.llm_url and self.llm_key:
            try:
                result = await self._classify_with_openai(complaint_text)
                if result:
                    return result
            except Exception as e:
                print(f"OpenAI classification failed: {e}")
        
        # Fallback to mock classification
        return self._get_mock_classification(complaint_text)

    async def _classify_with_openai(self, complaint_text: str) -> Optional[ClassificationResponse]:
        """Classify using OpenAI API"""
        prompt = f"""You are an expert classifier for SECP (Securities and Exchange Commission of Pakistan) complaints. 

Analyze the following complaint and classify it into the appropriate category, subcategory, and nature of issue.

Available Categories and their Subcategories:
1. Insurance Services: Health Insurance Claims, Life Insurance Claims, Motor Insurance Claims, Property Insurance Claims
2. Brokerage Services: Unauthorized Trading, Account Management, Commission Disputes, Market Manipulation
3. Investment Services: Mutual Funds, Securities Trading, Portfolio Management, Investment Advisory
4. Pension Services: Retirement Benefits, Provident Fund, Gratuity Claims, Pension Payments
5. Banking Services: Loan Services, Account Services, Credit Cards, Digital Banking
6. Capital Markets: Stock Exchange, Bond Markets, Derivatives, Market Infrastructure

Nature of Issues:
- Delayed Processing, Claim Rejection, Premium Issues, Policy Terms Dispute
- Account Manipulation, Excessive Charges, Poor Service Quality, Regulatory Violations
- Performance Issues, Misleading Information, Unauthorized Transactions, Fee Disputes
- Withdrawal Process, Calculation Errors, Delayed Payments, Documentation Issues
- Interest Rate Dispute, Service Charges, Account Access Issues, Transaction Disputes
- Trading Issues, Settlement Problems, Market Data Issues, Regulatory Compliance

Complaint: "{complaint_text}"

Respond with ONLY a JSON object in this exact format:
{{
  "category": "exact category name",
  "subcategory": "exact subcategory name", 
  "nature_of_issue": "exact nature of issue",
  "confidence": 0.85
}}"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.llm_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.llm_key}'
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 200
                }
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code}")

            data = response.json()
            content = data['choices'][0]['message']['content']
            
            if not content:
                raise Exception('No content in OpenAI response')

            # Parse the JSON response
            classification_data = json.loads(content.strip())
            
            classification = Classification(
                category=classification_data['category'],
                subcategory=classification_data['subcategory'],
                nature_of_issue=classification_data['nature_of_issue'],
                confidence=classification_data.get('confidence', 0.8)
            )
            
            return ClassificationResponse(
                classification=classification,
                processed_at=datetime.now().isoformat()
            )

    def _get_mock_classification(self, complaint_text: str) -> ClassificationResponse:
        """Get mock classification based on keywords"""
        text = complaint_text.lower()
        
        # Find best matching classification based on keywords
        best_match = self.mock_classifications[0]
        max_matches = 0

        for mock in self.mock_classifications:
            matches = sum(1 for keyword in mock['keywords'] 
                         if keyword.lower() in text)
            
            if matches > max_matches:
                max_matches = matches
                best_match = mock

        # Add some randomness to confidence if no keywords match
        confidence = best_match['classification']['confidence'] if max_matches > 0 else round(0.6 + (0.3 * hash(text) % 100) / 100, 2)

        classification = Classification(
            category=best_match['classification']['category'],
            subcategory=best_match['classification']['subcategory'],
            nature_of_issue=best_match['classification']['nature_of_issue'],
            confidence=confidence
        )

        return ClassificationResponse(
            classification=classification,
            processed_at=datetime.now().isoformat()
        )