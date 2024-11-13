<template>
  <div class="container mt-4">
    <div class="card">
      <div class="card-body">

        <!-- Steps Indicator -->
        <div class="mb-4">
          <div class="steps d-flex justify-content-center">
            <div class="step-item" :class="{ 'active': step >= 1 }">
              1. Select Model & Image
            </div>
            <div class="step-item" :class="{ 'active': step >= 2 }">
              2. Preview
            </div>
            <div class="step-item" :class="{ 'active': step >= 3 }">
              3. Results
            </div>
          </div>
        </div>

        <!-- Model Selection -->
        <div class="mb-4">
          <div class="card bg-light">
            <div class="card-body">

              <h5 class="card-title mb-3">Select Segmentation Model</h5>
              <div class="row align-items-center">
                <div class="col-md-6">
                  <select 
                    class="form-select"
                    v-model="selectedModel"
                    :disabled="isProcessing"
                  >
                    <option value="" disabled>Choose a model</option>
                    <option v-for="model in models" 
                            :key="model.id" 
                            :value="model.id">
                      {{ model.name }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6">
                  <div class="model-info mt-2 mt-md-0" v-if="selectedModelInfo">
                    <p class="mb-1 text-muted">
                      <small>{{ selectedModelInfo.description }}</small>
                    </p>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        <!-- File Upload Area -->
        <div class="mb-4">
          <div class="upload-area p-4 text-center border rounded">
            <!-- File Input -->
            <input 
              type="file" 
              class="form-control" 
              @change="handleFileChange"
              accept="image/*"
              ref="fileInput"
              multiple
              style="display: none"
            >
            <div 
              class="upload-trigger"
              @click="triggerFileInput"
              :class="{ 'has-file': imagePreview.length > 0 }"
            >
              <i class="bi bi-cloud-upload fs-1"></i>
              <div class="mt-2">
                {{ imagePreview.length > 0 ? 'Click to change images' : 'Click to select medical images' }}
              </div>
              <div class="small text-muted mt-1">
                Supports JPG, PNG formats
              </div>
            </div>
          </div>
        </div>

        <!--Show original image preview-->
        <div class="row" v-if="imagePreview.length > 0">
          <div v-for="(preview, index) in imagePreview" :key="'preview-' + index" class="mb-4">
            <div class="row">
                <div class="card h-100">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Original Image {{ index + 1 }}</span>
                    <span class="badge bg-primary" v-if="selectedModel">
                      Model: {{ selectedModelInfo.name }}
                    </span>
                  </div>
                  <div class="card-body text-center">
                    <img 
                      :src="preview"
                      class="preview-image" 
                      alt="Original Image {{ index + 1}}"
                    >
                  </div>
                </div>
            </div>
          </div>
        </div>

        <!--Show results after segmentation -->
        <div class="row" v-if="resultPreview.length > 0">
          <!-- Each group (original + 2 results) -->
          <div v-for="(preview, index) in resultPreview" :key="'preview-' + index" class="mb-4">
            <h5 class="mb-3">Image Group {{index + 1}}</h5>
            <div class="row">

              <!-- Original Image -->
              <div class="col-md-4">
                <div class="card h-100">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Original Image {{ index + 1 }}</span>
                    <span class="badge bg-primary" v-if="selectedModel">
                      Model: {{ selectedModelInfo.name }}
                    </span>
                  </div>
                  <div class="card-body text-center">
                    <img 
                      :src=resultPreview[index].original_resultUrl
                      class="preview-image" 
                      alt="Original Image {{ index + 1}}"
                    >
                  </div>
                </div>
              </div>      
          
              <!-- Segmentation Results -->
              <template v-if="resultPreview[index]">
                <!-- Result 1 -->
                <div class="col-md-4">

                  <div class="card h-100">

                    <div class="card-header">Segmentation Result 1 (Overlay)</div>
                    <div class="card-body text-center position-relative">

                      <!-- Original Image as background -->
                      <img 
                      :src=resultPreview[index].original_resultUrl
                      class="preview-image position-absolute"
                      style="top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 1;" 
                      alt="Original Image Overlay"
                      >

                      <!-- Segmentation result with opacity -->
                      <img 
                        :src="resultPreview[index].pre_resultUrl" 
                        class="preview-image position-absolute"
                        :style="{ 
                          opacity: resultPreview[index].opacity1,
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)'
                        }"
                        alt="Segmentation Result 1"
                      >

                    </div>   

                    <div class="row align-items-center mb-2">    
                      <div class="col">
                        <label class="form-label mb-0">
                            <small>Adjust Opacity</small>
                        </label>
                        <input 
                            type="range" 
                            class="form-range" 
                            v-model="resultPreview[index].opacity1" 
                            min="0" 
                            max="1" 
                            step="0.1"
                          >
                      </div>                     
                    </div>

                    <!-- download single result button -->
                    <div class="row">
                      <div class="col text-center">
                        <button 
                          class="btn btn-primary btn-sm"
                          @click="downloadSingleResult(index, 1)"
                        >
                          Save Result 1
                        </button>
                      </div>
                    </div>

                  </div>
                </div>

                <!-- Result 2 -->
                <div class="col-md-4">
                  <div class="card h-100">
                    <div class="card-header">Segmentation Result 2</div>

                      <div class="card-body text-center">
                        <img 
                          :src="resultPreview[index].over_resultUrl" 
                          class="preview-image" 
                          :style="{ opacity: resultPreview[index].opacity2 }"
                          alt="Segmentation Result 2"
                        >
                      </div>

                        <!-- Adjust opacity-->
                        <div class="row align-items-center mb-2">
                          <div class="col">
                            <label class="form-label mb-0">
                              <small>Adjust Opacity</small>
                            </label>
                            <input 
                              type="range" 
                              class="form-range" 
                              v-model="resultPreview[index].opacity2" 
                              min="0" 
                              max="1" 
                              step="0.1"
                            >
                          </div>
                        </div>

                        <!-- Download single button -->
                        <div class="row">
                          <div class="col text-center">
                            <button 
                              class="btn btn-primary btn-sm"
                              @click="downloadSingleResult(index, 2)"
                            >
                              Save Result 2
                            </button>
                          </div>
                        </div>
                  </div>
                </div>

              </template>             
            </div>
          </div>
        </div> 

        <!-- Action Buttons -->
        <div class="d-flex gap-2 justify-content-center mt-3" v-if="imagePreview">
          <button 
            class="btn btn-primary"
            @click="startSegmentation"
            :disabled="isProcessing || !selectedModel"
          >
            <span v-if="!isProcessing">Start Segmentation</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm" role="status"></span>
              Processing...
            </span>
          </button>

          <!-- Upload button -->
          <button 
            class="btn btn-primary"            
            @click="uploadImages"
          >
            Upload    
          </button>

          <!-- delete button -->
          <button 
            class="btn btn-primary"            
            @click="ClearTest"
          >
            Clear
          </button>
          
          <!-- download button -->
          <button 
            class="btn btn-success"
            @click="downloadResult"
            :disabled="!resultPreview"
          >
            Download All Results
          </button>
        </div>


        <!-- Processing Progress Bar -->
        <div class="mt-3" v-if="isProcessing">
          <div class="progress" style="height: 20px;">
            <div 
              class="progress-bar progress-bar-striped progress-bar-animated" 
              :style="{ width: progress + '%' }"
            >
              {{ progress }}%
            </div>
          </div>
        </div>

        <!-- Status Messages -->
        <div class="text-center mt-3" v-if="statusMessage">
          <div :class="['alert', statusMessageType]" role="alert">
            {{ statusMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import JSZip from 'jszip'
import { segmentationService, uploadService, deleteSession} from '../utils/apiConfig.js'

export default {
  name: 'ImageUploader',
  data() {
    return {
      selectedFile: null,
      imageFile: [],
      imagePreview: [],
      resultPreview: [],
      isProcessing: false,
      progress: 0,
      step: 1,
      statusMessage: '',
      statusMessageType: 'alert-info',
      selectedModel: '',
      processingTime: [], // to sotre the process time for each image
      confidence: [],     // to store the confidence 
      imageIDs: [],
      models: [ {
          id: 'ISIC18',
          name: "ISIC18",
          description: 'Standard segmentation model optimized for general medical imaging'
        },
        {
          id: 'MoNuSeg',
          name: "MoNuSeg",
          description: 'Enhanced model with improved accuracy for detailed tissue analysis'
        },
        {
          id: 'ISIC18_DCSAU',
          name: "ISIC18_DCSAU",
          description: 'Enhanced model with improved accuracy for detailed tissue analysis'
        },
        {
          id: 'MoNuSeg_LViT',
          name: "MoNuSeg_LViT",
          description: 'Enhanced model with improved accuracy for detailed tissue analysis'
        }
        ] 
    }
  },

  computed: {
    selectedModelInfo() {
      return this.models.find(model => model.id === this.selectedModel)
    }
  },

  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    // store the selected files into imageFile list
    // push the files into imagePreview
    handleFileChange(event) {
      const files = Array.from(event.target.files).sort((a, b) => {
        return a.name.localeCompare(b.name)
      })
      if (files.length === 0) return

      this.imageFile = []
      this.imagePreview = []
      this.resultPreview = []
      // this.processingTime = []
      // this.confidence = []
      this.step = 2
      this.statusMessage = ''

      files.forEach(file => {
        if (!['image/jpeg', 'image/png'].includes(file.type)) {
          this.showStatus('Please select a valid image file (JPG or PNG)', 'alert-danger')
          return
        } else {
          // store the selected files in imageFile[]
          this.imageFile.push(file)
          const reader = new FileReader()
          reader.onload = (e) => {
            // sotre the read images into imagePreview[]
            console.log(e.target.result)
            this.imagePreview.push(e.target.result)
          }
          reader.readAsDataURL(file)
        }
      })      
    },

    // temporarly empty parmeter of uploadImages
    async uploadImages() {
      // this.resultPreview = []
      try {     
        // if not select a files reutrn warning
        if (this.imageFile.length === 0){
          this.showStatus(
            `Please select a file to upload.`,
            'alert-warning'
          )
          return
        }
        // if not select a model return warning
        if (!this.selectedModel) {
          this.showStatus(
            `Please select a model.`,
            'alert-warning'
          )
          return
        }
        // upload selected file 
        const uploadPromises = this.imageFile.map(file => 
          uploadService.upload_images(file, this.selectedModelInfo.name)
        )
        this.showStatus(`Upload Completed.`)  
      } catch (error) {
        throw this.handleError(error)
      }
    },

    
    // define the start Segmentation methods
    async startSegmentation() {
      if (!this.imageFile || !this.selectedModel) {
        this.showStatus('Please select both a model and image', 'alert-warning')
        return
      }
      
      this.isProcessing = true
      this.progress = 0
      this.resultPreview = []
      this.imagePreview = []
      this.imageIDs = []
      
      this.showStatus(`Processing images with ${this.selectedModelInfo.name}...`, 'alert-info')
      
      try {
        const response = await segmentationService.segmentImage(this.selectedModel)                
        this.step = 3
        // save the result to the db
        const response1 = await segmentationService.save_to_db(this.selectedModelInfo.name)   
        const imagesInfo = response1.images_info         
        // get the uuid of each segemented image
        for (let i = 0; i < imagesInfo.length; i++) {
          this.imageIDs.push(imagesInfo[i].uuid)
        }
        this.showStatus('images Id collected')

        // now retrieve the result based on the uuid list
        // console.log(this.imageIDs)
        for (let i = 0; i < this.imageIDs.length; i++) {
          // get the result image 
          const original = await segmentationService.get_image('original', this.imageIDs[i])
          const pre_result = await segmentationService.get_image('predicted', this.imageIDs[i])
          const over_result = await segmentationService.get_image('overlayed', this.imageIDs[i])          
          this.resultPreview.push(
              {
                original_resultUrl: original,
                pre_resultUrl: pre_result,
                over_resultUrl: over_result,
                opacity1: 0,
                opacity2: 1
              }
          )
        }        
        this.showStatus('result retrieved')        
      } catch (error) {
        this.showStatus(error.message, 'alert-danger')
      } finally {
        this.isProcessing = false
        this.progress = 100
      }
    },


    // download single result
    async downloadSingleResult(index, resultNumber) {
      const result = this.resultPreview[index];
      const backgroundUrl = this.resultPreview[index].original_resultUrl;  // 原始背景图像
      const overlayUrl = resultNumber === 1 ? result.pre_resultUrl : result.over_resultUrl;  // 分割后的叠加图像
      const overlayOpacity = resultNumber === 1 ? result.opacity1 : result.opacity2;  // 透明度控制
      
      const backgroundImage = new Image();
      const overlayImage = new Image();
      
      // 设置图像来源
      backgroundImage.src = backgroundUrl;
      overlayImage.src = overlayUrl;

      // 加载图像完成后进行处理
      await Promise.all([
        new Promise((resolve) => (backgroundImage.onload = resolve)),
        new Promise((resolve) => (overlayImage.onload = resolve))
      ]);

      // 创建画布
      const canvas = document.createElement('canvas');
      canvas.width = backgroundImage.width;
      canvas.height = backgroundImage.height;
      const ctx = canvas.getContext('2d');

      // 绘制背景图像
      ctx.drawImage(backgroundImage, 0, 0, canvas.width, canvas.height);

      // 设置透明度并绘制叠加图像
      ctx.globalAlpha = overlayOpacity;
      ctx.drawImage(overlayImage, 0, 0, canvas.width, canvas.height);

      // 将合成图像转换为 Blob 以供下载
      canvas.toBlob((blob) => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `composite_result_${index + 1}_result${resultNumber}.png`;
        link.click();

        // 释放 URL 对象
        URL.revokeObjectURL(link.href);
      });
    },


    // download all results
    async downloadResult() {
      if (!this.resultPreview) return

      const zip = new JSZip()
      let i = 0
      for (const result of this.resultPreview) {
        const response_pre = await fetch(result.pre_resultUrl)
        const response_over = await fetch(result.over_resultUrl)
        const blob1 = await response_pre.blob()
        const blob2 = await response_over.blob()

        zip.file(`image${i + 1}_predicted_result.png`, blob1)      
        zip.file(`image${i + 1}_overlayed_result.png`, blob2)
        i++
      }

      zip.generateAsync({ type: "blob"}).then((content) => {
        const link = document.createElement("a")
        link.href = URL.createObjectURL(content)
        link.download = "segmentation_results.zip"
        link.click()
        URL.revokeObjectURL(link.href)
      })
      this.showStatus('Download started!', 'alert-success')
    },

    // clear session data
    async ClearTest(task) {
      try {
        const response = await deleteSession.clear_Test(this.selectedModel)
        this.showStatus(`Test images succefully cleared.`)
      } catch(error) {
        throw this.handleError(error)
      }    
    },

    // show status msg
    showStatus(message, type = 'alert-info') {
      this.statusMessage = message
      this.statusMessageType = type
    }
  }
}
</script>

<style scoped>
.preview-image {
  max-height: 300px;
  max-width: 100%;
  object-fit: contain;
}

.upload-area {
  border: 2px dashed #ccc;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #0d6efd;
  background-color: #f8f9fa;
}

.upload-trigger {
  color: #6c757d;
}

.upload-trigger.has-file {
  color: #198754;
}

.steps {
  margin-bottom: 2rem;
}

.step-item {
  padding: 0.5rem 1rem;
  margin: 0 1rem;
  border-radius: 20px;
  background-color: #e9ecef;
  color: #6c757d;
  transition: all 0.3s ease;
}

.step-item.active {
  background-color: #0d6efd;
  color: white;
}

.model-info {
  padding: 0.5rem;
  border-radius: 0.25rem;
}

.alert {
  margin-bottom: 0;
}

.badge {
  font-weight: normal;
}
</style>
