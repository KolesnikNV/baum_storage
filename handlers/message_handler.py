from datetime import datetime

from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.engine import engine, get_db
from db.models import Base, MessageModel
from shemes.messages_sheme import ResultData, ResultList
from utils.rabbit_sender import MessageSender

app = FastAPI()
message_router = APIRouter()
sender = MessageSender("rabbit", 5672)


@message_router.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


@message_router.on_event("shutdown")
async def shutdown_event():
    print("Shutting down. Cleaning up resources.")
    engine.dispose()


@message_router.post("/upload-text/")
async def upload_text(
    title: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        with open(file.filename, "r", encoding="utf-8") as f:
            for line in f:
                message = {
                    "datetime": datetime.utcnow(),
                    "title": title,
                    "text": f"{line}",
                }
                sender.send_message("message_queue", message)
        f.close()
        return {"status": "Text uploaded"}
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="File not found")
    except Exception as e:
        return {"status": "Error", "error_message": str(e)}


@message_router.get("/results/", response_model=ResultList)
async def get_results(db: Session = Depends(get_db)):
    try:
        query = select(MessageModel)
        results = db.execute(query).fetchall()
        result_list = []
        for result in results:
            x_avg_count = await calculate_x_avg_count(result.text)
            result_list.append(
                ResultData(
                    datetime=str(result.datetime),
                    title=result.title,
                    x_avg_count_in_line=x_avg_count,
                    text=result.text,
                )
            )
        return {"data": result_list}
    finally:
        db.close()


async def calculate_x_avg_count(text: str) -> float:
    count_x = text.lower().count("x")
    lines = text.split("\n")
    return count_x / len(lines) if len(lines) > 0 else 0
