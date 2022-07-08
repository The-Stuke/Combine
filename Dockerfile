# Select base image
FROM ubuntu

# Set Enviornment Variable for Flask
ENV FLASK_APP=run.py

# Set Timezone
ENV TZ=US
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installtion of dependencies
RUN apt-get update && apt-get upgrade -y 
RUN apt install python3-pip -y
RUN apt install python3-flask -y
RUN pip install flask flask_sqlalchemy flask_bcrypt flask_login flask_mail flask_wtf email_validator Pillow python-whois bs4 Selenium Selenium-Screenshot requests itsdangerous==2.0.1
RUN apt install wget -y

# Download and Install Stable Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt install ./google-chrome-stable_current_amd64.deb -y && rm google-chrome-stable_current_amd64.deb

# Change directory
WORKDIR /opt/combine

# Copy all files in folder to docker image
COPY . .

# Create path from chrome driver
RUN echo 'export PATH=$PATH:/opt/combine/drivers/chromedriver' >> ~/.bash_profile

# Run command on startup
CMD [ "flask", "run", "--host=0.0.0.0"]
