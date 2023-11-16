from src import personas
from asgiref.sync import sync_to_async
import os
import pickle
import openai
import numpy as np
from dotenv import load_dotenv
load_dotenv()

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


def gpt(history: list[dict]):
    l = [x['content'] for x in history]
    return '\n---\n'.join(l)
async def local_handle_response(message, client,user,stream=False,rag=False):
    # history = await client.get_chat_history(user)

    if rag:
        picklefile = "recursive_seperate_none_openai_embedding_textbook_1100.pkl"
        path_to_pickle = os.path.join("/home/bot/localgpt/rag/pickle/", picklefile)
        with open(path_to_pickle, 'rb') as f:
            data_loaded = pickle.load(f)
        doc_list = data_loaded['doc_list']
        embedding_list = data_loaded['embedding_list']
        history = [{"role": "user", "content": message}]
        # OPENAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = "https://api.openai.com/v1"
        query_embed = np.array(openai.Embedding.create(model="text-embedding-ada-002", input=gpt(history))['data'][0]['embedding'])
        # model
        openai.api_key = "empty"
        openai.api_base = "http://localhost:8000/v1"
        cosine_similarities = np.dot(embedding_list, query_embed)
        indices = np.argsort(cosine_similarities)[::-1]
        docs = doc_list[indices]
        top_docs=docs[:3]
        distances = cosine_similarities[:3]
        print(distances)
        insert_document = ""
        for i, docu in enumerate(top_docs):
            insert_document += f"doc{i + 1}: {docu}\n"
        print(insert_document)

        # message = "question: " + message + "\n---\n" + insert_document
        # message = "question: " + message
        document_no_space=insert_document.replace("\n", ' ')
        message = (f"Is the question:({message.strip()}) related to document:({document_no_space})?\n"
                   f"Just give me an Answer yes or no.\n")
        print(message)
    history=None
    if history is None:
        history=[]
        history.append({"role": "system", "content": client.starting_prompt})
    history.append({"role": "user", "content": message})
    # prompt=wizard_coder(history)
    if not stream:

        response= await openai.ChatCompletion.acreate(model=client.openAI_gpt_engine, messages=history, temperature=0.3,max_tokens=1000)
        history.append(response['choices'][0]['message'].replace('\n\n\n',''))
        await client.set_chat_history(user,history)
        return response['choices'][0]['message']['content'].replace('\n\n\n','')
    else:
        response= await openai.ChatCompletion.acreate(model=client.openAI_gpt_engine, messages=history, temperature=0.3,max_tokens=1000,stream=True)
        return response,history


# prompt engineering
async def switch_persona(persona, client) -> None:
    if client.chat_model == "LOCAL":
        client.chatbot.reset_chat()
        client.chatbot.ask(personas.PERSONAS.get(persona))
    elif client.chat_model == "OFFICIAL":
        client.chatbot = client.get_chatbot_model(prompt=personas.PERSONAS.get(persona))
