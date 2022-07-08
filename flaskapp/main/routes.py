from flask import redirect, render_template, request, Blueprint, url_for, current_app
from flask_login import current_user, login_required
from sqlalchemy import false
from flaskapp.main.forms import SubmitURL, SearchURL
import requests
import whois
from datetime import datetime
import hashlib
import os
from flaskapp import db
from flaskapp.models import Scans
from bs4 import BeautifulSoup
import re
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from flaskapp.config import Config
import json


main = Blueprint('main', __name__)


@main.route("/", methods=['POST', 'GET'])
@main.route("/scan", methods=['POST', 'GET'])
@login_required
def scan():
    form = SubmitURL()
    # If a URL is submitted to scan run this
    if form.validate_on_submit():
        # Set Variables
        url = form.SubmitURL.data # Submitted URL
        if not form.EnterUA.data:
            user_agent = form.SelectUA.data # Selected user agent
        else:
            user_agent = form.EnterUA.data # Submitted user agent
        domain = re.search(r'https?:\/\/([A-Za-z0-9\-\_\~\.]+)', url).group(1) # Regex out subdomain/domain from submitted URL
        ip = socket.gethostbyname(domain) # Get the IP of the submitted URL
        scan_time = str(datetime.now()) # Time when scanned was submitted
        pre_md5 = scan_time + domain # Combine both time submitted and the domain
        md5 = hashlib.md5(pre_md5.encode()).hexdigest() # Use combined scan time and domain to create a unique md5 to reference
        user_who_scanned = current_user.username # Log which user ran the scan
        full_path = os.path.join(current_app.root_path, 'static/results/') # Full path of where to save files
        file_path = '/static/results/' # Where files will be referenced and sent to the database
        
        # Create directory for each scan
        try:
            os.mkdir(full_path + md5)
        except:
            print("Directory Creation Error")

        # Run WHOIS search
        try:
            whois_var = whois.whois(domain)

            whois_path_full = full_path + md5 + "/whois.json"
            whois_path = file_path + "/whois.json"
            whois_file = open(whois_path_full, "w+")
            whois_file.write(str(whois_var))
            whois_file.close()
        except:
            print("WHOIS Error")

        # Selenium Screenshot
        try:
            screenshot_path_full = full_path + md5 + "/screenshot.png" # Full path of where to save files
            screenshot_path = file_path + md5 + "/screenshot.png" # Where files will be referenced and sent to the database
            chromeOptions = Options()
            chromeOptions.headless = True
            chromeOptions.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
            chromeOptions.add_argument("--no-sandbox"); # Bypass OS security model
            chromeOptions.add_argument("user-agent=" + user_agent)
            driver_path = os.path.join(current_app.root_path, 'drivers/chromedriver')
            driver = webdriver.Chrome(driver_path, options=chromeOptions)
            driver.set_window_size(1920, 1080)
            driver.get(url)
            time.sleep(3)
            driver.save_screenshot(screenshot_path_full)
            driver.quit()
        except:
            print("Screenshot Error")

        # Making a request to the website
        try:
            headers = {'User-Agent': user_agent}
            request = requests.get(url, headers=headers, verify=False)
        except:
            print("Request Error")
            
        # Pull links and write to file and delcare paths
        try:
            soup = BeautifulSoup(request.text, 'html.parser')

            links_path_full = full_path + md5 + "/links.txt"
            links_path = file_path + md5 + "/links.txt"

            links = open(links_path_full, "w")
            for link in soup.find_all("a"):
                data = link.get('href')
                if not data:
                    print("Not an href")
                else:
                    links.write(data)
                    links.write("\n")
            
            links.close()
        except:
            print("Link Parse Error")

        # VirusTotal API Scan of URL
        try:
            vt_url = 'https://www.virustotal.com/vtapi/v2/url/scan'
            params = {'apikey': Config.VIRUS_TOTAL_API_KEY , 'url': url }
            response = requests.post(vt_url, data=params)
            response = str(response.json())
            vt_link = re.search(r'(https?:\/\/www.virustotal.com/gui/url/[A-Za-z0-9-\/]+)', response).group(1)
        except:
            print("VirusTotal Error")

        # File Open and Declare Paths
        try:
            dom_path_full = full_path + md5 + "/dom.html"
            dom_path = file_path + "/dom.html"

            dom = open(dom_path_full, "w+")
            dom.write(request.text)
            dom.close()
        except:
            print("File Open Error")
        
        # Update the database with scan results
        try:
            scan = Scans(md5=md5, url=url , domain=domain, user_agent=user_agent, scan_time=scan_time, screenshot_path=screenshot_path, dom_path=dom_path, user_who_scanned=user_who_scanned, whois_path=whois_path, links_path=links_path, ip=ip, vt_link=vt_link)
            db.session.add(scan)
            db.session.commit()
        except:
            print("Database Update Error")

        return redirect(url_for("main.results", title='Scan', md5_hash=md5))
    return render_template('scan.html', title='Scan', form=form)


@main.route("/search", methods=['POST', 'GET'])
@login_required
def search():
    form = SearchURL()
    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
        scans = Scans.query.filter(Scans.url.contains(form.SearchURL.data)).order_by(Scans.scan_time.desc()).paginate(page=page, per_page=10)
    else:
        if 'SearchURL' in request.args:
            searchURL = request.args.get('SearchURL')
            scans = Scans.query.filter(Scans.url.contains(searchURL)).order_by(Scans.scan_time.desc()).paginate(page=page, per_page=10)
            return render_template('search.html', title='Search', scans=scans, form=form, searchURL=searchURL)
        else:
            scans = Scans.query.order_by(Scans.scan_time.desc()).paginate(page=page, per_page=10)
    return render_template('search.html', title='Search', scans=scans, form=form)
    


@main.route("/results/<string:md5_hash>")
@login_required
def results(md5_hash):
    scans = Scans.query.filter_by(md5 = str(md5_hash))
    if scans:
       with open(os.path.join(current_app.root_path, 'static/results/') + md5_hash + "/dom.html", "r") as f: 
            dom_info = f.read()
            f.close()
            with open(os.path.join(current_app.root_path, 'static/results/') + md5_hash + "/whois.json", "r") as f: 
                whois_info = json.load(f)
                f.close()
                with open(os.path.join(current_app.root_path, 'static/results/') + md5_hash + "/links.txt", "r") as f: 
                    links_info = f.read().split('\n')
                    f.close()
                return render_template('results.html', title='Results', scans = scans, dom_info = dom_info, whois_info = whois_info, links_info=links_info)
    else:
        return render_template('errors/404.html')