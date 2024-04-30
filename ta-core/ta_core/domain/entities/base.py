from abc import ABCMeta


class IEntity(metaclass=ABCMeta):
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, IEntity):
            return self.id == obj.id
        return False
