# Fitness App
# :swimmer::bicyclist::runner:

This repostitory contains source code of an app that is able to auto signup user to fitness class. The main idea behind this work was to automate things using python and make life easier.
Many of us attending gym classes probably know the pain of trying to sign up for our favorite class and realized that it has been just fully booked. :disappointed: To help prevent such situations, automatic registration could be a good solution. 

Default gym app doesn't allow to schedule trainings and signup automatically.


##### :heavy_check_mark: Pros of this solution:
* There is no pain if you forgot to sign up to your favourite class.
* It is a convinient solution.
* Works in parallel with default gym app.


##### :heavy_exclamation_mark: Cons:
* Works only on gym site that was designed for. After small changes it could also works for almost any other gym with website signups.
* This type of scripts with auto loggin and auto signup functions could be unwated.
* Due to the nature of this app, it generates real costs working deployed - Twillio & AWS. 


#### :hammer: How it works - gerneral:
1. Registration and creation of user profile - gym selection and class(es).
2. The app will scrap gym website at appropriate intervals to find out if user registration for class is possible. (Registration for classes are open 36 hours before given class starts.)
3. After correctly subscribing to training the user recievs a confirmation via :iphone:
4. If user wouldn't accept a confirmation from the app, his/her place in training will be unbooked 4 hours before the start.


#### How it works - backend:
1. Flask app uses blueprints objects.
2. App is deployed on AWS using docker containers. Pre-configured container uses headless chrome browser and selenium testing package.
3. Scrapping module is an inner part of the application. 
4. DB used: AWS PostgreSQL.


#### Main goals to accomplish:
1. [x] Firstly I had an idea of deploying app on Heroku, but that idea is not alive now. Foremost it's necessary to create API endpoints for scrapping gym website using AWS Lambda. ~~I will try to deploy the whole app using serverless technology (@ AWS Λ); both scrapping module and web app module.~~ AWS Lambda connected to DB instance within VPC generates high costs, so this idea has been dropped. Scrapping module is placed within the main app.
2. [x] Tests. I'm currently improving this skill. Some tests have been added recently.
3. [ ] Replace some app modules with Lambda functions and add new ones.
4. [x] Create API endpoints to handle HTTP requests - API Gateway.
5. [ ] Create complete REST API.
6. [x] Set time intervals using cron jobs - APScheduler.
7. [ ] Make some more user friendly frontend.


#### Improvement ideas:
1. [ ] Add an option to select more than one discipline and more than one training a day.


#### Made with :coffee: using:
* Python :snake:
* [Flask](https://github.com/pallets/flask)
* [SQLAlchemy](https://github.com/pallets/flask-sqlalchemy)
* [WTForms](https://flask-wtf.readthedocs.io/en/stable/)
* [Selenium](https://github.com/SeleniumHQ/selenium)
* [Twilio](https://www.twilio.com/)
* [Docker](https://www.docker.com/):whale:
* ~~will be~~ Has been deployed using [AWS](https://aws.amazon.com/lambda/) (RDS, API Gateway, Elastic Beanstalk, Docker)


#### Credits:
 - Fitness App is based on microblog application skeleton from [The Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg
 - Dockercontainer for running Python Selenium in headless Chrome[click](https://github.com/joyzoursky/docker-python-chromedriver)
 - Basic testing flask web app with Selenium [click](https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1)


#### Additional info
As an autor of this app I'm still a beginner :beginner: python programmmer constantly learning. I don't know many programming tricks and hacks. Many more experienced developers probably know better/easier solutions. I will be very grateful for suggestions where to go next. I'm open for constructive criticism.


### License:
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT) [![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/fold_left.svg?style=social&label=%20%40mihalw28)](https://twitter.com/mihalw28)
