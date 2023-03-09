import os
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = "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"

# response = openai.Completion.create(model="text-davinci-003", prompt="Say this is a test", temperature=0, max_tokens=7)

prompt = "Can you give me an complex html file that functions as a chatbot?"
model_engine = "text-davinci-003"

completions = openai.Completion.create(
    engine = model_engine,
    prompt = prompt,
    max_tokens = 1024,
    n = 1,
    stop = None,
    temperature=0.5,
)
message = completions.choices[0].text
print(message)