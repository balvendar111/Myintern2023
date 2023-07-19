from fastapi import FastAPI, WebSocket
import numpy as np
import openai
import pandas as pd
import tiktoken
import httpx

app = FastAPI()

EMBEDDING_MODEL = "text-embedding-ada-002"
MAX_SECTION_LEN = 1500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

# Fetch document embeddings and context
document_embeddings = {}
df = pd.DataFrame()  # Replace with your actual data

# Embedding code
def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(model=model, input=text)
    return result["data"][0]["embedding"]

def vector_similarity(x: list[float], y: list[float]) -> float:
    return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(
    query: str, contexts: dict[(str, str), np.array]
) -> list[(float, (str, str))]:
    query_embedding = get_embedding(query)

    document_similarities = sorted(
        [
            (vector_similarity(query_embedding, doc_embedding), doc_index)
            for doc_index, doc_embedding in contexts.items()
        ],
        reverse=True,
    )

    return document_similarities

def get_context(question: str, context_embeddings: dict, df: pd.DataFrame) -> str:
    most_relevant_document_sections = order_document_sections_by_query_similarity(
        question, context_embeddings
    )

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        num_tokens = df.loc[
            (df["title"] == section_index[0]) & (df["url"] == section_index[1])
        ].values[0][3]
        curr_text = df.loc[
            (df["title"] == section_index[0]) & (df["url"] == section_index[1])
        ].values[0][2]

        chosen_sections_len += num_tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(SEPARATOR + curr_text.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    context = "".join(chosen_sections)

    return context, chosen_sections_indexes

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()

    async with httpx.AsyncClient() as client:
        while True:
            data = await websocket.receive_text()
            if data == "disconnect":
                await websocket.close()
                break

            context, docs = get_context(data, document_embeddings, df)

            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": "Bearer YOUR_API_KEY",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. Return your response in markdown, so you can bold and highlight important steps for customers. If the answer cannot be found within the context, write 'I could not find an answer'"},
                        {"role": "system", "content": f"Use the following context from the AWS Well-Architected Framework to answer the user's query.\nContext:\n{context}"},
                                               {"role": "user", "content": data},
                    ],
                },
            )

            answer = response.json()["choices"][0]["message"]["content"].strip(" \n")
            await websocket.send_text(answer)

