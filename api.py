import decouple
import requests
from db import TMDB_media_detail_clt


TMBD_API_KEY = decouple.config("TMBD_API_KEY")
TMBD_API_READ_ACCESS_TOKEN = decouple.config("TMBD_API_READ_ACCESS_TOKEN")
TV_MEDIA_TYPE = "tv"
MOVIE_MEDIA_TYPE = "movie"
TMDB_IMG_URL = r"https://image.tmdb.org/t/p/w500/"
TMDB_MOVIE_PAGE = r"https://www.themoviedb.org/movie/"
TMDB_TV_SERIES_PAGE = r"https://www.themoviedb.org/tv/"


# TMBD API
TMBD_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMBD_API_READ_ACCESS_TOKEN}"
}

TMDB_MOVIE_DETAIL = "https://api.themoviedb.org/3/movie/"
TMDB_TV_SERIES_DETAIL = "https://api.themoviedb.org/3/tv/"


def TMDB_search_by_phrase(phrase, language="en-US"):
    """
    Searches for movies or TV series based on a given phrase and language.

    Args:
        phrase (str): The search phrase.
        language (str): The language you want to see the answer in

    Returns:
        dict or str: A dictionary containing search results if successful,
            otherwise returns 'error'.
    """
    url = f"https://api.themoviedb.org/3/search/multi?query={phrase}&language={language}"
    response = requests.get(url, headers=TMBD_HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        return "error"


def TMDB_get_movie_detail(movie_id, language="en-us"):
    """
    Retrieves detailed information about a movie.

    Args:
        movie_id (int): The ID of the movie.
        language (str): The language you want to see the answer in

    Returns:
        dict or str: A dictionary containing movie details if successful,
            otherwise returns 'error'.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language={language}"
    response = requests.get(url, headers=TMBD_HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        return "error"


def TMDB_get_movie_credits_name(movie_id, limit_number=5, language="en-US"):
    """
    Retrieves the credits (cast, directors, writers) for a movie.

    Args:
        movie_id (int): The ID of the movie.
        limit_number (int, optional): The maximum number of credits to retrieve.
            Defaults to 5.
        language (str): The language you want to see the answer in

    Returns:
        dict: A dictionary containing the casts, directors, and writers for the movie.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language={language}"
    response = requests.get(url, headers=TMBD_HEADERS)
    casts_name = []
    directors_name = []
    writers_name = []

    if response.status_code != 200:
        return {}
    try:
        if limit_number > len(response.json()["cast"]):
            limit_number = len(response.json()["cast"])
    except KeyError:
        return {}

    casts = response.json()["cast"][:limit_number]
    for cast in casts:
        casts_name.append(cast["name"])

    for item in response.json()["crew"]:
        if item["job"] == "Director":
            directors_name.append(item["name"])
        elif item["job"] == "Writer":
            writers_name.append(item["name"])

    return {"casts": casts_name,
            "directors": directors_name,
            "writers": writers_name}


def TMDB_get_movie_additional_detail(movie_id, cast_limit=5, detail=False, language="en-US"):
    """
    Retrieves additional details about a movie, including genres, languages, and credits.

    Args:
        movie_id (int): The ID of the movie.
        cast_limit (int, optional): The maximum number of credits to retrieve.
            Defaults to 5.
        detail (bool, optional): Whether to include the full movie details.
            Defaults to False.
        language (str): The language you want to see the answer in

    Returns:
        dict: A dictionary containing additional details about the movie.
    """
    genres = []
    languages = []
    movie_detail = {}

    response = TMDB_get_movie_detail(movie_id, language)
    if response == "error":
        return {}

    credits = TMDB_get_movie_credits_name(movie_id, cast_limit, language)

    try:
        # genres
        for genre in response["genres"]:
            genres.append(genre["name"])

        # languages
        for lang in response["spoken_languages"]:
            languages.append(lang["english_name"])

        movie_detail["imdb_id"] = response["imdb_id"]
        movie_detail["languages"] = languages
        movie_detail["genres"] = genres
        movie_detail["casts"] = credits["casts"]
        movie_detail["directors"] = credits["directors"]
        movie_detail["writers"] = credits["writers"]
        movie_detail["year"] = response["release_date"][:4]

    except KeyError:
        return {}
    if detail:
        return {**response, **movie_detail}
    return movie_detail


def TMDB_get_tv_series_detail(series_id, language="en-US"):
    """
    Retrieves detailed information about a TV series.

    Args:
        series_id (int): The ID of the TV series.
        language (str): The language you want to see the answer in

    Returns:
        dict or str: A dictionary containing TV series details if successful,
            otherwise returns 'error'.
    """
    url = f"https://api.themoviedb.org/3/tv/{series_id}?language={language}"
    response = requests.get(url, headers=TMBD_HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        return "error"


def TMDB_get_tv_series_credits_names(series_id, limit_number=5, language="en-US"):
    """
    Retrieves the credits (cast, directors, writers) for a TV series.

    Args:
        series_id (int): The ID of the TV series.
        limit_number (int, optional): The maximum number of credits to retrieve.
            Defaults to 5.
        language (str): The language you want to see the answer in

    Returns:
        dict: A dictionary containing the casts, directors, and writers for the TV series.
    """
    url = f"https://api.themoviedb.org/3/tv/{series_id}/credits?language={language}"
    response = requests.get(url, headers=TMBD_HEADERS)
    casts_name = []
    directors_name = []
    writers_name = []

    if response.status_code != 200:
        return {}
    try:
        if limit_number > len(response.json()["cast"]):
            limit_number = len(response.json()["cast"])
    except KeyError:
        return {}

    casts = response.json()["cast"][:limit_number]
    for cast in casts:
        casts_name.append(cast["name"])

    for item in response.json()["crew"]:
        if item["job"] == "Director":
            directors_name.append(item["name"])
        elif item["job"] == "Writer":
            writers_name.append(item["name"])

    return {"casts": casts_name,
            "directors": directors_name,
            "writers": writers_name}


def TMDB_get_tv_series_additional_detail(series_id, cast_limit=5, detail=False, language="en-us"):
    """
    Retrieves additional details about a TV series, including genres, languages, and credits.

    Args:
        series_id (int): The ID of the TV series.
        cast_limit (int, optional): The maximum number of credits to retrieve.
            Defaults to 5.
        detail (bool, optional): Whether to include the full TV series details.
            Defaults to False.
        language (str): The language you want to see the answer in

    Returns:
        dict: A dictionary containing additional details about the TV series.
    """
    genres = []
    languages = []
    series_detail = {}

    response = TMDB_get_tv_series_detail(series_id, language)
    if response == "error":
        return {}

    credits = TMDB_get_tv_series_credits_names(series_id, cast_limit, language)

    try:
        # genres
        for genre in response["genres"]:
            genres.append(genre["name"])

        # languages
        for lang in response["spoken_languages"]:
            languages.append(lang["english_name"])

        series_detail["languages"] = languages
        series_detail["genres"] = genres
        series_detail["casts"] = credits["casts"]
        series_detail["directors"] = credits["directors"]
        series_detail["writers"] = credits["writers"]
        series_detail["year1"] = response["first_air_date"][:4]
        series_detail["year2"] = response["last_air_date"][:4]

    except KeyError:
        return {}
    if detail:
        return {**response, **series_detail}
    return series_detail


def TMDB_get_trailer(ids, media_type, trailer_limit=1, language="en-US"):
    """
    Retrieves trailers for a movie or TV series.

    Args:
        ids (int): The ID of the movie or TV series.
        media_type (str): The media type ("movie" or "tv").
        trailer_limit (int, optional): The maximum number of trailers to retrieve.
            Defaults to 1.
        language (str): The language you want to see the answer in

    Returns:
        list: A list of dictionaries containing information about the trailers.
    """
    youtube_url = "https://www.youtube.com/watch?v="
    official_trailers = []
    non_official_trailers = []
    other_results = []
    if media_type == MOVIE_MEDIA_TYPE:
        url = f"https://api.themoviedb.org/3/movie/{ids}/videos?language={language}"
    elif media_type == TV_MEDIA_TYPE:
        url = f"https://api.themoviedb.org/3/tv/{ids}/videos?language={language}"
    response = requests.get(url, headers=TMBD_HEADERS)
    if response.status_code != 200:
        return official_trailers

    for item in response.json()['results']:
        temp = {
            "name": item['name'],
            "official": item['official'],
            "type": item["type"],
        }
        if item["type"] == "Trailer":
            if item["site"] == "YouTube" and item["key"]:
                temp["url"] = youtube_url + item["key"]
            if item['official']:
                official_trailers.append(temp)
            else:
                non_official_trailers.append(temp)
        else:
            if item["site"] == "YouTube" and item["key"]:
                temp["url"] = youtube_url + item["key"]
            other_results.append(temp)

    results = [*official_trailers, *non_official_trailers, *other_results]

    if trailer_limit > len(results):
        trailer_limit = len(results)
    return results[:trailer_limit]


def TMDB_search_response_bot(phrase, language="en-US"):
    """
    Searches for movies or TV series based on a given phrase and retrieves additional details.

    Args:
        phrase (str): The search phrase.
        language (str): The language you want to see the answer in

Returns:
        dict or str: A dictionary containing search results with additional details if successful,
            otherwise returns empty list.
    """
    response = TMDB_search_by_phrase(phrase, language)
    if response != "error":
        try:
            if response and response["results"]:
                for item in response["results"]:
                    if item["media_type"] == MOVIE_MEDIA_TYPE:
                        movie_id = item["id"]
                        movie = TMDB_media_detail_clt.find_one({"key": f"TMDB---{MOVIE_MEDIA_TYPE}---{movie_id}---{language}"})
                        if not movie:
                            movie = TMDB_get_movie_additional_detail(movie_id, language=language)
                            TMDB_media_detail_clt.insert_one({"key": f"TMDB---{MOVIE_MEDIA_TYPE}---{movie_id}---{language}",
                                                              "value": movie,})
                        else:
                            movie = movie.get('value')
                        item.update(movie)
                    elif item["media_type"] == TV_MEDIA_TYPE:
                        series_id = item["id"]
                        series = TMDB_media_detail_clt.find_one({"key": f"TMDB---{TV_MEDIA_TYPE}---{series_id}---{language}"})
                        if not series:
                            series = TMDB_get_tv_series_additional_detail(series_id, language=language)
                            TMDB_media_detail_clt.insert_one({"key": f"TMDB---{TV_MEDIA_TYPE}---{series_id}---{language}",
                                                              "value": series,})
                        else:
                            series = series.get('value')
                        item.update(series)
        except KeyError:
            return []
    else:
        return []

    return response["results"]
