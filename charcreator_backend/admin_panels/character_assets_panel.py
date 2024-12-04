import logging
from typing import Optional
import logging
import os
import base64
import secrets
import tracemalloc
import fastapi
from fastapi import status
import fastapi.exceptions
import fastapi.responses
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel
from starlette_admin.contrib.sqlmodel import Admin, ModelView
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLAlchemyEnum
from enum import Enum as e
from sqlalchemy.orm import declarative_base
from sqlalchemy_file import FileField, ImageField
from starlette_admin.contrib.sqla import ModelView
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file.storage import StorageManager

class AssetType(str, e):
    face_shape = "face_shape"
    eye_color = "eye_color"
    hair_color = "hair_color"
    hairstyle = "hairstyle"
    tatoo = "tatoo"
    scar = "scar"
    headwear = "headwear"
    jacket = "jacket"
    pants = "pants"
    boots = "boots"
    cloak = "cloak"
    weapon = "weapon"
    shield = "shield"
    backpack = "backpack"
    decorations = "decorations"
    ears = "ears"
    horns = "horns"
    nose = "nose"
    mouth = "mouth"

# Define the Asset model with the ENUMs
Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, autoincrement=True, primary_key=True)
    file_name = Column(UUID, unique=True, nullable=False)
    asset_type = Column(SQLAlchemyEnum(AssetType), nullable=False)  # Storing the enum as a string
    cover = Column(ImageField(), nullable=True)  # ImageField for cover
    colorable = Column(Boolean, default=False)
    default_properties = Column(JSONB, nullable=False)


async def init(app):

    driver = LocalStorageDriver("/app")  # Make sure this path is correct
    container_name = "Asset"
    try:
        container = driver.get_container(container_name)
    except:
        # Create the container if it doesn't exist
        container = driver.create_container(container_name)

    StorageManager.add_storage("default", container)

    engine = create_engine(f"postgresql://{os.environ["POSTGRES_USER"]}:{ os.environ["POSTGRES_PASSWORD"]}@{"cc-database"}/{os.environ["POSTGRES_DB"]}")
    
    SQLModel.metadata.create_all(engine)

    # Create an empty admin interface
    admin = Admin(engine, title="CharCreator AssetsEditor")

    # Add view
    admin.add_view(ModelView(Asset, icon="fas fa-list"))

    # Mount admin to your app
    admin.mount_to(app)