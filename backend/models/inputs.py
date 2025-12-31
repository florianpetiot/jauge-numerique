from pydantic import BaseModel

class CameraInput(BaseModel):
    image_base64: str
    top_threading: float
    bottom_threading: float
    diameter_piece: float
    x_piece: float
    y_piece: float

class TransformInput(BaseModel):
    x: float
    y: float
    scale: float
    angle: float
    matrix: dict[str, float]

class DiameterInput(BaseModel):
    transform: TransformInput