from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# FastAPI server
app = FastAPI()

# Configure CORS: Cannot read it from sveltekit unless this is set.
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:5173",
    # Add more allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# neo4j
from neo4j import GraphDatabase

class Neo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

neo4j = Neo4j("bolt://localhost:7687", "neo4j", "password")

def  query_neo4j(query):
    return  neo4j.driver.execute_query(query)

# Get ROOMS
class Room(BaseModel):
    name: str
    type: str = ""
    capacity: Union[int, str]
    isAvailable: bool = False

class Teacher(BaseModel):
    name: str
    isAvailable: bool = False

def get_rooms():
    result = query_neo4j("MATCH (room:Room) RETURN room")
    rooms = [record.data()['room'] for record in result.records]
    return [Room(**room) for room in rooms]

def get_teachers():
    result = query_neo4j("MATCH (teacher:Teacher) RETURN teacher ORDER BY teacher.name")
    teachers = [record.data()['teacher'] for record in result.records]
    return [Teacher(**teacher) for teacher in teachers]

# FastAPI server

# app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    return {"Hello":"Enio"}

@app.get("/rooms")
def read_rooms():
    return get_rooms()

@app.get("/teachers")
def read_teachers():
    return get_teachers()

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}