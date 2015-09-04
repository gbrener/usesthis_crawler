import inspect
from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from usesthis_crawler import Session


Base = declarative_base()


def init_models(db_path, enable_test_mode=False):
    engine = create_engine('sqlite:///'+db_path, echo=enable_test_mode)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)


people_to_tools_tbl = Table(
    'people_to_tools',
    Base.metadata,
    Column('person_id', Integer, ForeignKey('people.id'), primary_key=True, nullable=False),
    Column('tool_id', Integer, ForeignKey('tools.id'), primary_key=True, nullable=False)
)


class Person(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    pub_date = Column(String, nullable=False)
    title = Column(String, nullable=False)
    img_src = Column(String, unique=True, nullable=False)
    article_url = Column(String, unique=True, nullable=False)
    bio = Column(String, nullable=False)
    hardware = Column(String, nullable=False)
    software = Column(String, nullable=False)
    dream = Column(String, nullable=False)

    tools = relationship('Tool',
                         secondary=people_to_tools_tbl,
                         backref='people')

    def __repr__(self): # pragma: no cover
        cls_name = self.__class__.__name__
        variables = []

        for var_name in sorted(self.__table__.columns.keys()):
            value = getattr(self, var_name)

            if isinstance(value, str):
                pair = "{0}='{1}'".format(var_name, value)
            else:
                pair = "{0}={1}".format(var_name, value)

            # Prepend the 'id' to the list when we get to it
            if var_name == 'id':
                variables.insert(0, pair)
                continue

            variables.append(pair)

        return '<{0}({1})>'.format(cls_name, ', '.join(variables))


class Tool(Base):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, nullable=False)
    tool_name = Column(String, nullable=False)
    tool_url = Column(String, nullable=False)

    def __repr__(self): # pragma: no cover
        cls_name = self.__class__.__name__
        variables = []

        for var_name in sorted(self.__table__.columns.keys()):
            value = getattr(self, var_name)

            if isinstance(value, str):
                pair = "{0}='{1}'".format(var_name, value)
            else:
                pair = "{0}={1}".format(var_name, value)

            # Prepend the 'id' to the list when we get to it
            if var_name == 'id':
                variables.insert(0, pair)
                continue

            variables.append(pair)

        return '<{0}({1})>'.format(cls_name, ', '.join(variables))
