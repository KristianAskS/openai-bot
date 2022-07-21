import re
import requests


def get_petit_url() -> str:
    response = requests.get("https://petittube.com").text
    youtube_string = "https://www.youtube.com/watch?v="

    # the link to the video is in a youtube embed tag
    # the second group of the result will be something like this:
    # mIHw4UXX01o?version=3&f=videos&app=youtube_gdata&autoplay=1
    result = re.search(r"www.youtube.com/embed/(.*?)\"", response).group(1)
    video_id = result.split("?")[0]

    return youtube_string + video_id
