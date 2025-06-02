from cloudinary_storage.storage import MediaCloudinaryStorage

class LowQualityCloudinaryStorage(MediaCloudinaryStorage):
    def build_upload_params(self, name, content):
        params = super().build_upload_params(name, content)
        params.update({
            'quality': 'auto:30',     # ✅ Low quality optimization
            'fetch_format': 'auto',    # ✅ Serve best format (e.g., WebP)
        })
        return params