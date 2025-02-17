
import requests


class PerplexityResponse:

    def __init__(self, response: requests.Response):
        response = response.json()
        print(response)
        self.text = response['choices'][0]['message']['content']
        self.citations = response['citations']

    def getMarkdownCitations(self) -> str:
        return "<br>".join(f"[{i+1}]: {citation}" for i, citation in enumerate(self.citations))
    
    def getCitations(self) -> str:
        return "\n".join(f"[{i+1}]: {citation}" for i, citation in enumerate(self.citations))

    def getText(self) -> str:
        return self.text

def query_preplexity(prompt: str, api_key: str) -> tuple[str, str]:
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1200,
        "temperature": 0.2,
        "top_p": 0.9,
        "search_domain_filter": None,
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "year",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
        "response_format": None
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return PerplexityResponse(requests.request("POST", url, json=payload, headers=headers))