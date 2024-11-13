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
            <input 
              type="file" 
              class="form-control" 
              @change="handleFileChange"
              accept="image/*"
              ref="fileInput"
              style="display: none"
            >
            <div 
              class="upload-trigger"
              @click="triggerFileInput"
              :class="{ 'has-file': imagePreview }"
            >
              <i class="bi bi-cloud-upload fs-1"></i>
              <div class="mt-2">
                {{ imagePreview ? 'Click to change image' : 'Click to select medical image' }}
              </div>
              <div class="small text-muted mt-1">
                Supports JPG, PNG formats
              </div>
            </div>
          </div>
        </div>

        <!-- Image Preview and Results Area -->
        <div class="row" v-if="imagePreview">
          <div class="col-md-6 mb-3">
            <div class="card h-100">
              <div class="card-header d-flex justify-content-between align-items-center">
                <span>Original Image</span>
                <span class="badge bg-primary" v-if="selectedModel">
                  Model: {{ selectedModelInfo.name }}
                </span>
              </div>
              <div class="card-body text-center">
                <img 
                  :src="imagePreview" 
                  class="preview-image" 
                  alt="Original Image"
                >
              </div>
            </div>
          </div>
          
          <!-- Updated Segmentation Result Section -->
          <div class="col-md-6 mb-3" v-if="resultPreview">
            <div class="card h-100">
              <div class="card-header">Segmentation Result</div>
              <div class="card-body text-center">
                <img 
                  :src="resultPreview" 
                  class="preview-image" 
                  alt="Segmentation Result"
                >
              </div>
              <div class="card-footer bg-light">
                <div class="row text-center">
                  <div class="col">
                    <small class="text-muted">
                      Processing Time: {{ processingTime }}
                    </small>
                  </div>
                  <div class="col">
                    <small class="text-muted">
                      Confidence: {{ confidence }}
                    </small>
                  </div>
                </div>
              </div>
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
          
          <button 
            class="btn btn-success"
            @click="downloadResult"
            :disabled="!resultPreview"
          >
            Download Result
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
import { mockSegmentation } from '../utils/mockServise.js'

export default {
  name: 'ImageUploader',
  data() {
    return {
      imageFile: null,
      imagePreview: null,
      resultPreview: null,
      isProcessing: false,
      progress: 0,
      step: 1,
      statusMessage: '',
      statusMessageType: 'alert-info',
      selectedModel: '',
      processingTime: '', // 添加这行
      confidence: '',     // 添加这行
      models: [
        {
          id: 'model1',
          name: 'Model 1',
          description: 'Standard segmentation model optimized for general medical imaging'
        },
        {
          id: 'model2',
          name: 'Model 2',
          description: 'Enhanced model with improved accuracy for detailed tissue analysis'
        },
        {
          id: 'model3',
          name: 'Model 3',
          description: 'Advanced model specialized in high-resolution image segmentation'
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
    
    handleFileChange(event) {
      const file = event.target.files[0]
      if (!file) return
      
      if (!['image/jpeg', 'image/png'].includes(file.type)) {
        this.showStatus('Please select a valid image file (JPG or PNG)', 'alert-danger')
        return
      }
      
      this.imageFile = file
      this.resultPreview = null
      this.step = 2
      this.statusMessage = ''
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.imagePreview = e.target.result
      }
      reader.readAsDataURL(file)
    },
    
    async startSegmentation() {
      if (!this.imageFile || !this.selectedModel) {
        this.showStatus('Please select both a model and an image', 'alert-warning')
        return
      }
      
      this.isProcessing = true
      this.progress = 0
      this.showStatus(`Processing image with ${this.selectedModelInfo.name}...`, 'alert-info')
      
      try {
        // 创建进度模拟
        const progressInterval = setInterval(() => {
          if (this.progress < 90) {
            this.progress += 10
          }
        }, 200)

        // 使用模拟服务
        const response = await mockSegmentation(this.imagePreview, this.selectedModel)
        
        clearInterval(progressInterval)
        this.progress = 100
        
        this.resultPreview = response.resultUrl
        this.processingTime = response.processingTime
        this.confidence = response.confidence
        this.step = 3
        this.showStatus(
          `Segmentation completed successfully using ${this.selectedModelInfo.name}!`,
          'alert-success'
        )
      } catch (error) {
        console.error('Segmentation failed:', error)
        this.showStatus('Segmentation failed. Please try again.', 'alert-danger')
      } finally {
        this.isProcessing = false
      }
    },
    
    downloadResult() {
      if (!this.resultPreview) return
      
      const link = document.createElement('a')
      link.href = this.resultPreview
      link.download = `segmentation-result-${this.selectedModel}-${Date.now()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      this.showStatus('Download started!', 'alert-success')
    },

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
