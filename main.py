from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, time

# FastAPI server (configuration)
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

# MODELS
class Room(BaseModel):
    name: str
    type: str = ""
    capacity: Union[int, str]
    isAvailable: bool = False

class Teacher(BaseModel):
    name: str
    isAvailable: bool = False

class Block(BaseModel):
    name: str
    isAvailable: bool = False
    startTime: Union[time, str]
    endTime: Union[time, str]

# HTTP body MODELS
class UpdateAvailability(BaseModel):
    name: str
    isAvailable: bool

# GET

def get_rooms():
    result = query_neo4j("MATCH (room:Room) RETURN room")
    rooms = [record.data()['room'] for record in result.records]
    return [Room(**room) for room in rooms]

def get_teachers():
    result = query_neo4j("MATCH (teacher:Teacher) RETURN teacher ORDER BY teacher.name")
    teachers = [record.data()['teacher'] for record in result.records]
    return [Teacher(**teacher) for teacher in teachers]

def get_blocks():
    result = query_neo4j("MATCH (block:Block) RETURN block ORDER BY block.startTime")
    blocks = [record.data()['block'] for record in result.records]
    block_models = [Block(**block) for block in blocks]
    for block in block_models:
        block.startTime = block.startTime[:-3]
        block.endTime = block.endTime[:-3]
    return block_models

neo4j_update_SPIN_availability = 'MATCH (spin:SPIN) WHERE spin.SPIN = "{spin}" SET spin.isScheduled = {isAvailable} RETURN spin';
neo4j_update_room_availability = 'MATCH (room:Room) WHERE room.name = "{room}" SET room.isAvailable = {isAvailable} RETURN room';
neo4j_update_teacher_availability = 'MATCH (teacher:Teacher) WHERE teacher.name = "{teacher}" SET teacher.isAvailable = {isAvailable} RETURN teacher';
neo4j_update_block_availability = 'MATCH (block:Block) WHERE block.name = "{block}" SET block.isAvailable = {isAvailable} RETURN block';

def update_availability(entity: str, parameters: UpdateAvailability):
    print("This is the path and body", entity, parameters)
    if entity == "room":
        query = neo4j_update_room_availability.format(room=parameters.name, isAvailable=parameters.isAvailable)
    elif entity == 'teacher':
        query = neo4j_update_teacher_availability.format(teacher=parameters.name, isAvailable=parameters.isAvailable)
    elif entity == 'block':
        query = neo4j_update_block_availability.format(block=parameters.name, isAvailable=parameters.isAvailable)
    elif entity == 'spin':
        query = neo4j_update_SPIN_availability.format(spin=parameters.name, isAvailable=parameters.isAvailable)
    
    query_neo4j(query)


# FastAPI server

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

@app.get("/blocks")
def read_blocks():
    blocks = get_blocks()
    return get_blocks()

@app.put("/update/{entity}")
def update_entity(entity: str, parameters: UpdateAvailability):
    update_availability(entity, parameters)


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}