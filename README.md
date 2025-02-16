# eMed Selenium Web Scraper

## Requirements

- Python 3
- Pip 22.2.2+

You will need to install these in your computer before starting the setup

## Setup

1. Download required packages by running command

   ```
   pip install -r requirements.txt
   ```

   --- or ---

   ```
   pip3 install -r requirements.txt
   ```

2. Create a `config.ini`
   > **_Note:_** Use example file `config.ini.example` as a starting point
3. Get the `client_secrets.json`, `settings.yaml`, and `credentials.json` files and put it in the root directory of this project
4. Run the following command
   ```
   python main.py
   ```
   --- or ---
   ```
   python3 main.py
   ```

---

## Config INI Data Dictionary

| Key               | Description                                                                                                          | Type     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- | -------- |
| `loginid`         | The username to log into eMedical                                                                                    | `string` |
| `loginpassword`   | The password to login into eMedical                                                                                  | `string` |
| `datadir`         | The full path to where you want to output the data files into                                                        | `string` |
| `driveid`         | The folder ID in Google Drive. You can get this from the url when selected on the shared drive you want to upload to | `string` |
| `sharepoint_user` | Username login for DOH SharePoint                                                                                    | `string` |
| `sharepoint_pass` | Password login for DOH SharePoint                                                                                    | `string` |
| `datefrom`        | Start date of historical eMed data                                                                                   | `date`   |
| `cptgroup`        | Group to pull strings of CPT codes from eMed                                                                         |
# emed
