# omero server
clone install if you not have omero https://github.com/ome/docker-example-omero

# bundle

The production bundle of the application.

## 1 Submodules

### 1.1 Init all submodules
```bash
git submodule update --init
git submodule foreach git checkout master
```

### 1.2 Update all submodules
```bash
git pull
git submodule foreach "git fetch && git reset --hard @{u}"
```

## 2 Add .evn.local


### 2.1 env.common

Go to `microservices` folder, copy `.env.common` file and paste with name `.evn.common.local`.
In the file need to keep only the follow variables:
```dotenv
ARANGODB_PASSWORD=
REDIS_PASSWORD=
OMERO_HOST=
OMERO_WEB=
```
And set correct values for the variables.
Also, you can override any other variables from `.evn.common` file.

### 2.2 env.local

In all `microservices/ms-*` folders need to create empty `.env.local` file.
You can override any other variables from `.evn` file if you know what you do.


### 2.3 backend .env.local

Go to folder `backend`, copy `.env` file and paste with name `.evn.local`.
In the file need to keep only the follow variables:
```dotenv
ARANGODB_PASSWORD=

JWT_SECRET_KEY=

# env for docker
ARANGO_ROOT_PASSWORD=${ARANGODB_PASSWORD}
```
And set correct values for the variables.
Also, you can override any other variables from `.evn` file.
## before run commands
[I think you need to install docker on the server](https://www.docker.com/)

[and have access to omero server or install it locally](https://github.com/ome/docker-example-omero)


## 3 Commands of the application

To start the first time:
```bash
./app.sh build
```

To stop:
```bash
./app.sh stop
```

To start:
```bash
./app.sh start
```

to down (remove all docker containers of the application):
```bash
./app.sh down
```

to start after down:
```bash
./app.sh up
```

For more information run:
```bash
./app.sh usage
```
