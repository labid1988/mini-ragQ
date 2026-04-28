from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATION_SUCCESS="file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED="file_type_not_supported"
    FILE_SIZE_EXCEEDED="file_size_exceeded"
    FILE_UPLOAD_SUCCESS="file_upload_success"
    FILE_UPLOAD_FAILED="file_upload_failed"
    PROCESSING_FAILED="Processing_failed"
    PROCESSING_SUCCESS="Processing_success"
    NO_FILES_ERROR="no_files_error"
    FILE_ID_ERROR="file_id_error"