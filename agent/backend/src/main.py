from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Agent.multi_agent import manager_agent
from Agent.web_agent import web_agent
from Agent.db_agent import hybrid_agent

app = FastAPI(
    title="University Legislation QA System",
    description="An API that answers questions related to university legislation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://regulations-agent.com",
        "https://www.regulations-agent.com",
        "https://regulations-agent.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str
    agent_type: str = "multi"

def process_query(query: str, agent_type: str) -> str:
    """
    Processes the query according to the selected agent type with specific instructions.
    
    Args:
        query: The user's question
        agent_type: Agent type ("multi", "web", or "db")
        
    Returns:
        String: The processed and synthesized answer
    """
    if agent_type == "web":
        return web_agent.run(f"""
User asked: "{query}"

1. Search the web for the most up-to-date information related to this query.
2. Focus on university legislation during your search.
3. Generate an answer using the most relevant and reliable sources.
4. Ensure the answer is clear, understandable, and comprehensive.
5. Specify the source of the information and highlight uncertainties when necessary.
6. Return the answer in an academic tone and professional format.
7. Provide the final answer in Turkish.
""")
    elif agent_type == "db":
        return hybrid_agent.run(f"""
User asked: "{query}"

1. Locate the most relevant documents in the legislation database related to this query.
2. Focus the search on university regulations and legislation.
3. Select the most accurate and comprehensive information.
4. Simplify the legislative language to produce a clear answer.
5. Specify the sources and regulation numbers used.
6. Return the answer in a clear, formal, and structured format.
7. Provide the final answer in Turkish.
""")
    else:
        return manager_agent.run(f"""
User asked: "{query}"

1. Send this query to both web_agent and hybrid_agent.
2. Combine the results from both sources to create a comprehensive answer.
3. Use both database information and current web information in the answer.
4. If there is conflicting information, indicate this and, if possible, explain which source may be more reliable.
5. Give your answer in a clear, understandable and professional style.
6. Give the final answer in Turkish.
""")
    
@app.get("/")
async def root():
    return {"message": "Welcome to the University Legislation QA System"}

@app.post("/ask")
async def ask_question(query: Query):
    try:
        response = process_query(query.question, query.agent_type)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)