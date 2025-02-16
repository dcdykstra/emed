import pandas as pd


def clean_whitespace(df):
    for column in df.columns:
        try:
            df[column] = df[column].str.strip()
            df[column] = df[column].replace("", None)
        except AttributeError:
            pass

    df.columns = df.columns.str.replace("\xa0", "")
    df.columns = df.columns.str.replace(" ", "")

    return df


def clean_appointments(appointments):
    appointments = clean_whitespace(appointments)
    appointments["AppointmentDate"] = pd.to_datetime(
        appointments["AppointmentDate"], errors="coerce"
    )
    appointments = appointments.loc[appointments["AppointmentDate"].notnull()].copy()
    appointments = appointments.loc[
        ~appointments["Chart#"].isin([1, 2, 35, 426])
    ].copy()

    appointments["Chart#"] = pd.to_numeric(appointments["Chart#"])

    print(appointments.columns)
    print(f"NRows: {len(appointments)}")
    print(f"Nunique Chart #: {appointments['Chart#'].nunique()}")

    return appointments


def clean_cpts(cptReport):
    cptReport = clean_whitespace(cptReport)
    cptReport = cptReport.dropna(subset=["Chart#"]).copy()
    cptReport = cptReport.loc[~cptReport["Chart#"].isin([1, 2, 35, 426])].copy()

    cptReport["Chart#"] = pd.to_numeric(cptReport["Chart#"])

    print(cptReport.columns)
    print(f"NRows: {len(cptReport)}")
    print(f"Nunique Chart #: {cptReport['Chart#'].nunique()}")

    return cptReport


def clean_visitors(visitors):
    visitors = clean_whitespace(visitors)
    visitors = visitors.loc[~visitors["Chart#"].isin([1, 2, 35, 426])].copy()

    visitors["Chart#"] = pd.to_numeric(visitors["Chart#"])

    print(visitors.columns)
    print(f"NRows: {len(visitors)}")
    print(f"Nunique Chart #: {visitors['Chart#'].nunique()}")

    return visitors


def clean_billings(billings, cpt_codes, date):
    billings = clean_whitespace(billings)
    billings = billings.loc[
        billings["CPTSINEMR"].isin(cpt_codes["code"].unique())
    ].copy()
    billings = billings.loc[~billings["Chart#"].isin([1, 2, 35, 426])].copy()
    billings = billings.loc[
        billings["EncounterDate"] == pd.to_datetime(date, format="%Y-%m-%d")
    ].copy()

    billings["Chart#"] = pd.to_numeric(billings["Chart#"])

    print(billings.columns)
    print(f"NRows: {len(billings)}")
    print(f"Nunique Chart #: {billings['Chart#'].nunique()}")

    return billings
