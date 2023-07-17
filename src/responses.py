from src import personas
from asgiref.sync import sync_to_async


async def official_handle_response(message, client) -> str:
    return await sync_to_async(client.chatbot.ask)(message)

async def local_handle_response(message, client) -> str:
    #TODO
    return await sync_to_async(client.chatbot.ask)(message)


# prompt engineering
async def switch_persona(persona, client) -> None:
    if client.chat_model == "LOCAL":
        client.chatbot.reset_chat()
        client.chatbot.ask(personas.PERSONAS.get(persona))
    elif client.chat_model == "OFFICIAL":
        client.chatbot = client.get_chatbot_model(prompt=personas.PERSONAS.get(persona))
