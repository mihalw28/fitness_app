# Fitness App
# :swimmer::bicyclist::runner:

This repostitory contains source code of an app that is able to auto signup user to fitness class. The main idea behind this work was to automate things using python and make life easier.
Many of us attending gym classes probably know the pain of trying to sign up for our favorite class and realized that it has been just fully booked. :disappointed: To help prevent such situations, automatic registration could be a good solution. 


##### :heavy_check_mark: Pros of this solution:
* There is no pain if you forgot to sign up to your favourite class.
* It is a convinient solution.

##### :heavy_exclamation_mark: Cons:
* Works only on gym site that was designed for. Aafter small changes it could also works for almost any other gym with website signups.
* This type of scripts with auto loggin and auto signup functions could be unwated.
* Due to the nature of this app, it generates real costs working deployed - Twillio & AWS. 

#### :hammer: How it works.
1. Registration and creation of user profile - gym selection and class(es).
2. The app will scrap gym website at appropriate intervals to find out if user registration for class is possible. (Registration for classes are open 36 hours before given class starts.)
3. After correctly subscribing to training the user recievs a confirmation via :iphone:
4. If user wouldn't accept a confirmation from the app, his/her place in training will be unbooked 4 hours before the start.


#### Main goals to accomplish:
1. Firstly I had an idea of deploying app on Heroku, but that idea is not alive now. Foremost it's necessary to create API endpoints for scrapping gym website using AWS Lambda.  I will try to deploy the whole app using serverless technology (@ AWS Λ); both scrapping module and web app module.
3. Tests. ~~I haven't written independently any test before, hence lack of tests so far in this repo.~~ I'm currently improving this skill. Some tests have been added recently. 
2. Create API endpoints to handle HTTP requests.
3. Set time intervals using cron jobs in Lambda.
4. Make some user friendly frontend. 

#### Made with :heart: using:
* Python :snake:
* [Flask](https://github.com/pallets/flask)
* [SQLAlchemy](https://github.com/pallets/flask-sqlalchemy)
* [WTForms](https://flask-wtf.readthedocs.io/en/stable/)
* [Selenium](https://github.com/SeleniumHQ/selenium)
* [Twilio](https://www.twilio.com/)
* [Docker](https://www.docker.com/):whale:
* will be deployed probably using [AWS](https://aws.amazon.com/lambda/)

#### Credits:
 - Fitness App is based on microblog application skeleton from [The Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg
 - Headless chromium browser for python from 21Buttons Team [click](https://github.com/21Buttons/pychromeless)
 - Basic testing flask web app with Selenium [click](https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1)


#### Additional info
As an autor of this app I'm still a beginner :beginner: python programmmer constantly learning. I don't know many programming tricks and hacks. Many more experienced developers probably will pay attention to bad coding practises used here or know better/easier solutions. I will be very grateful for suggestions where to go next. I'm open for constructive criticism and any comments.

### License:
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT) [![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/fold_left.svg?style=social&label=%20%40mihalw28)](https://twitter.com/mihalw28)
