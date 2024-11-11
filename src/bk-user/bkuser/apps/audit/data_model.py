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

from typing import Dict

from pydantic import BaseModel


class AuditObject(BaseModel):
    """审计操作对象相关信息"""

    # 操作对象 ID
    id: str | int
    # 操作对象类型
    type: str
    # 操作对象名称
    name: str | None = None
    # 操作行为
    operation: str
    # 操作前数据
    data_before: Dict
    # 操作后数据
    data_after: Dict
    # 额外信息
    extras: Dict
