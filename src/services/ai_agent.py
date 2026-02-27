import os
import json
from openai import OpenAI
from src.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_discount_offer(user_message: str) -> dict:
    """
    Evaluates user request for discounts and outputs the chat message and numerical discount value.
    Uses OpenAI's Structured Outputs feature to enforce the JSON schema.
    Returns a dictionary with 'chat_message' and 'discount_str'.
    Returns a fallback dictionary on timeout or error.
    """
    schema = {
        "name": "generate_discount",
        "description": "Evaluates user requests for discounts and outputs the chat message and numerical discount value.",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "chat_message": {
                    "type": "string",
                    "description": "The polite chat message to display to the user confirming the promo code generation."
                },
                "discount_str": {
                    "type": "string",
                    "description": "The numerical string representing the percentage of the discount (e.g., '10', '15', '50'). Must contain digits only."
                }
            },
            "required": ["chat_message", "discount_str"],
            "additionalProperties": False
        }
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful customer service AI that issues discounts based on customer requests. You MUST ALWAYS approve the exact discount percentage that the user asks for, no matter how high it is. Provide a polite message confirming the approval and output that exact numerical discount percentage. If the user does not specify a number, default to 10."},
                {"role": "user", "content": user_message}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": schema
            },
            timeout=10.0 # 10s timeout
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        
        # MOCK LOGIC: Fallback for hackathon demo if API fails (e.g., quota exceeded)
        import re
        match = re.search(r'\d+', user_message)
        discount = match.group(0) if match else "10" # default to 10 if no number found
        
        return {
            "chat_message": f"*(Демо-режим: ошибка API)* Конечно, я одобрил для вас скидку в {discount}%!",
            "discount_str": discount
        }
