"""
Transcript Data Processing Controller

Main processor for multi-page transcript extraction with context management,
data consolidation, validation, and quality assurance.
"""

import logging
from typing import Dict, List, Any

from .pdf_converter import PDFToImageConverter
from .gpt_extractor import GPTVisionExtractor

logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """
    Main processor for multi-page transcript extraction with context management.
    Handles page consolidation, data validation, and quality assurance.
    """
    
    def __init__(self, pdf_converter: PDFToImageConverter, gpt_extractor: GPTVisionExtractor):
        """
        Initialize transcript processor with required components.
        
        Args:
            pdf_converter: PDF to image converter instance
            gpt_extractor: GPT Vision extractor instance
        """
        self.pdf_converter = pdf_converter
        self.gpt_extractor = gpt_extractor
        logger.info("Transcript processor initialized")
    
    def consolidate_page_data(self, page_extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate data from multiple pages into a single comprehensive record.
        
        Args:
            page_extractions: List of extracted data from each page
            
        Returns:
            Consolidated transcript data
        """
        try:
            consolidated = {
                "student_information": {},
                "institution_information": {},
                "gpa_summary_info": {},
                "degree_information": {},
                "honors_and_awards": [],
                "transfer_credits": {},
                "transcript_totals_info": {},
                "academic_records_info": []
            }
            
            logger.info(f"Consolidating data from {len(page_extractions)} pages")
            
            for page_data in page_extractions:
                if not page_data:
                    continue
                
                # Consolidate single-value sections (take first non-null value)
                for section in ["student_information", "institution_information", 
                               "gpa_summary_info", "degree_information", 
                               "transfer_credits", "transcript_totals_info"]:
                    if section in page_data and page_data[section]:
                        for key, value in page_data[section].items():
                            if value is not None and (key not in consolidated[section] or 
                                                     consolidated[section][key] is None):
                                consolidated[section][key] = value
                
                # Consolidate array sections (append all entries)
                if "academic_records_info" in page_data and page_data["academic_records_info"]:
                    consolidated["academic_records_info"].extend(page_data["academic_records_info"])
                
                if "honors_and_awards" in page_data and page_data["honors_and_awards"]:
                    consolidated["honors_and_awards"].extend(page_data["honors_and_awards"])
            
            # Remove duplicate academic records using Course ID + Term key
            seen_courses = set()
            unique_records = []
            for record in consolidated["academic_records_info"]:
                # Updated deduplication logic: Course ID + Term
                course_key = f"{record.get('course_id', '')}-{record.get('year_term', '')}"
                if course_key not in seen_courses:
                    seen_courses.add(course_key)
                    unique_records.append(record)
                else:
                    logger.debug(f"Duplicate course entry removed: {course_key}")
            
            consolidated["academic_records_info"] = unique_records
            
            logger.info(f"Consolidated {len(unique_records)} unique academic records")
            return consolidated
            
        except Exception as e:
            logger.error(f"Error consolidating page data: {str(e)}")
            raise
    
    def calculate_verification_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate verification metrics for data quality assurance.
        
        Args:
            data: Consolidated transcript data
            
        Returns:
            Verification metrics dictionary
        """
        try:
            metrics = {
                "total_courses": len(data.get("academic_records_info", [])),
                "total_credits_calculated": 0,
                "average_grade": None,
                "gpa_consistency_check": False,
                "data_completeness_score": 0,
                "unique_terms": 0,
                "course_distribution": {}
            }
            
            # Calculate total credits from course records
            academic_records = data.get("academic_records_info", [])
            if academic_records:
                total_credits = sum(float(record.get("credits_earned", 0) or 0) 
                                   for record in academic_records)
                metrics["total_credits_calculated"] = total_credits
                
                # Calculate unique terms
                unique_terms = set(record.get("year_term", "") for record in academic_records)
                metrics["unique_terms"] = len(unique_terms)
                
                # Calculate course distribution by level
                course_levels = {}
                for record in academic_records:
                    level = record.get("course_level", "Unknown")
                    course_levels[level] = course_levels.get(level, 0) + 1
                metrics["course_distribution"] = course_levels
                
                # Check GPA consistency
                transcript_totals = data.get("transcript_totals_info", {})
                reported_credits = float(transcript_totals.get("overall_earned_hours", 0) or 0)
                
                if abs(total_credits - reported_credits) < 0.5:  # Allow small rounding differences
                    metrics["gpa_consistency_check"] = True
                    logger.info("GPA consistency check passed")
                else:
                    logger.warning(f"GPA inconsistency: calculated {total_credits}, reported {reported_credits}")
            
            # Calculate data completeness score
            total_fields = 0
            completed_fields = 0
            
            for section_name, section_data in data.items():
                if isinstance(section_data, dict):
                    for value in section_data.values():
                        total_fields += 1
                        if value is not None and value != "":
                            completed_fields += 1
                elif isinstance(section_data, list) and section_data:
                    total_fields += 1
                    completed_fields += 1
            
            if total_fields > 0:
                metrics["data_completeness_score"] = round((completed_fields / total_fields) * 100, 2)
            
            logger.info(f"Verification metrics calculated: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating verification metrics: {str(e)}")
            return {}
    
    def validate_academic_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform academic integrity validation checks.
        
        Args:
            data: Consolidated transcript data
            
        Returns:
            Validation results dictionary
        """
        try:
            validation = {
                "credit_calculation_valid": False,
                "gpa_calculation_valid": False,
                "course_sequence_valid": True,
                "duplicate_courses_found": False,
                "warnings": []
            }
            
            academic_records = data.get("academic_records_info", [])
            
            # Check for duplicate courses (same course ID and term)
            course_terms = set()
            for record in academic_records:
                course_term = f"{record.get('course_id', '')}-{record.get('year_term', '')}"
                if course_term in course_terms:
                    validation["duplicate_courses_found"] = True
                    validation["warnings"].append(f"Duplicate course found: {course_term}")
                course_terms.add(course_term)
            
            # Validate credit calculations
            calculated_credits = sum(float(record.get("credits_earned", 0) or 0) 
                                   for record in academic_records)
            transcript_totals = data.get("transcript_totals_info", {})
            reported_credits = float(transcript_totals.get("overall_earned_hours", 0) or 0)
            
            if abs(calculated_credits - reported_credits) < 1.0:
                validation["credit_calculation_valid"] = True
            else:
                validation["warnings"].append(
                    f"Credit mismatch: calculated {calculated_credits}, reported {reported_credits}"
                )
            
            logger.info(f"Academic integrity validation completed: {len(validation['warnings'])} warnings")
            return validation
            
        except Exception as e:
            logger.error(f"Error in academic integrity validation: {str(e)}")
            return {"error": str(e)}
    
    def process_transcript(self, pdf_path: str) -> Dict[str, Any]:
        """
        Complete transcript processing pipeline.
        
        Args:
            pdf_path: Path to transcript PDF file
            
        Returns:
            Processed transcript data with verification metrics
        """
        try:
            logger.info(f"Starting transcript processing: {pdf_path}")
            
            # Step 1: Convert PDF to images
            logger.info("Step 1: Converting PDF to images")
            image_paths = self.pdf_converter.convert_pdf_to_images(pdf_path)
            total_pages = len(image_paths)
            
            # Step 2: Extract data from each page
            logger.info(f"Step 2: Extracting data from {total_pages} pages")
            page_extractions = []
            
            for i, image_path in enumerate(image_paths, 1):
                try:
                    page_data = self.gpt_extractor.extract_from_image(
                        image_path, i, total_pages, self.pdf_converter
                    )
                    
                    if self.gpt_extractor.validate_extraction(page_data):
                        page_extractions.append(page_data)
                        logger.info(f"Successfully processed page {i}")
                    else:
                        logger.warning(f"Validation failed for page {i}")
                        page_extractions.append({})
                        
                except Exception as e:
                    logger.error(f"Failed to process page {i}: {str(e)}")
                    page_extractions.append({})
            
            # Step 3: Consolidate multi-page data
            logger.info("Step 3: Consolidating multi-page data")
            consolidated_data = self.consolidate_page_data(page_extractions)
            
            # Step 4: Calculate verification metrics
            logger.info("Step 4: Calculating verification metrics")
            verification_metrics = self.calculate_verification_metrics(consolidated_data)
            
            # Step 5: Academic integrity validation
            logger.info("Step 5: Academic integrity validation")
            integrity_validation = self.validate_academic_integrity(consolidated_data)
            
            # Step 6: Prepare final output
            final_result = {
                "transcript_data": consolidated_data,
                "processing_metadata": {
                    "total_pages": total_pages,
                    "pages_processed": len([p for p in page_extractions if p]),
                    "verification_metrics": verification_metrics,
                    "integrity_validation": integrity_validation,
                    "deduplication_method": "course_id_plus_term"
                }
            }
            
            logger.info("Transcript processing completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Transcript processing failed: {str(e)}")
            raise