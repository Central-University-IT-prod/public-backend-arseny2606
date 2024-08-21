wait-for-it travel_bot_database:5432
alembic upgrade head
pytest
python3 main.py