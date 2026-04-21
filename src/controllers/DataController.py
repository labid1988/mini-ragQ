# from .BaseController import BaseController
# from fastapi import UploadFile

# class DataController(BaseController):

#     def __init__(self):
#         super().__init__()
#         self.size_scale = 1048576

#     def validation_upload_file(self, file: UploadFile):
#         if file.content_type not in app_settings.allowed_types:

#             return false

#         if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale :
#             return false

from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):

    def __init__(self):
        super().__init__()  # ← charge déjà self.app_settings
        self.size_scale = 1048576  # 1 MB en bytes

    def validate_uploaded(self, file: UploadFile):
        if file.content_type not in self.app_settings.allowed_types:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value #f"Type non autorisé : {file.content_type}"

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value #f"Fichier trop volumineux (max {self.app_settings.FILE_MAX_SIZE} MB)"

        return True, ResponseSignal.FILE_UPLOAD_SUCCESS.value #"Fichier valide"
    
    def generate_unique_filename(self,orig_file_name:str, project_id:str):
        random_filename= self.generate_random_string()
        project_path= ProjectController().get_project_path(project_id=project_id)

        cleand_file_name = self.get_clean_file_name(
            orig_file_name=orig_file_name
        )

        new_file_path= os.path.join(
            project_path,
            random_filename +"_"+ cleand_file_name

        )
        while os.path.exists(new_file_path):
            random_filename=self.generate_random_string()
            new_file_path= os.path.join(
            project_path,
            random_filename +"_"+ cleand_file_name

        )
        return new_file_path, random_filename +"_"+ cleand_file_name

    def get_clean_file_name(self, orig_file_name:str):
        cleand_file_name=re.sub(r'[^\w.]', '', orig_file_name.strip())

        cleand_file_name = cleand_file_name.replace(" ","-")

        return cleand_file_name