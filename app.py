import twitter
import code
import os
import time

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN_KEY = os.getenv("ACCESS_TOKEN_KEY")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


api = twitter.Api(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token_key=ACCESS_TOKEN_KEY,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

engine = create_engine(f"postgresql://postgres:1234@pyatlas-db/postgres")
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

if __name__ == "__main__":
    print("Listening for new Tweets...")

    while True:
        time.sleep(3600)

    # results = api.GetSearch(raw_query="q=ukraine%20&result_type=recent&count=100")
    # statuses = api.GetUserTimeline(screen_name="MaximEristavi")

    # for status in statuses:
    #     print(f"https://www.twitter.com/{status.user.screen_name}/status/{status.id}")
