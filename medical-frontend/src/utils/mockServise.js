export const mockSegmentation = (image, model) => {
    return new Promise((resolve, reject) => {
      // 模拟 API 处理时间（2 秒）
      setTimeout(() => {
        try {
          // 通过在原始图像上添加彩色叠加来创建模拟结果
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          const img = new Image();
          
          img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            
            // Draw original image
            ctx.drawImage(img, 0, 0);
            
            // Add different overlay effects based on the model
            ctx.globalAlpha = 0.3;
            switch(model) {
              case 'model1':
                ctx.fillStyle = 'red';
                break;
              case 'model2':
                ctx.fillStyle = 'blue';
                break;
              case 'model3':
                ctx.fillStyle = 'green';
                break;
              default:
                ctx.fillStyle = 'purple';
            }
            
            // 绘制随机分割形状
            for (let i = 0; i < 5; i++) {
              const x = Math.random() * canvas.width;
              const y = Math.random() * canvas.height;
              const size = Math.random() * 50 + 20;
              
              ctx.beginPath();
              ctx.arc(x, y, size, 0, Math.PI * 2);
              ctx.fill();
            }
            
            // 将画布转换为 base64 图像 URL
            const resultUrl = canvas.toDataURL('image/png');
            
            resolve({
              resultUrl,
              modelUsed: model,
              processingTime: '2.1 seconds',
              confidence: Math.round(Math.random() * 20 + 80) + '%'
            });
          };
          
          img.onerror = () => {
            reject(new Error('Failed to load image'));
          };
          
          img.src = image;
        } catch (error) {
          reject(error);
        }
      }, 2000);
    });
  };