import os
from pathlib import Path
import glob
import aiofiles
import aiohttp
import random
import requests
import asyncio
from datetime import datetime
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
import json
import re
import base64
from io import BytesIO
from PIL import Image

class CatPicBot:
    def __init__(self):
        self.all_images = []
        self.catapi_images = []
        self.user_images = []
        self.camera_roll_images = []
        self.special_image = None
        self.setup_assets_folder()

    def setup_assets_folder(self):
        """Create assets folder if it doesn't exist"""
        Path(ASSETS_FOLDER).mkdir(exist_ok=True)
        Path(CAMERA_ROLL_FOLDER).mkdir(exist_ok=True)
        print(f"Assets folder ready: {ASSETS_FOLDER}/")
        print(f"Camera roll folder ready: {CAMERA_ROLL_FOLDER}/")

    def scan_existing_images(self):
        """Scan assets folder for existing images and categorize them"""
        self.all_images = []
        self.catapi_images = []
        self.user_images = []
        self.camera_roll_images = []
        self.special_image = None

        # Get all image files in assets folder (main folder)
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        for ext in image_extensions:
            for filepath in glob.glob(os.path.join(ASSETS_FOLDER, ext)):
                filename = os.path.basename(filepath)

                # Check if it's the special image
                if filepath == SPECIAL_IMAGE_PATH:
                    self.special_image = filepath
                    continue

                # Check if it's from The Cat API (our naming convention)
                if filename.startswith('catapi_'):
                    self.catapi_images.append(filepath)
                else:
                    # It's a user-added image
                    self.user_images.append(filepath)

                self.all_images.append(filepath)

        # Get all images from camera roll folder
        for ext in image_extensions:
            for filepath in glob.glob(os.path.join(CAMERA_ROLL_FOLDER, ext)):
                self.camera_roll_images.append(filepath)
                self.all_images.append(filepath)

        print(f"Found images: {len(self.user_images)} user images, {len(self.catapi_images)} Cat API images, {len(self.camera_roll_images)} camera roll images")
        if self.special_image:
            print("Special 'MAN' image found!")

    def calculate_image_distribution(self):
        """Calculate how many Cat API images we need for balanced distribution"""
        # Reserve percentage for special image
        available_percentage = 100.0 - SPECIAL_IMAGE_CHANCE

        # If we have user images, they get equal share with Cat API images
        total_user_images = len(self.user_images) + len(self.camera_roll_images)

        if total_user_images == 0:
            # No user images, all available percentage goes to Cat API
            needed_catapi_images = 100  # Default to 100 Cat API images
        else:
            # Each image should get equal percentage
            # If we want each image to have ~1% chance:
            target_percentage_per_image = 1.0

            # Calculate how many Cat API images we need
            # Total images = user_images + catapi_images
            # Each gets: available_percentage / total_images

            # If user images exist, balance so each image gets roughly equal chance
            if available_percentage / (total_user_images + 1) >= 0.5:
                # We can add Cat API images while keeping reasonable percentages
                needed_catapi_images = min(100, max(1, int(available_percentage - total_user_images)))
            else:
                # Too many user images, use minimal Cat API images
                needed_catapi_images = max(1, int(available_percentage * 0.1))

        return needed_catapi_images

    async def rebalance_images(self):
        """Remove old Cat API images and download new ones to balance percentages"""
        needed_catapi_images = self.calculate_image_distribution()
        current_catapi_images = len(self.catapi_images)

        print(f"Current Cat API images: {current_catapi_images}")
        print(f"Needed Cat API images: {needed_catapi_images}")

        # Remove existing Cat API images if we have too many or need to refresh
        if current_catapi_images != needed_catapi_images:
            print("Removing old Cat API images...")
            for img_path in self.catapi_images:
                try:
                    os.remove(img_path)
                    print(f"Removed: {os.path.basename(img_path)}")
                except Exception as e:
                    print(f"Failed to remove {img_path}: {e}")

            self.catapi_images.clear()

        # Download new Cat API images
        if needed_catapi_images > 0:
            await self.download_cat_images(needed_catapi_images)

    async def download_cat_images(self, count):
        """Download specified number of cat images from The Cat API"""
        print(f"Downloading {count} cat images from The Cat API...")

        async with aiohttp.ClientSession() as session:
            for i in range(count):
                try:
                    # Get random cat image data from API
                    async with session.get("https://api.thecatapi.com/v1/images/search") as response:
                        if response.status == 200:
                            cat_data = await response.json()
                            image_url = cat_data[0]['url']
                            image_id = cat_data[0]['id']

                            # Determine file extension
                            file_extension = image_url.split('.')[-1].lower()
                            if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                file_extension = 'jpg'

                            # Download the actual image with our naming convention
                            async with session.get(image_url) as img_response:
                                if img_response.status == 200:
                                    filename = f"catapi_{i+1:03d}_{image_id}.{file_extension}"
                                    filepath = os.path.join(ASSETS_FOLDER, filename)

                                    # Save image
                                    async with aiofiles.open(filepath, 'wb') as f:
                                        await f.write(await img_response.read())

                                    self.catapi_images.append(filepath)
                                    print(f"Downloaded {i+1}/{count}: {filename}")

                                    # Small delay to be respectful
                                    await asyncio.sleep(0.1)

                except Exception as e:
                    print(f"Failed to download image {i+1}: {e}")
                    continue

        print(f"Download complete! {len(self.catapi_images)} Cat API images ready.")

    def get_image_stats(self):
        """Get current image distribution statistics"""
        total_regular_images = len(self.all_images)

        if total_regular_images == 0:
            return {
                'total_images': 0,
                'user_images': 0,
                'catapi_images': 0,
                'special_image': bool(self.special_image),
                'percentage_per_regular': 0,
                'special_percentage': SPECIAL_IMAGE_CHANCE
            }

        available_percentage = 100.0 - SPECIAL_IMAGE_CHANCE
        percentage_per_regular = available_percentage / total_regular_images

        return {
            'total_images': total_regular_images,
            'user_images': len(self.user_images),
            'camera_roll_images': len(self.camera_roll_images),
            'catapi_images': len(self.catapi_images),
            'special_image': bool(self.special_image),
            'percentage_per_regular': percentage_per_regular,
            'special_percentage': SPECIAL_IMAGE_CHANCE
        }

    def get_random_image(self):
        """Get a random image with weighted probability"""
        # Generate random number from 1 to 1000
        roll = random.randint(1, 1000)

        # 1 in 1000 chance for special image (0.1%)
        if roll == 1 and self.special_image and os.path.exists(self.special_image):
            return self.special_image, "special"

        # Otherwise, return random image from all available images
        if self.all_images:
            selected_image = random.choice(self.all_images)

            # Determine image type
            if selected_image in self.catapi_images:
                return selected_image, "catapi"
            elif selected_image in self.camera_roll_images:
                return selected_image, "camera_roll"
            else:
                return selected_image, "user"

        return None, None


ASSETS_FOLDER = "assets"
CAMERA_ROLL_FOLDER = os.path.join(ASSETS_FOLDER, "camera_roll")
SPECIAL_IMAGE_PATH = os.path.join(ASSETS_FOLDER, "man_horse.jpg")