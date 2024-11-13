import torch.optim
from Load_Dataset import ValGenerator, ImageToImage2D
from torch.utils.data import DataLoader
import warnings

warnings.filterwarnings("ignore")
import Config as config
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
from nets.LViT import LViT
from utils import *
import cv2

def overlay_mask_on_image(input_img, mask):
    color_mask = np.zeros_like(input_img)
    color_mask[mask == 1] = [0, 255, 0]
    overlayed_image = cv2.addWeighted(input_img, 0.8, color_mask, 0.2, 0)
    return overlayed_image

def show_image_with_dice(predict_save, labs, save_path):
    # tmp_lbl = (labs).astype(np.float32)
    # tmp_3dunet = (predict_save).astype(np.float32)
    # dice_pred = 2 * np.sum(tmp_lbl * tmp_3dunet) / (np.sum(tmp_lbl) + np.sum(tmp_3dunet) + 1e-5)
    # iou_pred = jaccard_score(tmp_lbl.reshape(-1), tmp_3dunet.reshape(-1))
    if config.task_name == "MoNuSeg":
        predict_save = cv2.pyrUp(predict_save, (448, 448))
        predict_save = cv2.resize(predict_save, (config.img_size, config.img_size))
        cv2.imwrite(save_path, predict_save * 255)
    else:
        cv2.imwrite(save_path, predict_save * 255)
    return dice_pred, iou_pred


def vis_and_save_heatmap(model, input_img, text, img_RGB, labs, vis_save_path, dice_pred, dice_ens):
    model.eval()
    
    batch_size = input_img.size(0)  # Typically 1 in your DataLoader
    seq_len = 10  # Adjust based on your model's expectations
    feature_dim = 768  # Commonly used feature size, adjust if needed
    dummy_text = torch.zeros((batch_size, seq_len, feature_dim), device=input_img.device)
    
    output = model(input_img, dummy_text)
    pred_class = torch.where(output > 0.5, torch.ones_like(output), torch.zeros_like(output))
    predict_save = pred_class[0].cpu().data.numpy()
    predict_save = np.reshape(predict_save, (config.img_size, config.img_size))
    
    cv2.imwrite(vis_save_path + '_original_' + model_type + '.jpg', img_RGB)
    
    overlayed_image = overlay_mask_on_image(img_RGB, predict_save)
    cv2.imwrite(vis_save_path + '_overlayed_' +
                model_type + '.jpg', overlayed_image)
    
    dice_pred_tmp, iou_tmp = show_image_with_dice(predict_save, labs,
                                                  save_path=vis_save_path + '_predict_' + model_type + '.jpg')
    return dice_pred_tmp, iou_tmp


if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    test_session = config.test_session
    
    file_path = f"./segmentation/LViT/datasets/MoNuSeg/Test_Folder/img"
    file_list = os.listdir(file_path)
    file_count = len(
        [file for file in file_list if os.path.isfile(os.path.join(file_path, file))])
    print(file_count, config.task_name)

    if config.task_name == "MoNuSeg":
        test_num = file_count
        model_type = config.model_name
        model_path = "./segmentation/LViT/MoNuSeg/Test_session_MoNuSeg_lvit/models/best_model-LViT.pth.tar"
    
    save_path = config.task_name + '/' + model_type + '/' + test_session + '/'
    vis_path = "./segmentation/LViT/" + config.task_name + '_visualize_test/'
    if not os.path.exists(vis_path):
        os.makedirs(vis_path)

    checkpoint = torch.load(model_path, map_location='cpu')

    if model_type == 'LViT':
        config_vit = config.get_CTranS_config()
        model = LViT(config_vit, n_channels=config.n_channels, n_classes=config.n_labels)
    else:
        raise TypeError('Please enter a valid name for the model type')

    model.load_state_dict(checkpoint['state_dict'], strict=False)
    print('Model loaded !')
    tf_test = ValGenerator(output_size=[config.img_size, config.img_size])
    # test_text = read_text(config.test_dataset + 'Test_text.xlsx')
    test_dataset = ImageToImage2D(config.test_dataset, config.task_name, None, tf_test, image_size=config.img_size)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

    dice_pred = 0.0
    iou_pred = 0.0
    dice_ens = 0.0

    with tqdm(total=test_num, desc='Test visualize', unit='img', ncols=70, leave=True) as pbar:
        for i, (sampled_batch, names) in enumerate(test_loader, 1):
            test_data, test_label = sampled_batch['image'], sampled_batch['label']
            arr = test_data.numpy()
            arr = arr.astype(np.float32())
            input_img = torch.from_numpy(arr)
            
            img_RGB = cv2.imread(config.test_dataset+"img/"+names[0], 1)
            img_RGB = cv2.resize(img_RGB, (config.img_size, config.img_size))
            
            dice_pred_t, iou_pred_t = vis_and_save_heatmap(model, input_img, None, img_RGB, None,
                                                           vis_path + str(names),
                                                           dice_pred=dice_pred, dice_ens=dice_ens)
            dice_pred += dice_pred_t
            iou_pred += iou_pred_t
            torch.cuda.empty_cache()
            pbar.update()
    print("Testing Done!")
    # print("dice_pred", dice_pred / test_num)
    # print("iou_pred", iou_pred / test_num)
