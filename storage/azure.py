from storage.base import StorageBackend
# from azure.storage.blob import BlobServiceClient
from django.conf import settings

class AzureStorage(StorageBackend):
	def __init__(self):
		self.client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
		self.container = settings.AZURE_CONTAINER

	def save(self, file, path) -> str:
		blob_client = self.client.get_blob_client(container=self.container, blob=path)
		blob_client.upload_blob(file, overwrite=True)
		return path

	def delete(self, path) -> bool:
		blob_client = self.client.get_blob_client(container=self.container, blob=path)
		blob_client.delete_blob()
		return True

	def url(self, path) -> str:
		return f"https://{self.client.account_name}.blob.core.windows.net/{self.container}/{path}"
