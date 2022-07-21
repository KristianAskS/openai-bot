import requests
import datetime
import random
import re

MINIMUM_VIDEO_DURATION_SEC = 18
MAXIMUM_DURATION_SEC = 70


class DailyLimitReached(Exception):
    """raised if YouTube v3 API key daily limit reached"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


def init_query_params(params, api_key):
    """Initializes the params that will be sent to the YouTube API"""

    this_week = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )

    params["key"] = api_key
    params["part"] = "snippet"
    params["type"] = "video"
    params["order"] = "date"
    params["maxResults"] = 50
    params["videoEmbeddable"] = "true"
    params["publishedAfter"] = this_week

    return params


def list_videos(yt_api_key, video_ids):
    """Returns a list of videos with the list of given IDs"""
    params = {}
    params["key"] = yt_api_key
    params["id"] = ",".join(video_ids)
    params["part"] = "id,statistics,snippet,contentDetails"
    params["maxResults"] = len(video_ids)

    request = requests.get(
        "https://www.googleapis.com/youtube/v3/videos", params=params
    ).json()

    return request


def format_response(video_list, view_count_dict):
    """Formats the response from the API"""

    video_results = []
    for item in video_list:
        video = {}
        video["id"] = item["id"]["videoId"]
        video["title"] = item["snippet"]["title"]
        video["creator"] = item["snippet"]["channelTitle"]
        video["view_count"] = view_count_dict.get(item["id"]["videoId"], 0)

        video_results.append(video)

    return video_results


def search(params, api_key):
    """Searches the YouTube API and formats the response"""

    params = init_query_params(params, api_key)
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/search", params=params
    ).json()

    if "error" in response.keys():
        # Daily quota for query searches reached
        raise DailyLimitReached("Daily limit for API key reached")

    # After we've found the video IDs, we need to get the view count
    # for each of them
    video_list = list_videos(
        api_key, [video["id"]["videoId"] for video in response["items"]]
    )

    # If the video is not between 18 and 70 seconds, it's added
    # To this list
    disallowed_video_ids = []
    view_count_dict = {}

    for video in video_list["items"]:

        view_count = int(video["statistics"]["viewCount"])
        duration_in_sec = parse_video_duration(video["contentDetails"]["duration"])
        if (
            not MINIMUM_VIDEO_DURATION_SEC < duration_in_sec < MAXIMUM_DURATION_SEC
            or view_count > 2
        ):
            disallowed_video_ids.append(video["id"])
        else:
            view_count_dict[video["id"]] = view_count

    video_list = [
        video
        for video in response["items"]
        if video["id"]["videoId"] not in disallowed_video_ids
    ]

    return format_response(video_list, view_count_dict)


def parse_video_duration(duration):
    """
    Parses the duration of a video and returns the duration in seconds
    """
    try:
        parsed_duration = re.search(f"PT(\d+H)?(\d+M)?(\d+S)", duration).groups()
        return sum(
            [
                int(duration[:-1]) * x
                for duration, x in zip(parsed_duration, [3600, 60, 1])
                if duration is not None
            ]
        )
    except AttributeError:
        return MAXIMUM_DURATION_SEC + 1


def create_queries(start_index, end_index):
    """Creates queries for the YouTube API, e.g: ["VID 0001"]"""
    queries = []
    tags = ["DSC", "IMG", "VID", "MOV"]
    for tag in tags:
        for i in range(end_index, start_index - 1, -1):
            params = {}
            params["q"] = '"' + tag + " " + str(i).zfill(4) + '"'
            queries.append(params)
    return queries


def get_vids(yt_api_key, amount=1):
    """
    Returns a list of dicts containing information about videos
    with titles such as "VID 0001" these often have no more than 1-5 views
    """

    start_index = 1
    end_index = 100

    queries = create_queries(start_index, end_index)
    random.shuffle(queries)

    # Changes the format for the queries from '"VID 0001"' to 'VID 0001'
    # And stores the queries in a list
    query_searches = [query.get("q")[1:-1] for query in create_queries(1, 9999)]

    results = []
    for query in queries:
        video_results = search(query, yt_api_key)
        results.extend([vid for vid in video_results if vid["title"] in query_searches])
        if len(results) >= amount:
            break

    return results
