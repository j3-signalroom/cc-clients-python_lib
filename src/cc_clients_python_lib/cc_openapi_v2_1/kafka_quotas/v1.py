# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2025-03-21T21:21:27+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, constr

from .. import EnvScopedObjectReference, GlobalObjectReference
from ..ListMeta import ListMeta
from ..ObjectMeta import ObjectMeta


class ApiVersion(Enum):
    kafka_quotas_v1 = 'kafka-quotas/v1'


class Kind(Enum):
    client_quota = 'ClientQuota'


class Metadata(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/kafka-quotas/v1/client-quotas/cq-12345'],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/client-quota=cq-12345'
        ],
    )


class Throughput(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    ingress_byte_rate: str = Field(
        ...,
        description='Ingress throughput limit for principals specified in bytes per second.',
        examples=['5'],
    )
    egress_byte_rate: str = Field(
        ...,
        description='Egress throughput limit for principals specified in bytes per second.',
        examples=['5'],
    )


class Kind1Model(Enum):
    client_quota_list = 'ClientQuotaList'


class Metadata1Model(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/kafka-quotas/v1/client-quotas']
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/kafka-quotas/v1/client-quotas?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/kafka-quotas/v1/client-quotas?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/kafka-quotas/v1/client-quotas?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class ClientQuotaSpec(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    display_name: Optional[str] = Field(
        None, description='The name of the client quota.', examples=['QuotaForSA1']
    )
    description: Optional[str] = Field(
        None,
        description='A human readable description for the client quota.',
        examples=[
            'This quota defines limits on how much the target principals can use cluster lkc-xxxxx'
        ],
    )
    throughput: Optional[Throughput] = Field(
        None, description='Throughput for the client quota.'
    )
    cluster: Optional[EnvScopedObjectReference] = Field(
        None,
        description='The ID of the Dedicated Kafka cluster where the client quota is applied.\n',
    )
    principals: Optional[List[GlobalObjectReference]] = Field(
        None,
        description='A list of principals to apply a client quota to.\nUse `"<default>"` to apply a client quota to all service accounts\n(see [Control application usage with Client Quotas](https://docs.confluent.io/cloud/current/clusters/client-quotas.html#control-application-usage-with-client-quotas) for more details).\n',
        min_length=1,
    )
    environment: Optional[GlobalObjectReference] = Field(
        None, description='The environment to which this belongs.'
    )


class ClientQuotaSpecUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    display_name: Optional[str] = Field(
        None, description='The name of the client quota.', examples=['QuotaForSA1']
    )
    description: Optional[str] = Field(
        None,
        description='A human readable description for the client quota.',
        examples=[
            'This quota defines limits on how much the target principals can use cluster lkc-xxxxx'
        ],
    )
    throughput: Optional[Throughput] = Field(
        None, description='Throughput for the client quota.'
    )
    principals: Optional[List[GlobalObjectReference]] = Field(
        None,
        description='A list of principals to apply a client quota to.\nUse `"<default>"` to apply a client quota to all service accounts\n(see [Control application usage with Client Quotas](https://docs.confluent.io/cloud/current/clusters/client-quotas.html#control-application-usage-with-client-quotas) for more details).\n',
        min_length=1,
    )


class Kind1Model1(Enum):
    client_quota = 'ClientQuota'


class Metadata1Model1(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/kafka-quotas/v1/client-quotas/cq-12345'],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/client-quota=cq-12345'
        ],
    )


class ClientQuotaUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: Optional[ApiVersion] = Field(
        None,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: Optional[Kind1Model1] = Field(
        None, description='Kind defines the object this REST resource represents.'
    )
    id: Optional[constr(max_length=255)] = Field(
        None,
        description='ID is the "natural identifier" for an object within its scope/namespace; it is normally unique across time but not space. That is, you can assume that the ID will not be reclaimed and reused after an object is deleted ("time"); however, it may collide with IDs for other object `kinds` or objects of the same `kind` within a different scope/namespace ("space").',
        examples=['dlz-f3a90de'],
    )
    metadata: Optional[Metadata1Model1] = None
    spec: Optional[ClientQuotaSpecUpdate] = None


class ClientQuota(BaseModel):
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
    spec: Optional[ClientQuotaSpec] = None


class Datum(ClientQuota):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    spec: Dict[str, Any]


class ClientQuotaList(BaseModel):
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
    data: List[Datum] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )
