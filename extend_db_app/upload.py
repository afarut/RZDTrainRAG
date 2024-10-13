from langchain_ollama import ChatOllama
import re
import requests as r
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader, Dataset
import pandas as pd
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from time import sleep



model_name = 'intfloat/multilingual-e5-large'
model = SentenceTransformer(model_name)

client = QdrantClient(url="http://176.109.100.141:6333")

def embed_text(text, model):
    text = text
    return model.encode(text).squeeze()


llm = ChatOllama(model="second_vikhr:latest", temperature=0.7,)



def get_norm_user(text):
    PROMT = f"""Забудь все что ты знаешь о внешнем мире. Ты русскоязычный лингвистическая модель. Твоя задача как можно разнообразнее сформулировать вопрос (небольшого кусочка текста) 15 раз. 
Ничего не придумывай и ничего лишнего не выводи основывайся только данном тебе тексте.
Задавай только корректные вопросы по структуре.
Выведи все вопросительные конструкции в формате один ответ - одна строка. Не выводи ответа на мою просьбу только готовый переформулированные вопросы, также не нумеруй строки.
Текст: {text}"""

    messages = [
                ("human", PROMT),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg.content.replace("\n\n", "\n").split("\n")


def get_old_user(text):
    PROMT = f"""Забудь все что ты знаешь о внешнем мире. Ты русскоязычный опытный пользователь который разбирается в тексте. Твоя задача как можно разнообразнее сформулировать глубокий и вдумчивый вопрос (небольшого кусочка текста) 15 раз. 
Ничего не придумывай и ничего лишнего не выводи основывайся только данном тебе тексте.
Задавай только корректные вопросы по структуре.
Выведи все вопросительные конструкции в формате один ответ - одна строка. Не выводи ответа на мою просьбу только готовый переформулированные вопросы, также не нумеруй строки.
Текст: {text}"""

    messages = [
                ("human", PROMT),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg.content.replace("\n\n", "\n").split("\n")


def get_new_user(text):
    PROMT = f"""Забудь все что ты знаешь о внешнем мире. Ты русскоязычный пользователь-новичок который не разбирается в тексте. Твоя задача как можно разнообразнее сформулировать поверхностный вопрос (небольшого кусочка текста) 15 раз. 
Ничего не придумывай и ничего лишнего не выводи основывайся только данном тебе тексте.
Задавай корректные по структуре вопросы.
Выведи все вопросительные конструкции в формате один ответ - одна строка. Не выводи ответа на мою просьбу только готовый переформулированные вопросы, также не нумеруй строки.
Текст: {text}"""

    messages = [
                ("human", PROMT),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg.content.replace("\n\n", "\n").split("\n")


def get_md_info(url):
    html = r.get(url, 
    headers={"Accept": "*/*", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive", "User-Agent": "PostmanRuntime/7.42.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    chuncks = []
    titles = []
    for el in soup.find_all("div", "docTextPartDiv"):
        chuncks.append(md(el.find("div", "onePartTextOut_text").text))
        titles.append(md(el.find("h3", "parttext").text))
    return pd.DataFrame({"chunck": chuncks, "title": titles})


def get_punk(text):
    pattern = r'(\d+\\\.\d+(?:\\\.\d+)?\\\.)\s+((?:.|\n)+?)(?=\n\d+\\\.\d+(?:\\\.\d+)?\\\.|\Z)'
    res = []
    matches = re.findall(pattern, text)
    for match in matches:
        number = match[0].replace('\\', '')
        text = match[1].strip()
        res.append((number, text))
    if len(res) == 0:
        res.append(("-1.1", text))
    return res

def magic_transform(df):
    to_del = []
    fix_add = ""
    fix_num = "None"
    for i in range(1, len(df)):
        prev_num = df["num"][i - 1]
        curr_num = df["num"][i]
        if curr_num.startswith(prev_num):
            fix_add = df["text"][i - 1]
            fix_num = prev_num
            to_del.append(i - 1)
            df.loc[i, "text"] = fix_add + " " + df["text"][i]
        elif curr_num.startswith(fix_num):
            df.loc[i, "text"] = fix_add + " " + df["text"][i]
        else:
            fix_add = ""
            fix_num = "None"
    df = df.drop(to_del)
    df = df.reset_index(drop=True)
    return df


def get_questions(df):
    text = df["text"].values
    text = text.tolist()
    df["norm"] = get_norm_user(text)
    df["nub"] = get_new_user(text)
    df["pro"] = get_old_user(text)
    return df



def upload_to_collection(collection_name, model, url):
    points = []
    id = 1
    df = pd.read_csv("res.csv")


    #client.delete_collection(collection_name)
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
    except Exception as e:
        print(e)

    for i in tqdm(range(len(df)), desc="Create points"):
        tmp_text = df["text"][i]
        id += 1
        norm = eval(df["norm"][i])
        embeds = embed_text(norm, model)
        for j in range(len(norm)):
            points.append(PointStruct(id=id, vector=embeds[j].tolist(), payload={"answer_chank": tmp_text, "question": norm[j], 
                                                                                                            "razdel": df['razdel'][i],
                                                                                                            "role": "norm",
                                                                                                            "paragraph": df["num"][i],
                                                                                                            "url": url}))
            id += 1
        pro = eval(df["pro"][i])
        embeds = embed_text(pro, model)
        for j in range(len(pro)):
            points.append(PointStruct(id=id, vector=embeds[j].tolist(), payload={"answer_chank": tmp_text, "question": pro[j], 
                                                                                                            "razdel": df['razdel'][i],
                                                                                                            "role": "pro",
                                                                                                            "paragraph": df["num"][i],
                                                                                                            "url": url}))
            id += 1
        nub = eval(df["nub"][i])
        embeds = embed_text(nub, model)
        for j in range(len(nub)):
            points.append(PointStruct(id=id, vector=embeds[j].tolist(), payload={"answer_chank": tmp_text, "question": nub[j], 
                                                                                                            "razdel": df['razdel'][i],
                                                                                                            "role": "nub",
                                                                                                            "paragraph": df["num"][i],
                                                                                                            "url": url}))
            id += 1
    return points

def get_result_csv(url):
    yield "Начинаем парсить"
    md_info = get_md_info(url)
    if not len(md_info):
        yield "Этот url не может быть спаршен"
        return
    else:
        cv = pd.DataFrame({}) 

        texts = []
        num = []
        razdel = []
        sleep(0.5)
        yield f"Нашли {len(md_info)} разделов"
        for i in range(len(md_info)):
            text = md_info["chunck"][i]
            for j in get_punk(text):
                razdel.append(md_info["title"][i])
                texts.append(j[1])
                num.append(j[0])
        cv["num"] = num
        cv["text"] = texts
        cv["razdel"] = razdel
        cv = magic_transform(cv)

        texts = cv["text"].values.tolist()
        for i in range(len(texts)):
            text = texts[i]
            cv["norm"] = get_norm_user(text)
            yield round((i + 1) / len(texts) * 100, 0)

        for i in range(len(texts)):
            text = texts[i]
            cv["nub"] = get_new_user(text)
            yield round((i + 1) / len(texts) * 100, 0)

        for i in range(len(texts)):
            text = texts[i]
            cv["pro"] = get_old_user(text)
            yield round((i + 1) / len(texts) * 100, 0)

        yield "Начинаем загрузку на Qdrant"
        collection_name = "dota3"

        points = upload_to_collection(collection_name, model, url)

        batch_size = 256

        for i in tqdm(range(0, len(points), batch_size), desc="Upload in qdrant"):
            point = points[i:i + batch_size]
            operation_info = client.upsert(
                collection_name=collection_name,
                wait=True,
                points=point,
            )

        yield "Успех"


#url = "https://company.rzd.ru/ru/9353/page/105104?id=1604"
#df = get_result_csv(url)
