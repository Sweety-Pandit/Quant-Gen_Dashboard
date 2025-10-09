from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

def generate_report(risk_score, accuracy):
    prompt = f"""
    A financial analyst AI is reviewing a customer with risk score {risk_score}.
    The model has accuracy {accuracy}.
    Write a professional one-paragraph report for management with recommendation.
    """

    result = generator(prompt, max_length=120, num_return_sequences=1)
    return result[0]["generated_text"]
