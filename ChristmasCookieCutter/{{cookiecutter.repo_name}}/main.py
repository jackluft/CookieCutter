from fastapi import FastAPI, Response, status, Depends,Security
import psycopg2 as ps
from pydantic import BaseModel
from psycopg2 import pool, sql
from psycopg2.extras import execute_values
from typing import Optional, Dict, List
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer,HTTPAuthorizationCredentials
from datetime import datetime, time, timedelta
import jwt
import os
import ast
import uvicorn
import json
import sys

PORT = os.getenv("PORT")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")

SECRET_KEY = "supersecretpassword"
ALGORITM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
#Pool conection count
#min number of connections to pool
min_pool: int = 1
#max number of connections to pool
max_pool: int = 20
#Classes
class Item(BaseModel):
	id: Optional[int] = None
	first_name: str
	last_name: str
	toy: List[str]
class Toys(BaseModel):
	toy: List[str]
class AuthDetails(BaseModel):
	name: str
	password: str

class AuthHandler():
	security = HTTPBearer()
	pwd_context = CryptContext(schemes=["bcrypt"])
	secret = "supersecretpassword"

	def encode_token(self,user_id):
		payload = {"sub":user_id}
		return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITM)
	def decode_token(self,token):
		try:
			payload = jwt.decode(token,self.secret,algorithms=["HS256"])
			return payload['sub']
		except jwt.ExpiredSignatureError:
			raise  HTTPException(status_code=401,detail="signature has expired")
		except jwt.InvalidTokenError as e:
			raise HTTPException(status_code=401,detail="Invalod token")
	def auth_wrapper(self,auth: HTTPAuthorizationCredentials = Security(security)):
		return self.decode_token(auth.credentials)



class Database:
	def __init__(self):
		try:
			self.pool = pool.SimpleConnectionPool(min_pool,max_pool,user=POSTGRES_USERNAME,password=POSTGRES_PASSWORD,host=POSTGRES_HOST,port=POSTGRES_PORT,database=POSTGRES_DB_NAME)
		except Exception as e:
			print(f"Error connecting to the database ->: {e}")
			sys.exit(1)
	
	def delete_element(self,id: int):
		#NOT IN USE
		##This command this delete a element from the database
		try:
			c1 = f"DELETE FROM toys WHERE child_id = {id};"
			c2 = f"DELETE FROM children WHERE id = {id};"
			with self.pool.getconn() as self.connection:
				with self.connection.cursor() as self.cursor:
					self.cursor.execute(c1)
					self.connection.commit()
					self.cursor.execute(c2)
					self.connection.commit()
					return True
		except Exception as e:
			print(f"ERROR delete element from database: {e}")
			return False
	def remove_toys(self,id: int, toys: Toys):
		#This function will delete toys in the array based on the id. In the database
		try:
			with self.pool.getconn() as connection:
				with connection.cursor() as cursor:
					# Connected to the database
					toy_list = toys.toy
					toy_names_literals = [str(sql.Literal(name)) for name in toy_list]
					# Use parameterized query to avoid SQL injection
					command = """
					DELETE FROM toys
					WHERE child_id = %s
					AND name IN ({})
					""".format(', '.join(['%s'] * len(toy_list)))
					cursor.execute(command, [id] + toy_list)
					connection.commit()
					return {"message": f"Removed toys of Christmas lift at ID: {id}"}
		except Exception as e:
			print(f"ERROR at delete_toys: {e}")
			return {"Could not delete"}
	def add_to_christmasList(self,id:int, toys:Toys):
		#This function will let you add toys to your christmas list based on the id
		try:
			exist = self.element_exist(id,"children")
			if exist:
				#Child exist with id
				formatted_data = [(value, id) for value in toys.toy]
				command = "INSERT INTO toys (name, child_id) VALUES %s"
				with self.pool.getconn() as self.connection:
					with self.connection.cursor() as self.cursor:
						execute_values(self.cursor,command,formatted_data)
						self.connection.commit()
						return True



		except Exception as e:
			print(f"ERROR in add_to_christmasList: {e}")
			return False
	def check_elf_exist(self,elf: AuthDetails):
		#This function will check and see their exist an account for the elf
		try:
			command = f"SELECT * FROM elf WHERE name = '{elf.name}' AND password = '{elf.password}';"
			with self.pool.getconn() as self.connection:
				with self.connection.cursor() as self.cursor:
					#Connect with pool
					self.cursor.execute(command)
					self.connection.commit()
					if self.cursor.fetchone():
						#Elf exist
						return True


		except Exception as e:
			print(f"ERROR at check_elf_exist: {e}")

	def element_exist(self,id:int,table:str):
		#This function will check if a id (primary key) exist in the table provided
		try:
			command = f"SELECT * FROM {table} WHERE id = {id};"
			with self.pool.getconn() as self.connection:
				with self.connection.cursor() as self.cursor:
					self.cursor.execute(command)
					self.connection.commit()
					if self.cursor.fetchone():
						return True

		except Exception as e:
			print(f"ERROR in element_exist: {e}")
			return False
	def getChristmasList(self):
		try:
			christmas_list = []
			command = f"SELECT DISTINCT ON (children.id, children.first_name, children.last_name) children.id, children.first_name,children.last_name,ARRAY_AGG(toys.name) AS toys FROM children JOIN toys ON children.id = toys.child_id GROUP BY children.id, children.first_name, children.last_name, toys.child_id;"
			with self.pool.getconn() as self.connection:
				with self.connection.cursor() as self.cursor:
					self.cursor.execute(command)
					self.connection.commit()
					results = self.cursor.fetchall()
					for r in results:
						child_id = r[0]
						first_name = r[1]
						last_name = r[2]
						toy_list = r[3]
						wish = Item(id=child_id,first_name=first_name,last_name=first_name,toy=toy_list)
						christmas_list.append(wish)

			return christmas_list
		except Exception as e:
			print(f"----------ERROR----: {e}")
	def insert(self, data):
		try:
			#Construct command
			data_dict = data
			first_name = data.first_name
			last_name = data.last_name
			command = f"INSERT INTO children (first_name, last_name) VALUES ('{first_name}','{last_name}') RETURNING id;"
			with self.pool.getconn() as self.connection:
				with self.connection.cursor() as self.cursor:
					self.cursor.execute(command)
					self.connection.commit()
					child_id = self.cursor.fetchall()[0]
					for toy in data_dict.toy:
						command = f"INSERT INTO toys (name,child_id) VALUES ('{toy}', {child_id[0]});"
						self.cursor.execute(command)
						self.connection.commit()
			return True
		except Exception as e:
			print(f"Error inserting data into the database: {e}")
			return False
