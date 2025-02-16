from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
import os

from src.config.configlog import config


class SharePoint_Connector:
    def __init__(self, site) -> None:

        # YOUR SHAREPOINT EMAIL AND PASSWORD
        self.user_email = config.sharepoint_user
        self.user_password = config.sharepoint_pass

        # YOUR SHAREPOINT SITES' CLIENT ID AND SECRET
        self.client_id = None
        self.client_secret = None

        self.sharepoint_url = "https://hawaiioimt.sharepoint.com"
        self.site = site

    def get_sharepoint_context(self, source="client"):
        """
        Create SharePoint Context based on either client credentials
        or user credentials.
        """
        if source == "client":
            # Initialize the client credentials
            credentials = ClientCredential(self.client_id, self.client_secret)
        elif source == "user":
            # Initialize the user credentials
            credentials = UserCredential(self.user_email, self.user_password)
        else:
            print("[X] Invalid source. Try 'user' or 'client'")
            return

        # create client context object
        ctx = ClientContext(self.sharepoint_url + self.site).with_credentials(
            credentials
        )
        return ctx

    def create_sharepoint_directory(self, dir_name: str, source="client"):
        """
        Creates a folder in the sharepoint directory.
        Directory is from root /Documents/
        """
        if dir_name:

            ctx = self.get_sharepoint_context(source)

            result = ctx.web.folders.add(f"Shared Documents/{dir_name}").execute_query()

            if result:
                # documents is titled as Shared Documents for relative URL in SP
                relative_url = f"Shared Documents/{dir_name}"
                return relative_url

    def upload_to_sharepoint(self, dir_name: str, file_url: str, source="client"):
        """
        Uploads {file_url} to {dir_name}
        """
        sp_relative_url = self.create_sharepoint_directory(dir_name, source)
        ctx = self.get_sharepoint_context(source)

        target_folder = ctx.web.get_folder_by_server_relative_url(sp_relative_url)

        with open(file_url, "rb") as content_file:
            file_content = content_file.read()
            target_folder.upload_file(
                os.path.basename(file_url), file_content
            ).execute_query()
        print(f"[OK] file has been uploaded to: {sp_relative_url}")

    def download_from_sharepoint(self, relative_url, download_path, source="client"):
        """
        Downloads {relative_url} to {download_path}
        """
        ctx = self.get_sharepoint_context(source)
        file_url = self.site + relative_url

        with open(download_path, "wb") as local_file:
            file = (
                ctx.web.get_file_by_server_relative_url(file_url)
                .download(local_file)
                .execute_query()
            )
        print("[OK] file has been downloaded into: {0}".format(download_path))
