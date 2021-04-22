## https://nz.indeed.com/  SCRAPER
# Author : Haytham Taymour 
# Email  : haytham.taymour@gmail.com


import requests
import os
from bs4 import BeautifulSoup
from nltk import wordpunct_tokenize,corpus
import traceback
# import csv
# from openpyxl import load_workbook
# from openpyxl.styles import Alignment
from datetime import datetime , timedelta
import json
from time import sleep
from fake_useragent import UserAgent
import re
#nltk.download('words')
words = set(corpus.words.words())
extra_word = [".com",".gov",".edu","www.","com","gov","edu","\n",".","\r","@","U.S","twiter","facebook","linkedin","instagram","P.O","<h5>","<p>","<div>",".com.",".gov.",".edu.","au","a.u"]
requests.packages.urllib3.disable_warnings()
logf = open("log.txt","w")


def get_job_data(URL):
    try:
        global proxies
        global extra_word
        j_id = ""
        contact_detail = ""
        title = ""
        desc = ""
        det = ""
        salary = ""
        salary_min = ""
        salary_max= ""
        salary_currency = ""
        salary_type = ""
        review_overall = ""
        review_total_overall = ""
        location = ""
        job_type = ""
        original_link = ""
        company_name = ""
        post_age = ""

        page = requests.get(URL,proxies=proxies,headers=header, verify=False,timeout=180)
        soup = BeautifulSoup(page.content, 'html.parser')
        j_id = URL.replace('https://nz.indeed.com/viewjob?jk=','')
        if soup.find('title').get_text().upper().find("CAPTCHA") > 0 : 
            print ("Found a captcha at getting job details. Moving to proxy.") 
            proxies = { "http": 'http://scraperapi:8a562ddd940a60b50c445db89d201b7c@proxy-server.scraperapi.com:8001', 
            "https": 'http://scraperapi:8a562ddd940a60b50c445db89d201b7c@proxy-server.scraperapi.com:8001' }
            page = requests.get(URL,proxies=proxies,headers=header, verify=False,timeout=180)
            soup = BeautifulSoup(page.content, 'html.parser')

        if  (len(soup.find('title').get_text().replace (" - Indeed.com","").split(' - '))) > 0: 
            location = soup.find('title').get_text().replace (" - Indeed.com","").split(' - ')[-1]   #remove last split

        title = soup.find('title').get_text().replace (" - Indeed.com","").split(' - ')[0]   #remove last split



        # SECTION ORIGINAL URL 
        if soup.find(id ="originalJobLinkContainer") : 
            original_link = soup.find(id ="originalJobLinkContainer").find("a")['href']
            if original_link.find('indeed.com') > -1 :
                try: r = requests.get(original_link,proxies=proxies,headers=header, verify=False,allow_redirects=True,timeout=350)
                except: try : sleep (1) ; r = requests.get(original_link,proxies=proxies,headers=header, verify=False,allow_redirects=True,timeout=650) ; expect: print("timeout")
                if proxies == {} and r : original_link = r.url
                elif proxies != {} and r : original_link = r.headers['sa-final-url']
    
        d = soup.find(class_="miniRefresh").find_all("script")[1]  # .find(string=re.compile("Failed to Save Job"))
        d = str(d.encode("ansi")).replace(r"\\x22","").replace(r"\\","")
        if d.find("companyName:") >= 0 : company_name = d.split("companyName:")[1].split(",")[0]
        if d.find("ariaContent:") >= 0 : review_overall = d.split("ariaContent:")[1].split(" out")[0]
        if d.find("countContent:") >= 0 : review_total_overall = d.split("countContent:")[1].split(" reviews")[0]
        if d.find("salaryText") >= 0 : salary = d.split("salaryText:")[1].split(",salaryTextFormatted")[0] 
        if d.find("Job Type::") >= 0 : job_type = d.split("Job Type::")[1].split(r"},")[0].replace("[","").replace("]","")
        # **************** SALARY SECTION 
        if salary :  salary_min = salary.split(" ")[0]
        if salary.find(" - ") >= 0 : 
            salary_min = salary.split(" - ")[0] 
            salary_max = salary.split(" - ")[1].split(' ')[0]
        if salary.find("a ") >= 0 : 
            if salary.split('a ')[1] == 'year': salary_type = "Annually"
            if salary.split('a ')[1] == 'month': salary_type = "Monthly"
        if salary.lower().find("monthly") >= 0 : salary_type = "Monthly"
        if salary.lower().find("annually") >= 0 : salary_type = "Annually"
        if salary.lower().find("an hour") >= 0 : salary_type = "Hourly"
        if salary.lower().find("a week") >= 0 : salary_type = "Weekly"
        if salary.lower().find("usd") >= 0 or salary.find("$") >= 0 : salary_currency = "$"
        if salary.find("an hour") >= 0 : salary_type = "Hourly"

        desc = d.split("sanitizedJobDescription:")[1].split("{")[1].split("}")[0]
        ######## SECTION EMAIL FINDING 
        if desc.find("@") != -1 :
            try:
                if re.findall('x3\w+@',desc) : contact_detail = re.findall('x3\w+@',desc)[-1].split('x3')[-1][1:] + desc.split(re.findall('x3\w+@',desc)[-1])[1].split('x3')[0]
                else : 
                    contact_detail = re.findall('\w+@',desc)[-1].split('x3')[-1] + desc.split(re.findall('\w+@',desc)[-1])[-1].split(' ')[0]
                    if contact_detail.endswith('.'): contact_detail = contact_detail[:-1]
            except : pass
                
            if len(contact_detail) > 30 :
                try:
                    contact_detail = desc.split("@")[0].split(" ")[-1] + '@' + desc.split("@")[1].split(".com")[0] + ".com"
                except expression as identifier:
                    pass
                # if desc.split("@")[1].split(".com")[1][0] == '.' : contact_detail = contact_detail + desc.split(".com")[1].split(" ")[0]
                if len(contact_detail) > 30: 
                    contact_detail = desc.split("@")[0].split(" ")[-1] + '@' + desc.split("@")[1].split(".gov")[0] + ".gov"
            
        for e in range(1,len(desc[1:-2])):
            if desc[e].islower() and desc[e-1].isupper() and desc[e-2].isupper() and desc[e-3].isupper(): # eg POSITIONx
                desc = desc[:e] + " " + desc[e:]
            if desc[e].islower() and desc[e+1].isupper():     # eg eREQUIRED
                desc = desc[:e+1] + " " + desc[e+1:]
            if desc[e] == '.' and desc[e+1:e+4] not in extra_word:   #.x3cbrx3en
                desc = desc[:e+1] + " " + desc[e+1:]
            if desc[e-3].islower() and desc[e-2].islower() and desc[e-1].islower() and desc[e] == 'x' and desc[e+1].isdigit() :   # Developmentx3
                desc = desc[:e] + " " + desc[e:]
            if desc[e:e+4]== 'www.' :
                if desc[e-1] != ' ' : desc = desc[:e] + " " + desc[e:]
                if desc[e+4] == " ": desc = desc[:e+4] + desc[e+5:]  

        desc = desc.replace("Header"," <h5> ").replace("Section"," <p> ").replace("div"," <div> ")
        desc = " ".join(w for w in wordpunct_tokenize(desc) if w.lower() in words or w.lower()[0:-1] in words or w in wordpunct_tokenize(company_name) or w.isnumeric() or w.lower() in extra_word).replace('content ','')
        desc = desc.replace("h5"," <h5> ").replace(" p "," <p>").replace("div","<div>").replace("\n","")
        if desc.upper().find(' NZ . ') >= 0 : desc = desc.replace(' NZ .','NZ.').replace(" nz .","nz.")
        if desc.find(' P . O ') >= 0 : desc = desc.replace(' P . O ','P.O')
        
        if d.find("{age:") >= 0 : post_age = d.split("{age:")[1].split(",")[0]
        
        # another way better one
        # ddesc = soup.find_all('p')  #+ soup.find_all('li')
        # desc = desc +"".join(t.get_text() for t in ddesc)

        det = "<p>".join(t.get_text() + "</p>" for t in soup.find_all('p')[6:-18])
        det = det + "<li>".join(t.get_text() + "</li>" for t in soup.find_all('li')[6:-18])
        det = det.replace("\n","")
        if det.find("@") != -1 : 
            contact_detail = det.split("@")[0].split(" ")[1] + '@' + det.split("@")[1].split(".com")[0] + ".com"
            if det.split("@")[1].split(".com")[1][0] == '.' : contact_detail = contact_detail + split(".com")[1].split(" ")[0]
            if len(contact_detail) > 30: 
                contact_detail = det.split("@")[0].split(" ")[1] + '@' + det.split("@")[1].split(".gov")[0] + ".gov"
                if det.split("@")[1].find(".gov") > 0 : 
                    if det.split("@")[1].split(".gov")[1][0] == '.' : contact_detail = contact_detail + split(".gov")[1].split(" ")[0]
                    


        if d.find("Email: ") >= 0 : 
            contact_detail = d.split("Email: ")[1].split(".com")[0] + ".com"
            if len(contact_detail) > 25: contact_detail = d.split("Email: ")[1].split(".gov")[0] + ".gov"

        if len(contact_detail) > 30: contact_detail = ""
        if len(location.split(" ")) > 3: det = location + "\n" + det ; location = ""

    except Exception as e: 
        print ("error happend during this job   "+ str(e) + " URL = " + URL)
        print(traceback.format_exc())
        logf.write("error happend during this job   "+ str(e) + " URL = " + URL)
        logf.flush()
        pass

    row = [j_id,title,location,desc,det,original_link,company_name,review_overall,review_total_overall,salary,contact_detail,'',post_age,salary_currency,salary_type,salary_min,salary_max]



    return(row)




