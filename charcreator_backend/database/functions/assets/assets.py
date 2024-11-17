import dataclasses
import enum
import string
import datetime
import json

from asyncpg import Connection


class AssetType(enum.Enum):
    FACE_SHAPE = 'face_shape'
    EYE_COLOR = 'eye_color'
    HAIR_COLOR = 'hair_color'
    HAIRSTYLE = 'hairstyle'
    TATOO = 'tatoo'
    SCAR = 'scar'
    HEADWEAR = 'headwear'
    JACKET = 'jacket'
    BOOTS = 'boots'
    CLOAK = 'cloak'
    WEAPON = 'weapon'
    SHIELD = 'shield'
    BACKPACK = 'backpack'
    DECORATIONS = 'decorations'
    EARS = 'ears'
    HORNS = 'horns'
    NOSE = 'nose'
    MOUTH = 'mouth'


@dataclasses.dataclass
class Asset:
    id: int
    file_name: string
    created_at: datetime.datetime
    modified_at: datetime.datetime
    asset_type: AssetType
    colorable: bool
    default_properties: json

    @classmethod
    def from_row(cls, row):
        _id, file_name, created_at, modified_at, asset_type, colorable, default_properties = tuple(row)

        return cls(
            id=_id,
            file_name=file_name,
            created_at=created_at,
            modified_at=modified_at,
            asset_type=asset_type,
            colorable=colorable,
            default_properties=default_properties,
        )

class AssetsFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn


