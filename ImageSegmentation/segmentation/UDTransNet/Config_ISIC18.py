import os
import torch
import time
## PARAMETERS OF THE MODEL
save_model = True
tensorboard = True
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
use_cuda = torch.cuda.is_available()
seed = 666
os.environ['PYTHONHASHSEED'] = str(seed)

kfold = 5
cosineLR = True
n_channels = 3
n_labels = 1
epochs = 500
img_size = 224
img_size2 = 224
print_frequency = 1
save_frequency = 5000
vis_frequency = 5000


task_name = 'ISIC18'
model_name = 'UDTransNet'


if task_name == "ISIC18":
    if model_name == "UDTransNet":
        test_session = "Test_session_ISIC18"


elif task_name == "MoNuSeg":
    if model_name == "UDTransNet":
        test_session = "Test_session_MoNuSeg"

# train_dataset = './segmentation/UDTransNet/datasets/'+ task_name+ '/Train_Folder/'
test_dataset = './segmentation/UDTransNet/datasets/'+ task_name+ '/Test_Folder/'

session_name       = test_session
save_path          = task_name +'_kfold/'+ model_name +'/' + session_name + '/'
model_path         = save_path + 'models/'
tensorboard_folder = save_path + 'tensorboard_logs/'
logger_path        = save_path + session_name + ".log"
visualize_path     = save_path + 'visualize_val/'