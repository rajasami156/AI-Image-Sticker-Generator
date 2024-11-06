# 🖼️ Image Sticker Generator API
Welcome to the Image Sticker Generator API! This service is designed to transform images into "stickers" by isolating the main object with advanced semantic segmentation. The stickers are crafted with smooth, feathered edges to ensure a clean and professional appearance.


## Examples 

![Example1](output/sticker_check3.png)
![Example2](output/sticker_check3.png)
![Example3](output/sticker_check5.png)


## 📋 Features
### 🔍 Semantic Segmentation: Automatically detects and highlights the main object in an image, ensuring accurate cutouts and clear subject isolation.
### 🌟 Feathered Edges: Applies a soft Gaussian blur to mask edges, creating a natural transition to transparency.
### ⚡ Built with FastAPI: Ensures high performance, scalability, and rapid response times for production use.
### 📂 Versatile Image Support: Accepts both PNG and JPEG image formats.

### 🚀 Quick Start Guide
Clone the repository and navigate to the project directory.
Install Dependencies with Python 3.8+.
Start the API Server using the provided configuration.
Once running, the API will be accessible locally, ready for image uploads and sticker creation.

## 🛠️ API Endpoints
POST /create_sticker/
Description: Upload an image to generate a sticker with a transparent background.
Supported File Types: Accepts PNG and JPEG formats.
Response: Returns a PNG image of the sticker with a transparent background. In case of an unsupported file format, an error message will be returned.
## 🧩 How It Works
Model & Preprocessing: Uploaded images are preprocessed and passed through a pre-trained model for semantic segmentation.
Mask Generation: A binary mask isolates the main object in the image.
Edge Feathering: A Gaussian blur is applied to the mask edges to create a soft transition.
Sticker Creation: The mask is used to add transparency, producing an image that can be directly used as a sticker.
## 📂 Directory Structure
The main application file manages the API and endpoints, while generated stickers are saved in a designated output directory. This ensures easy access and organization for generated images.

## ⚙️ Configuration
Before running the application, confirm that the output directory exists. This is essential for storing all generated stickers for easy retrieval and management.

## 📜 License
Licensed under the MIT License, making it easy for anyone to adapt and build upon the work.

## 🙋‍♂️ Contributing
Contributions are welcome! To contribute, create a new issue or pull request for bug fixes, enhancements, or new features. All contributions should adhere to the project's coding standards and guidelines.

## Built with ❤️ by [SAMIULLAH]

## 📞 Support
For support or inquiries, please contact nicesami156@gmail.com.