import pandas as pd
import datetime as dt

from src.scraper.scrape import scrape_yesterday, scrape_date, scrape_date_range
from src.transform.transform import (
    parse_appointments,
    parse_cpts,
    parse_visitors,
    parse_billings,
    merge_daily_report,
)
from src.load.gdriveupload import upload_files


def lambda_handler(event, context, headless):
    date = scrape_yesterday(headless=headless)
    # date = scrape_date("2024-10-14", headless=headless)
    apt_df = parse_appointments()
    cpt_df = parse_cpts()
    vis_df = parse_visitors()
    bill_df = parse_billings(date)
    print(date)
    print("[ OK ] Scrape Complete")

    final = merge_daily_report(apt_df, cpt_df, vis_df, bill_df)
    # final.to_excel(f"data/output/detainee_list_{date}.xlsx", index=False)
    final.to_csv(f"data/output/detainee_list_{date}.csv", index=False)

    upload_files([f"data/output/detainee_list_{date}.csv"])
    print("[ SUCCESS ]")


def scrape_date_list(datelist, headless):
    for i in datelist:
        date = scrape_date(i, headless=headless)
        apt_df = parse_appointments()
        cpt_df = parse_cpts()
        vis_df = parse_visitors()
        bill_df = parse_billings(date)
        print(date)
        print("[ OK ] Scrape Complete")

        final = merge_daily_report(apt_df, cpt_df, vis_df, bill_df)
        final.to_csv(f"data/output/detainee_list_{date}.csv", index=False)

        upload_files([f"data/output/detainee_list_{date}.csv"])
        print("[ SUCCESS ]")


if __name__ == "__main__":
    lambda_handler(event=None, context=None, headless=False)

    datelist = [
        "2024-10-16",
        "2024-10-17",
        "2024-10-18",
    ]
    rangelist = pd.date_range("10-16-2024", "11-06-2024")
    rangelist = [i.strftime("%Y-%m-%d") for i in rangelist]

    # scrape_date_list(datelist)
