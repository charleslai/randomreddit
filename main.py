#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#== Dependencies ========================================================#
import sys
import os
import jinja2
import webapp2
import random
from google.appengine.api import memcache
from google.appengine.ext import ndb
import praw #!important

#PRAW Dependencies
r = praw.Reddit(user_agent="Random Reddit Comments v1.0 by /u/sirprinceking")

#Jinja2 Template Directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = False)

#Global/Super URL Handler Class
class Handler(webapp2.RequestHandler):
    """
    Global superclass for request handlers
    """
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#== Main Application =====================================================#
class MainHandler(Handler):
    """
    Main view handler for the rrc application
    """
    def render_rrc(self, action_title="", comment="", author="", submission_title="", submission_link="",
                   comment_link="", comment_score=""):
    	#Render the main rrc template
    	self.render("rrc.html", action_title=action_title, comment=comment, author=author, submission_title=submission_title,
                    submission_link=submission_link, comment_link=comment_link, comment_score=comment_score)

    def get(self):
        #Render landing page on load
        self.render_rrc("Get a random comment from Reddit!")

    def post(self):
        try:
            #Get the sr entitiy from the data store and chose a random subreddit.
            sr = ndb.Key(urlsafe='ag5zfnJhbmRvbXJlZGRpdHIUCxIHU1JDYWNoZRiAgICAgICACgw').get()
            random_sr = random.choice(sr.srlist)
            #Pick a random comment from the random subreddit
            all_comments = list(r.get_comments(random_sr))
            random_comment = random.choice(all_comments)

            #Comment Body
            comment_body = random_comment.body
            #Comment Score
            if random_comment.score <= 0:
                comment_score = "Comment Score:  " + "<span style=\"color:red\">" + `random_comment.score` + "</span>"
            elif random_comment.score > 0:
                comment_score = "Comment Score:  " + "<span style=\"color:green\">" + `random_comment.score` + "</span>"
            #Submission Title
            if len(random_comment.submission.title) > 75:
                submission_title = "Submission Title:  " + random_comment.submission.title[0:75] + "..." + "</br>"
            elif len(random_comment.submission.title) <= 75:
                submission_title = "Submission Title:  " + random_comment.submission.title + "</br>"
            #Submission Link
            submission_link = "Submission Link:  " + "<a href=\"" + random_comment.submission.short_link + "\">" + \
                               random_comment.submission.short_link + "</a></br>"
            #Comment Link
            comment_link = "Comment Link:  " + "<a href=\"" + random_comment.permalink + "\">" + \
                            random_comment.permalink[0:50] + "..." + "</a></br>"
            #Author
            author = "By: " + random_comment.author.name

            #Render the page template with API response values
            self.render_rrc("Get another comment!", comment_body, author, submission_title, submission_link,
                            comment_link, comment_score)
        except Exception:
            self.render_rrc("Oops! Something broke on our side. Try again!")


class CacheHandler(Handler):
    """
    Subreddit cache updater
    """
    def get(self):
        #Create a new list of subreddits from the sr.txt file
        srlist = [line.strip() for line in open("sr.txt", "r")]
        #Get the entity from the datastore and update it with the new list
        sr = ndb.Key(urlsafe='ag5zfnJhbmRvbXJlZGRpdHIUCxIHU1JDYWNoZRiAgICAgICACgw').get()
        sr.srlist = srlist
        sr.put()

class SRCache(ndb.Model):
    """
    Datastore model to hold a cache of various subreddits.
    """
    srlist = ndb.StringProperty(repeated=True)

#Routing Logic
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/refresh_SRCache', CacheHandler)
], debug=True)
