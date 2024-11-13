import numpy as np
import torch
from torch.autograd import Variable
import torch.nn as nn
from data_loading import binary_class
import albumentations as A
from albumentations.pytorch import ToTensor
from pytorch_lightning.metrics import Accuracy, Precision, Recall, F1
import time
import cv2
import os

class IoU(nn.Module):
    def forward(self, inputs, targets, smooth=1):
        inputs = inputs.view(-1)
        targets = targets.view(-1)
        intersection = (inputs * targets).sum()
        total = (inputs + targets).sum()
        union = total - intersection 
        IoU = (intersection + smooth) / (union + smooth)
        return IoU

class Dice(nn.Module):
    def forward(self, inputs, targets, smooth=1):
        intersection = (inputs * targets).sum()
        dice = (2. * intersection + smooth) / (inputs.sum() + targets.sum() + smooth)
        return dice

def overlay_mask_on_image(original_img, mask):
    color_mask = np.zeros_like(original_img)
    color_mask[mask == 255] = [0, 255, 0]
    overlayed_image = cv2.addWeighted(original_img, 0.8, color_mask, 0.2, 0)
    return overlayed_image

def get_transform():
   return A.Compose(
       [
           A.Resize(256, 256),
           A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
           ToTensor()
       ]
   )
   
def get_transform_ori():
   return A.Compose(
       [
           A.Resize(256, 256),
           ToTensor()
       ]
   )

if __name__ == '__main__':
    dataset_path = './segmentation/DCSAU-Net/datasets/ISIC18/test'
    model_path = './segmentation/DCSAU-Net/save_models/epoch_last.pth'
    predicts = True
    os.makedirs('./segmentation/DCSAU-Net/predicts/', exist_ok=True)

    test_files = os.listdir(os.path.join(dataset_path, 'images'))
    test_dataset = binary_class(dataset_path, test_files, get_transform(), get_transform_ori())
    # print(test_dataset)
    model = torch.load(model_path, map_location=torch.device('cpu'))

    acc_eval = Accuracy()
    pre_eval = Precision()
    dice_eval = Dice()
    recall_eval = Recall()
    f1_eval = F1(2)
    iou_eval = IoU()

    # iou_score, acc_score, pre_score, recall_score, f1_score, dice_score, time_cost = [], [], [], [], [], [], []
    since = time.time()

    with torch.no_grad():
        for img, original_img, img_id in test_dataset:
            img = Variable(torch.unsqueeze(img, dim=0).float(), requires_grad=False)
            start = time.time()
            pred = model(img)
            end = time.time()
            
            pred = torch.sigmoid(pred)
            pred[pred >= 0.5] = 1
            pred[pred < 0.5] = 0
            
            if predicts:
                img_id = os.path.splitext(img_id)[0]
                pred_numpy = (pred.cpu().numpy()[0][0] * 255).astype(np.uint8)
                cv2.imwrite(f'./segmentation/DCSAU-Net/predicts/{img_id}_predict.png', pred_numpy)
                
                # Save original image
                original_img_numpy = (original_img.cpu().squeeze(0).numpy().transpose(1, 2, 0) * 255).astype(np.uint8)
                cv2.imwrite(f'./segmentation/DCSAU-Net/predicts/{img_id}_original.png', original_img_numpy)
                
                # print(pred_numpy.shape, original_img_numpy.shape)
                overlayed_image = overlay_mask_on_image(original_img_numpy, pred_numpy)
                cv2.imwrite(f'./segmentation/DCSAU-Net/predicts/{img_id}_overlayed.png', overlayed_image)

            torch.cuda.empty_cache()

    time_elapsed = time.time() - since
    print(f'Evaluation complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    # print(f'FPS: {1.0 / (sum(time_cost) / len(time_cost)):.2f}')
    # print('mean IoU:', round(np.mean(iou_score), 4), round(np.std(iou_score), 4))
    # print('mean Dice:', round(np.mean(dice_score), 4), round(np.std(dice_score), 4))
    # print('mean accuracy:', round(np.mean(acc_score), 4), round(np.std(acc_score), 4))
    # print('mean precision:', round(np.mean(pre_score), 4), round(np.std(pre_score), 4))
    # print('mean recall:', round(np.mean(recall_score), 4), round(np.std(recall_score), 4))
    # print('mean F1-score:', round(np.mean(f1_score), 4), round(np.std(f1_score), 4))
