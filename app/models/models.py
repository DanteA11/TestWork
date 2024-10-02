from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, DeclarativeBase

from .database import session, engine


class Base(DeclarativeBase):

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        res = ", ".join([f"{k}={v}" for k, v in self.to_dict().items()])
        return f"{type(self).__name__}({res})"


class Cat(Base):
    __tablename__ = 'cats'
    id = Column(Integer, primary_key=True)
    color = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    description = Column(String, nullable=False)

    _cat_breed = relationship("CatBreed", back_populates="cat", uselist=False, lazy="joined", cascade="all, delete")
    breed = association_proxy(
        "_cat_breed", "breed",
        # creator=lambda breed_obj: CatBreed(breed_id=breed_obj.id)
        # creator=lambda name: Breed(name=name)
    )


class Breed(Base):
    __tablename__ = "breeds"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    _cat_breed = relationship("CatBreed", back_populates="breed")
    cats = association_proxy("_cat_breed", "cat")


class CatBreed(Base):
    __tablename__ = "catbreeds"
    cat_id = Column(Integer, ForeignKey("cats.id", ondelete="CASCADE"), primary_key=True)
    breed_id = Column(Integer, ForeignKey("breeds.id"), primary_key=True)

    cat = relationship("Cat", back_populates="_cat_breed", cascade="all,delete")
    breed = relationship("Breed", back_populates="_cat_breed", lazy="joined")

    def __init__(self, name, id=None):
        super().__init__()
        if id:
            self.breed_id = id
            return
        self.breed = Breed(name=name)


async def start_conn(drop_all=False):
    async with engine.begin() as conn:
        if drop_all:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def stop_conn():
    await session.close()
    await engine.dispose()
