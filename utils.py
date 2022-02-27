import profile
from discord import Embed, Colour
from typing import Tuple, List, Union
from dataclasses import dataclass
from enum import Enum
from twitter import Api, models
from sqlalchemy.ext.asyncio import AsyncSession
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from asyncio import get_running_loop
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy.orm import selectinload


from models import Subscription, Status, User


class DiscordLogging:
    @classmethod
    def _format(
        cls, rgb: Tuple, description: str, footer: str = None, thumbnail: str = None
    ):
        embed = Embed(description=description, colour=Colour.from_rgb(*rgb))
        if footer:
            embed.set_footer(text=footer)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        return embed

    @classmethod
    def plaintext(cls, text):
        return text

    @classmethod
    def error(cls, text, **kwargs) -> Embed:
        return cls._format(description=text, rgb=(252, 28, 3), **kwargs)

    @classmethod
    def info(cls, text, **kwargs) -> Embed:
        return cls._format(description=text, rgb=(52, 235, 82), **kwargs)

    @classmethod
    def warning(cls, text, **kwargs) -> Embed:
        return cls._format(description=text, rgb=(255, 207, 33), **kwargs)


@dataclass
class Twitter:
    consumer_key: str
    consumer_secret: str
    access_token_key: str
    access_token_secret: str
    async_db_session: AsyncSession
    pool: ThreadPoolExecutor

    class Type(Enum):
        USER = 0
        HASHTAG = 1
        QUERY = 2

    @cached_property
    def _event_loop(self):
        return get_running_loop()

    @cached_property
    def _api(self) -> Api:
        return Api(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.access_token_key,
            access_token_secret=self.access_token_secret,
        )

    def _determine_subscription_type(self, text: str):
        if text.startswith("@"):
            return self.Type.USER
        if text.startswith("#"):
            return self.Type.HASHTAG
        return self.Type.QUERY

    def _status_url(self, status: models.Status) -> str:
        return f"https://www.twitter.com/{status.user.screen_name}/status/{status.id}"

    async def add_new_twitter_subscription(
        self, handle: str, channel_id: str, username: str, discord_id: str
    ) -> DiscordLogging:
        handle_type = self._determine_subscription_type(handle)
        if handle_type == self.Type.USER:
            async with self.async_db_session() as session:
                # Before anything else, check if this Discord user is in our db. If not, create an entry for them
                q = select(User).where(User.username == username)
                result = await session.execute(q)
                if data := list(result.scalars()):
                    user = data.pop()
                else:
                    user = User(username=username, discord_id=discord_id)
                    session.add_all([user])
                    await session.commit()

                # Check if there is already a subscription for this topic in this channel
                q = (
                    select(Subscription)
                    .where(
                        and_(
                            Subscription.text == handle,
                            Subscription.channel_id == channel_id,
                        )
                    )
                    .options(selectinload(Subscription.users))
                )
                result = await session.execute(q)
                sub_list = list(result.scalars())

                # If a subscription already exists, then we just need to add this user to that subscription
                if sub_list:
                    sub = sub_list.pop()
                    # Check if this user is already subscribed to this topic
                    if user not in sub.users:
                        sub.users.append(user)
                        session.add_all([sub])
                        await session.commit()
                    return DiscordLogging.info(
                        f"Hi <@{discord_id}>! Looks like you already subscribed to this topic. If you deactivated your subscription, it is now active!"
                    )

                else:
                    new_sub = Subscription(channel_id=channel_id, text=handle)
                    new_sub.users.append(user)
                    session.add_all([new_sub])
                    await session.commit()

                    with self.pool() as executor:
                        sub_user = await self._event_loop.run_in_executor(
                            executor,
                            lambda: self._api.GetUser(screen_name=handle),
                        )

                    return DiscordLogging.info(
                        f"Hi <@{discord_id}>! you are now subscribed to {handle}!",
                        thumbnail=sub_user.profile_image_url,
                    )

    async def grab_latest_tweet(self, handle: str) -> Union[str, bool]:
        handle_type = self._determine_subscription_type(handle)
        if handle_type == self.Type.USER:
            with self.pool() as executor:
                statuses = await self._event_loop.run_in_executor(
                    executor,
                    lambda: self._api.GetUserTimeline(
                        screen_name=handle, exclude_replies=True, count=1
                    ),
                )

                twitter_status = statuses.pop()
                # Check if this is new

                async with self.async_db_session() as session:
                    # Remember that we store these Twitter IDs as varchars
                    q = select(Status).where(
                        Status.twitter_id == str(twitter_status.id)
                    )
                    result = await session.execute(q)
                    status = list(result.scalars())

                    if not status:
                        # This tweet is new to us so we need to record it
                        new_status = Status(twitter_id=str(twitter_status.id))
                        session.add_all([new_status])
                        await session.commit()

                        # Now return the status URL
                        return self._status_url(twitter_status)

        return False
