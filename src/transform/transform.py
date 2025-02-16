import pandas as pd
import datetime as dt
import numpy as np

from src.transform.clean import (
    clean_appointments,
    clean_cpts,
    clean_visitors,
    clean_billings,
)
from src.transform.test import (
    appointmentsFullfilledVisitorValidation,
    assertIsUniqueColumn,
    assertNotNullColumn,
)


def parse_appointments():
    """No try/catch, AppointmentsReport is required for data transformation"""
    appointments = pd.read_csv(
        "data/downloads/AppointmentsReport.csv",
        skiprows=1,
        parse_dates=["Appointment Date", "Patient DOB"],
    )
    appointments = clean_appointments(appointments)

    return appointments


def parse_cpts():
    try:
        cptReport = pd.read_csv("data/downloads/cptreport.csv")
    except FileNotFoundError:
        cptReport = pd.DataFrame(
            columns=[
                "Chart#",
                "Bill#",
                "Patient",
                "Gender",
                "DOB",
                "Phone",
                "Provider",
                "Facility",
                "Insurance",
                "ReferralProvider",
                "ServiceDate",
                "CPTCode",
                "CPTDescription",
                "ICDCodes",
                "RVUScores",
                "CPTPrice",
                "Qty",
                "TotalPrice",
                "Allowed",
                "PrimaryPaid",
                "SecondaryPaid",
                "TertiaryPaid",
                "PatientPaid",
                "BillStatus",
                "ServiceStatus",
            ]
        )
    cptReport = clean_cpts(cptReport)

    return cptReport


def parse_visitors():
    try:
        visitors = pd.read_csv("data/downloads/VisitReport.csv")
        visitors = clean_visitors(visitors)
    except FileNotFoundError:
        visitors = pd.DataFrame(
            columns=[
                "Chart#",
                "OldChart#",
                "LastName",
                "FirstName",
                "Gender",
                "DOB",
                "Address1",
                "Address2",
                "city",
                "State",
                "ZipCode",
                "ContactNo",
                "MobileNo",
                "E-mail",
                "ProviderName",
                "FacilityName",
                "InsuranceName",
                "VisitType",
                "VisitDate",
            ]
        )

    return visitors


def parse_billings(date):
    """No try/catch, BillingServicesReport is required for data transformation"""
    billings = pd.read_csv(
        "data/downloads/BillingServicesReport.csv",
        skiprows=7,
        parse_dates=["Encounter Date"],
    )
    cpt_codes = pd.read_csv("data/output/cpt_codes.csv")
    billings = clean_billings(billings, cpt_codes, date)

    return billings


def merge_daily_report(apt, cpt, vis, bil):
    apt_subset = apt[
        ["Chart#", "PatientDOB", "AppointmentDate", "AppointmentType", "Time", "Reason"]
    ]
    apt_subset["PatientDOB"] = pd.to_datetime(
        apt_subset["PatientDOB"], format="%m-%d-%Y"
    )
    now = dt.date.today()
    apt_subset["Age"] = now - apt_subset["PatientDOB"].dt.date
    apt_subset["Age"] = apt_subset["Age"].fillna(dt.timedelta(days=0))
    apt_subset["Age"] = (apt_subset["Age"] / np.timedelta64(1, "D")).astype(int) // 365

    vis_charts = vis[["Chart#", "LastName", "FirstName", "Gender"]].drop_duplicates()
    vis_charts["LastName"] = vis_charts["LastName"].str.upper()
    vis_charts["FirstName"] = vis_charts["FirstName"].str.upper()
    assertIsUniqueColumn(vis_charts, "Chart#")

    # Left merge all appointments with visitors information
    apt_list = apt_subset.merge(vis_charts, how="left", on="Chart#")

    # Filter for patients who were in the visitor report
    apt_list = apt_list.loc[apt_list["Chart#"].isin(vis_charts["Chart#"])]
    assertNotNullColumn(apt_list, "Gender")
    assertNotNullColumn(apt_list, "LastName")
    assertNotNullColumn(apt_list, "FirstName")
    # apt_fulfilled isn't necesarrily unique to Chart#
    # Someone can visit more than once per day. See 2024-07-06

    cpt_codes = (
        cpt.groupby(["Chart#", "ServiceDate"])
        .agg({"CPTCode": lambda x: sorted(pd.Series.unique(x))})
        .reset_index()
    )
    assertIsUniqueColumn(cpt_codes, "Chart#")

    billingcpts = (
        bil.groupby(["Chart#"])
        .agg({"CPTSINEMR": lambda x: sorted(pd.Series.unique(x))})
        .reset_index()
    )

    final = apt_list.merge(cpt_codes, how="left", on="Chart#")
    final = final.merge(billingcpts, how="left", on="Chart#")
    final["CPTCode"] = final["CPTCode"].fillna(final["CPTSINEMR"])

    final = final.rename(columns={"CPTCode": "CRDPROG CPT"})
    final["CRDPROG CPT Count"] = final["CRDPROG CPT"].str.len()

    final = final[
        [
            "Chart#",
            "LastName",
            "FirstName",
            "Age",
            "PatientDOB",
            "Gender",
            "AppointmentDate",
            "Time",
            "AppointmentType",
            "Reason",
            "CRDPROG CPT",
            "CRDPROG CPT Count",
        ]
    ]
    return final
