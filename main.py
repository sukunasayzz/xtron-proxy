from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

VALID_TOKENS = {"XTRON-BETA-01", "XTRON-BETA-02", "XTRON-BETA-03"}

@app.post("/v1/chat/completions")
async def proxy_chat(payload: dict, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    user_token = authorization.split(" ")[1]
    if user_token not in VALID_TOKENS:
        raise HTTPException(status_code=403, detail="Invalid or unauthorized beta token")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    async def stream_generator():
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", GROQ_URL, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    yield f"Error from AI provider: {response.status_code}".encode()
                    return
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
