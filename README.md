BReader
================================
My name is Brian. This is my Reader. It's modeled after the parts I like in Google Reader (I only used the story view and the 'J', 'K' shortcuts for navigating). This project contains a google app engine backend, website and android mobile app.

API_KEY
-------
The android project authenticates with the app engine backend via an API Key. This is something you must generate and fill in on both projects. For the android project, this is defined on the Globals.java class on line 42. Whatever value you assign your API_KEY, this same value must be placed in the app engine project. In app engine, copy config.py.sample to config.py and fill in the key value. If both keys are the same, the android app should be able to authenticate.

Android
-------
To setup the android project, you must first setup the app engine backend (see below). Once that is setup, copy the url of the hosted app engine project into line 36 of Globals.java. Also, make sure you fill in the API_KEY (see above).

App Engine
----------
To setup the app engine project, you need to create a new app engine identifier on app engine. Once you have one, copy app.yaml.sample to app.yaml and fill in your values.

To import your feeds from google reader, you can go the feeds tab and upload the xml file containing the feeds you get from the google reader export.

I created the app engine backend to be single-user, so I treat the User object as a singleton. This was because I wanted to host this for free, and my traffic alone falls under the free tier. To accomplish this, I made the web controller force admin authentication. This means that only the user who owns the app engine project will be able to log in.

Another consideration for hosting on the free tier is the polling interval. I follow around 200 feeds. For me to fall under the free tier, I am polling my feeds once an hour. I wanted control of exactly when the polling occured, and app engine's cron syntax doesn't support this (you can specify you want something to fire once per hour, but you can't specify that you want it to fire at exactly 23 minutes past the hour). In order to accomplish this, I have the cron job firing every minute. When the cron job fires, I check the minutes of the current time. If minutes == 30, I run the job. Otherwise, I ignore the request.

To navigate stories on the website, I implemented some vim shortcuts. 'J' goes to the next story. 'K' goes to the previous story.

To star or unstar a story, use 'S' and 'U' respectively.

Known Issues
------------
I deployed this project in April of 2013, and have been using it as a replacement to Google Reader ever since. So far it's worked out well. Occasionally, a story can't parse, or a large image extends the bounds of the story div.
