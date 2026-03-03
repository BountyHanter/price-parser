from . import (
    csk,
    krepezh159,
    uralmaster,
    etm,
    krepline,
    krep,
    krepimir,
)

REGISTRY = {
    "ЦСК": csk,
    "Крепеж 159": krepezh159,
    "УралМастер": uralmaster,
    "ЭТМ": etm,
    "Креплайн": krepline,
    "Креп": krep,
    "Крепимир": krepimir,
}


def get_extractor(site_name: str):
    return REGISTRY.get(site_name)