"""
GPT Vision API Integration Controller

Handles OpenAI GPT Vision API integration for structured transcript 
data extraction with advanced prompting and error handling.
"""

import json
import logging
from typing import Dict, Any
from openai import OpenAI

from .schema import TRANSCRIPT_SCHEMA, validate_schema_compliance
from .pdf_converter import PDFToImageConverter

logger = logging.getLogger(__name__)


class GPTVisionExtractor:
    """
    Handles GPT Vision API integration for structured transcript data extraction.
    Implements best practices for multi-page document processing and context management.
    """
    
    def __init__(self, client: OpenAI, model: str = "gpt-4o", max_retries: int = 3):
        """
        Initialize GPT Vision extractor.
        
        Args:
            client: OpenAI client instance
            model: OpenAI model to use
            max_retries: Maximum retry attempts for failed extractions
        """
        self.client = client
        self.model = model
        self.max_retries = max_retries
        logger.info(f"GPT Vision extractor initialized with model: {model}")
    
    def create_extraction_prompt(self, page_number: int, total_pages: int) -> str:
        """
        Create structured prompt for transcript data extraction.
        
        Args:
            page_number: Current page number
            total_pages: Total number of pages
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are a professional document analysis system specializing in US academic transcript extraction.

TASK: Extract structured data from this academic transcript page ({page_number}/{total_pages}).

INSTRUCTIONS:
1. Extract ALL visible data that matches the provided schema categories
2. Use exact values from the document - do not infer or generate data
3. For missing fields, use null values
4. Maintain high accuracy - this is for official academic record processing
5. Pay special attention to numerical values (GPA, credits, grades)
6. Preserve exact formatting of course names and institutional information

REQUIRED JSON SCHEMA:
{json.dumps(TRANSCRIPT_SCHEMA, indent=2)}

EXTRACTION RULES:
- Student Information: Extract personal details, contact information, academic dates
- Institution Information: Extract school details, registrar information, transcript metadata
- GPA Summary: Extract all GPA calculations, class rankings, quality points
- Degree Information: Extract graduation details, majors, minors, honors
- Honors/Awards: Extract academic recognitions and achievements  
- Transfer Credits: Extract transfer institution and credit information
- Transcript Totals: Extract cumulative credit and GPA calculations
- Academic Records: Extract ALL course entries with complete details

QUALITY REQUIREMENTS:
- Ensure numerical accuracy for GPA and credit calculations
- Maintain exact spelling of names and course titles
- Extract complete date information (MM/DD/YYYY format preferred)
- Include all visible course-level details

Return ONLY valid JSON matching the exact schema structure. Do not include explanations or additional text.
"""
        return prompt
    
    def extract_from_image(self, image_path: str, page_number: int, total_pages: int, 
                          pdf_converter: PDFToImageConverter) -> Dict[str, Any]:
        """
        Extract structured data from a single transcript page image.
        
        Args:
            image_path: Path to image file
            page_number: Current page number  
            total_pages: Total pages in document
            pdf_converter: PDF converter instance for encoding
            
        Returns:
            Extracted data as dictionary
        """
        try:
            # Encode image to base64
            base64_image = pdf_converter.encode_image_to_base64(image_path)
            
            # Create extraction prompt
            prompt = self.create_extraction_prompt(page_number, total_pages)
            
            logger.info(f"Processing page {page_number}/{total_pages}: {image_path}")
            
            # Make API call with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64_image}",
                                            "detail": "high"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=4000,
                        temperature=0.1  # Low temperature for consistent extraction
                    )
                    
                    # Parse response
                    content = response.choices[0].message.content.strip()
                    
                    # Attempt to parse JSON
                    if content.startswith('```json'):
                        content = content.split('```json')[1].split('```')[0].strip()
                    elif content.startswith('```'):
                        content = content.split('```')[1].split('```')[0].strip()
                    
                    extracted_data = json.loads(content)
                    
                    logger.info(f"Successfully extracted data from page {page_number}")
                    return extracted_data
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed on attempt {attempt + 1}: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    continue
                    
                except Exception as e:
                    logger.error(f"API call failed on attempt {attempt + 1}: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    continue
            
        except Exception as e:
            logger.error(f"Failed to extract data from page {page_number}: {str(e)}")
            raise
    
    def validate_extraction(self, data: Dict[str, Any]) -> bool:
        """
        Validate extracted data for completeness and consistency.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            True if validation passes
        """
        return validate_schema_compliance(data)
    
    def get_extraction_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about the extracted data.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Statistics dictionary
        """
        try:
            stats = {
                "academic_records_count": len(data.get("academic_records_info", [])),
                "honors_count": len(data.get("honors_and_awards", [])),
                "has_student_info": bool(data.get("student_information", {}).get("student_name")),
                "has_gpa_info": bool(data.get("gpa_summary_info", {}).get("unweighted_gpa")),
                "has_institution_info": bool(data.get("institution_information", {}).get("institution_name"))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating extraction stats: {str(e)}")
            return {}