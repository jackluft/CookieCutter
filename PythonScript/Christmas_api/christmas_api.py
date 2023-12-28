import requests
from pydantic import BaseModel
from typing import Optional, Dict, List
from .item import Item

class ChristmasAPI:
    def __init__(self,base_url: str):
        self.URL = base_url
        self.token = None
    
    def login(self,user:str,password: str):
        #This function will try and login into the api and return a token if successful
        payload = {
        "name": user,
        "password": password
        
        }
        url = self.URL +"/login"
        response = requests.post(url,json=payload)
        if response.status_code == 200:
            data =response.json()
            
            data_token = data["Token"]
            self.token = data_token
            return "Successfully login"
        else:
            return "Unable to login to api, check username and password"
            
    def create_account(self,user:str,password:str):
        #This function will create a account in the database
        payload = {
        "name": user,
        "password": password
        }
        url = self.URL+"create-account"
        response = response.post(url,json=playload)
        if response.status_code == 201:
            return "Elf account has been created!"
        else:
            return "ERROR, creating Elf account"

    def christmasList(self):
        #This function will get all the christmas list from the api
        if self.token != None:
            header = {"Authorization": f"Bearer {self.token}"}
            url = self.URL+"/christmas-list"
            response = requests.get(url,headers=header)
            return response.json()
        return "Token has not been Authericated. Please login with the login() function"
        
    def createChristmasList(self, wish: Item):
        #This function will add a wish to the christmas list
        if self.token != None:
            header = {"Authorization": f"Bearer {self.token}"}
            url = self.URL+"/christmas-list"
            response = requests.post(url,headers=header,json=wish.dict())
            return response.json()
        return "Token has not been Authericated. Please login with the login() function"
        
    def deleteChristmasWish(self, id: int):
        #This function will delete a christmas wish from the christmas list
        if self.token != None:
            header = {"Authorization": f"Bearer {self.token}"}
            args = {"item_id":id}
            url = self.URL+"/christmas-list"
            response = requests.delete(url,headers=header,params=args)
            if response.status_code == 201:
                return "Wish deleted from chirstmas list"
        else:
            return "Token has not been Authericated. Please login with the login() function"
            
    def addToWish(self, id: int, toys: List[str]):
        #This function will add toys to your christlist based on the id.
        if self.token != None:
            header = {"Authorization": f"Bearer {self.token}"}
            args = {"item_id":id}
            url = self.URL+"/add-to-wish"
            response = requests.patch(url,headers=header,json=toys,params=args)
            return response.json()
        else:
            return "Token has not been Authericated. Please login with the login() function"
        
    def deleteToysFromWish(self,id: int, toys: List[str]):
        #This function will let you delete toys from your christmas list
        if self.token != None:
            header = {"Authorization": f"Bearer {self.token}"}
            args = {"id":id}
            url = self.URL+"/remove-from-christmas"
            response = requests.delete(url,headers=header,json=toys,params=args)
            return response.json()
        else:
            return "Token has not been Authericated. Please login with the login() function"
data = {"first_name": "Python", "last_name": "fake", "toy": ["C++", "Java", "Books"]}
x = Item(**data)#.model_dump_json()

