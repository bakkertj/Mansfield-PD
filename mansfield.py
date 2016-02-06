import mechanize
import cookielib
import urllib
import re
import json
import suds
import datetime
import argparse
from time import sleep
from _common import get_api
import tweetpony
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--geocode", help="print out the geocode data", action="store_true");
parser.add_argument("--google_locations", help="print out locations in google map friendy format", action="store_true");
parser.add_argument("--json", help="print out data in JSON", action="store_true");
parser.add_argument("--type", help="type of report to generate: incident, arrest, all");
parser.add_argument("--begin_date", help="start date to track");
parser.add_argument("--end_date", help="end date to track");
args = parser.parse_args()

print_google_locations = args.google_locations;
print_json = args.json;
print_type = args.type;
print_geocode = args.geocode;

if( args.end_date ):
	now= datetime.datetime.strptime(args.end_date, "%m-%d-%Y");
	now  = datetime.datetime.strptime( now.isoformat(),"%Y-%m-%dT%H:%M:%S")
	now  = (str(now).split(" "))[0]
else:
	now = datetime.date.today();
	

if( args.begin_date ):
	then = datetime.datetime.strptime(args.begin_date, "%m-%d-%Y");
	then = datetime.datetime.strptime(then.isoformat(),"%Y-%m-%dT%H:%M:%S")
	then = (str(then).split(" "))[0]
else:
	then = str(now.fromordinal( now.toordinal() - 6 ));
	now  = str(now);
		
# At this point the dates are both strings that are suitable for the POST
# Now, the length of time needs to be determined in case the time length exceeds
# 6 days
# Calculate the date difference.  We can request data in sets of 6 or less days.
ordinal_date_requested = datetime.datetime.strptime( then, "%Y-%m-%d").toordinal();
days_requested = datetime.datetime.strptime( now, "%Y-%m-%d").toordinal() - datetime.datetime.strptime( then, "%Y-%m-%d").toordinal()
if days_requested <= 0:
	print("The end date requested must be after the begin date\n");
	exit();

class Incident(object):
	def __init__(self, date=None, incident_type=None, details=None, location=None):
    		self.date = date;
    		self.incident_type = incident_type;
    		self.details = details;
    		self.location = location;
    		

incidentList = []
# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# Here we are going to loop enough to grab the dates in sets of 1 day
# \TODO Make this in units of six
loop = 0;

