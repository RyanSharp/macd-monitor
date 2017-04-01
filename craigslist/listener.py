from celery import task
from bs4 import BeautifulSoup
from craigslist.classes import CraigslistRecord
from models.database import get_collection
import urllib2
import urllib
import smtplib


CRAIGSLIST_SEARCH = "http://{0}.craigslist.org/search/sss?format=rss&{1}"

craigslist_queries = [
    {
        "keyword": "west elm",
        "cities": ["losangeles", "orangecounty"],
        "weak": [],
        "strong": [
            ["couch"],
            ["sectional"],
            ["sofa"],
            ["chaise"],
        ]
    },
    {
        "keyword": "cb2",
        "cities": ["losangeles", "orangecounty"],
        "weak": [],
        "strong": [
            ["couch"],
            ["sectional"],
            ["sofa"],
            ["chaise"],
        ]
    }
]

USERNAME = "secure.trutracker@gmail.com"
PASSWORD = "backatitagainwiththewhitevans"


def send_email(recipients, message):
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(USERNAME, PASSWORD)
    server.sendmail(USERNAME, recipients, message)
    server.close()


@task()
def run_query_task():
    for query in craigslist_queries:
        run_query(query)


def run_query(query):
    collection = get_collection("CraigslistRecords")
    def run_query_for_city(city, keyword):
        response = urllib2.urlopen(
            CRAIGSLIST_SEARCH.format(city, urllib.urlencode({"query": keyword}))).read()
        soup = BeautifulSoup(response)
        results = soup.find_all(name="item")
        for result in results:
            process_result(result)

    def process_result(result):
        def check_listing(listing_info):
            match_found = False
            for words in query["strong_keys"]:
                count = 0
                for word in words:
                    if word in listing.get("title", "") or\
                            word in listing.get("description"):
                        count += 1
                match_found = count == len(words)
                if match_found:
                    break
            else:
                count = 0
                for words in query["weak_keys"]:
                    for word in words:
                        if word in listing.get("title", "") or\
                                word in listing.get("description"):
                            count += 1
                            break
                        match_found = count >= 2
                        if match_found:
                            break
            return match_found

        post_id = result.attrs["rdf:about"].split("/")[-1]
        post = collection.find_one({"post_id": post_id})
        if post is None:
            post = urllib2.urlopen(result.attrs["rdf:about"]).read()
            post = CraigslistRecord(dict(post_id=post_id,
                                         article_content=post))
            post.commit()
        if post.get_property("found").get_val():
            return
        post = post.get_property("article_content").get_val()
        soup = BeautifulSoup(post)
        description = soup.find_all(id="postingbody")
        desc = ""
        for string in description[0].strings:
            string = string.replace('\n', ' ').replace('\r', ' ')
            desc += string
        title_text = soup.find_all(id="titletextonly")
        listing = {
            "description": desc.lower(),
            "title": title_text[0].string.lower()
        }
        if check_listing(listing):
            post.get_property("found").apply_transaction("$set", True)
            send_email(["choi.stephanie.y@gmail.com", "rtsharp90@gmail.com"],
                       ("A match has been found for {0}\n"
                        "Title: {1}\n"
                        "Description: {2}\n"
                        "Link: {3}").format(query["keyword"],
                                            listing["title"],
                                            listing["description"],
                                            result.attrs["rdf:about"]))
    for city in query["cities"]:
        run_query_for_city(city, query["keyword"])
