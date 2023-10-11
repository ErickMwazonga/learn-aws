import os
import time
import boto3

from uuid import uuid4
from typing import Optional

from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key

app = FastAPI()


class PutTaskRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    task_id: Optional[str] = None
    is_done: bool = False


@app.get("/")
def read_root():
    return {"message": "TODO API"}


@app.put("/create-task")
async def create_task(put_task_request: PutTaskRequest):
    created_at = int(time.time())

    item = {
        "user_id": put_task_request.user_id,
        "content": put_task_request.content,
        "is_done": False,
        "created_time": created_at,
        "task_id": f"task_{uuid4().hex}",  # Primary Key
        "ttl": int(created_at + 86400),  # Expire after 24 hours.
    }

    # Put it into the table.
    table = _get_table()
    table.put_item(Item=item)
    return {"task": item}


@app.get("/get-task/{task_id}")
async def get_task(task_id: str):
    table = _get_table()
    response = table.get_item(Key={"task_id": task_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    return item


@app.get("/list-tasks/{user_id}")
async def list_tasks(user_id: str):
    # List the top N tasks from the table, using the user index.
    table = _get_table()
    response = table.query(
        IndexName="user-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False,
        Limit=10,
    )
    tasks = response.get("Items")
    return {"tasks": tasks}


@app.put("/update-task")
async def update_task(put_task_request: PutTaskRequest):
    table = _get_table()
    table.update_item(
        Key={"task_id": put_task_request.task_id},
        UpdateExpression="SET content = :content, is_done = :is_done",
        ExpressionAttributeValues={
            ":content": put_task_request.content,
            ":is_done": put_task_request.is_done,
        },
        ReturnValues="ALL_NEW",
    )
    return {"updated_task_id": put_task_request.task_id}


@app.delete("/delete-task/{task_id}")
async def delete_task(task_id: str):
    table = _get_table()
    table.delete_item(Key={"task_id": task_id})
    return {"deleted_task_id": task_id}


def _get_table():
    ddb = boto3.resource('dynamodb')
    table_name = os.environ.get("TABLE_NAME")
    return ddb.Table(table_name)


handler = Mangum(app, lifespan="off")
