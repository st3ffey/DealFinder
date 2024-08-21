import os
from anthropic import Anthropic

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_restaurant_content(content: str) -> str:
    """Use Claude's 3.5-sonnet model to analyze restaurant content."""

    message = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": f"Analyze the following restaurant website content and provide a brief summary, highlighting any potential deals or special offers:\n\n{content}"
            }
        ]
    )
    
    return message.content[0].text