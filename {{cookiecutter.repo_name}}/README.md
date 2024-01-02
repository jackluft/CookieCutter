#Welcome to the Christmas API
---------------------------------------------------------------------------------------------------------------------------------------
To get started make sure you have docker & docker-compose installed on your local machine.
If you wish to customize the postgres setting like: (username,password,port). Navigate to the docker-compose.yml file to changes this enviroment variables.
If you wish to customize the fastAPI settings like:(port,POSTGRES_HOST,POSTGRES_PORT,POSTGRES_USERNAME,POSTGRES_PASSWORD,ext). Navigate to the 
docker-compose.yml file under the fastapi_app: sections. These values will be used in the FastAPI script to connect to the database.
After docker has been installed run "docker-compose build".
This command will create the images required for the API. These images include: Postgres container, FastAPI (Python) container, and Flyway container.
After docker-compose build has successfully finished. You can run the containers in images but executing the command: "docker-compose up".
This will start all the required images and you will be able to connect to the API.

To get documentation on how to the works and its functionality, navigate to the: domainName/docs. (default: 'http://127.0.0.1/docs')
This will give you the swagger documentation of the API. Once you have started the API, you will need to get a JWT token to make
any requests. To get a token you must login or create an account in the database. To create an account, go to the hostname/create-account
and and provide your username and password, in json format. If you already have an account in the database, go to
hostname/login and provide your username and password as json. After succefully logging in you will recieve a 200 status code, with the
JWT Authenticaion code. With this token you will be able to make requires to all other API end points.
