from src import personas
from asgiref.sync import sync_to_async
from langchain.schema import messages_from_dict, messages_to_dict


def llama_v2_prompt(
        messages: list[dict], system_prompt: str = None
):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    BOS, EOS = "<s>", "</s>\\"
    DEFAULT_SYSTEM_PROMPT = system_prompt

    messages[0]['data']['content'] = B_SYS + DEFAULT_SYSTEM_PROMPT + E_SYS + messages[0]['data']["content"]
    messages_list = [
        f"{BOS}{B_INST} {(prompt['data']['content']).strip()} {E_INST} {(answer['data']['content']).strip()} {EOS}\n"
        for prompt, answer in zip(messages[::2], messages[1::2])
    ]
    messages_list.append(f"{BOS}{B_INST} {(messages[-1]['data']['content']).strip()} {E_INST}")

    return "".join(messages_list)

async def official_handle_response(message, client) -> str:
    return await sync_to_async(client.chatbot.ask)(message)

async def local_handle_response(message, client) -> str:
    client.memory.add_user_message(message)
    dicts =messages_to_dict(client.memory.messages)
    messages=llama_v2_prompt(dicts, client.starting_prompt)
    response= await sync_to_async(client.chatbot.predict)(messages)
    client.memory.add_ai_message(response)
    return response


# prompt engineering
async def switch_persona(persona, client) -> None:
    if client.chat_model == "LOCAL":
        client.chatbot.reset_chat()
        client.chatbot.ask(personas.PERSONAS.get(persona))
    elif client.chat_model == "OFFICIAL":
        client.chatbot = client.get_chatbot_model(prompt=personas.PERSONAS.get(persona))
