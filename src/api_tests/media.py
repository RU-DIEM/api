from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

########################################################################################

PDF: bytes = (
    b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
)

########################################################################################


def image_bytes(fmt: str = "PNG", size: tuple[int, int] = (256, 128)) -> bytes:
    buffer = BytesIO()

    Image.new("RGB", size, color=(228, 100, 37)).save(buffer, format=fmt)

    return buffer.getvalue()


def upload(
    content: bytes,
    *,
    content_type: str = "image/png",
    name: str = "upload.png",
) -> SimpleUploadedFile:
    return SimpleUploadedFile(content=content, content_type=content_type, name=name)
