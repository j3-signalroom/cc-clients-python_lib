# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2025-03-21T21:21:27+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, constr

from ...ListMeta import ListMeta
from ...ObjectMeta import ObjectMeta


class ApiVersion(Enum):
    iam_v2_sso = 'iam.v2/sso'


class Kind(Enum):
    group_mapping = 'GroupMapping'


class Metadata(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/iam.v2/sso/group-mappings/gm-12345'],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/group-mapping=gm-12345'
        ],
    )


class GroupMapping(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: Optional[ApiVersion] = Field(
        None,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: Optional[Kind] = Field(
        None, description='Kind defines the object this REST resource represents.'
    )
    id: Optional[constr(max_length=255)] = Field(
        None,
        description='ID is the "natural identifier" for an object within its scope/namespace; it is normally unique across time but not space. That is, you can assume that the ID will not be reclaimed and reused after an object is deleted ("time"); however, it may collide with IDs for other object `kinds` or objects of the same `kind` within a different scope/namespace ("space").',
        examples=['dlz-f3a90de'],
    )
    metadata: Optional[Metadata] = None
    display_name: Optional[str] = Field(
        None,
        description='The name of the group mapping.',
        examples=['Application Developers'],
    )
    description: Optional[str] = Field(
        None,
        description='A description explaining the purpose and use of the group mapping.',
        examples=['Admin access to production environment for Engineering'],
    )
    filter: Optional[constr(max_length=300)] = Field(
        None,
        description='A single group identifier or a condition based on [supported CEL operators](https://docs.confluent.io/cloud/current/access-management/authenticate/sso/group-mapping/overview.html#supported-cel-operators-for-group-mapping) that defines which groups are included.',
        examples=['"kafka" in groups && "all" in groups || "everyone" in groups'],
    )
    principal: Optional[str] = Field(
        None,
        description='The unique federated identity associated with this group mapping.',
        examples=['group-a1b2'],
    )
    state: Optional[str] = Field(
        None,
        description='The current state of the group mapping.',
        examples=['ENABLED'],
    )


class Kind1Model(Enum):
    group_mapping_list = 'GroupMappingList'


class Metadata1Model(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/iam.v2/sso/group-mappings']
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/iam.v2/sso/group-mappings?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/iam.v2/sso/group-mappings?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/iam.v2/sso/group-mappings?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class GroupMappingList(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: ApiVersion = Field(
        ...,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: Kind1Model = Field(
        ..., description='Kind defines the object this REST resource represents.'
    )
    metadata: Metadata1Model
    data: List[GroupMapping] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )
