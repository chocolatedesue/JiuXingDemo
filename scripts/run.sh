export SECRET_KEY=dfc5e53d46f7038b955ccbae977fe657e4da15cf8ab444c1be200030ab4d62e0
uvicorn app:app  --host 0.0.0.0  --port 8000  \
 --log-config configs/logs.ini