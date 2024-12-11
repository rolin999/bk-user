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
from django.conf import settings
from django.views.generic import View

from bklogin.authentication.manager import BkTokenManager
from bklogin.common.error_codes import error_codes
from bklogin.common.response import APISuccessResponse
from bklogin.component.bk_user import api as bk_user_api

from .mixins import APIGatewayAppVerifiedMixin


class TokenVerifyApi(APIGatewayAppVerifiedMixin, View):
    """Token 解析"""

    def get(self, request, *args, **kwargs):
        bk_token = request.GET.get(settings.BK_TOKEN_COOKIE_NAME)

        ok, username, msg = BkTokenManager().is_valid(bk_token)
        if not ok:
            raise error_codes.VALIDATION_ERROR.f(msg, replace=True)

        # FIXME (nan): 调整 bk_token 签发逻辑，DB BKToken 表额外添加 tenant_id / idp_id 等信息，
        #  避免需频繁查询用户管理接口
        user = bk_user_api.get_tenant_user(username)

        return APISuccessResponse(data={"bk_username": user.id, "tenant_id": user.tenant_id})


class TokenUserInfoRetrieveApi(APIGatewayAppVerifiedMixin, View):
    """Token 用户信息解析"""

    def get(self, request, *args, **kwargs):
        bk_token = request.GET.get(settings.BK_TOKEN_COOKIE_NAME)

        ok, username, msg = BkTokenManager().is_valid(bk_token)
        if not ok:
            raise error_codes.VALIDATION_ERROR.f(msg, replace=True)

        # 通过用户管理查询用户信息
        user = bk_user_api.get_tenant_user(username)

        return APISuccessResponse(
            data={
                "bk_username": user.id,
                "tenant_id": user.tenant_id,
                # 基本信息
                "display_name": user.display_name,
                "language": user.language,
                "time_zone": user.time_zone,
            }
        )