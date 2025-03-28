# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2025-03-21T21:21:27+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, List, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel, constr

from .. import GlobalObjectReference
from ..ListMeta import ListMeta
from ..ObjectMeta import ObjectMeta


class ApiVersion(Enum):
    notifications_v1 = 'notifications/v1'


class Kind(Enum):
    subscription = 'Subscription'


class Metadata(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/notifications/v1/subscriptions/s-12345'],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/subscription=s-12345'
        ],
    )


class Subscription(BaseModel):
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
    current_state: Optional[str] = Field(
        None,
        description='Denotes the state of the subscription. When the subscription is ENABLED, the user will receive\nnotification on the configured Integrations. If the subscription is DISABLED, the user will not\nrecieve any notification for the configured notification type. Note that, you cannot disable\na subscription for `REQUIRED` notification type.\n',
        examples=['ENABLED'],
    )
    notification_type: Optional[GlobalObjectReference] = Field(
        None, description='The type of notification to subscribe to.'
    )
    integrations: Optional[List[GlobalObjectReference]] = Field(
        None,
        description='Integrations to which notifications are to be sent.',
        min_length=1,
    )


class KindModel(Enum):
    integration = 'Integration'


class MetadataModel(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/notifications/v1/integrations/i-12345'],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/integration=i-12345'
        ],
    )


class KindModel1(Enum):
    notification_type = 'NotificationType'


class MetadataModel1(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/notification-types/nt-12345'
        ],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/notification-type=nt-12345'
        ],
    )


