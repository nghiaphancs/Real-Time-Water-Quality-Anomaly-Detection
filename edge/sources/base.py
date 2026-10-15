from abc import ABC, abstractmethod
from typing import Optional
from edge.schemas import Reading, SourceStatus


class DataSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_status(self) -> SourceStatus:
        pass

    @abstractmethod
    def poll_reading(self) -> Optional[Reading]:
        """Lấy mẫu đo tiếp theo (non-blocking) hoặc None nếu chưa có dữ liệu"""
        pass