def get_company_data(company):
    try:
    # global d,soup
        URL = "https://nz.indeed.com/cmp/"+ company.replace(' ','-')  + "/reviews"
        logoUrl = ""
        jobsBoardUrl = "https://nz.indeed.com/cmp/"+ company.replace(' ','-')
        website = ""
        address = ""
        leader_name = ""
        leader_photo = ""
        #rating": 
        totalOverall = ""
        overall = ""
        workLife = ""
        salary = ""
        jobSecurity = ""
        culture = ""
        management = ""
        leadership = ""
        industry = ""
        revenue = ""
        size = ""
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        d = soup.find(class_="turnstileInfo").find("div")
        logoUrl = d.find(class_="cmp-CompactHeaderCompanyLogo-logo")["src"]
        if d.find(class_="u-screenReaderOnly") != '': overall= d.find(class_="u-screenReaderOnly").get_text().split(" out of ")[0].split(" ")[-1]
        else : overall= d.find_all("span")[5].get_text()
        if len(d.find_all(class_="u-screenReaderOnly")) > 1 : totaloverall= d.find_all(class_="u-screenReaderOnly")[1].get_text().split(" out of ")[0]
        else : totaloverall= d.find_all("span")[6].get_text()
        workLife = d.find_all(class_="cmp-TopicFilter-rating")[0].get_text().split(" ")[0]
        salary= d.find_all(class_="cmp-TopicFilter-rating")[1].get_text().split(" ")[0]
        jobSecurity = d.find_all(class_="cmp-TopicFilter-rating")[2].get_text().split(" ")[0]
        culture = d.find_all(class_="cmp-TopicFilter-rating")[4].get_text().split(" ")[0]
        management= d.find_all(class_="cmp-TopicFilter-rating")[3].get_text().split(" ")[0]
    except : pass
    try :
        leadership= ""
        URL = "https://nz.indeed.com/cmp/"+ company.replace(' ','-')
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        d = soup.find(class_="turnstileInfo").find("div").find_all(class_="css-1p4nx4e eu4oa1w0")
        if len(d) == 1 : industry= d[0].get_text()
        if len(d) == 2 : size = d[0].get_text() ; industry= d[1].get_text()
        if len(d) == 3 or len(d) == 3: revenue = d[2].get_text(); size = d[0].get_text() ; industry= d[1].get_text()
        if len(d) == 5 : revenue = d[3].get_text(); size = d[2].get_text() ; industry= d[4].get_text() ; leader_name = d[0].get_text()
        leader_name = str(soup.find(class_="turnstileInfo").find_next_sibling()).split('aboutCeo":{"name":"')[1].split('"')[0]
        leader_photo = str(soup.find(class_="turnstileInfo").find_next_sibling()).split('photoUrl":"')[1].split('"')[0]
    except : 
        pass

    crow = [logoUrl,jobsBoardUrl,website,address,leader_name,leader_photo,totalOverall,overall,workLife,salary,jobSecurity,culture,management,leadership,industry,revenue,size]
    return(crow)










