import cloudinary.uploader

def upload_image_to_cloudinary(django_file):
    result = cloudinary.uploader.upload(
        django_file,
        folder="n8n"
        
    )
    return result["secure_url"]

print(cloudinary.config().api_key, " Cloudinary configuration loaded")