.env dosyası oluşturulup içerisine DB_STRING değişkenine database connection stringi eklenir

pip install -r requirements.txt
uvicorn main:app --reload veya
hypercorn main:app --reload