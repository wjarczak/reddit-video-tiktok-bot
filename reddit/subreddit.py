from asyncore import write
from re import sub
from utils.console import print_markdown, print_step, print_substep
import praw
import random
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright

def get_subreddit_threads(input_subreddit="", input_thread=""):
    print_step("Getting subreddit threads...")
    random.seed()
    content = {}
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing AskReddit threads",
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
    )
    if input_thread == "":
        if input_subreddit == "":
            if os.getenv("ASK_EACH_TIME") == "TRUE":
                try:
                    subreddit = reddit.subreddit(input("What subreddit would you like to pull from? "))
                except ValueError:
                    subreddit = reddit.subreddit("askreddit")
                    print_substep("Subreddit not defined. Using AskReddit.")
            else:
                try:
                    subreddit = reddit.subreddit(os.getenv("SUBREDDIT"))
                except ValueError:
                    subreddit = reddit.subreddit("askreddit")
                    print_substep("Subreddit not defined. Using AskReddit.")
        else:
            subreddit = reddit.subreddit(input_subreddit)

        threads = subreddit.top("year", limit=100)
        thread_list = list(threads)
        
        if os.getenv("ALLOW_NSFW") == "FALSE":
            NSFW = True
            while NSFW:
                content = {}
                submission = random.choice(thread_list)
                content["thread_url"] = submission.url
                with sync_playwright() as p:
                    print_substep("Testing if post is NSFW...")
                    browser = p.chromium.launch()

                    # Get the thread screenshot
                    page = browser.new_page()
                    page.goto(content["thread_url"])

                    if page.locator('[data-testid="content-gate"]').is_visible():
                        thread_list.remove(submission)
                        print_substep("Post is NSFW, getting new post...")
                    
                    else:
                        print_substep("Post is not NSFW, continuing...")
                        NSFW = False
        else:
            submission = random.choice(thread_list)
    else:
        submission = reddit.submission(url=input_thread)
    
    titles_used = open("titles_used.txt", "r").read().split("\n")
    while submission.title in titles_used:
        submission = random.choice(thread_list)
        
    write_title = open("titles_used.txt", "a")
    write_title.write(submission.title + "\n")
    write_title.close()
    
    print_substep(f"Video will be: {submission.title} :thumbsup:")
    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["comments"] = []

        for top_level_comment in submission.comments:
            if not top_level_comment.author.is_mod:
                content["comments"].append(
                    {
                        "comment_body": top_level_comment.body,
                        "comment_url": top_level_comment.permalink,
                        "comment_id": top_level_comment.id,
                    }
                )

    except AttributeError as e:
        pass
    print_substep("Received subreddit threads Successfully.", style="bold green")
    with open("title.txt", "w") as f:
        f.write(content["thread_title"] + " | " + "Parkour done by: bbswitzer | shorturl.at/dgzGV | #parkour #minecraft #nostupidquestions #reddit #chill")
    return content