# Backend

If you want to setup the backend locally for development, you can follow the steps below.

1. Install Python3 and sqlite3 on your machine.
2. `pip install -r ./requirements.txt`
3. `./run.sh`

Alternatively, if you need to only run the backend for frontend development, you can use the docker image. Ensure your current working directory is in the backend folder.

```bash
docker build -t backend .
docker run -p 5000:5000 --rm --name backend backend
```