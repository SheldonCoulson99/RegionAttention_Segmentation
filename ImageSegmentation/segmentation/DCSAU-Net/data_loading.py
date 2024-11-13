import os
from skimage import io, transform, img_as_ubyte
import numpy as np
from torch.utils.data import Dataset
import torch
import albumentations as A
from albumentations.pytorch import ToTensor

def Normalization():
    return A.Compose(
        [
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensor()
        ]
    )

# Dataset Loader for multi-class segmentation
class multi_classes(Dataset):
    def __init__(self, path, data, transform=None):
        self.path = path
        self.folders = data
        self.transforms = transform
        self.normalization = Normalization()
        
    def __len__(self):
        return len(self.folders)
        
    def __getitem__(self, idx):
        image_folder = os.path.join(self.path, str(self.folders[idx]), 'images/')
        # mask_folder = os.path.join(self.path, str(self.folders[idx]), 'masks/')
        
        # 获取第一个以 .png 结尾的图像文件
        image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
        if not image_files:
            raise FileNotFoundError(f"No image files found in {image_folder}")
        image_path = os.path.join(image_folder, image_files[0])  # 获取第一个有效的图像文件
        
        image_id = self.folders[idx]
        img = io.imread(image_path)[:, :, :3].astype('float32')         
        # mask = self.get_mask(mask_folder, 256, 256)
   
        augmented = self.transforms(image=img, mask=mask)
        img = augmented['image']
        mask = augmented['mask']
        
        normalized = self.normalization(image=img, mask=mask)
        img_nl = normalized['image']
        mask_nl = normalized['mask']
        mask_nl = np.squeeze(mask_nl)
        
        mask = img_as_ubyte(mask) 
        mask = np.squeeze(mask)
        mask[(mask > 0) & (mask < mask.max())] = 1
        mask[mask == mask.max()] = 2
        mask = torch.from_numpy(mask)
        mask = torch.squeeze(mask)
        mask = torch.nn.functional.one_hot(mask.to(torch.int64), 3)
        mask = mask.permute(2, 0, 1)
        return (img_nl, mask, mask_nl, image_id)

    def get_mask(self, mask_folder, IMG_HEIGHT, IMG_WIDTH):
        mask = np.zeros((IMG_HEIGHT, IMG_WIDTH, 1), dtype=np.bool)
        for mask_file in os.listdir(mask_folder):
            if mask_file.endswith('_segmentation.png'):  # 确保只处理掩码文件
                mask_ = io.imread(os.path.join(mask_folder, mask_file), as_gray=True)
                mask_ = transform.resize(mask_, (IMG_HEIGHT, IMG_WIDTH))
                mask_ = np.expand_dims(mask_, axis=-1)
                mask = np.maximum(mask, mask_)

        return mask

# Dataset Loader for binary segmentation
class binary_class(Dataset):
    def __init__(self, path, data, transform=None, transform_original=None):
        self.path = path
        self.folders = data
        self.transforms = transform
        self.transforms_resize = transform_original
        
    def __len__(self):
        return len(self.folders)
        
    def __getitem__(self, idx): 
        # 获取图像和掩码路径
        image_filename = self.folders[idx]
        # if not image_filename.endswith('.jpg') or '.ipynb_checkpoints' in image_filename:
            # 如果文件名不以 .png 结尾或包含 .ipynb_checkpoints，则跳过
            # return self.__getitem__((idx + 1) % len(self.folders))
            
        image_path = os.path.join(self.path, 'images', image_filename)
        # mask_path = os.path.join(self.path, 'masks', image_filename.replace('.png', '_segmentation.png'))

        # 加载图像和掩码
        img = io.imread(image_path).astype('float32')[:,:,:3]
        original_img = io.imread(image_path)
        original_img = original_img[:, :, ::-1]
        # mask = io.imread(mask_path, as_gray=True)

        # 数据增强
        augmented = self.transforms(image=img)
        augmented_resize = self.transforms_resize(image=original_img)
        img = augmented['image']
        original_img = augmented_resize['image']
        # mask = augmented['mask']

        return (img, original_img, image_filename)
        