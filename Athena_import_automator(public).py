#!python

import sys
sys.path.append('C:\\WebDriver\\bin\\')	#necessary for selenium
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import getpass
from datetime import datetime
import logging
import time	#will sleep(1) between page refresh

logging.basicConfig(level=logging.INFO)#, filename='Athena_import.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def clear_downloaded_file():
	if os.path.isfile(os.path.expanduser('~')+"\\Downloads\\reportdisplay.csv"):
		os.rename(os.path.expanduser('~')+"\\Downloads\\reportdisplay.csv",os.path.expanduser('~')+"\\Downloads\\reportdisplay(1).csv")

def rename_download_file(n):
    pass    #unnecessary for Athena 21.7 update on: 14Oct21
    '''
    while not os.path.isfile(os.path.expanduser('~')+"\\Downloads\\reportdisplay.csv"):
		time.sleep(1)
	os.rename(os.path.expanduser('~')+"\\Downloads\\reportdisplay.csv",os.path.expanduser('~')+"\\Downloads\\%s.csv"%(n,))
    '''

site = "https://athenanet.athenahealth.com"
date = "Today"	#format: M/D/YYYY, "Today", "Last Week", "Two Weeks Ago", "Three Weeks Ago", "One Month or More"
#python should open Athena with user credetials
#print("Type Athena credentials below:")
login_titles = { "username" : "USERNAME", "password" : "PASSWORD" }
k = tuple(login_titles.keys())
credentials = {
	k[0] : input("Username: "),
	k[1] : getpass.getpass()
}
logging.info("user %s logged in (password redacted)" % (credentials[k[0]],) )

#Navigate to athenaNet
try:
	driver = webdriver.Chrome()
	driver.get(site)
	assert "athenaNet" in driver.title
except AssertionError:
	logging.error("'athenaNet' not found in %s" % (driver.title,))
	driver.close()
	sys.exit("error encountered, exiting")

#login
while True:
	try:
		if credentials[k[0]] == "q":
			logging.info("user exit")
			sys.exit("user exit")
		element1 = driver.find_element_by_id(login_titles[k[0]])
		element2 = driver.find_element_by_id(login_titles[k[1]])
	except selenium.common.exceptions.NoSuchElementException:
		logging.error("%s not found, exiting..." % (k,))
		driver.close()
		sys.exit()
	else:
		element1.send_keys(credentials[k[0]])
		element2.send_keys(credentials[k[1]])
		element1.send_keys(Keys.RETURN)
		try:
			element = driver.find_element_by_name('zform')
			assert (element.get_attribute("action") == site + "/15462/87/login/complete.esp"), \
				logging.warning("Login failed, try again...")
		except AssertionError:
			print("Login failed. Please try again or 'q' to quit.")
			credentials = {
				k[0] : input("Username: "),
				k[1] : getpass.getpass()
			}
		else:
			del(element1,element2)
			login_button = driver.find_element_by_id('loginbutton')
			login_button.click()
			time.sleep(1)
			del(login_button)
	break

#catch Password Expires exception
try:
	change_password = driver.find_element_by_id("simplemodal-data")
	driver.switch_to.frame(change_password)
	change_password = driver.find_element_by_name("LATER")
	logging.warning("password set to expire soon")
	change_password.click()
	time.sleep(1)
except NoSuchElementException as exception:
	logging.debug("password expire alert not yet necessary")
else:
	del(change_password)

#Navigate to the Report Inbox
#click Report
driver.switch_to.frame("GlobalNav")
driver.find_element_by_id("reportsmenucomponent").click()
time.sleep(1)
#click Report Inbox
driver.switch_to.default_content()
elements = driver.find_elements_by_class_name("categoryitem")	#find "Report Inbox"
for element in elements:
	if "Report Inbox" in element.get_attribute('innerHTML'):
		id = element.get_attribute('id')
		logging.info("found 'Report Inbox' under: " + id)
del(elements)
driver.find_element_by_id(id).click()
time.sleep(10)
#get list of "Today" reports
driver.switch_to.frame("GlobalWrapper")
driver.switch_to.frame("frameContent")
driver.switch_to.frame("frScheduleNav")
elements = driver.find_element_by_id("deliveredReports")	#find "Today"

for element in elements.find_elements_by_class_name("ui-accordion"):
	i = element.find_element_by_class_name("ui-accordion-header-inner")
	if date in i.get_attribute('innerHTML'):	#download reports
		logging.info("found '%s', downloading reports" %(date,))
		report_table = element.find_elements_by_class_name("ax_dynamic_panel")
		clear_downloaded_file()
		for j in report_table:
			r = j.find_element_by_class_name("hiddendata").get_attribute('reportname') + "_" + j.find_element_by_class_name("hiddendata").get_attribute('date').replace('/','_')
			try:
				j.find_element_by_class_name('sprite-download').click()
			except ElementNotInteractableException as exception:	#table not visible
				element.find_element_by_class_name("ui-icon").click()
				time.sleep(1)
				j.find_element_by_class_name('sprite-download').click()	#try again
			logging.info("downloading %s..." %(r,) )
			rename_download_file(r)
		del(j)
	del(i)
del(elements)


driver.close()
print("Success!")