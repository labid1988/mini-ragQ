from fastapi import APIRouter, Depends, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest

from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk

from models.ChunkModel import ChunkModel


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

# @data_router.post("/upload/{project_id}")
# async def upload_data(request: Request, project_id: str, file: UploadFile,
#                       app_settings: Settings = Depends(get_settings)):
    
#     proejct_model =ProjectModel(
#         db_client=request.app.db_client
#     )
#     project = await proejct_model.get_project_or_create_one(
#         project_id=project_id
#     )

#     data_controller =DataController()
    
#     is_valid, message = data_controller.validate_uploaded(file=file)
    
#     if not is_valid:
#         raise HTTPException(status_code=400, detail=str(message))

#     project_dir_path = ProjectController().get_project_path(project_id=project_id)
#     file_path, file_id = data_controller.generate_unique_filename(
#         orig_file_name=file.filename,
#         project_id=project_id)

#      #os.path.join(project_dir_path, file.filename)
#     try:
#         async with aiofiles.open(file_path, "wb") as f:
#             while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
#                 await f.write(chunk)
#     except Exception as e:

#         logger.error(f"Error while uploading file: {e}")

#         return JSONResponse(content={
#         "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
#         }
#         )
#     return JSONResponse(
#         content={
#         "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
#         "file_id": file_id,
#         #"project_id": str(project_id)
#     })

# @data_router.post("/process/{project_id}")
# async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
#     file_id = process_request.file_id
#     chunk_size= process_request.chunk_size
#     overlap_size = process_request.overlap_size

#     proejct_model =ProjectModel(
#         db_client= request.app.db_client
#     )
#     project = await proejct_model.get_project_or_create_one(
#         project_id=project_id
#     )

#     process_controller = ProcessController(project_id=project_id)
#     file_content=process_controller.get_file_content(file_id=file_id)
#     file_chunks = process_controller.process_file_content(
#         file_content=file_content,
#         file_id=file_id,
#         chunk_size=chunk_size,
#         overlap_size=overlap_size
#     )


#     if file_chunks is None or len(file_chunks)==0:
#         return JSONResponse(content={
#         "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
#         })
    
#     file_chunks_records =[
#         DataChunk(
#             chunk_text=chunk.page_content,
#             chunk_metadata=chunk.metadata,
#             chunk_order=i+1,
#             chunk_project_id= project.id,
#         )
#         for i, chunk in enumerate(file_chunks)
        
#     ]
#     chunk_model =ChunkModel(
#             db_client=request.app.db_client
#         )
#     no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
#     return no_records


@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):

    data_controller = DataController()
    is_valid, message = data_controller.validate_uploaded(file=file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=str(message))

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
        )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    file_path, file_id = data_controller.generate_unique_filename(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value})

    return JSONResponse(content={
        "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
        "file_id": file_id,
    })


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset= process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client) 
    
    project = await project_model.get_project_or_create_one(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    if not file_chunks:
        return JSONResponse(content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value})

    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
        )
    
    if do_reset == 1:
        _= await chunk_model.delete_chunks_by_project_id(
            project_id = project.id
            )

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)  # ✅ await
    
    return JSONResponse(
        content={"signal": ResponseSignal.PROCESSING_SUCCESS.value,
                    "inserted_chunks": no_records
        })