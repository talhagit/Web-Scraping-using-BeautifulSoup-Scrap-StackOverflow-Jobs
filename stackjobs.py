"""Scrape the pages of stackoverflow jobs for python jobs.
- The job title
- The company name
- The location
- The date posted
- The link to the actual job posting
-Is it Relocation?
-Is it Visa Sponsored?
"""
from bs4 import BeautifulSoup as bs
from datetime import datetime
import os
import requests
import re
import pandas as pd
import smtplib

DOMAIN = 'https://stackoverflow.com'


def scraper(response):
    """Scrape a page for Python jobs.
    """
    content = bs(response.content, 'html.parser')
    jobs = content.find_all('div', class_='-job-summary')

    all_job_data = []
    
    for job in jobs:

        job_data = []
        title = job.find('a', class_='s-link s-link__visited').text
        job_data.append(title if title else '')

        company = job.find('div', class_='fc-black-700 fs-body2 -company')
        company_name=company.find('span').text.strip()
        job_data.append(company_name if company_name else '')

        company_location = company.find('span', class_='fc-black-500')
        locrepl=company_location.text.replace("-","")
        locstrip=locrepl.strip()
        job_data.append(locstrip if locstrip else '')

        date_posted = job.find('span', class_='ps-absolute pt2 r0 fc-black-500 fs-body1 pr12 t24')
        if date_posted:
            datestrip=date_posted.text.strip()
        else:
            datestrip=""
        job_data.append(datestrip if datestrip else '')
        
        
        link = job.find('a', class_='s-link s-link__visited').get('href')
        full_link = DOMAIN + link
        job_data.append(full_link)
        
        relocation=job.find('span',class_="-relocation")
        if relocation:
            relocstrip=relocation.text.strip()
        else:
            relocstrip=""
        job_data.append(relocstrip if relocstrip else '')
        
        
        VisaSpons=job.find('span',class_="-visa pr16")
        if VisaSpons:
            VisaSponstrip=VisaSpons.text.strip()
        else:
            VisaSponstrip=""
        job_data.append(VisaSponstrip if VisaSponstrip else '')
        
        all_job_data.append(job_data)

    return all_job_data

def send_email(username,password,body):
    """Sending Job titles n Email"""
    s = smtplib.SMTP('smtp-mail.outlook.com:587')
    s.starttls()
    TO = "someone@someone.com"
    FROM = "someone@someone.com"
    BODY = ("Subject:"+"All Jobs"+"\n\n"+body)  
    s.login(username,password)
    s.sendmail(FROM, TO,BODY)


def results(results, output):
    """Save the scraping results to a file."""
    df=pd.DataFrame(results)
    DfSubset=df.loc[df[3].str.contains(r'< \d+(?:h.*)|\d+(?:h.*)')]
    OnlyJobs=DfSubset[0].str.cat(sep='\n').encode('ascii', 'ignore').decode('ascii')
    send_email('someone@someone.com','password',OnlyJobs)
    DfSubsetList=DfSubset.values.tolist()
    data = ['\t'.join(job_data) for job_data in DfSubsetList]
    output.write('\n' + '\n'.join(data))


def job_page(page_num):
    """Scrape the page number from job postings."""
    response = requests.get(DOMAIN + '/jobs?pg={}&sort=p'.format(page_num))
    return scraper(response)


##Main Begins
if __name__ == '__main__':
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results')#Create the folder "results in your directory
    output_file = 'StackOverflow jobs - {}.txt'.format(datetime.now().strftime('%m-%d-%y'))
    output_path = os.path.join(dir_path, output_file)

    with open(output_path, 'w', encoding="utf-8") as output:
        output.write('Job Title\tCompany\tLocation\tDate Posted\tLink\tRelocation\tVisaSponsor')

    output = open(output_path, 'a',encoding="utf-8")

    print('Scraping the StackOverflow.com Jobs!!!')
    for n in range(1,25):
        print('Scraping page {}...'.format(n))
        data = job_page(n)
        results(data, output)

    output.close()
    print('Done, Path to file: results/{}'.format(output_file))
    

    
    
    #    s.smtpssl = False
    #    s.connect('smtp.live.com', 587)
    #    s.ehlo()
    #    server.close()
    


    
    
    
  
