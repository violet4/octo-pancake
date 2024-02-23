from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ButtonBoard(Base):
    __tablename__ = 'button_board'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    layout_type = Column(String)

    # For custom layouts
    layout_rows = Column(Integer)
    layout_columns = Column(Integer)

class ButtonConfig(Base):
    __tablename__ = 'button_config'

    id = Column(Integer, primary_key=True)
    button_board_id = Column(Integer, ForeignKey('button_board.id'))
    position_x = Column(Integer)
    position_y = Column(Integer)
    image_filename = Column(String, CheckConstraint("image_filename NOT LIKE '%/%'"))

    # Ensure that no two buttons on the same board share coordinates
    __table_args__ = (
        UniqueConstraint('button_board_id', 'position_x', 'position_y'),
    )

class FunctionalityType(Base):
    __tablename__ = 'functionality_type'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class FunctionalityAssignment(Base):
    __tablename__ = 'functionality_assignment'

    id = Column(Integer, primary_key=True)
    button_config_id = Column(Integer, ForeignKey('button_config.id'))
    functionality_type_id = Column(Integer, ForeignKey('functionality_type.id'))
    app_name = Column(String)  # If applicable
    script_path = Column(String)  # If applicable
    target_button_board_id = Column(Integer, ForeignKey('button_board.id'))  # If 'page_switch'

# Database Setup
engine = create_engine('sqlite:///data.sqlite', echo=False)  
Base.metadata.create_all(engine)

# Session 
Session = sessionmaker(bind=engine)
session = Session()


# continues to use strings instead of enums
board = ButtonBoard(name="My Board", layout_type="8x4")
session.add(board)

button_config = ButtonConfig(
                    button_board_id=board.id, 
                    position_x=0, 
                    position_y=0, 
                    image_filename="button_image.png")
session.add(button_config)


func_type = FunctionalityType(name="app_switch")
session.add(func_type)

func_assignment = FunctionalityAssignment(
                    button_config_id=button_config.id, 
                    functionality_type_id=func_type.id, 
                    app_name="Calculator")

session.add(func_assignment)
session.commit()

# +--------------+----+----------+-------------+-------------+----------------+
# | button_board | id |   name   | layout_type | layout_rows | layout_columns |
# +--------------+----+----------+-------------+-------------+----------------+
# |              | 1  | My Board | 8x4         |             |                |
# +--------------+----+----------+-------------+-------------+----------------+
# +--------------------+----+------------+
# | functionality_type | id |    name    |
# +--------------------+----+------------+
# |                    | 1  | app_switch |
# +--------------------+----+------------+
# +---------------+----+-----------------+------------+------------+------------------+
# | button_config | id | button_board_id | position_x | position_y |  image_filename  |
# +---------------+----+-----------------+------------+------------+------------------+
# |               | 1  |                 | 0          | 0          | button_image.png |
# +---------------+----+-----------------+------------+------------+------------------+
# +--------------------------+----+------------------+-----------------------+------------+-------------+------------------------+
# | functionality_assignment | id | button_config_id | functionality_type_id |  app_name  | script_path | target_button_board_id |
# +--------------------------+----+------------------+-----------------------+------------+-------------+------------------------+
# |                          | 1  |                  |                       | Calculator |             |                        |
# +--------------------------+----+------------------+-----------------------+------------+-------------+------------------------+
