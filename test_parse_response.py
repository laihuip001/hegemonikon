import logging
logging.basicConfig(level=logging.WARNING)

from mekhane.ccl.semantic_validator import CCLSemanticValidator

validator = CCLSemanticValidator()

response = 'Here is the response: {"aligned": true, "confidence": 0.5, "reasoning": "malformed JSON'
result = validator._parse_response(response)
print("Result for malformed JSON:")
print(result)

response = 'Here is the response: {"aligned": true, "confidence": 0.5, "reasoning": "malformed JSON"}'
result = validator._parse_response(response)
print("Result for good JSON:")
print(result)

response = 'Here is the response: {"aligned": true, "confidence": "broken", "reasoning": "malformed JSON"}'
result = validator._parse_response(response)
print("Result for good JSON, broken value:")
print(result)
