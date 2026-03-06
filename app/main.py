import asyncio
import os
import subprocess
import sys
from typing import List

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
from openpyxl import load_workbook
from sqlalchemy import select
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from app.dependencies import SessionDependence
from app.models.data import ParseJob, ParseStatus
from app.parser.paths import STORAGE_DIR, XLSX_PATH, OUTPUT_PATH
from app.schemas import ParseJobSchema
from app.utils.database.seed import init_db
from app.utils.database.stats import get_all_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield
    # shutdown (пока ничего)

app = FastAPI(lifespan=lifespan)

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/excel/upload")
async def upload_excel(file: UploadFile = File(...)):
    # --- проверка расширения ---
    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Файл должен быть Excel (.xlsx/.xls)")

    # --- проверка content-type ---
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Неверный тип файла")

    # --- создаём папку если нет ---
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # --- сохраняем (перезаписываем) ---
    with XLSX_PATH.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    await file.close()

    return {"status": "ok", "filename": XLSX_PATH.name}


@app.get("/excel/download")
async def download_result(db: SessionDependence):

    # --- проверяем статусы ---
    result = await db.execute(select(ParseJob.status))
    statuses = result.scalars().all()

    if not statuses:
        raise HTTPException(404, "Статистика не найдена")

    # если хоть один НЕ created → файл ещё не готов
    if any(status != ParseStatus.created for status in statuses):
        raise HTTPException(
            status_code=409,
            detail="Файл ещё не сформирован",
        )

    # --- проверяем существование файла ---
    if not OUTPUT_PATH.exists():
        raise HTTPException(404, "Файл результата не найден")

    # --- отдаём файл ---
    return FileResponse(
        OUTPUT_PATH,
        filename="result.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )

@app.post("/parser/start")
async def start_parser(db: SessionDependence):

    # --- 0) проверяем что source.xlsx существует ---
    if not XLSX_PATH.exists():
        raise HTTPException(
            status_code=400,
            detail="Excel файл не загружен"
        )

    # --- 0.1) проверяем что файл не пустой ---
    if XLSX_PATH.stat().st_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Excel файл пустой"
        )

    # --- 0.2) проверяем что это валидный Excel ---
    try:
        load_workbook(XLSX_PATH, read_only=True)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Файл повреждён или не является Excel"
        )

    # --- 1) проверка что нет running ---
    running = await db.execute(
        select(ParseJob.id)
        .where(ParseJob.status == ParseStatus.running)
        .limit(1)
    )

    if running.scalar_one_or_none():
        raise HTTPException(409, "Парсер уже выполняется")

    # --- 2) каталог под логи ---
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    log_path = STORAGE_DIR / "parser_process.log"

    # --- 3) запуск процесса ---
    cmd = [sys.executable, "-u", "-m", "app.parser.runner"]

    with log_path.open("ab") as log_file:
        subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).resolve().parent.parent),
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
            env=os.environ.copy(),
        )

    return {"status": "started"}

@app.get("/parser/status", response_model=List[ParseJobSchema])
async def status_parser(db: SessionDependence):
    jobs = await get_all_jobs(db)
    return jobs


templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def parser_page(request: Request):
    return templates.TemplateResponse(
        "parser_page.html",
        {"request": request}
    )