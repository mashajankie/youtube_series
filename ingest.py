import logging
import os
import fnmatch
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from utils.code.general.ignore_list import IGNORE_LIST


from constants import (
    CHROMA_SETTINGS,
    DOCUMENT_MAP,
    EMBEDDING_MODEL_NAME,
    INGEST_THREADS,
    PERSIST_DIRECTORY,
    SOURCE_DIRECTORY,
)


def load_single_document(file_path: str) -> Document:
    # Loads a single document from a file path
    file_extension = os.path.splitext(file_path)[1]
    loader_class = DOCUMENT_MAP.get(file_extension)
    if loader_class:
        loader = loader_class(file_path)
    else:
        raise ValueError("Document type is undefined")
    return loader.load()[0]


def load_document_batch(filepaths):
    logging.info("Loading document batch")
    # create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # load files
        futures = [exe.submit(load_single_document, name) for name in filepaths]
        # collect data
        data_list = [future.result() for future in futures]
        # return data and file paths
        return (data_list, filepaths)

def should_ignore(path: str, ignore_list: list[str]) -> bool:
    """Check if the given path should be ignored based on the ignore list."""
    for pattern in ignore_list:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def load_documents(source_dir: str) -> list[Document]:
    # Loads all documents from the source documents directory, including nested folders
    paths = []
    for root, _, files in os.walk(source_dir):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1]
            source_file_path = os.path.join(root, file_name)
            # Check if the path should be ignored
            if should_ignore(source_file_path, IGNORE_LIST):
                continue
            if file_extension in DOCUMENT_MAP.keys():
                paths.append(source_file_path)

    # Have at least one worker and at most INGEST_THREADS workers
    n_workers = min(INGEST_THREADS, max(len(paths), 1))
    chunksize = round(len(paths) / n_workers)
    docs = []
    with ProcessPoolExecutor(n_workers) as executor:
        futures = []
        # split the load operations into chunks
        for i in range(0, len(paths), chunksize):
            # select a chunk of filenames
            filepaths = paths[i : (i + chunksize)]
            # submit the task
            future = executor.submit(load_document_batch, filepaths)
            futures.append(future)
        # process all results
        for future in as_completed(futures):
            # open the file and load the data
            contents, _ = future.result()
            docs.extend(contents)

    return docs


def split_documents(documents: list[Document]) -> tuple[list[Document], list[Document]]:
    # Splits documents for correct Text Splitter
    text_docs, python_docs, script_docs, markdown_docs = [], [], [], []
    for doc in documents:
        file_extension = os.path.splitext(doc.metadata["source"])[1]
        if file_extension == ".py":
            python_docs.append(doc)
        elif file_extension in [".js", ".jsx", ".ts", ".tsx"]:
            script_docs.append(doc)
        elif file_extension == ".md":
            markdown_docs.append(doc)
        else:
            text_docs.append(doc)

    return text_docs, python_docs, script_docs, markdown_docs


device_type = 'cpu'
def main(device_type=device_type):
    # Load documents and split in chunks
    logging.info(f"Loading documents from {SOURCE_DIRECTORY}")
    documents = load_documents(SOURCE_DIRECTORY)
    text_documents, python_documents, script_documents, markdown_documents = split_documents(documents)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=880, chunk_overlap=200
    )
    script_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JS, chunk_size=880, chunk_overlap=200
    )
    markdown_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN, chunk_size=880, chunk_overlap=200
    )

    texts = text_splitter.split_documents(text_documents)
    texts.extend(python_splitter.split_documents(python_documents))
    texts.extend(script_splitter.split_documents(script_documents))
    texts.extend(markdown_splitter.split_documents(markdown_documents))

    logging.info(f"Loaded {len(documents)} documents from {SOURCE_DIRECTORY}")
    logging.info(f"Split into {len(texts)} chunks of text")

    # Create embeddings
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": device_type},
    )
    # change the embedding type here if you are running into issues.
    # These are much smaller embeddings and will work for most appications
    # If you use HuggingFaceEmbeddings, make sure to also use the same in the
    # run_localGPT.py file.

    # embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    db = Chroma.from_documents(
        texts,
        embeddings,
        persist_directory=PERSIST_DIRECTORY,
        client_settings=CHROMA_SETTINGS,
    )
   
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    main()