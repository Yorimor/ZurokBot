import os
import yaml
from dataclasses import dataclass


current_dir = os.path.dirname(os.path.realpath(__file__))


@dataclass
class DBConfig:
    host: str
    port: int
    db: str
    user: str
    pwd: str


@dataclass
class VersionConfig:
    major: int
    minor: int
    code: str
    dev: bool


@dataclass
class BotConfig:
    prefix: str
    version: VersionConfig
    database: DBConfig


def load_config(name: str):
    with open(os.path.join(current_dir, f"{name}.yaml")) as f:
        cfg = yaml.load(f, Loader=yaml.SafeLoader)

    db_cfg = DBConfig(
        host=cfg["database"]["host"],
        port=cfg["database"]["port"],
        db=cfg["database"]["db"],
        user=cfg["database"]["user"],
        pwd=cfg["database"]["pass"]
    )

    version_cfg = VersionConfig(
        major=cfg["version"]["major"],
        minor=cfg["version"]["minor"],
        code=cfg["version"]["code"],
        dev=cfg["version"]["dev"]
    )

    config = BotConfig(
        prefix=cfg["prefix"],
        version=version_cfg,
        database=db_cfg
    )

    token = cfg["token"]

    # token passed separately as only used on boot
    return config, token