# Find links to jobs 
URL_BASE = 'https://nz.indeed.com/jobs?q=&l=New+Zealand&sort=date&fromage=1&start='
URL = URL_BASE

proxies = {}
j_urls = set()
print ("         Collecting Jobs\n ===============================")
for start in range(10,30,10):
    try:
        ua = UserAgent()
        header = {'User-Agent':str(ua.chrome),'referer': 'https://nz.indeed.com/?from=gnav-viewjob'}
        page = requests.get(URL, proxies=proxies,headers=header, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        if soup.find('title').get_text().upper().find("CAPTCHA") > 0 : 
            print ("Found a captcha from collecting jobs. Moving to proxy")
            logf.write("Found a captcha from collecting jobs. Moving to proxy")
            proxies = { "http": 'http://scraperapi:8a562ddd940a60b50c445db89d201b7c@proxy-server.scraperapi.com:8001', 
            "https": 'http://scraperapi:8a562ddd940a60b50c445db89d201b7c@proxy-server.scraperapi.com:8001' }

        results = soup.find_all('a',target="_blank")
        # results[6].attrs['href']
        for e,x in enumerate(results):
            if "rc/clk?jk" in x.attrs['href'] :
                u = "https://nz.indeed.com/viewjob?" + x.attrs['href'].split(r'?')[1].split("&")[0]
                j_urls.add(u)
                # print (u + str(e),str(start))
                
    except Exception as e: 
        print ("error appear in collecting jobs ...." + str(e))
        logf.write("error appear in collecting jobs ...." + str(e))
        pass

    URL = URL_BASE + str(start)
    print ("Number of collected jobs : " + str(len(j_urls)))
    logf.write ("\nNumber of collected jobs : " + str(len(j_urls)))
    logf.flush()

# URL = 'http://www.indeed.com/viewjob?jk=815464c6243f8ecd'
# /rc/clk?jk=90399e9659e9c2b1&fccid=138588eb6cb98a02&vjs=3
# Jobs section
x = 0
# sheet = open('indeed.csv','a', encoding="utf-8",newline='')
# writer = csv.writer(sheet)
# workbook = load_workbook(filename="indeed.xlsx")
# sheet = workbook.active
filename = "data//"+datetime.now().strftime("%Y-%m-%d")+"-nz.json"
jfile = open(filename,'w', encoding="utf-8", newline='\r\n')
jfile.write("[")
for URL in list(j_urls):
# URL = list(j_urls)[11]
    try:
        x+= 1
        print ("=======================================================  collecting job info for Job number : " + str(x))
        row = get_job_data(URL)
        # print (str(row))
        print ("=======================================================  collecting job info for comany : " + row[6])
        logf.write("===============  collecting job info for comany : " + row[6])
        logf.flush()
        crow = get_company_data(row[6])
        if x%45 == 0 : proxies= {}
        # print (str(crow))
        # for r,row_items in enumerate(row):
        #     sheet.cell(row=x+1, column=r+1).value = row_items
        #     sheet.cell(row=x+1, column=r+1).alignment = Alignment(wrapText=True)
        #     sheet.cell(row=x+1, column=r+1).alignment = Alignment(horizontal='center')
        #     sheet.cell(row=x+1, column=r+1).alignment = Alignment(vertical='center')
        #         0      1     2        3  4     5                 6         7             8                    9      10          11   12          13                14       15       16
        # row = [j_id,title,location,desc,det,original_link,company_name,review_overall,review_total_overall,salary,contact_detail,'',post_age,salary_currency,salary_type,salary_min,salary_max]
        # crow = [logoUrl,jobsBoardUrl,website,address,leader_name,leader_photo,totalOverall,overall,workLife,salary,jobSecurity,culture,management,leadership,industry,revenue,size]
        JSON_JOB  =    {
        "id": row[0],
        "title": row[1],
        "location": {
            "address":row[2],
            "suburb": '',
            "postcode":'',
            "country":'New Zealand'
        },
        "description": row[3]+"\n"+row[4] ,
        "jobTypeCode": '' ,
        "salary": {
            "description": row[9] ,
            "type": row[14] ,
            "min":  row[15] ,
            "max":  row[16] ,
            "currency": row[13]
        },
        "url": URL ,
        "directUrl": row[5] ,
        "listingDate": row[12],
        "scrapeDate": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "contacts": [
            {
                "email": row[10],
                "phone": row[11]
            }],     
        "company": {
            "name": row[6],
            "logoUrl": crow[0],
            "jobsBoardUrl": crow[1],
            "website": crow[2],
            "location": {
                "address": crow[3],
                "suburb": '',
                "postcode": '',
                "country": 'New Zealand'
        },
        "leader": {
            "name": crow[4],
            "photoUrl": crow[5],
        },
        "rating": {
            "totalOverall": crow[6],
            "totalLeadership": '',
            "overall": crow[7],
            "workLife": crow[8],
            "salary": crow[9],
            "jobSecurity": crow[10],
            "culture": crow[11],
            "management": crow[12],
            "leadership": crow[13]
        },
        "industry": crow[14],
        "revenue": crow[15],
        "size": crow[16],
        "socialMedia": {
            "twitter": '',
            "instagram": '',
            "facebook": '',
            "youtube": ''
        }}}

        # print (JSON_JOB)
        json.dump(JSON_JOB, jfile, indent=4, sort_keys=False, ensure_ascii=False)
        jfile.write("\n,")
        jfile.flush()
    except Exception as e: 
        print ("error appear in jobs loop ...." + str(e))
        logf.write("error appear in jobs loop ...." + str(e))
        continue

try:

    jfile.write("\n]")
    jfile.close()
    logf.close()
################# Addition of the common jobs
    filename = "data//"+datetime.now().strftime("%Y-%m-%d")+"-nz.txt"
    jfile = open(filename,'w+', encoding="utf-8")
    jfile.write("[\n")

    for t in range (0,5):
        ydate = datetime.now() - timedelta(t)
        ofilename = "data//"+datetime.strftime(ydate, '%Y-%m-%d')+"-nz.json"
        if not os.path.isfile(ofilename) : continue
        f_in = open(ofilename, 'r', encoding="utf-8", newline='\r\n')
        x = f_in.readlines()
        jfile.write("{\n")
        for l in x[1:-1]:
            y = l.replace(datetime.strftime(ydate, '%d/%m/%Y'),datetime.strftime(datetime.now(), '%d/%m/%Y')).replace("\n\r","").replace("\n","")
            jfile.write(y)
        f_in.close()

    jfile.write('\n]')
    jfile.close()

    filename = "ftp//"+datetime.now().strftime("%Y-%m-%d")+"-nz.json"
    jfile = open(filename,'w+', encoding="utf-8", newline='\r\n')
    ofilename = "data//"+datetime.now().strftime("%Y-%m-%d")+"-nz.txt"
    f_in = open(ofilename, 'r', encoding="utf-8", newline='\r\n')
    x = f_in.readlines()
    for y in x[0:-1]:
        jfile.write(y.replace("\n\r","").replace("\n",""))

    for y in x[1:]:
        jfile.write(y.replace("\n\r","").replace("\n",""))

    f_in.close()
    jfile.close()
    os.remove(ofilename)


except Exception as e: 
    print ("error appear in addition of duplicate jobs filation ...." + str(e))
    logf.write("error appear in addition of duplicate jobs filation ...." + str(e))
    logf.close()

try:
    import gzip
    with open(filename, 'rb') as f_in, gzip.open(filename.replace(".json",".gz"), 'wb+') as f_out:
        f_out.writelines(f_in)
    # os.remove(filename)
    os.system('copy ftp\\'+ filename[5:] + ' ..\\us_scraper\\ftp')
    #workbook.save(filename="indeed.xlsx")
    #workbook.close()
except Exception as e: 
        print ("error appear in end save file ...." + str(e))
        logf.write("error appear in end save file ...." + str(e))
        logf.close()

