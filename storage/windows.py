import os
from django.conf import settings
from storage.base import StorageBackend

class WindowsStorage(StorageBackend):
	def save(self, file, path) -> str:
		full_path = os.path.join(settings.MEDIA_ROOT, path)
		os.makedirs(os.path.dirname(full_path), exist_ok=True)
		with open(full_path, 'wb+') as destination:
			for chunk in file.chunks():
				destination.write(chunk)
		return path

	def delete(self, path) -> bool:
		full_path = os.path.join(settings.MEDIA_ROOT, path)
		if os.path.exists(full_path):
			os.remove(full_path)
			return True
		return False

	def url(self, path) -> str:
		return os.path.join(settings.MEDIA_URL, path).replace('\\', '/')
