# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2025-03-21T21:21:27+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, constr

from .. import EnvScopedObjectReference, GlobalObjectReference
from ..ListMeta import ListMeta
from ..ObjectMeta import ObjectMeta


class ApiVersion(Enum):
    service_quota_v1 = 'service-quota/v1'


class Kind(Enum):
    applied_quota = 'AppliedQuota'


class Metadata(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/applied-quotas/aq-12345'
        ],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/applied-quota=aq-12345'
        ],
    )


class AppliedQuota(BaseModel):
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
    scope: Optional[str] = Field(
        None,
        description='The applied scope that this quota belongs to.',
        examples=['ORGANIZATION'],
    )
    display_name: Optional[str] = Field(
        None,
        description='A human-readable name for the quota type name.',
        examples=['Kafka Cluster Per Organization'],
    )
    default_limit: Optional[int] = Field(
        None, description='The default service quota value.\n'
    )
    applied_limit: Optional[int] = Field(
        None,
        description='The latest applied service quota value, taking into account any limit adjustments.\n',
    )
    usage: Optional[int] = Field(
        None,
        description='Show the quota usage value if the quota usage is available for this quota.\n',
    )
    user: Optional[GlobalObjectReference] = Field(
        None, description='The user associated with this object.'
    )
    organization: Optional[GlobalObjectReference] = Field(
        None,
        description='A unique organization id to associate a specific organization to this quota.',
    )
    environment: Optional[GlobalObjectReference] = Field(
        None, description='The environment ID the quota is associated with.\n'
    )
    network: Optional[EnvScopedObjectReference] = Field(
        None, description='The network ID the quota is associated with.\n'
    )
    kafka_cluster: Optional[EnvScopedObjectReference] = Field(
        None, description='The kafka cluster ID the quota is associated with.\n'
    )


class KindModel(Enum):
    scope = 'Scope'


class MetadataModel(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/service-quota/v1/scopes/s-12345']
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/scope=s-12345'
        ],
    )


class Scope(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: Optional[ApiVersion] = Field(
        None,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: Optional[KindModel] = Field(
        None, description='Kind defines the object this REST resource represents.'
    )
    id: Optional[constr(max_length=255)] = Field(
        None,
        description='ID is the "natural identifier" for an object within its scope/namespace; it is normally unique across time but not space. That is, you can assume that the ID will not be reclaimed and reused after an object is deleted ("time"); however, it may collide with IDs for other object `kinds` or objects of the same `kind` within a different scope/namespace ("space").',
        examples=['dlz-f3a90de'],
    )
    metadata: Optional[MetadataModel] = None
    description: Optional[str] = Field(
        None,
        description='the quota scope for listing quotas queries',
        examples=['ORGANIZATION scope that quotas would be applied to'],
    )


class KindModel1(Enum):
    applied_quota_list = 'AppliedQuotaList'


class MetadataModel1(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/service-quota/v1/applied-quotas']
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/applied-quotas?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/applied-quotas?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/applied-quotas?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class AppliedQuotaList(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: ApiVersion = Field(
        ...,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: KindModel1 = Field(
        ..., description='Kind defines the object this REST resource represents.'
    )
    metadata: MetadataModel1
    data: List[AppliedQuota] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )


class KindModel2(Enum):
    scope_list = 'ScopeList'


class MetadataModel2(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/service-quota/v1/scopes']
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/scopes?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/scopes?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/service-quota/v1/scopes?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class ScopeList(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: ApiVersion = Field(
        ...,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: KindModel2 = Field(
        ..., description='Kind defines the object this REST resource represents.'
    )
    metadata: MetadataModel2
    data: List[Scope] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )
