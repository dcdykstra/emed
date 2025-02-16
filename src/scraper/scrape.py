import time
import datetime as dt

import pandas as pd

from selenium.common.exceptions import TimeoutException


from src.config.configlog import config, logger


from src.scraper.pages.login import LoginPage
from src.scraper.pages.content import ContentPage
from src.scraper.pages.practice import PracticePage
from src.scraper.pages.reports import ReportsPage
from src.scraper.pages.visitsReport import VisitsReport
from src.scraper.pages.cptReport import CPTsReport
from src.scraper.pages.aptReport import AppointmentsReport
from src.scraper.pages.billing import BillingReport

from src.scraper.helpers.driver import Driver
from src.scraper.helpers.cleaners import FileCleaner


def scrape_yesterday(headless):
    ## Set the dates for the report
    now = dt.datetime.now()
    yesterday = now - dt.timedelta(days=1)

    date = yesterday.strftime("%Y-%m-%d")
    bill_start_date, bill_end_date = get_billing_date_range(date)
    yesterday = yesterday.strftime("%m-%d-%Y")

    scrape_all_reports(
        start_date=yesterday,
        end_date=yesterday,
        bill_start_date=bill_start_date,
        bill_end_date=bill_end_date,
        headless=headless,
    )

    return date


def scrape_date(date: str, headless):
    """date -> YYYY-MM-DD"""
    ## Set the dates for the report
    date_parse = pd.to_datetime(date, format="%Y-%m-%d")
    bill_start_date, bill_end_date = get_billing_date_range(date)

    date_parse = date_parse.strftime("%m-%d-%Y")

    scrape_all_reports(
        start_date=date_parse,
        end_date=date_parse,
        bill_start_date=bill_start_date,
        bill_end_date=bill_end_date,
        headless=headless,
    )

    return date


def scrape_date_range(start_date: str, end_date: str, headless):
    """date -> YYYY-MM-DD
    Date range cannot be more than 88 days
    BillingServicesReport may fail if date range is not large enough to automatically warrant a zip file when sourcing through eMed
    """
    ## Set the dates for the report
    start_date = pd.to_datetime(start_date, format="%Y-%m-%d")
    start_date = start_date.strftime("%m-%d-%Y")

    ## Set the dates for the report
    end_date = pd.to_datetime(end_date, format="%Y-%m-%d")
    end_date = end_date.strftime("%m-%d-%Y")

    scrape_all_reports(
        start_date=start_date,
        end_date=end_date,
        bill_start_date=start_date,
        bill_end_date=end_date,
        headless=headless,
    )

    return start_date, end_date


def scrape_all_reports(start_date, end_date, bill_start_date, bill_end_date, headless):
    ## Instantiate the helper class
    helper = FileCleaner()

    ## Set the directories for downloads and output
    downloads = helper.get_dir_path("downloads")

    ## Set the driver settings
    driver_settings = Driver.get_driver(downloads, headless=headless)
    driver = driver_settings.driver

    ## Instantiate the page objects
    login = LoginPage(driver_settings)
    content = ContentPage(driver_settings)
    reports = ReportsPage(driver_settings)
    practice = PracticePage(driver_settings)
    apts = AppointmentsReport(driver_settings)
    visits = VisitsReport(driver_settings)
    cptpage = CPTsReport(driver_settings)
    bill = BillingReport(driver_settings)

    ## Start the scraping process
    driver.get("https://service.emedpractice.com/index.aspx")

    ## LOGIN
    login.enter_username(config.loginid)
    login.enter_password(config.loginpassword)
    login.click_login()

    ## GET THE CURRENT CPTS
    content.nav_practice()
    practice.nav_favorites()
    practice.select_crd()
    cpts = practice.scrape_cpts()
    cpts.to_csv("data//output//cpt_codes.csv", index=False)
    time.sleep(10)

    try:
        ## GET THE APPOINTMENTS REPORT
        content.nav_reports()
        reports.load_report("AppointmentReportv1")
        apts.show_all_schedulers()
        apts.select_search_by("R")
        apts.select_date_range(start_date, end_date)

        apts.click_submit()
        helper.extract_zips(downloads)

        apts.download_csv()
        time.sleep(5)
    except TimeoutException as e:
        logger.info(f"[ FAILED ] Couldn't Get Appointments Report: {e}")

    try:
        ## GET THE BILLINGS REPORT
        content.nav_reports()
        reports.load_report("BillingServicesReportV1")
        bill.select_dates(bill_start_date, bill_end_date)
        bill.run_report()
        time.sleep(5)
        helper.extract_zips(downloads)
    except TimeoutException as e:
        logger.info(f"[ FAILED ] Couldn't Get Billings Report: {e}")

    try:
        ## GET CPTs REPORT
        content.nav_reports()
        reports.load_report("cpt_bills_reportV2")
        cptpage.enter_cpt_code(",".join(cpts["code"].unique()))
        cptpage.select_search_by("R")
        cptpage.select_date_range(start_date, end_date)

        cptpage.click_submit()
        helper.extract_zips(downloads)

        cptpage_df = cptpage.scrape_table()
        cptpage_df.to_csv("data//downloads//cptreport.csv", index=False)
    except TimeoutException as e:
        logger.info(f"[ FAILED ] Couldn't Get CPTs Report: {e}")

    try:
        ## GET THE VISITS REPORT
        reports.load_report("visitreport")
        visits.stage_visits(start_date, end_date)

        visits.click_submit()
        helper.extract_zips(downloads)

        visits.download_csv()
        time.sleep(5)
        helper.clear_zips(downloads)
    except TimeoutException as e:
        logger.info(f"[ FAILED ] Couldn't Get Visits Report: {e}")

    helper.rename_csv("AppointmentsReport.csv", "Appointment_Report", downloads)
    helper.rename_csv("BillingServicesReport.csv", "BillingServicesReport", downloads)
    helper.rename_csv("VisitReport.csv", "Visit_Report", downloads)

    logger.info("[ OKAY ] Completed Scrape Execution")

    driver.close()
    driver.quit()


def get_billing_date_range(date: str):
    """
    Calculate the billing date range based on a given date.

    Args:
        date (str): The date in the format "YYYY-MM-DD".

    Returns:
        tuple: The start and end dates of the billing period.
    """
    max_days = 88

    date_parse = pd.to_datetime(date, format="%Y-%m-%d")
    emr_start_date = pd.to_datetime("2024-05-20", format="%Y-%m-%d")
    emr_end_date = dt.datetime.now()

    num_days = (emr_end_date - emr_start_date).days

    if num_days < max_days:
        bill_start_date = emr_start_date
        bill_end_date = emr_end_date
    else:
        start_date_parse_diff = abs((date_parse - emr_start_date).days)
        if start_date_parse_diff > max_days:
            bill_start_date = date_parse - dt.timedelta(days=max_days)
            bill_end_date = date_parse
        else:
            bill_start_date = date_parse - dt.timedelta(days=start_date_parse_diff)
            bill_end_date = date_parse + dt.timedelta(
                days=max_days - start_date_parse_diff
            )

    assert (bill_end_date - bill_start_date).days > 0
    assert (bill_end_date - bill_start_date).days <= max_days
    assert bill_end_date <= emr_end_date
    assert bill_start_date >= emr_start_date

    bill_start_date = bill_start_date.strftime("%m-%d-%Y")
    bill_end_date = bill_end_date.strftime("%m-%d-%Y")
    return bill_start_date, bill_end_date
