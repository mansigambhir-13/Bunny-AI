# quick_voice_token.py
from livekit import api

token = api.AccessToken(
    "APIsgLwcjQcb6ow", 
    "tEVcd5iXzuEKBZPSBtk4wEyVmzjWbneTfUqjHeHYl60A"
).with_identity("voice_user").with_grants(
    api.VideoGrants(room_join=True, room="voice_chat", can_publish=True, can_subscribe=True)
).to_jwt()

print(f"URL: wss://my-bunny-ai-yr79oftp.livekit.cloud")
print(f"Token: {token}")
print(f"Room: voice_chat")