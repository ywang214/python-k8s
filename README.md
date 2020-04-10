<b>A python app using Flask, deploying on kubernetes</b>

# kubernetes deployment
```kubectl create -f deployment.yaml```

# docker deployment
- Build python service image
```
cd api
docker build -t python-api
```
- Build postgres db image
```
cd ../db
docker build -t postgres .
```
- Start running docker containers 
```
cd ..
docker-compose up -d
```

# apis:
Upload API
http://localhost:5000/

Download API
http://localhost:5000/text.txt

Erase API
curl http://localhost:5000/data -X DELETE

Endpoint to query current database data
http://localhost:5000/data OR
curl http://localhost:5000/data -X GET


