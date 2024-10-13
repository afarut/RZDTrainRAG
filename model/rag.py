from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_ollama import ChatOllama
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from collections import Counter


class RAG:
    def __init__(self):
        self.bi_encoder = SentenceTransformer('intfloat/multilingual-e5-large') # model.encode(text).squeeze()
        self.client = QdrantClient(url="http://176.109.100.141:6333")
        self.llm = ChatOllama(model="rscr/vikhr_nemo_12b:Q4_K_M", temperature=0.01,)
        self.cross_encoder_model = AutoModelForSequenceClassification.from_pretrained('DiTy/cross-encoder-russian-msmarco')
        self.cross_encoder_tokenizer = AutoTokenizer.from_pretrained('DiTy/cross-encoder-russian-msmarco')

    def rerank(self, question, chunks):
        scores_chunks = []
        for chunk in chunks:
            inputs = self.cross_encoder_tokenizer.encode_plus(question, chunk, return_tensors="pt", max_length=512, truncation=True)
            with torch.no_grad():
                outputs = self.cross_encoder_model(**inputs)
                score = outputs.logits[0].item()
            scores_chunks.append((score, chunk))
        sorted_chunks = sorted(scores_chunks, key=lambda x: x[0], reverse=True)
        if all(score < -1 for score, _ in sorted_chunks):
            return None
        return [chunk for _, chunk in sorted_chunks]

    def get_chuncks(self, example):
        vector = self.bi_encoder.encode([example]).squeeze()
        hits = self.client.search(
                    collection_name="dota2",
                    query_vector=vector,
                    limit=45 * 10
                )
        chuncks = []
        was = set()
        for i in hits:
            if i.payload["answer_chank"] not in was:
                was.add(i.payload["answer_chank"])
                chuncks.append(i.payload["answer_chank"])
        chuncks = list(map(lambda x: x[0], sorted(Counter(chuncks).items(), key=lambda x: x[1], reverse=True)))
        if len(chuncks) > 30:
            chuncks = chuncks[:30]
        chuncks = self.rerank(example, chuncks)
        return chuncks

    def __call__(self, quest):
        chuncks = self.get_chuncks(quest)
        if chuncks is None:
            return "Ответ не найден."
        chuncks = "\n".join(chuncks[:4])
        eval_prompt = f"### Ты РУССКОЯЗЫЧНЫЙ человек-ассистент пользователя, сотрудник компании РЖД, у которого есть доступ к нормативно-правовым актам, на основе которых ты должен составить ответ пользователю, не передавая документ, а только максимально понятно и четко разьясняя пользователю ответ на его вопрос.  ВАЖНО: выводи только сам ответ на вопрос и больше ничего. Проверяй себя, что ты делаешь именно так и не размышляешь над вопросом. Не используй специальных символов. НИКАК НЕ КОММЕНТИРУЙ ВОПРОС ###Question: {quest} Контекст, опираясь на который ты должен ответить: {chuncks}/n"
        messages = [
            ("human", eval_prompt),
        ]
        #for i in self.llm.stream(messages):
        #    yield i
        return self.llm.stream(messages)

    def get_more(self, quest):
        chuncks = self.get_chuncks(quest)
        if chuncks is None:
            return "Ответ не найден."
        chuncks = "\n".join(chuncks[:8])
        eval_prompt = f"### Ты РУССКОЯЗЫЧНЫЙ человек-ассистент пользователя, сотрудник компании РЖД, у которого есть доступ к нормативно-правовым актам, на основе которых ты должен составить ответ пользователю, не передавая документ, а только максимально понятно и четко разьясняя пользователю ответ на его вопрос.  ВАЖНО: выводи только сам ответ на вопрос и больше ничего. Проверяй себя, что ты делаешь именно так и не размышляешь над вопросом. Не используй специальных символов. НИКАК НЕ КОММЕНТИРУЙ ВОПРОС ###Question: {quest} Контекст, опираясь на который ты должен ответить: {chuncks}/n"
        messages = [
            ("human", eval_prompt),
        ]
        return self.llm.stream(messages)