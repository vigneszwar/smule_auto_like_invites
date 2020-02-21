import argparse
import configparser
from datetime import datetime
import json
import logging
from selenium.common.exceptions import *
from selenium.webdriver.remote.remote_connection import LOGGER
import time
import traceback
from urllib3.connectionpool import log as urllibLogger

import selenium_driver


class UserEndedException(Exception):
    pass


def site_login():
    driver.get("https://www.smule.com")
    driver.ge_by_id("react-login-button").click()
    time.sleep(1)
    driver.ge_by_link_text("Email").click()
    driver.ge_by_name("snp-username").send_keys(config['DEFAULT']['UserName'])

    myElem = driver.wge_by_name('snp-password')
    myElem.send_keys(config['DEFAULT']['password'])
    elements = driver.ges_by_xpath("//a[.//span[text()='Log In']]")
    for element in elements:
        if not element.get_attribute("id"):
            element.click()


def like_collabs(user_url):
    global driver
    driver.get(user_url)

    elements = driver.ges_by_partial_link("collab")

    count = len(elements)
    for i in xrange(count):
        try:
            navigate_and_like(i)
        except UserEndedException as e:
            logger.exception("User no more has recent collabs " + str(user_url), exc_info=True)
            break
        except TimeoutException as e:
            logger.exception("Timed out exception " + str(user_url), exc_info=True)
            driver.get(user_url)
            navigate_and_like(i)
        except Exception as e:
            logger.exception("Collab " + str(i) + " failed for " + str(user_url), exc_info=True)
            traceback.print_exc()
            driver.get(user_url)


def navigate_and_like(i):
    elements = driver.ges_by_partial_link("collab")
    logger.debug('-' * 80)
    logger.debug('len ' + str(len(elements)))
    element = elements[i]
    element.click()
    time_elem = driver.ge_by_class_name('timeago')
    time_ago = time_elem.get_attribute('innerHTML')
    album_title_elem = driver.ge_by_tag_name('h1').find_element_by_tag_name('a')
    title_name = album_title_elem.get_attribute('innerHTML')
    logger.info("title - " + str(title_name.encode('utf-8')))
    logger.info("time ago - " + str(time_ago))
    if len(time_ago) <= 3 and (time_ago.endswith("h") or time_ago.endswith("m")):
        dumm = driver.wges_by_class_name('playable')
        element = driver.ge_by_xpath("//div[contains(@class, 'playable')]")

        logger.info(str(element.get_attribute('innerHTML')))
        element.click()
        time.sleep(2)
        try:
            liked = driver.ge_by_xpath("//div[contains(@class, 'icon-love') and contains(@class, 'active')]")
        except NoSuchElementException as e:
            logger.exception("collab not liked yet. No such element exception", exc_info=True)
        except Exception as e:
            logger.exception("collab not liked yet basic exception", exc_info=True)
        else:
            driver.back()
            raise Exception("already liked")
        finally:
            print e
            import traceback
            traceback.print_exc()

        print 'past the exception'
        driver.wge_by_class_name('jp-pause').click()
        myElem = driver.wge_by_class_name('jp-duration')
        play_time = myElem.get_attribute('innerHTML')
        driver.wge_by_class_name('volume-icon').click()
        driver.wge_by_class_name('jp-play').click()
        logger.info("full play_time" + str(play_time))
        mins, secs = play_time.split(':')
        logger.info("play time " + mins + ":" + secs)
        mins, secs = int(mins), int(secs)
        if mins >= 4:
            mins = 4
        logger.info("sleeping for " + str(mins * 60 + secs))
        current_mins, current_secs = driver.wge_by_class_name('jp-current-time').get_attribute('innerHTML').split(':')
        logger.info("current time " + str(current_mins) + ":" + str(current_secs))
        time.sleep(4)

        while True:
            logger.debug(str(type(current_mins)) + str(type(current_secs)))
            time.sleep(10)
            current_mins, current_secs = driver.wge_by_class_name('jp-current-time').get_attribute('innerHTML').split(
                ':')
            logger.info("current time " + str(current_mins) + ":" + str(current_secs))
            if str(current_mins) == '00' and str(current_secs) == '00':
                break

        # time.sleep(mins*60+secs)
        dumm = driver.wge_by_class_name('icon-love')
        driver.ge_by_class_name("icon-love").click()
        time.sleep(2)
        logger.info("Liked ")
    else:
        raise UserEndedException()
    logger.info("going back")
    logger.info('-' * 80)
    driver.back()

def main():

    config.read('smule_properties.ini')
    LOGGER.setLevel(logging.WARNING)
    urllibLogger.setLevel(logging.WARNING)


    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=str, help="batch of users to pick - morning or night")
    args = parser.parse_args()
    batch = args.batch


    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    date_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    log_name = "logs\\" + str(batch) + '-' + date_time + '.log'

    formatter = '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_name, level=logging.DEBUG, format=formatter, filemode='w+')

    logger.debug("Start Time- " + str(current_time))
    user_lists = []
    batch = 'night'
    if batch == 'morning':
        logger.info('assigning morning batch')
        user_lists = json.loads(config['DEFAULT']['MorningBatch'])
    elif batch == 'night':
        logger.info('assigning night batch')
        user_lists = json.loads(config['DEFAULT']['NightBatch'])
    logger.debug("user lists" + str(user_lists))
    if not user_lists:
        logger.info('quitting as user list is empty')
        driver.quit()
        quit()
    logger.info('Signing in')
    site_login()
    for user in user_lists:
        logger.info('current user ' + str(user))
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        logger.debug("current time " + current_time)
        if current_time.startswith('01') or current_time.startswith('10:15'):
            logger.info("times up - current time is " + current_time)
            break
        try:
            like_collabs(user)
        except Exception as e:
            logger.exception("like collab failed for user " + str(user), exc_info=True)
            logger.error(traceback.format_exc())
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    logger.debug("End Time- " + current_time)
    driver.quit()

if __name__ == '__main__':
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger(__name__)
    driver = selenium_driver.ChromeDriver()
    config = configparser.ConfigParser()
    main()
