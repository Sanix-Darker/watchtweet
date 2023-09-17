from typing import TypedDict
from tweepy.client import Client
from tweepy.errors import Forbidden, TweepyException, Unauthorized
import logging

_LOGGER = logging.getLogger(__file__)

# Some globla tokens
_AUTHENTICATION_BEARER_TOKEN = ""

_CONSUMER_API_KEY=""
_CONSUMER_API_KEY_SECRET=""

_ACCESS_TOKEN=""
_ACCESS_TOKEN_SECRET=""

# Because elon is a DUMBASS
_REQUEST_LIMIT_PERDAY=25
_REQUEST_MADE=0


class RateLimitErrorException(Exception):
    """This appears when a limit of requests have been made, we should wait for 24h"""


class NotFoundTweetException(TweepyException):
    """When a tweet is not found by tweepy"""


class AuthenticationException(TweepyException):
    """Occurs when an client authentification fails"""


class BadTweetIdException(Exception):
    """When the tweet id is not found"""


class Quote(TypedDict):
    author: str
    text: str


# because we like "types" mdr(just to structure the response for WatchTweetStats)
class WatchTweetStats(TypedDict):
    # basic stats
    retweet_count: int
    reply_count: int
    like_count: int
    quote_count: int
    impression_count: int
    bookmark_count: int


def _check_and_get_tweet(api_client: Client, tweet_id: str) -> WatchTweetStats | dict:
    """
    Get the tweet object
    or raise an error if it's not available
    """
    global _REQUEST_MADE

    if _REQUEST_MADE >= _REQUEST_LIMIT_PERDAY:
        _LOGGER.error(
            "The rate limit happened, thanks to Elon,"
            " we need to wait for tomorrow"
        )
        raise RateLimitErrorException

    try:
        _LOGGER.info(f">> getting tweet for {tweet_id}")
        res: dict = api_client.get_tweet(
            id=tweet_id, tweet_fields=["referenced_tweets", "public_metrics"]
        ).json()  # type: ignore[assigment]

        _LOGGER.info(f"> response for {tweet_id=}", extra=res)

        _REQUEST_MADE += 1

        return {
            "retweet_count": res.get("retweet_count", 0),
            "reply_count": res.get("reply_count", 0),
            "like_count": res.get("like_count", 0),
            "quote_count": res.get("quote_count", 0),
            "impression_count": res.get("impression_count", 0),
            "bookmark_count": res.get("bookmark_count", 0),
        }
    except (Unauthorized, Forbidden) as excp:
        raise AuthenticationException from excp
    except TweepyException as excp:
        raise NotFoundTweetException from excp


def _check_and_get_twitter_client() -> Client:
    """Check and get the twitter client"""
    try:
        _LOGGER.info(">> Creating tweepy client...")
        client: Client = Client(
            bearer_token=_AUTHENTICATION_BEARER_TOKEN,
            consumer_key=_CONSUMER_API_KEY,
            consumer_secret=_CONSUMER_API_KEY_SECRET,
            access_token=_ACCESS_TOKEN,
            access_token_secret=_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        print(client)

        return client
    except TweepyException as excp:
        raise AuthenticationException from excp


def _check_and_get_tweet_id(tweet_url: str) -> str:
    """Extract the tweet-id from a tweet-url"""
    try:
        tweet_id: str = tweet_url.split("/")[-1].split("?")[0]
        if not tweet_id or len(tweet_id) < 19:
            raise BadTweetIdException(f"{tweet_id=} is not valid...")

        return tweet_id
    except Exception as excp:
        raise BadTweetIdException from excp


def get_tweet_infos(tweet_url: str) -> WatchTweetStats | dict:
    """
    Instantiate a new api client and extract the tweet object from the given
    tweet url.

    """

    api_client: Client = _check_and_get_twitter_client()
    tweet_id: str = _check_and_get_tweet_id(tweet_url)
    tweet_stats: WatchTweetStats | dict = _check_and_get_tweet(
        api_client=api_client, tweet_id=tweet_id
    )

    return tweet_stats


"""
ok, just saw how the pricing works and even on freetier, you may got some
WEIRD SHITTY ERRORS

    raise Forbidden(response)
tweepy.errors.Forbidden: 403 Forbidden
When authenticating requests to the Twitter API v2 endpoints, you must use keys and tokens from a Twitter developer App that is attached to a Project. You can create a project via the developer portal.
"""

print(get_tweet_infos("https://x.com/Morbidful/status/1703015258317578386?s=20"))
