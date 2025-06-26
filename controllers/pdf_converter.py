"""
PDF to Image Conversion Controller

Handles PDF document conversion to high-quality images optimized 
for GPT Vision processing with proper resolution and encoding.
"""

import os
import base64
import logging
from typing import List, Optional
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)


class PDFToImageConverter:
    """
    Converts PDF documents to high-quality images for GPT Vision processing.
    Optimized for transcript extraction with proper resolution handling.
    """
    
    def __init__(self, dpi: int = 300, format: str = 'PNG'):
        """
        Initialize converter with quality settings.
        
        Args:
            dpi: Resolution for image conversion (300 recommended for text clarity)
            format: Output image format
        """
        self.dpi = dpi
        self.format = format
        logger.info(f"PDF converter initialized with DPI: {dpi}, Format: {format}")
    
    def convert_pdf_to_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Convert PDF pages to individual images.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images (optional)
            
        Returns:
            List of image file paths
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Set output directory
            if output_dir is None:
                output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(exist_ok=True)
            
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                output_folder=str(output_dir),
                fmt=self.format.lower()
            )
            
            # Save images and collect paths
            image_paths = []
            for i, image in enumerate(images, 1):
                image_path = output_dir / f"page_{i:03d}.{self.format.lower()}"
                image.save(image_path, self.format)
                image_paths.append(str(image_path))
                logger.debug(f"Saved page {i} to: {image_path}")
            
            logger.info(f"Successfully converted {len(images)} pages to images")
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image to base64 for API transmission.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            logger.debug(f"Encoded image to base64: {image_path}")
            return encoded_string
            
        except Exception as e:
            logger.error(f"Error encoding image to base64: {str(e)}")
            raise
    
    def validate_image_quality(self, image_path: str) -> bool:
        """
        Validate image quality for text extraction.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image meets quality standards
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Check minimum resolution for text readability
                min_dimension = 800
                if width < min_dimension or height < min_dimension:
                    logger.warning(f"Image resolution too low: {width}x{height}")
                    return False
                
                # Check file size (too small might indicate poor quality)
                file_size = os.path.getsize(image_path)
                if file_size < 50000:  # 50KB minimum
                    logger.warning(f"Image file size too small: {file_size} bytes")
                    return False
                
                logger.debug(f"Image quality validation passed: {width}x{height}, {file_size} bytes")
                return True
                
        except Exception as e:
            logger.error(f"Error validating image quality: {str(e)}")
            return False