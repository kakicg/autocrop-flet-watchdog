from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLAlchemyの設定
Base = declarative_base()
engine = create_engine("sqlite:///product_data.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# データベースモデル
class ItemInfo(Base):
    __tablename__ = "item_info"
    id = Column(Integer, primary_key=True)
    barcode = Column(String, nullable=False)
    barcode_whole = Column(String)
    precessed_url = Column(String, nullable=False)
    original_url = Column(String)
    height = Column(Float)
    top_y = Column(Integer)
    real_height = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

# テーブルを作成
Base.metadata.create_all(engine)
