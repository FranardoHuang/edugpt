from src import personas
from asgiref.sync import sync_to_async

import openai


def llama_v2_prompt(
        messages: list[dict], system_prompt: str = None
):
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    BOS, EOS = "<s>", "</s>\\"
    DEFAULT_SYSTEM_PROMPT = system_prompt
    messages=messages.copy()
    messages[0]['data']['content'] = B_SYS + DEFAULT_SYSTEM_PROMPT + E_SYS + messages[0]['data']["content"]
    messages_list = [
        f"{BOS}{B_INST} {(prompt['data']['content']).strip()} {E_INST} {(answer['data']['content']).strip()} {EOS}\n"
        for prompt, answer in zip(messages[::2], messages[1::2])
    ]
    messages_list.append(f"{BOS}{B_INST} {(messages[-1]['data']['content']).strip()} {E_INST}")

    return "".join(messages_list)

def wizard_coder(history: list[dict]):
    DEFAULT_SYSTEM_PROMPT = history[0]['content']+'\n\n'
    B_INST, E_INST = "### Instruction:\n", "\n\n### Response:\n"
    messages = history.copy()
    messages_list=[DEFAULT_SYSTEM_PROMPT]
    messages_list.extend([
        f"{B_INST}{(prompt['content']).strip()}{E_INST}{(answer['content']).strip()}\n\n"
        for prompt, answer in zip(messages[1::2], messages[2::2])
    ])
    messages_list.append(f"{B_INST}{(messages[-1]['content']).strip()}{E_INST}")
    return "".join(messages_list)


async def official_handle_response(message, client) -> str:
    return await sync_to_async(client.chatbot.ask)(message)

async def local_handle_response(message, client,user,stream=False):
    # history = await client.get_chat_history(user)
    history=None
    if history is None:
        history=[]
        history.append({"role": "system", "content": client.starting_prompt})
    history.append({"role": "user", "content": message})
    prompt=wizard_coder(history)
    if not stream:
        response= await openai.Completion.acreate(model=client.openAI_gpt_engine, prompt=prompt, temperature=0.3,max_tokens=1000)
        history.append(response['choices'][0]['message'])
        await client.set_chat_history(user,history)
        return response['choices'][0]['message']['content']
    else:
        response= await openai.Completion.acreate(model=client.openAI_gpt_engine, prompt=prompt, temperature=0.3,max_tokens=1000,stream=True)
        return response,history


# prompt engineering
async def switch_persona(persona, client) -> None:
    if client.chat_model == "LOCAL":
        client.chatbot.reset_chat()
        client.chatbot.ask(personas.PERSONAS.get(persona))
    elif client.chat_model == "OFFICIAL":
        client.chatbot = client.get_chatbot_model(prompt=personas.PERSONAS.get(persona))
