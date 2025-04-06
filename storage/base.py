from abc import ABC, abstractmethod

class StorageBackend(ABC):
	@abstractmethod
	def save(self, file, path) -> str:
		pass
	
	@abstractmethod
	def delete(self, path) -> bool:
		pass

	@abstractmethod
	def url(self, path) -> str:
		pass
