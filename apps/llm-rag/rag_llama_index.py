from llama_parse import LlamaParse
from llama_index.core import (
    VectorStoreIndex,
    Document,
    Settings,
    StorageContext,
)
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.kdbai import KDBAIVectorStore
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core import SimpleDirectoryReader

import kdbai_client as kdbai
import os
from common_constants import (
    OPENAI_API_KEY,
    COHERE_API_KEY,
    LLAMA_CLOUD_API_KEY,
    KDBAI_API_KEY,
    KDBAI_ENDPOINT,
    KDBAI_TABLE_NAME,
    GENERATION_MODEL,
    EMBEDDING_MODEL,
)
from typing import List

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["COHERE_API_KEY"] = COHERE_API_KEY
os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY


def initialize_vector_store_and_storage_context() -> StorageContext:
    session = kdbai.Session(api_key=KDBAI_API_KEY, endpoint=KDBAI_ENDPOINT)

    schema = dict(
        columns=[
            dict(name="document_id", pytype="bytes"),
            dict(name="text", pytype="bytes"),
            dict(
                name="embedding",
                vectorIndex=dict(type="flat", metric="L2", dims=1536),
            ),
        ]
    )

    # First ensure the table does not already exist
    if KDBAI_TABLE_NAME in session.list():
        session.table(KDBAI_TABLE_NAME).drop()

    # Create the table
    table = session.create_table(KDBAI_TABLE_NAME, schema)
    vector_store = KDBAIVectorStore(table)
    return StorageContext.from_defaults(vector_store=vector_store)


def get_parsed_documents(current_file_path: str) -> List[Document]:
    upload_dir = str(os.path.join(current_file_path.parents[1], "uploads"))
    parsing_instructions = """This document is regarding a company called Bumble. It contains many tables and graphs. Answer questions using the information in this article and be precise."""
    parser = LlamaParse(
        result_type="markdown", parsing_instructions=parsing_instructions
    )

    file_extractor = {".pdf": parser}
    return SimpleDirectoryReader(upload_dir, file_extractor=file_extractor).load_data()


def get_rag_query_engine(current_file_path: str) -> BaseQueryEngine:
    llm = OpenAI(model=GENERATION_MODEL)
    embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)

    Settings.llm = llm
    Settings.embed_model = embed_model

    documents = get_parsed_documents(current_file_path)

    # Parse the documents using MarkdownElementNodeParser
    node_parser = MarkdownElementNodeParser(llm=llm, num_workers=8).from_defaults()

    # Retrieve nodes (text) and objects (table)
    nodes = node_parser.get_nodes_from_documents(documents)

    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    storage_context = initialize_vector_store_and_storage_context()
    # Create the index, inserts base_nodes and objects into KDB.AI
    recursive_index = VectorStoreIndex(
        nodes=base_nodes + objects, storage_context=storage_context
    )

    ### Define reranker
    cohere_rerank = CohereRerank(top_n=10)

    ### Create the query_engine to execute RAG pipeline using LlamaIndex, KDB.AI, and Cohere reranker
    query_engine = recursive_index.as_query_engine(
        similarity_top_k=15, node_postprocessors=[cohere_rerank]
    )

    return query_engine


# def get_response(query: str):
# response_1 = query_engine.query(query_1)

# query_1 = "What are 10 takeaways from Bumble’s equity research PDFs?"
