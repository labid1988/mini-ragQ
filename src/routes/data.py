from fastapi import APIRouter, Depends, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest

from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk, Asset
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


# =========================
# UPLOAD
# =========================
@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):

    data_controller = DataController()
    is_valid, message = data_controller.validate_uploaded(file=file)

    if not is_valid:
        raise HTTPException(status_code=400, detail=str(message))

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

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
        return JSONResponse(content={
            "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
        })

    # Store asset in DB
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(content={
        "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
        "file_id": str(asset_record.id),
    })


# =========================
# PROCESS
# =========================
@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest
):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    # Project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # Asset model (FIX: toujours créé avant usage)
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )
    project_files_ids={}


    # =========================
    # Récupérer les fichiers
    # =========================
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id, 
            asset_name=process_request.file_id
        )
        if asset_record is None:
            return JSONResponse(content={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "signal": ResponseSignal.FILE_ID_ERROR.value
            })

        project_files_ids = {
            record.id:record.asset_name
            for record in project_file
          
        }
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value
        )

        project_files_ids = {
            record.id:record.asset_name
            for record in project_files
        }

    # Vérification
    if len(project_files_ids) == 0:
        return JSONResponse(content={
            "status_code": status.HTTP_400_BAD_REQUEST,
            "signal": ResponseSignal.NO_FILES_ERROR.value
        })

    # Controllers
    process_controller = ProcessController(project_id=project_id)

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    # Reset si demandé
    if do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    # =========================
    # Traitement
    # =========================
    no_records = 0
    no_files = 0

    for id,file_id in project_files_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if not file_content:
            logger.error(f"Failed to load content for file_id: {file_id}")
            continue  # Skip to the next file

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if not file_chunks:
            return JSONResponse(content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            })

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_asset_id=id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(
            chunks=file_chunks_records
        )

        no_files += 1

    return JSONResponse(content={
        "signal": ResponseSignal.PROCESSING_SUCCESS.value,
        "inserted_chunks": no_records,
        "processed_files": no_files
    })