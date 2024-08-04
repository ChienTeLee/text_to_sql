import os
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.writers import DocumentWriter
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.rankers import TransformersSimilarityRanker


def create_document_store(source):
    document_store = InMemoryDocumentStore()
    text_file_converter = TextFileToDocument()
    cleaner = DocumentCleaner()
    splitter = DocumentSplitter()
    embedder = OpenAIDocumentEmbedder()
    writer = DocumentWriter(document_store)

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("converter", text_file_converter)
    indexing_pipeline.add_component("cleaner", cleaner)
    indexing_pipeline.add_component("splitter", splitter)
    indexing_pipeline.add_component("embedder", embedder)
    indexing_pipeline.add_component("writer", writer)

    indexing_pipeline.connect("converter.documents", "cleaner.documents")
    indexing_pipeline.connect("cleaner.documents", "splitter.documents")
    indexing_pipeline.connect("splitter.documents", "embedder.documents")
    indexing_pipeline.connect("embedder.documents", "writer.documents")
    indexing_pipeline.run(data={"sources": [str(source)]})
    return document_store


def create_rag_pipeline(document_store):
    text_embedder = OpenAITextEmbedder()
    retriever = InMemoryEmbeddingRetriever(document_store)
    ranker = TransformersSimilarityRanker(model="BAAI/bge-reranker-base")
    template = """
    You are a SQLite expert.

    Please help to generate a SQLite query to answer the question. Your response should ONLY be based on the given document and follow the response guidelines.

    ===Original Query
    {{query}}

    ===Document
    {% for doc in documents %}
        {{ doc.content }}
    {% endfor %}

    ===Response Guidelines
    1. Please generate a valid query without any explanations for the question.
    2. Please use the most relevant table(s).
    3. Please format the query before responding.
    6. Please genertae the query only.
    """
    prompt_builder = PromptBuilder(template=template)
    llm = OpenAIGenerator()

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("text_embedder", text_embedder)
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("ranker", ranker)
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)

    rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    rag_pipeline.connect("retriever", "ranker")
    rag_pipeline.connect("ranker.documents", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm")
    return rag_pipeline


def run_rag_pipeline(rag_pipeline, query):
    result = rag_pipeline.run(data={"prompt_builder": {"query":query}, "text_embedder": {"text": query}, "ranker": {"query":query}})
    return result["llm"]["replies"][0]
