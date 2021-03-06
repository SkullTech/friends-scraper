'''
Scrapes the list of Friends of a given Facebook account and saves them in a .csv file.
'''

import codecs
import csv
import sys
import time
from getpass import getpass
from configparser import ConfigParser
from urllib.parse import urlparse

from lxml import html
from wdstart import start_webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FacebookBot:
    def __init__(self):
        config = ConfigParser()
        config.read('config.ini')

        if not config:
            print('Config file not available!')
            sys.exit()
        try:
            self.fbusername = config['SETTINGS']['Username']
            self.fbpassword = config['SETTINGS']['Password']
        except KeyError:
            print('Credentials not found in config file!\nEnter your credentials manually...\n')
            self.fbusername = input('Enter your Facebook username: ')
            self.fbpassword = getpass('Enter your Facebook password: ')

        self.targeturl = input('Enter the URL of target Facebook profile: ')
        if not self.targeturl[-1] == '/': self.targeturl += '/'
        
        self.driver = start_webdriver('Chrome')

    def facebook_login(self):
        self.driver.get('http://www.facebook.com')
        WebDriverWait(self.driver, 30).until(EC.title_is('Facebook - Log In or Sign Up'))

        email = self.driver.find_element_by_name('email')
        pas = self.driver.find_element_by_name('pass')
        email.send_keys(self.fbusername)
        pas.send_keys(self.fbpassword)
        email.submit()

    def filter_url(self, x):
        elem = urlparse(x).path[1:]
        if elem == 'profile.php':
            elem = 'Not Available'
        return elem

    def scrape_friends(self):
        self.driver.get(self.targeturl)
        self.name = self.driver.title
        self.id = html.fromstring(self.driver.page_source.encode('utf-8')).xpath(
                    '//meta[@property="al:android:url"]/@content')[0][13:]
        self.username = self.filter_url(bot.driver.current_url)

        
        self.driver.get(self.targeturl + 'friends/')
        body = self.driver.find_element_by_tag_name('body')

        self.scroll(body)

        page = self.driver.page_source
        tree = html.fromstring(page.encode('utf-8'))

        names = tree.xpath('//div[@id="collection_wrapper_2356318349"]//div[@class="fsl fwb fcb"]/a/text()')
        usernames = [self.filter_url(x) for x in
                     tree.xpath('//div[@id="collection_wrapper_2356318349"]//div[@class="fsl fwb fcb"]/a/@href')]
        ids = [x[28:43] for x in
               tree.xpath('//div[@id="collection_wrapper_2356318349"]//div[@class="fsl fwb fcb"]/a/@data-hovercard')]

        self.data = [ids, usernames, names]

    def scroll(self, body):
        num = 0
        count = 0

        while True:
            time.sleep(2)
            for i in range(40):
                body.send_keys(Keys.END)
            if not len(html.fromstring(self.driver.page_source.encode('utf-8')).xpath('//li[@class="_698"]')) > num:
                count += 1
            if count > 4:
                break
            num = len(html.fromstring(self.driver.page_source.encode('utf-8')).xpath('//li[@class="_698"]'))

    def save_data(self):
        with codecs.open(self.username + '.csv', mode='w', encoding='utf-8') as f:
            csvwriter = csv.writer(f)

            for i in range(len(self.data[0])):
                csvwriter.writerow(
                        [self.data[0][i], self.data[1][i], self.data[2][i]])

    def execute(self):

        self.facebook_login()
        self.scrape_friends()
        self.save_data()
        print('[*] List of friends saved as {}.csv'.format(self.username))


bot = FacebookBot()
bot.execute()
