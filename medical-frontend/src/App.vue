<template>
  <div>
    <nav class="navbar navbar-dark bg-primary">
      <div class="container">
        <span class="navbar-brand mb-0 h1">Medical Image Segmentation System</span>
      </div>
    </nav>
    <ImageUploader />
  </div>
</template>

<script>
import ImageUploader from './components/ImageUploader.vue'

export default {
  name: 'App',
  components: {
    ImageUploader
  }
}
</script>

<style>
body {
  background-color: #f8f9fa;
}
</style>