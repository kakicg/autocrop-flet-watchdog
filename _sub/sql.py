from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# データベースエンジンの作成
engine = create_engine('sqlite:///product_data.db', echo=True)
Base = declarative_base()

# モデルの定義
class ProductImage(Base):
    __tablename__ = 'product_images'

    id = Column(Integer, primary_key=True)
    photo_url = Column(String, nullable=False)
    product_size = Column(String)
    product_height = Column(Float)
    barcode_no = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# テーブルの作成
Base.metadata.create_all(engine)

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

# データの挿入
def insert_product(photo_url, product_size, product_height, barcode_no, created_at=None):
    if created_at is None:
        created_at = datetime.now()
        
    new_product = ProductImage(
        photo_url=photo_url,
        product_size=product_size,
        product_height=product_height,
        barcode_no=barcode_no,
        created_at=created_at
    )
    session.add(new_product)
    session.commit()

# データの取得
def fetch_all_products():
    products = session.query(ProductImage).all()
    for product in products:
        print(f"ID: {product.id}, URL: {product.photo_url}, Size: {product.product_size}, Height: {product.product_height}, Barcode: {product.barcode_no}, Created At: {product.created_at}")

# データの挿入例
insert_product("http://example.com/photo1.jpg", "Large", 1.503, "123456", datetime(2024, 11, 2, 14, 30))
insert_product("http://example.com/photo2.jpg", "Medium", 2.228, "789012")

# データの表示
fetch_all_products()

# セッションのクローズ
session.close()