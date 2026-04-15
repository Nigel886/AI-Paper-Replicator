from typing import List
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks 
from fastapi.openapi.utils import get_openapi
import os
import shutil
from core.engine import PaperReplicator
from dotenv import load_dotenv

app = FastAPI(title="Lumina Paper Replicator V3-TEST")

load_dotenv()
replicator = PaperReplicator(os.getenv("GEMINI_API_KEY"))

# --- Helper function to cleanup files ---
def cleanup_temp_files(file_paths: List[str]):
    """Removes temporary files after the response is sent."""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Successfully removed: {path}")
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")

@app.post("/replicate")
async def replicate_paper(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Select multiple images"),
    output_name: str = Form("model.py")
):
    # 1. Initialize temporary directory
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_paths = []
    # 2. Save uploaded files
    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        temp_paths.append(file_path)
    
    # 3. Call the core engine
    raw_response = replicator.analyze_paper_set(temp_paths)

    # 4. Schedule the cleanup task to run AFTER the response is sent
    background_tasks.add_task(cleanup_temp_files, temp_paths)

    return {
        "status": "success",
        "analysis": raw_response,
        "suggested_filename": output_name,
        "note": "Temporary files scheduled for deletion."
    }

# ==================== The "Magic Fix": Custom OpenAPI Schema ====================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version="0.1.0",
        description="Standardized API for paper replication with multi-image support",
        routes=app.routes,
    )
    
    try:
        # Note: The Pydantic model name might change if you change function params
        properties = openapi_schema["components"]["schemas"]["Body_replicate_paper_replicate_post"]["properties"]
        if "files" in properties:
            properties["files"]["items"] = {
                "type": "string",
                "format": "binary"
            }
    except KeyError:
        pass
        
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
# ===============================================================================

# http://127.0.0.1:8000/docs
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)