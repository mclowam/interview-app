from typing import Protocol, runtime_checkable


@runtime_checkable
class IInterview(Protocol):
    async def add(self, user_id: str, position:str):
        pass

    async def update(self, user_id:str, level:str):
        pass

    async def get_interview(self, user_id):
        pass
