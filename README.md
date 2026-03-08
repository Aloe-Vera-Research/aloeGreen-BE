aloeGreen-BE/
│
├── app/
│   ├── main.py
│   ├── model/
│   │   ├── aloe_model.tflite
│   │   └── labels.txt
│   │
│   ├── services/
│   │   └── inference.py
│   │
│   ├── routes/
│   │   └── detect.py
│   │
│   └── utils/
│       └── image_preprocess.py
│
├── requirements.txt
└── README.md


python -m venv venv
venv\Scripts\activate   # Windows

pip install fastapi uvicorn pillow numpy tensorflow python-multipart


fastapi
uvicorn
pillow
numpy
tensorflow
python-multipart
