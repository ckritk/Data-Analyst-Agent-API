import os
import shutil

from fastapi import FastAPI, Request, UploadFile, HTTPException
from typing import List

from classify import (
    classify,
    handle_execute_code_class,
    api_creation,
    simple_llm,
    static_answer,
    query_only
)

SAVE_FOLDER = "files"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def save_and_decode_file(upload: UploadFile) -> dict:
    file_path = os.path.join(SAVE_FOLDER, upload.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    try:
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8")
    except UnicodeDecodeError:
        content = f"<binary file saved at {file_path}>"
    except Exception as e:
        content = f"<error reading file: {e}>"

    return {
        "filename": upload.filename,
        "content": content
    }

app = FastAPI()

@app.post("/api")
async def upload_files(request: Request):
    form = await request.form()
    uploads = []

    for value in form.values():
        if hasattr(value, "filename") and value.filename:  # file upload
            uploads.append(value)

    if not uploads:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results = []
    question_text = None

    for f in uploads:
        file_info = save_and_decode_file(f)
        results.append(file_info)

        if f.filename.lower() in ("questions.txt", "question.txt"):
            question_text = file_info["content"]

    if not question_text:
        raise HTTPException(status_code=400, detail="Missing required questions.txt file")

    print(question_text)
    if not question_text.strip():
        raise HTTPException(status_code=400, detail="questions.txt is empty")

    try:
        category = classify(question_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    try:
        print(category)
        if category == "code_execution":
            answer = handle_execute_code_class(question_text)
        elif category == "api_creation":
            answer = api_creation(question_text)
        elif category == "simple_llm":
            answer = simple_llm(question_text)
        elif category == "static_answer":
            answer = static_answer(question_text)
        elif category == "query_only":
            answer = query_only(question_text)
        else:
            answer = f"Unsupported category: {category}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling category '{category}': {str(e)}")
    print(answer)
    return answer

