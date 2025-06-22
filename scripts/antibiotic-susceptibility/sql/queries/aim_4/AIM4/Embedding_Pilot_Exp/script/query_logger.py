import logging
from datetime import datetime
import os

def setup_logging(method = "strictest", run = "generated_question_set_1"):
    """
    Set up logging configuration to write to both file and console.
    Returns the logger instance.
    """
    # Create data directory if it doesn't exist
    os.makedirs(f"../{method}/{run}/logs", exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = f"../{method}/{run}/logs/query_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Configure logging
    logger = logging.getLogger('query_logger')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers to prevent duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    return logger

def log_original_message(logger, original_query_message):
    """Log original message"""
    logger.info("Original Message:")
    logger.info(f"original_query_message: {original_query_message}")

def log_query_parameters(logger, query_message, receiver, department, specialty):
    """Log query parameters"""
    logger.info("Query Parameters:")
    logger.info(f"query_message: {query_message}")
    logger.info(f"receiver: {receiver}")
    logger.info(f"department: {department}")
    logger.info(f"specialty: {specialty}")

def log_results(logger, results, beautiful_print_thread_func, answer_question_paired_data_dedup):
    """Log query results"""
    logger.info(f"\nNumber of results: {len(results)}")
    
    if len(results) > 0:
        for row in results:
            logger.info("##" * 40 + "START" + "##" * 40)
            # Log personalization information if available
            if 'personalization_tier' in row and 'personalized_score' in row:
                logger.info(f"[{row['personalization_tier']}] Score: {row['personalized_score']:.3f} (CosSim: {row['cosine_similarity']:.3f})")
            else:
                logger.info(f"✅ similarity: {row['cosine_similarity']:.4f}")
            
            logger.info(f"Sender: {row['Message Sender']} -> the retrieved similar message : {row['Patient Message']}")
            logger.info(f"Provider's response to this similar message: {row['Actual Response Sent to Patient']}")
            
            # Log tier information if available (either retrieval_tier or personalization_tier)
            if 'retrieval_tier' in row:
                logger.info(f"This result is from tier: {row['retrieval_tier']}")
            elif 'personalization_tier' in row:
                logger.info(f"This result is from tier: {row['personalization_tier']}")
                
            logger.info("-----------printing the whole thread-------------")
            # Get the thread output as a string and log it
            thread_output = beautiful_print_thread_func(row["Thread ID"], answer_question_paired_data_dedup)
            logger.info(thread_output)
            logger.info("##" * 40 + "END" + "##" * 40)
    else:
        logger.info("No results found matching the criteria")

def log_error(logger, error_message):
    """Log error messages"""
    logger.error(f"Error getting results: {str(error_message)}") 