#--------------
auth_handler = AuthHandler()

app = FastAPI(title="Santas Christmas List",summary = "Chirstmas list API, where you can create and list childrens chirstmas list🎅")
connection = Database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Login page
@app.post("/login",tags=["Authentication"],description="This will be the login in url, for elfs to get their Auth Token")
async def login(account: AuthDetails):
	#This is the login page to get the token
	exist = connection.check_elf_exist(account)
	if exist:
		token = auth_handler.encode_token("jluft0661@gmial.com")
		return {"Token" : token}
	return {"elf is not in the database"}
@app.post("/create-account",tags=["Authentication"],description="This will let you create an Elf account in the database.")
async def create_account(account: AuthDetails):
	return {"None"}

#get offerations
@app.get("/christmas-list",tags=["API calls"],description="This will return all the items on Santas Christams list")
async def get_toys(token = Depends(auth_handler.auth_wrapper)) -> List[Item]:
	result = connection.getChristmasList()
	return result

#post offeration
@app.post("/christmas-list",tags=["API calls"],description="This function will let you add an item to Santas christmas list")
async def create(item: Item,token = Depends(auth_handler.auth_wrapper)):
	response = connection.insert(item)
	if response:
		return {"Added to database"}
	return {"ERROR"}

#delete operation
@app.delete("/christmas-list",tags=["API calls"],description="This will let you delete an item from Santas Christams list, by specifiy the ID of the item",status_code=201)
async def delete(item_id:int,response: Response,token = Depends(auth_handler.auth_wrapper)):
	result = connection.delete_element(item_id)
	if result:
		response.status_code = status.HTTP_201_CREATED
		return {"successfully delete element from database"}
	response.status_code = status.HTTP_404_NOT_FOUND
	return {"Coud not delete element from database"}

@app.patch("/add-to-wish",tags=["API calls"],description="This will let you add toys to your christmas list")
async def edit_list(item_id: int,toys: Toys,token = Depends(auth_handler.auth_wrapper)):
	#This function will update the christmas list base on the id
	result = connection.add_to_christmasList(item_id,toys)
	if result:
		return {"successfully added toys to Christams list🎅"}
	return {"Unable to add toys to Christams lsit, make sure the ID is valid"}
@app.delete("/remove-from-christmas",tags=["API calls"],description="This will let you delete toyos off your Christmas list")
async def delete_list(id: int,toys: Toys,token = Depends(auth_handler.auth_wrapper)):
	#This function will delete toys off christmas list based on the id
	result = connection.remove_toys(id,toys)
	return result





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
