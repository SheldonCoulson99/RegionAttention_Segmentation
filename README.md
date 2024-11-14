# capstone-project-2024-t3-9900w17bcloudv

capstone-project-2024-t3-9900w17bcloudv created by GitHub Classroom

# COMP[39]900

## 2024, Term 3

## 9900W17B_CloudV

## P16 - Region-attention based medical image segmentation

| Name         | zID      | Role                                                                         | Email                   |
| ------------ | -------- | ---------------------------------------------------------------------------- | ----------------------- |
| Boyang Peng  | z5499630 | Scrum master, Model designer, Model developer, UI Backend, System deployment | z5499630@ad.unsw.edu.au |
| Zenghua Wang | z5575408 | Model designer, Model developer                                              | z5575408@ad.unsw.edu.au |
| Pengfei Pu   | z5463304 | Model designer, Model developer                                              | z5463304@ad.unsw.edu.au |
| Jingjie Xu   | z5442663 | UI Frontend, Model designer, Model developer                                 | z5442663@ad.unsw.edu.au |
| Yanping Liu  | z5437486 | UI Backend, System deployment, Model developer                               | z5437486@ad.unsw.edu.au |


## 1. Prerequisites:

### 1) Pre-Trained Models: Due to the huge size of the pre-trained model, they can't be uploaded to GitHub. 
### So, the solution is putting them on my Google Drive, [here is the link](https://drive.google.com/drive/folders/1C7sCpqvhX-r5zkz1Z06PvnTGbn66qa8Q?usp=drive_link) to download them from my Google Drive.

### If the link is not working, feel free to email me at z5499630@ad.unsw.edu.au.

### Pre-trained model for LViT needs to be placed at this location: `ImageSegmentation/segmentation/LViT/MoNuSeg/Test_session_MoNuSeg_lvit/models/`

### Pre-trained model for ISIC18-UDTransNet needs to be placed at this location: `ImageSegmentation/segmentation/UDTransNet/ISIC18_kfold/UDTransNet/Test_session_ISIC18/models/fold_1/`

### Pre-trained model for MoNuSeg-UDTransNet needs to be placed at this location: `ImageSegmentation/segmentation/UDTransNet/MoNuSeg_kfold/UDTransNet/Test_session_MoNuSeg/models/fold_1/`

### Pre-trained model for DCSAU-Net needs to be placed at this location: `ImageSegmentation/segmentation/DCSAU-Net/save_models/`

### 2) Docker: Use the newest version of Docker. It can be downloaded from this link: https://www.docker.com/

### 3) Ensure that the project file structure is precisely as shown below.

### The directory is structured in a hierarchical manner, as follows:

- ImageSegmentation: Main backend directory containing Django files, Dockerfile, and docker-compose.yml.
  - Dockerfile: Defines the Docker environment.
  - db.sqlite3: SQLite database file.
  - manage.py: Django’s main entry point for commands.
  - mysite: Likely contains Django settings.
  - segmentation: Django app with subdirectories for each model. DCSAU-Net, LViT and UDTransNet. And with Django core files like models.py and views.py.
- medical-frontend: Frontend directory
  - src and public: Standard frontend directories for source code and public files.
  - package.json: Manages frontend dependencies.

```shell
.
├── ImageSegmentation
│   ├── Dockerfile
│   ├── db.sqlite3
│   ├── docker-compose.yml
│   ├── manage.py
│   ├── media
│   ├── mysite
│   ├── requirements.txt
│   └── segmentation
│       ├── DCSAU-Net
│       ├── LViT
│       ├── UDTransNet
│       ├── __init__.py
│       ├── __pycache__
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── index.html
└── medical-frontend
    ├── README.md
    ├── index.html
    ├── node_modules
    ├── package-lock.json
    ├── package.json
    ├── public
    ├── src
    └── vite.config.js
```

- Backend service:
  - Maps Django port `8000` to the host’s port `8000`.
  - Mounts the backend directory for live updates in development.
  - Waits for the frontend service for any Requests.
- Frontend service:
  - Maps Vite development server port 5173 to the host's port 5173, using Node.js 16 as the base image
  - Mounts the frontend directory for hot reloading during development and communicates with the backend service through port 8000
  - Provides an interactive web interface for medical image segmentation with features including multiple image processing, model selection, and result visualization

## 2. How to build and run the containers:

### 1) Navigate to the backend root directory (ImageSegmentation) :

```shell
cd /your/path/ImageSegmentation
```

### 2) Build and start the containers:

```shell
docker-compose up --build
```

### 3) After starting the project, you should see these prompts:

### 4) Access the servers:

- Django Backend: Visit [http://localhost:8000](http://localhost:8000).
- Frontend: Visit [http://localhost:3000](http://localhost:3000).
