""" Database models """

# pylint: disable=missing-docstring

from datetime import datetime
import enum

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from trade_companion.pluralize import pluralize

engine = create_engine('sqlite:///companion.db')  # pylint: disable=invalid-name
Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name

Base = declarative_base()

CONVERTERS = {
    "Varchar": lambda s, _: None if s is None else str(s),
    "String": lambda s, _: None if s is None else str(s),
    "Float": lambda s, _: None if s is None else float(s),
    "Boolean": lambda s, _: None if s is None else bool(int(s)),
    "Integer": lambda s, _: None if s is None else int(s),
    "DateTime": lambda s, _: None if s is None else datetime.fromtimestamp(int(s)),
    "Enum": lambda s, ct: None if s is None else ct.enum_class(s),
}


class Defaults:
    """ Default functionality mixin for the models.

    This does not include any fields since they would not be iterable
    and thus the current `to_filtered_dict()` would not work.
    """

    # pylint: disable=no-member

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return pluralize(cls.__name__.lower())

    @declared_attr
    def id_column(cls):  # pylint: disable=no-self-argument
        return "%s.id" % cls.__tablename__

    @classmethod
    def from_dict(cls, data):
        filtered_data = cls.to_filtered_dict(data)
        instance = cls(**filtered_data)
        return instance

    @classmethod
    def to_filtered_dict(cls, data):
        data = {k: v if v else None for k, v in data.items()}
        filtered_data = {
            c.name: CONVERTERS[c.type.__class__.__name__](data[c.name], c.type)
            for c in cls.__table__.columns if c.name in data}
        return filtered_data  # , data


class Government(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Allegiance(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class MinorFaction(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)

    updated_at = Column(DateTime)

    government_id = Column(ForeignKey(Government.id), nullable=True)
    government = relationship(Government)

    allegiance_id = Column(ForeignKey(Allegiance.id), nullable=True)
    allegiance = relationship(Allegiance)

    home_system_id = Column(ForeignKey("systems.id"), nullable=True)
    home_system = relationship("System")

    is_player_faction = Column(Boolean)


class SecurityLevel(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Economy(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class PowerState(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Power(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class ReserveType(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class System(Base, Defaults):

    id = Column(Integer, primary_key=True)
    edsm_id = Column(Integer)

    name = Column(String)

    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

    population = Column(Integer)
    is_populated = Column(Boolean)

    government_id = Column(ForeignKey(Government.id), nullable=True)
    government = relationship(Government)

    allegiance_id = Column(ForeignKey(Allegiance.id), nullable=True)
    allegiance = relationship(Allegiance)

    security_id = Column(ForeignKey(SecurityLevel.id), nullable=True)
    secyrity = relationship(SecurityLevel)

    primary_economy_id = Column(ForeignKey(Economy.id), nullable=True)
    primary_economy = relationship(Economy)

    power_state_id = Column(ForeignKey(PowerState.id), nullable=True)
    power_state = relationship(PowerState)

    power_id = Column(ForeignKey(Power.id), nullable=True)
    power = relationship(Power)

    needs_permit = Column(Boolean)

    updated_at = Column(DateTime)

    controlling_minor_faction_id = Column(ForeignKey(MinorFaction.id),
                                          nullable=True)
    controlling_minor_faction = relationship(MinorFaction)

    minor_factions = relationship(MinorFaction, back_populates="home_system")

    reserve_type_id = Column(ForeignKey(ReserveType.id),
                             nullable=True)
    reserve_type = relationship(ReserveType)

    stations = relationship("Station", back_populates="system")


class Body(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class StationType(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class SettlementSize(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class SettlementSecurity(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)


class LandingPadSize(enum.Enum):
    small = "S"
    medium = "M"
    large = "L"
    none = "None"


class Station(Base, Defaults):

    id = Column(Integer, primary_key=True)
    name = Column(String)

    system_id = Column(ForeignKey(System.id))
    system = relationship(System, back_populates="stations")

    updated_at = Column(DateTime)

    max_landing_pad_size = Column(Enum(LandingPadSize), nullable=True)

    distance_to_star = Column(Integer)

    government_id = Column(ForeignKey(Government.id), nullable=True)
    government = relationship(Government)

    allegiance_id = Column(ForeignKey(Allegiance.id), nullable=True)
    allegiance = relationship(Allegiance)

    station_type_id = Column(ForeignKey(StationType.id), nullable=True)
    station_type = relationship(StationType)

    has_blackmarket = Column(Boolean)
    has_refuel = Column(Boolean)
    has_repair = Column(Boolean)
    has_rearm = Column(Boolean)
    has_outfitting = Column(Boolean)
    has_shipyard = Column(Boolean)
    has_docking = Column(Boolean)
    has_commodities = Column(Boolean)

    shipyard_updated_at = Column(DateTime)
    outfitting_updated_at = Column(DateTime)
    market_updated_at = Column(DateTime)

    is_planetary = Column(Boolean)

    settlement_size_id = Column(ForeignKey(SettlementSize.id))
    settlement_size = relationship(SettlementSize)

    settlement_security_id = Column(ForeignKey(SettlementSecurity.id))
    settlement_security = relationship(SettlementSecurity)

    body_id = Column(ForeignKey(Body.id))
    body = relationship(Body)

    controlling_minor_faction_id = Column(ForeignKey(MinorFaction.id),
                                          nullable=True)
    controlling_minor_faction = relationship(MinorFaction)


def create_tables():
    Base.metadata.create_all(engine)