while loop < days_requested:
	# Open the mansfield police site 
	r = br.open("http://p2c.mansfield-tx.gov/Summary_Disclaimer.aspx")
	html = r.read()

	# I agree to the terms
	br.select_form(nr=0);
	br.submit()

	br.select_form(nr=0);
	br.submit()

	sp = BeautifulSoup(br.response().read(), "html.parser")
	eventvalidation = sp.find('input', id='__EVENTVALIDATION')['value']
	viewstate = sp.find('input', id='__VIEWSTATE')['value']


	url = 'http://p2c.mansfield-tx.gov/Summary.aspx'


	date_requested = datetime.datetime.fromordinal( ordinal_date_requested + loop )
	date_requested = datetime.datetime.strptime(date_requested.isoformat(),"%Y-%m-%dT%H:%M:%S")
	date_requested = (str(date_requested).split(" "))[0]
	#print date_requested;
	
	values = {
	'__LASTFOCUS':'',	
	'__EVENTTARGET'	:'MasterPage$mainContent$cmdSubmit2',
	'__EVENTARGUMENT':''	,
	'__VIEWSTATE':viewstate,
	'__EVENTVALIDATION':eventvalidation,
	'MasterPage$DDLSiteMap1$ddlQuickLinks':'~/main.aspx',
	'MasterPage$mainContent$chkTA2':'on',
	'MasterPage$mainContent$chkAR2':'on',
	'MasterPage$mainContent$chkLW2':'on',
	'MasterPage$mainContent$txtCase2':'',
	'MasterPage$mainContent$rblSearchDateToUse2':'Date Occurred',
	'MasterPage$mainContent$ddlDates2':'Specify Date',
	'MasterPage$mainContent$txtDateFrom2':date_requested,
	'MasterPage$mainContent$txtDateTo2':date_requested,
	'MasterPage$mainContent$txtLName2':'',
	'MasterPage$mainContent$txtFName2':'',
	'MasterPage$mainContent$txtMName2':'',
	'MasterPage$mainContent$txtStreetNo2':'',
	'MasterPage$mainContent$txtStreetName2':'',
	'MasterPage$mainContent$CGeoCityDDL12':'',
	'MasterPage$mainContent$ddlNeighbor2':'',
	'MasterPage$mainContent$ddlRange2':''
	}

	data = urllib.urlencode(values)
	response = urllib.urlopen(url, data)
	the_page = response.read()

	soup = BeautifulSoup(the_page,"html.parser")

	for e in soup.findAll('br'):
		e.extract()

	for e in soup.findAll('strong'):
		e.extract()

	t = soup.find('table', id='mainContent_gvSummary' )

	rows = t.findAll('tr')

	nextPages = rows[len(rows)-1]

	listOfPages =  re.findall(r'\bPage\$\w+', str(nextPages))

	del rows[len(rows)-1]
	del rows[len(rows)-1]
	del rows[0]

	for row in rows:

		cols = row.findAll('td')

        date = str(cols[1].find(text=True))
        type = str(cols[2].find(text=True))
        
        s = cols[3].text
        details = str(" ".join(s.split()) )
        location = str(cols[4].find(text=True))
        location = re.sub("-BLK", " BLK", location)
        incidentList.append(Incident(date, type, details, location))
		
	numberOfPages = len(listOfPages)

	eventvalidation = soup.find('input', id='__EVENTVALIDATION')['value']
	viewstate = soup.find('input', id='__VIEWSTATE')['value']

	for i in listOfPages:
		values['__EVENTTARGET'] = 'MasterPage$mainContent$gvSummary'
		values['__EVENTARGUMENT'] = i 
		values['__EVENTVALIDATION'] = eventvalidation 
		values['__VIEWSTATE'] = viewstate 
		 

		data = urllib.urlencode(values)
		response = urllib.urlopen(url, data)
		the_page = response.read()

		soup = BeautifulSoup(the_page, "html.parser")

		for e in soup.findAll('br'):
			e.extract()
	
		for e in soup.findAll('strong'):
			e.extract()
	
		t = soup.find('table', id='mainContent_gvSummary' )
	
		rows = t.findAll('tr')
	
		del rows[len(rows)-1]
		del rows[len(rows)-1]
		del rows[0]

		for row in rows:
		
			cols = row.findAll('td')
	
			date = str(cols[1].find(text=True))
			type = str(cols[2].find(text=True))
		
			s = cols[3].text
			details = str(" ".join(s.split()) )
			
			location = str(cols[4].find(text=True))
			location = re.sub("-BLK", " BLK", location)
			location = re.sub(r"/", " AND", location)
			incidentList.append(Incident(date, type, details, location))
			

	# dump the JSON data retrieved from the PD websiter
	print_json = 1;
	if print_json:
		print json.dumps(incidentList, default=lambda o: o.__dict__)

	# instantiate the geocode service
	# \TODO We use bing for geocode but google for mapping.  Need to consolidate
	url = 'http://dev.virtualearth.net/webservices/v1/geocodeservice/geocodeservice.svc?wsdl'
	
	client = suds.client.Client(url)
	client.set_options(port='BasicHttpBinding_IGeocodeService')
	request = client.factory.create('GeocodeRequest')

	credentials = client.factory.create('ns0:Credentials')
	credentials.ApplicationId = 'AltFWQY2TzJSDciGamRNlABLPpXl4aRmet3C6QxC9j1eVoltffKHel56awkSJ_c-'
	request.Credentials = credentials
	for incident in incidentList:
			# ignore any location at 1600 heritage Pkwy since that's the police station
			if incident.location != "1600 BLK    HERITAGE PKWY":
				if ( print_type == "all" or 
					 ( print_type == "incident" and incident.incident_type == "Incident" ) or
					 ( print_type == "arrest" and incident.incident_type == "Arrest" ) ):
					#print "Type: "+incident.incident_type + " " + incident.details;
					#Address
					address = client.factory.create('ns0:Address')
					address.AddressLine = incident.location
					address.AdminDistrict = "Texas"
					address.Locality = "Mansfield"      
					address.CountryRegion = "United States"
					request.Address = address
					#print "Location: " + incident.location
					if print_google_locations or print_geocode:
						try:       
							response = client.service.Geocode(request)    
						except suds.client.WebFault, e:        
							print "ERROR!"        
							print(e)
							sys.exit(1)

						try:
							locations = response['Results']['GeocodeResult'][0]['Locations']['GeocodeLocation']
	
							for location in locations:
								if print_geocode:
									print(location)
								if print_google_locations:
									print "new google.maps.LatLng("+repr(location.Latitude) + ", " + repr(location.Longitude) + "),"
						except TypeError:
							# Log addresses that give us trouble here
							error_count = 1;
	loop = loop + 1;
	sleep(0.5);

api = get_api();
if not api:
  exit
tweet = "("+repr(location.Latitude) + ", " + repr(location.Longitude) + ")"
print tweet
try:
  #status = api.update_status(status = tweet)
  status = api.update_status(tweet)
except tweetpony.APIError as err:
  print "Oh no! Your tweet could not be sent. Twitter returned error #%i and said: %s" % (err.code, err.description)
else:
  print "Yay! Your tweet has been sent! View it here: https://twitter.com/%s/status/%s" % (status.user.screen_name, status.id_str)
