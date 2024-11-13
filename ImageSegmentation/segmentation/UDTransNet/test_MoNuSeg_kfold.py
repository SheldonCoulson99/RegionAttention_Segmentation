import cv2
from utils import *
import os
from nets.TF_configs import get_model_config
from nets.UDTransNet import UDTransNet
from nets.UNet import *
from tqdm import tqdm
import matplotlib.pyplot as plt
import Config_MoNuSeg as config
import torch.optim
from Load_Dataset import ValGenerator, ImageToImage2D_kfold
from torch.utils.data import DataLoader
import warnings
import time
warnings.filterwarnings("ignore")


def overlay_mask_on_image(input_img, mask):
    color_mask = np.zeros_like(input_img)
    color_mask[mask == 1] = [0, 255, 0]
    overlayed_image = cv2.addWeighted(input_img, 0.8, color_mask, 0.2, 0)
    return overlayed_image


def show_ens(predict_save, input_img, labs, save_path):
    fig, ax = plt.subplots()
    plt.imshow(predict_save, cmap='gray')
    plt.axis("off")
    height, width = predict_save.shape
    fig.set_size_inches(width / 100.0 / 3.0, height / 100.0 / 3.0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig(save_path, dpi=300)
    plt.close()


def vis_and_save_heatmap(ensemble_models, input_img, img_RGB, labs, lab_img, vis_save_path):
    outputs = []
    for model_ in ensemble_models:
        output = model_(input_img)
        pred_class = torch.where(output > 0.5, torch.ones_like(
            output), torch.zeros_like(output))
        predict_save = pred_class[0].cpu().data.numpy()
        outputs.append(predict_save)

    predict_save = np.array(outputs).mean(0)
    predict_save = np.reshape(predict_save, (config.img_size, config.img_size))
    predict_save = np.where(predict_save > 0.5, 1, 0)

    cv2.imwrite(vis_save_path + '_original_' + model_type + '.jpg', img_RGB)

    overlayed_image = overlay_mask_on_image(img_RGB, predict_save)
    cv2.imwrite(vis_save_path + '_overlayed_' +
                model_type + '.jpg', overlayed_image)

    show_ens(predict_save, None, None, save_path=vis_save_path +
             '_predict_'+model_type+'.jpg')


if __name__ == '__main__':
    # PARAMS
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    file_path = f"./segmentation/UDTransNet/datasets/{config.task_name}/Test_Folder/img"
    file_list = os.listdir(file_path)
    file_count = len(
        [file for file in file_list if os.path.isfile(os.path.join(file_path, file))])
    print(file_count, config.task_name)
    ensemble_models = []
    test_session = config.test_session

    for i in range(0, 5):
        if config.task_name == "ISIC18":
            test_num = file_count
            model_type = config.model_name
            model_path = "./segmentation/UDTransNet/ISIC18_kfold/" + \
                model_type+"/"+test_session+"/models/fold_" + \
                str(i+1)+"/best_model-"+model_type+".pth.tar"

        elif config.task_name == "MoNuSeg":
            test_num = file_count
            model_type = config.model_name
            model_path = "./segmentation/UDTransNet/MoNuSeg_kfold/" + \
                model_type+"/"+test_session+"/models/fold_" + \
                str(i+1)+"/best_model-"+model_type+".pth.tar"

        save_path = config.task_name + '/' + model_type + '/' + test_session + '/'

        att_vis_path = "./segmentation/UDTransNet/" + \
            config.task_name + '_visualize_test/'

        if not os.path.exists(att_vis_path):
            os.makedirs(att_vis_path)

        maxi = 5
        if not os.path.exists(model_path):
            maxi = i
            print("====", maxi, "models loaded ====")
            break
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))

        if model_type == 'UNet':
            model = UNet(n_channels=config.n_channels,
                         n_classes=config.n_labels)
        elif model_type == 'R34_UNet':
            model = R34_UNet(n_channels=config.n_channels,
                             n_classes=config.n_labels)
        elif model_type == 'UDTransNet':
            config_vit = get_model_config()
            model = UDTransNet(config_vit, n_channels=config.n_channels,
                               n_classes=config.n_labels, img_size=config.img_size)

        else:
            raise TypeError('Please enter a valid name for the model type')

        model.load_state_dict(checkpoint['state_dict'])
        print('Model loaded !')
        model.eval()
        ensemble_models.append(model)

    if config.n_labels == 1:
        filelists = os.listdir(config.test_dataset+"img")
    else:
        filelists = os.listdir(config.test_dataset)
    tf_test = ValGenerator(output_size=[config.img_size, config.img_size])
    test_dataset = ImageToImage2D_kfold(config.test_dataset,
                                        tf_test,
                                        image_size=config.img_size,
                                        task_name=config.task_name,
                                        filelists=filelists,
                                        split='test')
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

    dice_pred = np.zeros((maxi))
    iou_pred = np.zeros((maxi))
    dice_class = np.zeros((maxi, 8))
    dice_ens = 0.0
    dice_5folds = []
    iou_5folds = []
    end = time.time()
    with tqdm(total=test_num, desc='Test visualize', unit='img', ncols=70, leave=True) as pbar:
        for i, (sampled_batch, names) in enumerate(test_loader, 1):
            test_data = sampled_batch['image']

            arr = test_data.numpy()
            arr = arr.astype(np.float32())

            img_RGB = cv2.imread(config.test_dataset+"img/"+names[0], 1)
            img_RGB = cv2.resize(img_RGB, (config.img_size, config.img_size))

            input_img = torch.from_numpy(arr)

            vis_and_save_heatmap(ensemble_models, input_img,
                                 img_RGB, None, None, att_vis_path+names[0][:-4])

            torch.cuda.empty_cache()
            pbar.update()
    inference_time = (time.time() - end)/test_num
    print("inference_time", inference_time)
