import twitter
import code
import discord
import os
import time
import re
import asyncio
import logging

from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import create_engine
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from models import Subscription, User, Status
from utils import DiscordLogging, Twitter

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN_KEY = os.getenv("ACCESS_TOKEN_KEY")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
PING_INTERVAL_IN_SECONDS = 10


engine = create_async_engine(f"postgresql+asyncpg://postgres:1234@pyatlas-db/postgres")
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

api = Twitter(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token_key=ACCESS_TOKEN_KEY,
    access_token_secret=ACCESS_TOKEN_SECRET,
    async_db_session=async_session,
    pool=ThreadPoolExecutor,
)


# Session = sessionmaker()
# Session.configure(bind=engine)
# session = Session()

BOT_TOKEN = os.getenv("BOT_TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


async def ping_twitter():
    await client.wait_until_ready()
    # channel = client.get_channel(id=123456789) # replace with channel_id
    while not client.is_closed():
        await asyncio.sleep(PING_INTERVAL_IN_SECONDS)
        async with async_session() as session:
            # Why are we prefetching users? Because greenlet doesn't like ORM's lazy loading
            # https://stackoverflow.com/questions/68195361/how-to-properly-handle-many-to-many-in-async-sqlalchemy
            q = select(Subscription).options(selectinload(Subscription.users))
            result = await session.execute(q)
            subscriptions = list(result.scalars())
            print(subscriptions)
        if subscriptions:
            # session.add_all(subscriptions)
            for subscription in subscriptions:
                topic = subscription.text
                users = subscription.users
                channel = client.get_channel(id=int(subscription.channel_id))
                # q = select(subscription.users)
                # result = await session.execute(q)
                # users = list(result.scalars())
                usernames = (", ").join([f"<@{user.discord_id}>" for user in users])
                try:
                    data = await api.grab_latest_tweet(topic)
                    if data:
                        embed = DiscordLogging.info(usernames, footer=data)
                        await channel.send(f"{usernames} {data}")
                except twitter.error.TwitterError as e:
                    # await channel.send(embed=DiscordLogging.error(e))
                    pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("/atlas follow"):
        topic = re.sub("/atlas follow +", "", message.content)
        try:
            embed = await api.add_new_twitter_subscription(
                topic,
                str(message.channel.id),
                message.author.name,
                str(message.author.id),
            )
            await message.channel.send(embed=embed)

        except twitter.error.TwitterError as e:
            await message.channel.send(embed=DiscordLogging.error(e))


if __name__ == "__main__":
    print("Listening for new Tweets...")

    client.loop.create_task(ping_twitter())
    client.run(BOT_TOKEN)
