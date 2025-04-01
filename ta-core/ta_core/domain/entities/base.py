from abc import ABCMeta

from ta_core.utils.uuid import UUID


class IEntity(metaclass=ABCMeta):
    def __init__(self, entity_id: UUID):
        self.id = entity_id

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, IEntity):
            return self.id == obj.id
        return False
