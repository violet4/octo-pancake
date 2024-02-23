import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, UniqueConstraint, CheckConstraint, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class LayoutType(enum.Enum):
    GRID_8x4 = "8x4_grid"
    CUSTOM = "custom"


class ButtonBoard(Base):
    __tablename__ = "button_board"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    layout_type = Column(Enum(LayoutType))

    # For custom layouts:
    layout_width = Column(Integer)
    layout_height = Column(Integer)

    buttons = relationship("ButtonConfig", back_populates="board")

    # undesirable constraint.
    __table_args__ = (
        UniqueConstraint(
            "layout_type", "layout_width",
            "layout_height", name="unique_custom_layout",
        ),
    )


class ButtonFunctionalityType(enum.Enum):
    APP_SWITCH = "app_switch"
    RUN_SCRIPT = "run_script"
    PAGE_SWITCH = "page_switch"


class ButtonConfig(Base):
    __tablename__ = "button_config"
    id = Column(Integer, primary_key=True)
    button_board_id = Column(Integer, ForeignKey("button_board.id"))
    position_x = Column(Integer)
    position_y = Column(Integer)
    image_filename = Column(String, CheckConstraint("image_filename NOT LIKE '%/%'"))

    functionality_type = Column(Enum(ButtonFunctionalityType))
    functionality_data = relationship(
        "ButtonFunctionalityData", uselist=False,
        back_populates="button_config"
    )

    board = relationship("ButtonBoard", back_populates="buttons")
    # named constraint :D
    __table_args__ = (UniqueConstraint("button_board_id", "position_x", "position_y", name="unique_button_position"),)


class ButtonFunctionalityData(Base):
    __tablename__ = "button_functionality_data"
    id = Column(Integer, primary_key=True)
    button_config_id = Column(Integer, ForeignKey("button_config.id"))

    app_name = Column(String)
    script_path = Column(String)
    target_board_id = Column(Integer, ForeignKey("button_board.id"))

    button_config = relationship("ButtonConfig", back_populates="functionality_data")
    target_board = relationship("ButtonBoard")


if __name__ == "__main__":
    engine = create_engine("sqlite:///data.sqlite")#, echo=True)
    # enable foreign key constraint checking
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    # # enable WAL mode
    # @event.listens_for(engine, "connect")
    # def set_sqlite_pragma2(dbapi_connection, connection_record):
    #     cursor = dbapi_connection.cursor()
    #     cursor.execute("PRAGMA journal_mode=WAL")
    #     cursor.close()
    # # enable case-sensitive LIKE
    # @event.listens_for(engine, "connect")
    # def set_sqlite_pragma3(dbapi_connection, connection_record):
    #     cursor = dbapi_connection.cursor()
    #     cursor.execute("PRAGMA case_sensitive_like=ON;")
    #     cursor.close()

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    board = ButtonBoard(name="My Board", layout_type=LayoutType.GRID_8x4)
    button1 = ButtonConfig(
        board=board,
        position_x=0,
        position_y=0,
        image_filename="button1.png",
        functionality_type=ButtonFunctionalityType.APP_SWITCH,
        functionality_data=ButtonFunctionalityData(app_name="Chrome")
    )
    button2 = ButtonConfig(
        board=board,
        position_x=1,
        position_y=0,
        image_filename="button2.png",
        functionality_type=ButtonFunctionalityType.PAGE_SWITCH,
        functionality_data=ButtonFunctionalityData(target_board_id=2)
    )
    session.add_all([board, button1, button2])
    session.commit()
    session.refresh(button2)
    target_board: ButtonBoard = button2.functionality_data.target_board
    print("target_board id:", target_board)


# +--------------+----+----------+-------------+--------------+---------------+
# | button_board | id |   name   | layout_type | layout_width | layout_height |
# +--------------+----+----------+-------------+--------------+---------------+
# |              | 1  | My Board | GRID_8x4    |              |               |
# +--------------+----+----------+-------------+--------------+---------------+
# +---------------+----+-----------------+------------+------------+----------------+--------------------+
# | button_config | id | button_board_id | position_x | position_y | image_filename | functionality_type |
# +---------------+----+-----------------+------------+------------+----------------+--------------------+
# |               | 1  | 1               | 0          | 0          | button1.png    | APP_SWITCH         |
# |               | 2  | 1               | 1          | 0          | button2.png    | PAGE_SWITCH        |
# +---------------+----+-----------------+------------+------------+----------------+--------------------+
# +---------------------------+----+------------------+----------+-------------+-----------------+
# | button_functionality_data | id | button_config_id | app_name | script_path | target_board_id |
# +---------------------------+----+------------------+----------+-------------+-----------------+
# |                           | 1  | 1                | Chrome   |             |                 |
# |                           | 2  | 2                |          |             | 2               |
# +---------------------------+----+------------------+----------+-------------+-----------------+
