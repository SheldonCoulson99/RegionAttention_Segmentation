import axios from 'axios'

// 设置基础 URL
const API_BASE_URL = 'http://0.0.0.0:8000/seg/'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  }
})

export const uploadService = {
  // upload images
  async upload_images(filename, task) {
    const formData = new FormData()
    formData.append('image', filename)
    formData.append('model_name', task)
    
    try {
        const response = await apiClient.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
}

// clear ISIC/moniseg test images
export const deleteSession = {
  async clear_Test(task) {
    if (task === 'ISIC18' || task === 'ISIC18_DCSAU') {
      try {
        const response = await apiClient.post(
            '/clear_isic/', 
            {headers:{'Content-Type': 'multipart/form-data'}}
        )
        return response
      } catch (error) {
        throw this.handleError(error)
      }
    } else {
      try {
        const response = await apiClient.post(
            '/clear_monuseg/', 
            {headers:{'Content-Type': 'multipart/form-data'}}
        )
        return response
      } catch (error) {
        throw this.handleError(error)
      }
    } 


    
  }
}

// segmentation related function
export const segmentationService = {
  // 图像分割
  async segmentImage(task_name) {
    const formData = new FormData()
    formData.append('task_name', task_name)
    
    try {
      const response = await apiClient.post('/start-segmentation/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  },

  // method to save the result to db
  async save_to_db(task_name) {
    const formData = new FormData()
    formData.append('task_name', task_name)

    try {
        const response = await apiClient.post('/save_to_db/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      console.error("Save to DB failed:", error.response || error.message)
      throw this.handleError(error)
    }
  },

  // retrieve images
  async get_image(imageType, imageId) {
    try {
      const response = await apiClient.get(`/get-image/${imageType}/${imageId}/`, {
        responseType: 'blob', //Ensures the response is treated as binary data (image)
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      // Convert the response blob into an object URL to display the image
      const imageUrl = URL.createObjectURL(response.data);
      return imageUrl
    } catch (error) {
      console.error("Failed to retrieve image:", error.response || error.message);
      throw this.handleError(error);
    }
  },


  // // 获取可用模型列表
  // async getModels() {
  //   try {
  //     const response = await apiClient.get('/models/')
  //     return response.data
  //   } catch (error) {
  //     throw this.handleError(error)
  //   }
  // },

  // 错误处理
  handleError(error) {
    if (error.response) {
      // 服务器返回错误状态码
      const message = error.response.data.message || 'Server error occurred'
      throw new Error(message)
    } else if (error.request) {
      // 请求发送失败
      throw new Error('Network error. Please check your connection.')
    } else {
      // 其他错误
      throw error
    }
  }
}