import os
import tempfile

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption
from fastapi import FastAPI, UploadFile

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

app = FastAPI()


@app.post("/to_markdown/")
async def post_root(file: UploadFile):
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(temp_file_path)
        markdown = result.document.export_to_markdown()

        with open("output.md", "w") as f:
            f.write(markdown)

        return {
            "filename": file.filename,
            "markdown": markdown,
        }
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