class NotificationType(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: Optional[ApiVersion] = Field(
        None,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: Optional[KindModel1] = Field(
        None, description='Kind defines the object this REST resource represents.'
    )
    id: Optional[constr(max_length=255)] = Field(
        None,
        description='ID is the "natural identifier" for an object within its scope/namespace; it is normally unique across time but not space. That is, you can assume that the ID will not be reclaimed and reused after an object is deleted ("time"); however, it may collide with IDs for other object `kinds` or objects of the same `kind` within a different scope/namespace ("space").',
        examples=['dlz-f3a90de'],
    )
    metadata: Optional[MetadataModel1] = None
    display_name: Optional[str] = Field(
        None,
        description='Human readable display name of the notification type\n',
        examples=['Cluster Shrink'],
    )
    category: Optional[str] = Field(
        None,
        description='Represents the group with which the notification is associated.\nNotifications are grouped under certain categories for better organization.\n- BILLING_LICENSING: All billing, payments or licensing related notifications are grouped here.\n- SECURITY: All Confluent Cloud and Platform security related notifications are grouped here.\n- SERVICE: All Confluent services (eg. Kafka, Schema Registry, Connect etc.) related notifications are\n  grouped here.\n- ACCOUNT: All Confluent account related notifications are grouped here.\nFor example: Billing, payment or license related notifications are grouped in BILLING_LICENSING category.\n',
        examples=['BILLING_LICENSING'],
    )
    description: Optional[str] = Field(
        None,
        description='Human readable description of the notification type\n',
        examples=['Cluster shrink operation is completed'],
    )
    subscription_priority: Optional[str] = Field(
        None,
        description="Indicates whether the notification is auto-subscribed and if the user can opt-out.\n- REQUIRED: the user is auto-subscribed to this notification and can't opt-out.\n- RECOMMENDED: the user is auto-subscribed to this notification and can opt-out.\n- OPTIONAL: the user is not auto-subscribed to this notification but can explicitly subscribe to it.\n",
        examples=['REQUIRED'],
    )
    is_included_in_plan: Optional[bool] = Field(
        None,
        description="Whether this notification is available to subscribe or not\nas per the user's current billing plan.\n",
    )
    severity: Optional[str] = Field(
        None,
        description='Severity indicates the impact of this notification.\n- CRITICAL: a high impact notification which needs immediate attention.\n- WARN: a warning notification which can be addressed now or later.\n- INFO: an informational notification.\n',
        examples=['INFO'],
    )


class KindModel2(Enum):
    slack = 'Slack'


class SlackTarget(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    kind: Literal['Slack'] = Field(
        ..., description='Integration Type', examples=['Slack']
    )
    webhook_url: AnyUrl = Field(
        ...,
        description='Slack Webhook URL for the particular Slack channel',
        examples=['https://hooks.slack.com/services/{id}/{id}/{id}'],
    )


class KindModel3(Enum):
    role_email = 'RoleEmail'


class RoleEmailTarget(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    kind: Literal['RoleEmail'] = Field(
        ..., description='Email Integration type for Role', examples=['RoleEmail']
    )
    role_name: str = Field(
        ..., description='name of the role', examples=['OrganizationAdmin']
    )


class KindModel4(Enum):
    user_email = 'UserEmail'


class UserEmailTarget(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    kind: Literal['UserEmail'] = Field(
        ..., description='Email Integration type for User', examples=['UserEmail']
    )
    user: str = Field(..., description='ID of the user', examples=['u-temp1'])


class KindModel5(Enum):
    webhook = 'Webhook'


class WebhookTarget(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    kind: Literal['Webhook'] = Field(
        ..., description='Integration Type', examples=['Webhook']
    )
    url: AnyUrl = Field(
        ...,
        description='URL endpoint for the webhook',
        examples=['https://my.webhook.url/{id}'],
    )


class KindModel6(Enum):
    ms_teams = 'MsTeams'


class MsTeamsTarget(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    kind: Literal['MsTeams'] = Field(
        ..., description='Integration Type', examples=['MsTeams']
    )
    webhook_url: AnyUrl = Field(
        ...,
        description='MS Teams Webhook URL for the particular team channel',
        examples=[
            'https://admin.webhook.office.com/webhookb2/{id}/IncomingWebhook/{id}'
        ],
    )


class Target(
    RootModel[
        Union[
            SlackTarget, RoleEmailTarget, UserEmailTarget, WebhookTarget, MsTeamsTarget
        ]
    ]
):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    root: Union[
        SlackTarget, RoleEmailTarget, UserEmailTarget, WebhookTarget, MsTeamsTarget
    ] = Field(
        ...,
        description='Target for the particular integration',
        discriminator='kind',
        examples=[
            {
                'kind': 'Slack',
                'webhook_url': 'https://hooks.slack.com/services/{id}/{id}/{id}',
            }
        ],
    )


class KindModel7(Enum):
    subscription_list = 'SubscriptionList'


class MetadataModel2(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/notifications/v1/subscriptions']
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/subscriptions?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/subscriptions?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/subscriptions?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class SubscriptionList(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: ApiVersion = Field(
        ...,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: KindModel7 = Field(
        ..., description='Kind defines the object this REST resource represents.'
    )
    metadata: MetadataModel2
    data: List[Subscription] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )


class KindModel8(Enum):
    integration_list = 'IntegrationList'


class MetadataModel3(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None, examples=['https://api.confluent.cloud/notifications/v1/integrations']
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/integrations?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/integrations?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/integrations?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class KindModel9(Enum):
    notification_type_list = 'NotificationTypeList'


class MetadataModel4(ListMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    first: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/notifications/v1/notification-types'],
    )
    last: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/notification-types?page_token=bcAOehAY8F16YD84Z1wT'
        ],
    )
    prev: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/notification-types?page_token=YIXRY97wWYmwzrax4dld'
        ],
    )
    next: Optional[Any] = Field(
        None,
        examples=[
            'https://api.confluent.cloud/notifications/v1/notification-types?page_token=UvmDWOB1iwfAIBPj6EYb'
        ],
    )


class NotificationTypeList(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: ApiVersion = Field(
        ...,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: KindModel9 = Field(
        ..., description='Kind defines the object this REST resource represents.'
    )
    metadata: MetadataModel4
    data: List[NotificationType] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )


class Kind1(Enum):
    subscription = 'Subscription'


class Metadata1(ObjectMeta):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    self: Optional[Any] = Field(
        None,
        examples=['https://api.confluent.cloud/notifications/v1/subscriptions/s-12345'],
    )
    resource_name: Optional[Any] = Field(
        None,
        examples=[
            'crn://confluent.cloud/organization=9bb441c4-edef-46ac-8a41-c49e44a3fd9a/subscription=s-12345'
        ],
    )


class SubscriptionUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: Optional[ApiVersion] = Field(
        None,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: Optional[Kind1] = Field(
        None, description='Kind defines the object this REST resource represents.'
    )
    id: Optional[constr(max_length=255)] = Field(
        None,
        description='ID is the "natural identifier" for an object within its scope/namespace; it is normally unique across time but not space. That is, you can assume that the ID will not be reclaimed and reused after an object is deleted ("time"); however, it may collide with IDs for other object `kinds` or objects of the same `kind` within a different scope/namespace ("space").',
        examples=['dlz-f3a90de'],
    )
    metadata: Optional[Metadata1] = None
    current_state: Optional[str] = Field(
        None,
        description='Denotes the state of the subscription. When the subscription is ENABLED, the user will receive\nnotification on the configured Integrations. If the subscription is DISABLED, the user will not\nrecieve any notification for the configured notification type. Note that, you cannot disable\na subscription for `REQUIRED` notification type.\n',
        examples=['ENABLED'],
    )
    integrations: Optional[List[GlobalObjectReference]] = Field(
        None,
        description='Integrations to which notifications are to be sent.',
        min_length=1,
    )


class Integration(BaseModel):
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
    display_name: Optional[constr(max_length=64)] = Field(
        None,
        description='A human readable name for the particular integration\n',
        examples=['Slack integration'],
    )
    description: Optional[constr(max_length=128)] = Field(
        None,
        description='A human readable description for the particular integration\n',
        examples=['A Slack channel integration'],
    )
    target: Optional[Target] = Field(
        None, description='Integration-specific details (integration targets)\n'
    )


class IntegrationList(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    api_version: ApiVersion = Field(
        ...,
        description='APIVersion defines the schema version of this representation of a resource.',
    )
    kind: KindModel8 = Field(
        ..., description='Kind defines the object this REST resource represents.'
    )
    metadata: MetadataModel3
    data: List[Integration] = Field(
        ...,
        description='A data property that contains an array of resource items. Each entry in the array is a separate resource.',
    )
