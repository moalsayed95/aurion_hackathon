from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.claims import router as claims_router
from server.routes.claims_stream import router as claims_stream_router
from server.routes.mailbox import router as mailbox_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Aurion Claim Workflow API",
        version="0.1.0",
        description="Automated insurance claim intake workflow for Aurion",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(claims_router, prefix="/api")
    app.include_router(claims_stream_router, prefix="/api")
    app.include_router(mailbox_router, prefix="/api")

    @app.get("/api/workflow/diagram")
    def workflow_diagram():
        from agent_framework import WorkflowViz

        from server.deps import get_workflow

        workflow = get_workflow()
        viz = WorkflowViz(workflow)
        return {"mermaid": viz.to_mermaid()}

    return app


app = create_app()


def start():
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
