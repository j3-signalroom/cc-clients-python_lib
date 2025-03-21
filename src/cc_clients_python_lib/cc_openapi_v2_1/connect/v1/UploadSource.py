# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2025-03-21T21:21:27+00:00

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PresignedUrl(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    location: Literal['PRESIGNED_URL_LOCATION'] = Field(
        ...,
        description='Location of the Custom Connector Plugin source.\n',
        examples=['PRESIGNED_URL_LOCATION'],
    )
    upload_id: str = Field(
        ...,
        description='Upload ID returned by the `/presigned-upload-url` API. This field returns an empty string in all responses.',
        examples=['e53bb2e8-8de3-49fa-9fb1-4e3fd9a16b66'],
    )
