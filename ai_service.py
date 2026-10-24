import os

import boto3
from botocore.config import Config


def generate_text(prompt):
    region = os.environ.get("BEDROCK_REGION")
    model_id = os.environ.get("BEDROCK_MODEL_ID")

    if not region or not model_id:
        raise ValueError(
            "Set BEDROCK_REGION and BEDROCK_MODEL_ID first."
        )

    client = boto3.client(
        "bedrock-runtime",
        region_name=region,
        config=Config(
            connect_timeout=10,
            read_timeout=60,
            retries={"max_attempts": 1},
        ),
    )

    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0.5,
        },
    )

    blocks = response["output"]["message"]["content"]
    text = "\n".join(
        block["text"] for block in blocks if "text" in block
    )

    if not text.strip():
        raise RuntimeError("The model returned no text.")

    return text


if __name__ == "__main__":
    try:
        answer = generate_text(
            "Write a short welcome message for HouseVerdi "
            "Arithmancy, a numerology reflection application."
        )
        print("\nAI RESPONSE:\n")
        print(answer)
    except Exception as error:
        print(f"\nAI connection failed: {error}")
        raise SystemExit(1)