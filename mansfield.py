import mechanize
import cookielib
import urllib
import re
import json
import suds
import datetime
import argparse

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--geocode", help="print out the geocode data", action="store_true");
parser.add_argument("--google_locations", help="print out locations in google map friendy format", action="store_true");
parser.add_argument("--json", help="print out data in JSON", action="store_true");
parser.add_argument("--type", help="type of report to generate: incident, arrest, all");

args = parser.parse_args()

print_google_locations = args.google_locations;
print_json = args.json;
print_type = args.type;
print_geocode = args.geocode;


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

# Open the mansfield police site 
r = br.open("http://p2c.mansfield-tx.gov/Summary_Disclaimer.aspx")
html = r.read()

# I agree to the terms
br.select_form(nr=0);
br.submit()

br.select_form(nr=0);
br.submit()

sp = BeautifulSoup(br.response().read())
eventvalidation = sp.find('input', id='__EVENTVALIDATION')['value']
viewstate = sp.find('input', id='__VIEWSTATE')['value']


url = 'http://p2c.mansfield-tx.gov/Summary.aspx'


now = datetime.date.today();
then = now.fromordinal( now.toordinal() - 6 );

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
'MasterPage$mainContent$txtDateFrom2':then.isoformat(),
'MasterPage$mainContent$txtDateTo2':now.isoformat(),
'MasterPage$mainContent$txtLName2':'',
'MasterPage$mainContent$txtFName2':'',
'MasterPage$mainContent$txtMName2':'',
'MasterPage$mainContent$txtStreetNo2':'',
'MasterPage$mainContent$txtStreetName2':'',
'MasterPage$mainContent$CGeoCityDDL12':'',
'MasterPage$mainContent$ddlNeighbor2':'',
'MasterPage$mainContent$ddlRange2':''
}
#'MasterPage$mainContent$txtDateFrom2':'3/21/2013',
#'MasterPage$mainContent$txtDateTo2':'3/27/2013',
data = urllib.urlencode(values)
response = urllib.urlopen(url, data)
the_page = response.read()

soup = BeautifulSoup(the_page)

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

	soup = BeautifulSoup(the_page)

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
				if print_google_locations or print_geocode:
					try:       
   	 					response = client.service.Geocode(request)    
					except suds.client.WebFault, e:        
   	 					print "ERROR!"        
   	 					print(e)
   	 					sys.exit(1)

					locations = response['Results']['GeocodeResult'][0]['Locations']['GeocodeLocation']
    
					for location in locations:
						if print_geocode:
							print(location)
						if print_google_locations:
							print "new google.maps.LatLng("+repr(location.Latitude) + ", " + repr(location.Longitude) + "),"

		
