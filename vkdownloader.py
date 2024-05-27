#!/usr/bin/env python3

"""
This script downloads videos from a given list of URLs.

It extracts video URLs from the provided web pages,
allows the user to select the desired resolution
(if multiple resolutions are available),
and downloads the videos using multiprocessing for faster download speeds.
"""

import multiprocessing
import re
import sys
import unicodedata
from functools import partial

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Define a constant for the user agent string
USER_AGENT = """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"""


def get_videos(session, path):
    """
    Extracts video information from a given URL.

    Args:
        session (requests.Session): A requests session object.
        path (str): The URL of the page containing the video.

    Returns:
        tuple: A tuple containing a dictionary of video URLs (keyed by resolution)
               and the filename for the video, or an empty dictionary and None
               if no video is found.
    """
    print(f"\n[+] Getting videos from [{path}]...")
    response = session.get(path)
    soup = BeautifulSoup(response.content, "html.parser")
    elements = soup.find_all("script", {"type": "module"})
    elements = [e for e in elements if "al_video.php" in e.text]
    if len(elements) != 1:
        return {}, None
    e = elements[0]

    # Extract video URLs and resolutions using regex
    pattern_url = r'"url(\d+)":\s*"([^"]+)"'
    matches_url = re.findall(pattern_url, e.text)
    videos = {int(number): value for number, value in matches_url}

    # Extract video title using regex
    pattern_name = r'"title":\s*"([^"]+)"'
    name = re.findall(pattern_name, e.text)[0]

    # Normalize and sanitize the filename
    name = unicodedata.normalize("NFKC", name)
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[-\s]+", "-", name).strip("-_")

    return videos, name + ".mp4"


def download_file(session, filename, url):
    """
    Downloads a file from a given URL and displays a progress bar.

    Args:
        session (requests.Session): A requests session object.
        filename (str): The name to save the downloaded file as.
        url (str): The URL of the file to download.
    """
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))

        with open(filename, "wb") as f:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=filename,
                ncols=100,
            ) as progress_bar:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        progress_bar.update(len(chunk))


def get_resolution(options):
    """
    Prompts the user to select a resolution from a list of available options.

    Args:
        options (list): A list of available video resolutions.

    Returns:
        int: The selected resolution.
    """

    while True:
        print(
            f"\n[+] Select resolution from the options: "
            f"{', '.join(map(str, options))}: ",
            end="",
        )
        try:
            resol = int(input().strip())
            if resol in options:
                return resol
            else:
                print("Invalid resolution. Please choose from the available options.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def worker(session, params):
    """
    Worker function for multiprocessing, downloads a single file.

    Args:
        session (requests.Session): A requests session object.
        params (list): A list containing the filename and URL of the file to download.
    """
    download_file(session, params[0], params[1])


def main(paths):
    """
    Main function for the video downloader script.

    Args:
        paths (list): A list of URLs to download videos from.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    download_files = []

    for path in paths:
        videos, filename = get_videos(session, path)
        if not videos:
            print("Error: No videos found!\n")
            continue

        if len(videos) > 1:
            selected_resolution = get_resolution(sorted(videos.keys()))
            formatted_url = re.sub(r"\\/", "/", videos[selected_resolution])
            download_files.append([filename, formatted_url])
        else:
            # If only one resolution is available, download it directly
            formatted_url = re.sub(r"\\/", "/", list(videos.values())[0])
            download_files.append([filename, formatted_url])

    print("\n[+] Downloading...")
    with multiprocessing.Pool(processes=4) as pool:
        partial_worker = partial(worker, session)
        pool.map(partial_worker, download_files)


if __name__ == "__main__":
    main(sys.argv[1:])
