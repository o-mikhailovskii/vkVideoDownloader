# Simple VK Video Downloader

This Python script downloads videos from a list of given URLs. It can handle multiple resolutions and uses multiprocessing for faster downloads.

## Features

* Extracts video URLs and titles from web pages.
* Allows users to select their preferred resolution from available options.
* Downloads videos using multiprocessing for increased speed.
* Displays a progress bar during download.

## Requirements

* Python 3.6 or higher
* `requests` library
* `beautifulsoup4` library
* `tqdm` library

You can install these libraries using pip:

```bash
pip install requests beautifulsoup4 tqdm
```

## Usage

1. Save the script to a file (e.g., `video_downloader.py`).
2. Provide a list of URLs as command-line arguments.

   ```bash
   python video_downloader.py <url_1> <url_2> ... <url_n>
   ```

3. The script will extract video information from each URL.
4. If multiple resolutions are available, you will be prompted to choose one.
5. The videos will be downloaded to the current directory.

## Notes

* The script is designed to work with VKVideo only and may require modification for other sites.
* The number of simultaneous downloads can be adjusted by changing the `processes` argument in the `multiprocessing.Pool` call.

## Disclaimer

Downloading copyrighted material without permission may be illegal in your jurisdiction. Use this script responsibly and at your own risk.
