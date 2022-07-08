![Combine](/flaskapp/static/img/combine-logo.png)

Combine: The International Web Harvester is a web application I built as a self hosted alternative to URLScan.io.

## Showcase
When launching the application for the first time create a user account and make sure to secure it behind a strong password.

After logging in you can scan any site you wish. After entering your URL you can leave the default user agent, select another from the drop down, or enter your own. Then hit scan and allow Combine to "harvest" the site's data.
![Scan](/flaskapp/static/img/scan.png)

Results will be displayed after a scan is complete. All results are saved to the application and can be viewed at later dates. Data you current get is a image of the page, the html code behind the page, whois information, all links found on the page, and a submission to Virus Total.
![Results](/flaskapp/static/img/results.png)

You can look at historic searches as well! Results are displayed in newest to oldest by time scanned. You can click the URL itself to go to the results page.
![Search](/flaskapp/static/img/search.png)

## Installation
There are multiple ways of running Combine. You can either download the Docker image and run it via Docker or Docker-Compose or you can build the image manually


### Docker-Compose
The recommended way of running this application is to use Docker-Compose. Copy the following into a docker-compose.yml file and make sure to update the SECRET_KEY and VIRUS_TOTAL_API_KEY variables. Run docker-compose up -d or utilize a service like [Portainer](https://www.portainer.io/) for easier management of all your Docker containers.

```yml
version: '3.3'
services:
  combine:
    image: thestuke/combine:latest
    container_name: combine
    environment:
      - PUID=1000
      - PGID=1000
      - SECRET_KEY=${SECRET_KEY} # This is your secret key for your Flask application
      - VIRUS_TOTAL_API_KEY=${VIRUS_TOTAL_API_KEY} # This is your VirusTotal API Key
    volumes:
      - /opt/combine/data/profile_pics/:/combine/flaskapp/static/profile_pics
      - /opt/combine/data/results:/combine/flaskapp/static/results
      - /opt/combine/data/site.db:/combine/flaskapp/site.db
    ports:
      - 5000:5000
    restart: unless-stopped
```

### Bare Metal Deployment
If you would like to run Combine not in a docker container you can clone the repo and run the following commands.

```bash
apt-get update && apt-get upgrade -y
apt install python3-pip -y
apt install python3-flask -y
pip install flask flask_sqlalchemy flask_bcrypt flask_login flask_mail flask_wtf email_validator Pillow python-whois bs4 Selenium Selenium-Screenshot requests
apt install wget -y
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install ./google-chrome-stable_current_amd64.deb -y && rm google-chrome-stable_current_amd64.deb
echo 'export PATH=$PATH:/opt/combine/drivers/chromedriver' >> ~/.bash_profile
```

## Troubleshooting
To avoid most issues I strongly recommend running Combine in a Docker container as there are many dependencies that could break with updates.

### Chrome Driver Verison issue
If you need to update the chrome driver you can download it [here](https://chromedriver.chromium.org/downloads). Make sure to get the Linux driver for your current version of Chrome.

### Database Recreation
If you ever need to rebuild the database for the application run the following in a Python command line
```python
from flaskapp import db, create_app
db.create_all(app=create_app())
```