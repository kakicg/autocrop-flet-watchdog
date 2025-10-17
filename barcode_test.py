import cv2
from pyzbar import pyzbar

# 画像読み込み
image = cv2.imread("barcode.jpg")

# グレースケール化とコントラスト補正
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.equalizeHist(gray)

# バーコード検出
barcodes = pyzbar.decode(gray)

for barcode in barcodes:
    x, y, w, h = barcode.rect
    barcode_data = barcode.data.decode("utf-8")
    barcode_type = barcode.type
    print(f"Type: {barcode_type}, Data: {barcode_data}")

    # 検出領域を可視化
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Result", image)
cv2.waitKey(0)