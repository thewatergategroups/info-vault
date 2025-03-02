# document-parsing
- [pgvector for sqlalchemy](https://github.com/pgvector/pgvector-python?tab=readme-ov-file#sqlalchemy)
- [openai vector embeddings](https://platform.openai.com/docs/guides/embeddings)
- https://python.langchain.com/docs/integrations/providers/unstructured/
- https://python.langchain.com/docs/integrations/document_loaders/unstructured_file/
- https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.s3_directory.S3DirectoryLoader.html
- https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.s3_file.S3FileLoader.html

- https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
### Todos


DO `python -m nltk.downloader all` during docker build


### Setup
1. `touch ./credentials.json` and add the following
```json
{
    "web": {
        "client_id": "1073381030817-4if7kg2bnsshhtm0jn4nest62idt4ls1.apps.googleusercontent.com",
        "project_id": "smart-oasis-450219-t4",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "xzy",
        "redirect_uris": [
            "http://localhost:8000/redirect",
            "https://chat.treehousehl.com/redirect"
        ],
        "javascript_origins": [
            "http://localhost:8000",
            "https://chat.treehousehl.com"
        ]
    }
}
```