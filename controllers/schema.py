"""
Transcript Data Schema Definitions

Comprehensive JSON schema for US academic transcript extraction
covering all university requirements and validation structures.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Comprehensive JSON Schema for US Academic Transcript Extraction
TRANSCRIPT_SCHEMA = {
    "student_information": {
        "student_name": "string",
        "birth_date": "string",
        "student_id": "string", 
        "grade": "string",
        "gender": "string",
        "mailing_address": "string",
        "entry_date": "string",
        "student_phone": "string",
        "graduation_date": "string",
        "email": "string",
        "citizenship_status": "string",
        "previous_name": "string"
    },
    "institution_information": {
        "institution_name": "string",
        "address": "string",
        "phone": "string", 
        "transcript_type": "string",
        "zip_code": "string",
        "state": "string",
        "city": "string",
        "institution_code": "string",
        "registrar_signature": "string",
        "seal_present": "boolean",
        "transcript_issue_date": "string",
        "transcript_request_date": "string"
    },
    "gpa_summary_info": {
        "unweighted_gpa": "number",
        "weighted_gpa": "number",
        "unweighted_classrank": "string", 
        "weighted_classrank": "string",
        "gpa_scale": "string",
        "quality_points": "number",
        "term_gpa_history": "array"
    },
    "degree_information": {
        "degree_awarded": "string",
        "degree_date": "string",
        "major": "array",
        "minor": "array", 
        "concentration": "array",
        "academic_program": "string",
        "graduation_honors": "string"
    },
    "honors_and_awards": [
        {
            "honor_name": "string",
            "award_date": "string",
            "description": "string",
            "gpa_requirement": "string"
        }
    ],
    "transfer_credits": {
        "transfer_institutions": "array",
        "transfer_credits_accepted": "number",
        "transfer_gpa": "number",
        "transfer_courses": "array"
    },
    "transcript_totals_info": {
        "total_institution_earned_hours": "number",
        "total_transfer_earned_hours": "number",
        "overall_earned_hours": "number", 
        "overall_gpa": "number",
        "total_attempted_hours": "number",
        "academic_standing": "string",
        "probation_status": "string",
        "honors_eligibility": "boolean"
    },
    "academic_records_info": [
        {
            "year_term": "string",
            "course_id": "string",
            "course_name": "string",
            "grades": "string",
            "credits_earned": "number",
            "credits_attempted": "number", 
            "marks": "number",
            "grade_points": "number",
            "course_level": "string",
            "department": "string",
            "instructor": "string",
            "repeat_indicator": "string"
        }
    ]
}


def validate_schema_compliance(data: Dict[str, Any]) -> bool:
    """
    Validate extracted data for schema compliance.
    
    Args:
        data: Extracted data dictionary
        
    Returns:
        True if validation passes
    """
    try:
        # Check required top-level keys
        required_keys = list(TRANSCRIPT_SCHEMA.keys())
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            logger.warning(f"Missing required keys: {missing_keys}")
            return False
        
        # Validate academic records structure
        if 'academic_records_info' in data and data['academic_records_info']:
            for record in data['academic_records_info']:
                if not isinstance(record, dict):
                    logger.warning("Invalid academic record structure")
                    return False
        
        logger.info("Schema validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Schema validation error: {str(e)}")
        return False


def get_schema_summary() -> Dict[str, int]:
    """
    Get summary statistics about the schema structure.
    
    Returns:
        Dictionary with schema statistics
    """
    stats = {
        "total_sections": len(TRANSCRIPT_SCHEMA),
        "student_fields": len(TRANSCRIPT_SCHEMA["student_information"]),
        "institution_fields": len(TRANSCRIPT_SCHEMA["institution_information"]),
        "gpa_fields": len(TRANSCRIPT_SCHEMA["gpa_summary_info"]),
        "academic_record_fields": len(TRANSCRIPT_SCHEMA["academic_records_info"][0])
    }
    return stats