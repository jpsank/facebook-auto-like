# facebook-auto-like
Python program that uses Selenium to scroll through Facebook News Feed and automatically like all noncontroversial posts.

## Usage
To run, type:

    python main.py

It will ask for your username/password, and then will open a Selenium webdriver to go through your account's news feed. It will like all posts with five likes or more and without any Angry or Sad Reactions (This can be reconfigured, however).
