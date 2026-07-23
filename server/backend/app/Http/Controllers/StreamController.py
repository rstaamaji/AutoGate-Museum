from fastapi import HTTPException
from fastapi.responses import Response

from app.Services import StreamService
from app.Services.CameraService import CameraError
import traceback


def live(direction: str):
    try:
        image_bytes = StreamService.get_snapshot(direction)
        return Response(content=image_bytes, media_type="image/jpeg")

    except CameraError as e:
        print("=" * 80)
        print(f"[STREAM ERROR {direction}]")
        print(e)
        traceback.print_exc()
        print("=" * 80)
        raise HTTPException(status_code=502, detail=str(e))

def snapshot(direction: str):
    """
    Snapshot tunggal.
    """
    try:
        image_bytes = StreamService.get_snapshot(direction)

    except CameraError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return Response(
        content=image_bytes,
        media_type="image/jpeg",
    )