from django.shortcuts import render

# Create your views here.
import os, logging, traceback
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import subprocess
import sys
from .models import SegmentedImage

logger = logging.getLogger(__name__)


# Return Python version and executable path
def check_python_version(request):
    return JsonResponse({
        "python_version": sys.version,
        "python_path": sys.executable
    })


# Handle image upload and save to the specified model's folder
@csrf_exempt
def upload_image(request):
    if (request.method == "POST" and request.FILES.get("image")
            and request.POST.get("model_name")):
        uploaded_file = request.FILES["image"]
        model_name = request.POST["model_name"]

        # Set save path based on model name
        if model_name == "ISIC18":
            save_dir = os.path.join(
                settings.BASE_DIR,
                "./segmentation/UDTransNet/datasets/ISIC18/Test_Folder/img",
            )
        elif model_name == "MoNuSeg":
            save_dir = os.path.join(
                settings.BASE_DIR,
                "./segmentation/UDTransNet/datasets/MoNuSeg/Test_Folder/img",
            )
        elif model_name == "ISIC18_DCSAU":
                save_dir = os.path.join(
                settings.BASE_DIR,
                "./segmentation/DCSAU-Net/datasets/ISIC18/test/images",
            )
        elif model_name == "MoNuSeg_LViT":
                save_dir = os.path.join(
                settings.BASE_DIR,
                "./segmentation/LViT/datasets/MoNuSeg/Test_Folder/img",
            )
        else:
            return JsonResponse({"error": "Invalid model name"}, status=400)

        # Create directory if not exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save the uploaded file
        save_path = os.path.join(save_dir, uploaded_file.name)
        with open(save_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return JsonResponse({
            "message": "File uploaded successfully",
            "filename": uploaded_file.name,
            "model": model_name,
        })
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


# Start segmentation by running an external script
@csrf_exempt
def start_segmentation(request):
    if request.method == "POST":
        try:
            task_name = request.POST.get('task_name')
            if task_name == 'MoNuSeg':
                script_path = os.path.join(settings.BASE_DIR, "segmentation",
                                           "UDTransNet",
                                           "test_MoNuSeg_kfold.py")
                python_path = "python3.11"
                result = subprocess.run([python_path, script_path],
                                        capture_output=True,
                                        text=True)
            elif task_name == 'ISIC18':
                script_path = os.path.join(settings.BASE_DIR, "segmentation",
                                           "UDTransNet",
                                           "test_ISIC18_kfold.py")
                python_path = "python3.11"
                result = subprocess.run([python_path, script_path],
                                        capture_output=True,
                                        text=True)
                
            elif task_name == 'ISIC18_DCSAU':
                script_path = os.path.join(settings.BASE_DIR, "segmentation",
                                           "DCSAU-Net",
                                           "eval_binary.py")
                python_path = "python3.11"
                result = subprocess.run([python_path, script_path],
                                        capture_output=True,
                                        text=True)

            elif task_name == 'MoNuSeg_LViT':
                script_path = os.path.join(settings.BASE_DIR, "segmentation",
                                           "LViT",
                                           "test_model.py")
                python_path = "python3.11"
                result = subprocess.run([python_path, script_path],
                                        capture_output=True,
                                        text=True)
                
                            # Log output and errors for clarity
            logger.debug("Segmentation output: %s", result.stdout)
            logger.debug("Segmentation error: %s", result.stderr)

            # Return success or error based on script output
            if result.returncode == 0:
                return JsonResponse({
                    "message": "Segmentation started successfully",
                    "output": result.stdout,
                })
            else:
                logger.error("Segmentation script failed with error: %s", result.stderr)
                return JsonResponse(
                    {
                        "error": "Segmentation failed",
                        "details": result.stderr,
                    },
                    status=500,
                )

        except Exception as e:
            logger.error("Exception occurred during segmentation: %s", traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


# Save segmented image paths to the database
@csrf_exempt
def save_segmented_image_paths_to_db(request):
    task_name = request.POST["task_name"]
    if task_name == "MoNuSeg":
        image_dir = "./segmentation/UDTransNet/MoNuSeg_visualize_test"
    elif task_name == "ISIC18":
        image_dir = "./segmentation/UDTransNet/ISIC18_visualize_test"
    elif task_name == "ISIC18_DCSAU":
        image_dir = "./segmentation/DCSAU-Net/predicts"
    elif task_name == "MoNuSeg_LViT":
        image_dir = "./segmentation/LViT/MoNuSeg_visualize_test"
    files = os.listdir(image_dir)

    # Filter original, overlayed, and predicted images
    original_images = sorted([f for f in files if "original" in f])
    overlayed_images = sorted([f for f in files if "overlayed" in f])
    predicted_images = sorted([f for f in files if "predict" in f])

    # Check if image counts match
    if len(original_images) != len(overlayed_images) or len(
            original_images) != len(predicted_images):
        print("Image count mismatch, check the image directory.")
        return None

    images_info = []
    # Save paths to the database
    for original, overlayed, predicted in zip(original_images,
                                              overlayed_images,
                                              predicted_images):
        segmented_image = SegmentedImage.objects.create(
            original_image_path=os.path.join(image_dir, original),
            overlayed_image_path=os.path.join(image_dir, overlayed),
            predicted_image_path=os.path.join(image_dir, predicted),
        )

        images_info.append({
            "uuid": str(segmented_image.uuid),
            "original_image": original,
            "overlayed_image": overlayed,
            "predicted_image": predicted,
        })
        


    return images_info


# API to save image info to database and return status
@csrf_exempt
def save_to_db(request):
    images_info = save_segmented_image_paths_to_db(request)

    if images_info:
        return JsonResponse({
            "status": "success",
            "message": "Images saved to database",
            "images_info": images_info,
        })
    else:
        return JsonResponse(
            {
                "status": "error",
                "message": "Image count mismatch or no images found"
            },
            status=400,
        )


# Get paths for a specific image using image ID
@csrf_exempt
def get_segmented_image(request, image_id):
    try:
        segmented_image = SegmentedImage.objects.get(uuid=image_id)
        image_urls = {
            "original_image_path": segmented_image.original_image_path,
            "overlayed_image_path": segmented_image.overlayed_image_path,
            "predicted_image_path": segmented_image.predicted_image_path,
        }
        return JsonResponse(image_urls)
    except SegmentedImage.DoesNotExist:
        return JsonResponse({"error": "Image not found"}, status=404)
    except ValueError:
        return JsonResponse({"error": "Invalid UUID"}, status=400)


# Return a specific image file based on type and ID
@csrf_exempt
def get_image(request, image_type, image_id):
    try:
        segmented_image = SegmentedImage.objects.get(uuid=image_id)

        # Return appropriate image based on type
        if image_type == "original":
            image_path = segmented_image.original_image_path
        elif image_type == "overlayed":
            image_path = segmented_image.overlayed_image_path
        elif image_type == "predicted":
            image_path = segmented_image.predicted_image_path
        else:
            return JsonResponse({"error": "Invalid image type"}, status=400)

        # Return the image file
        if os.path.exists(image_path):
            return FileResponse(open(image_path, "rb"),
                                content_type="image/jpeg")
        else:
            raise Http404("Image not found")

    except SegmentedImage.DoesNotExist:
        raise Http404("Image not found")


@csrf_exempt
def clear_monuseg_visualize_test(request):
    if request.method == "POST":
        try:
            folder_path = os.path.join(settings.BASE_DIR, "segmentation", "UDTransNet", "MoNuSeg_visualize_test")
            
            folder_path_LViT = os.path.join(settings.BASE_DIR, "segmentation", "LViT", "MoNuSeg_visualize_test")

            if not os.path.exists(folder_path):
                return JsonResponse({f"error": "Folder {folder_path} does not exist"}, status=400)
            
            if not os.path.exists(folder_path_LViT):
                return JsonResponse({f"error": "Folder {folder_path_LViT} does not exist"}, status=400)

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    
            for filename in os.listdir(folder_path_LViT):
                file_path_LViT = os.path.join(folder_path_LViT, filename)
                if os.path.isfile(file_path_LViT):
                    os.remove(file_path_LViT)
            
            db_path = "./segmentation/UDTransNet/MoNuSeg_visualize_test"
            SegmentedImage.objects.filter(
                original_image_path__startswith=db_path
            ).delete()
            SegmentedImage.objects.filter(
                overlayed_image_path__startswith=db_path
            ).delete()
            SegmentedImage.objects.filter(
                predicted_image_path__startswith=db_path
            ).delete()
            
            db_path_LViT = "./segmentation/LViT/MoNuSeg_visualize_test"
            SegmentedImage.objects.filter(
                original_image_path__startswith=db_path_LViT
            ).delete()
            SegmentedImage.objects.filter(
                overlayed_image_path__startswith=db_path_LViT
            ).delete()
            SegmentedImage.objects.filter(
                predicted_image_path__startswith=db_path_LViT
            ).delete()

            return JsonResponse({"message": "All images cleared from MoNuSeg_visualize_test folder and paths cleared in database"})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
    

@csrf_exempt
def clear_isic_visualize_test(request):
    if request.method == "POST":
        try:
            folder_path = os.path.join(settings.BASE_DIR, "segmentation", "UDTransNet", "ISIC18_visualize_test")
            folder_path_dcsau = os.path.join(settings.BASE_DIR, "segmentation", "DCSAU-Net", "predicts")

            if not os.path.exists(folder_path):
                return JsonResponse({f"error": "Folder {folder_path} does not exist"}, status=400)
            
            if not os.path.exists(folder_path_dcsau):
                return JsonResponse({f"error": "Folder {folder_path_dcsau} does not exist"}, status=400)

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            for filename in os.listdir(folder_path_dcsau):
                file_path_dcsau = os.path.join(folder_path_dcsau, filename)
                if os.path.isfile(file_path_dcsau):
                    os.remove(file_path_dcsau)
                    
            db_path = "./segmentation/UDTransNet/ISIC18_visualize_test"
            SegmentedImage.objects.filter(
                original_image_path__startswith=db_path
            ).delete()
            SegmentedImage.objects.filter(
                overlayed_image_path__startswith=db_path
            ).delete()
            SegmentedImage.objects.filter(
                predicted_image_path__startswith=db_path
            ).delete()
            
            db_path_dcsau = "./segmentation/DCSAU-Net/predicts"
            SegmentedImage.objects.filter(
                original_image_path__startswith=db_path_dcsau
            ).delete()
            SegmentedImage.objects.filter(
                overlayed_image_path__startswith=db_path_dcsau
            ).delete()
            SegmentedImage.objects.filter(
                predicted_image_path__startswith=db_path_dcsau
            ).delete()

            return JsonResponse({"message": "All images cleared from ISIC18_visualize_test folder and paths cleared in database"})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

