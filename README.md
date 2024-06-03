# Prosights ChatBot

## Project Demo Video

[![Watch the video](https://raw.githubusercontent.com/Kingpin-27/prosights-chatbot/main/demo-assets/Project%20Thumbnail.png)](https://raw.githubusercontent.com/Kingpin-27/prosights-chatbot/main/demo-assets/Project%20Demo.mp4)

## Install Requirements

Run `pip install requirements.txt && npm install`

## Project Structure

```
├───apps
│   ├───chat-be             <---- Express-Node backend app
│   ├───chat-fe             <---- Angular-Tailwind fronetend app
│   └───llm-rag             <---- FastAPI + LlamaIndex RAG server
├───demo-assets
├───libs
│   ├───backend
│   │   └───chatbot-core    <---- TRPC Server config
│   └───frontend
│       └───utils
│           └───api-client  <---- TRPC Client config
├───uploads                 <---- directory for all RAG file uploads
```

## Start the application

1. Run `npm run dev:be` to start the Node backend app
2. Run `npm run dev:fe` to start the Angular fronetend app
3. Run `npm run rag-server` to start the RAG server

## Explanation

1. The RAG Server consists of :
    - Parse the uploaded PDFs from the `uploads\` folder.
    - Clean the Embedding table in KDB.AI Vector Database and initialize the table
    - Configure a MarkdownElementNodeParser and recursive retrieval RAG technique to hierarchically index and query over tables and text in the uploaded documents
    - Get the RAG QueryEngine configured with Post processing Rerank embedding model (Cohere) which is used to RAG over complex documents that can answer questions over both tabular and unstructured data
    - A FastAPI server to trigger the file upload process and to query the RAG Server
2. The Angular Frontend app consists of:
    - A TRPC Client to communicate with the backend server
    - An Upload Component which accepts documents to be uploaded
    - A Chat component to interact with the AI assistant to fetch details from the previously uploaded PDFs
3. The Node backend app consists of:
    - `/api` route to connect the TRPC Server, which is used to communicate with the browser client
    - `/upload` route to accept files, to circumvent the issue of multipart-formdata not supported by trpc at the moment
4. The project uses Nx Monorepo framework to host all the above apps

## Screenshots

-   Upload Screen
    ![Screenshot-1](https://raw.githubusercontent.com/Kingpin-27/prosights-chatbot/main/demo-assets/Project%20Thumbnail.png)

-   Answer from given Bumble's Equity research PDF
    ![Screenshot-2](https://raw.githubusercontent.com/Kingpin-27/prosights-chatbot/main/demo-assets/Equity%20research%20PDFs%20convo.png)

-   Answer from given Bumble's Tegus Expert Call PDFs
    ![Screenshot-3](https://raw.githubusercontent.com/Kingpin-27/prosights-chatbot/main/demo-assets/Tegus%20Call%20transcript%20convo.png)
