# Web part of Kiedy Bajki app.
Doesn't include task for checking pages for certain changes and making notifications to users about subscribed titles.

## In a nutshell
Application send notifications through Discord communicator about new anime episodes
choosed by user on choosed sites. Notifications contains links to episodes and small cover picture which can be enlarge by click.

## How it works
App core is web scrapper which looking for certain changes in html of certain pages which contains information about new episodes. When web scrapper finds new episodes notification about them will be sended to users which subscribe notification about given titles on choosed sites. Notification are maked by using Discord API feature calles webhook.

## Tech stack

### Server
- Apache on Ubuntu.

### Backend
- Python with Flask framework,
- PostgreSQL database used through SQLAlchemy,
- Unix cron utility for triggering web scraper.

### Frontend
- Vanilla JS,
- CSS3,
- HTML5.

### Other tools
- Git,
- Github.

## Few words about frontend
I used Responsive Web Design and Mobile First approaches for making the app.
App can be used comfoirtably despite of screen size.
It works well both on mobile and desktop devices. Touch on mobile displays is handled well. 
For example title covers can be displayed with ease by holding touch on titles.

To improve loading times i use service worker for loading static content. When there is no internet connection instead of standard notification provided by browser user will see custom page loaded through service worker. Headers related to cache are set in a way which reduce fetching content from server to minimum. Useful for older browsers which doesn't support service workers. 

## Security
I tried to make this app to be secure by following most of the recommendations from [Flask official documentation](https://flask.palletsprojects.com/en/2.0.x/security/), [Mozilla Fundation Web Security guideline](https://infosec.mozilla.org/guidelines/web_security) and other reliable sources.
The most important solutions include bcrypt for hashing passwords, CSRF tokens, HTTPS, TLS configuration for Apache and certain HTTP headers set in right way such like:
- Content-Security-Policy,
- Strict-Transport-Security, 
- Referrer-Policy,
- X-Frame-Options,
- X-Content-Type-Options.

## Official site:
https://kiedybajki.moe

## More about application:
https://kiedybajki.moe/about
