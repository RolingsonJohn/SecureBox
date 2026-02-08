from configparser import ConfigParser

config = ConfigParser()
config.read("./SecureBox/config.ini")

DATABASEBK = config.get("SECUREBOX", "DATABASEBK")
DATABASE = config.get("SECUREBOX", "DATABASE", fallback=DATABASEBK)
CHECKSUM = config.get("SECUREBOX", "CHECKSUM")
CONFIG_DRIVE = config.get("SECUREBOX", "CONFIG_DRIVE")