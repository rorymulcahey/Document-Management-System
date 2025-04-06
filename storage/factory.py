from django.conf import settings
from storage.base import StorageBackend
from storage.windows import WindowsStorage
from storage.azure import AzureStorage
# from storage.linux import LinuxStorage (future)

def get_storage_backend() -> StorageBackend:
	if settings.STORAGE_BACKEND == "windows":
		return WindowsStorage()
	elif settings.STORAGE_BACKEND == "azure":
		return AzureStorage()
	# elif settings.STORAGE_BACKEND == "linux":
	#	return LinuxStorage()
	else:
		raise ValueError("Unsupported storage backend")
