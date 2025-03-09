# document-parsing
- [pgvector for sqlalchemy](https://github.com/pgvector/pgvector-python?tab=readme-ov-file#sqlalchemy)
- [openai vector embeddings](https://platform.openai.com/docs/guides/embeddings)
- https://python.langchain.com/docs/integrations/providers/unstructured/
- https://python.langchain.com/docs/integrations/document_loaders/unstructured_file/
- https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.s3_directory.S3DirectoryLoader.html
- https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.s3_file.S3FileLoader.html

- https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
- https://github.com/fastapi-users/fastapi-users?tab=readme-ov-file
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

https://accounts.google.com/signin/oauth/error/v2?authError=ChVyZWRpcmVjdF91cmlfbWlzbWF0Y2gSsAEKWW91IGNhbid0IHNpZ24gaW4gdG8gdGhpcyBhcHAgYmVjYXVzZSBpdCBkb2Vzbid0IGNvbXBseSB3aXRoIEdvb2dsZSdzIE9BdXRoIDIuMCBwb2xpY3kuCgpJZiB5b3UncmUgdGhlIGFwcCBkZXZlbG9wZXIsIHJlZ2lzdGVyIHRoZSByZWRpcmVjdCBVUkkgaW4gdGhlIEdvb2dsZSBDbG91ZCBDb25zb2xlLgogIBptaHR0cHM6Ly9kZXZlbG9wZXJzLmdvb2dsZS5jb20vaWRlbnRpdHkvcHJvdG9jb2xzL29hdXRoMi93ZWItc2VydmVyI2F1dGhvcml6YXRpb24tZXJyb3JzLXJlZGlyZWN0LXVyaS1taXNtYXRjaCCQAyo6CgxyZWRpcmVjdF91cmkSKmh0dHA6Ly9sb2NhbGhvc3Q6ODAwMC9hdXRoL2dvb2dsZS9jYWxsYmFjazKkAggBErABCllvdSBjYW4ndCBzaWduIGluIHRvIHRoaXMgYXBwIGJlY2F1c2UgaXQgZG9lc24ndCBjb21wbHkgd2l0aCBHb29nbGUncyBPQXV0aCAyLjAgcG9saWN5LgoKSWYgeW91J3JlIHRoZSBhcHAgZGV2ZWxvcGVyLCByZWdpc3RlciB0aGUgcmVkaXJlY3QgVVJJIGluIHRoZSBHb29nbGUgQ2xvdWQgQ29uc29sZS4KICAabWh0dHBzOi8vZGV2ZWxvcGVycy5nb29nbGUuY29tL2lkZW50aXR5L3Byb3RvY29scy9vYXV0aDIvd2ViLXNlcnZlciNhdXRob3JpemF0aW9uLWVycm9ycy1yZWRpcmVjdC11cmktbWlzbWF0Y2g%3D&client_id=1073381030817-4if7kg2bnsshhtm0jn4nest62idt4ls1.apps.googleusercontent.com&flowName=GeneralOAuthFlow