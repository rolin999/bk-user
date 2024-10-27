# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - 用户管理 (bk-user) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from typing import Dict, List, Optional, Union

from bkuser.utils.uuid import generate_uuid

from .constants import ObjectType, Operation
from .models import OperationAuditRecord


def add_operation_audit_record(
    operator: str,
    tenant_id: str,
    operation: Operation,
    object_type: ObjectType,
    object_id: str,
    extras: Dict | None = None,
) -> OperationAuditRecord:
    """
    添加操作审计记录

    :param operator: 操作者
    :param tenant_id: 租户 ID
    :param operation: 操作行为
    :param object_type: 操作对象类型
    :param object_id: 操作对象 ID
    :param extras: 额外信息
    """
    return OperationAuditRecord.objects.create(
        creator=operator,
        tenant_id=tenant_id,
        operation=operation,
        object_type=object_type,
        object_id=object_id,
        extras=extras,
    )


def add_batch_operation_audit_records(
    operator: str,
    tenant_id: str,
    operation: Operation,
    object_type: ObjectType,
    objects: List[Dict[str, Optional[Union[str, Dict]]]],
) -> List[OperationAuditRecord]:
    """
    批量添加操作审计记录

    :param operator: 操作者
    :param tenant_id: 租户 ID
    :param operation: 操作类型
    :param object_type: 对象类型
    :param objects: 包含 object_id 和 extras 的字典列表
    """
    records = []
    event_id = generate_uuid()
    bulk_create_batch_size = 100

    for obj in objects:
        object_id = obj.get("object_id")
        object_extras = obj.get("extras", None)

        records.append(
            OperationAuditRecord(
                creator=operator,
                event_id=event_id,
                tenant_id=tenant_id,
                operation=operation,
                object_type=object_type,
                object_id=object_id,
                extras=object_extras,
            )
        )

    OperationAuditRecord.objects.bulk_create(records, batch_size=bulk_create_batch_size)

    return records
