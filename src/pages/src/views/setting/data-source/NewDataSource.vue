<template>
  <div
    :class="['data-source-card user-scroll-y', { 'has-alert': userStore.showAlert }]"
    v-bkloading="{ loading: isLoading, zIndex: 9 }"
  >
    <DataSourceCard
      v-if="!isSuccess"
      :plugins="currentPlugins"
      @handle-collapse="handleCollapse">
      <template #content v-if="showContent">
        <div class="steps-wrapper">
          <bk-steps
            ext-cls="steps"
            :cur-step="curStep"
            :steps="typeSteps"
          />
        </div>
        <div>
          <Http
            v-if="currentType === 'general'"
            :cur-step="curStep"
            :data-source-id="dataSourceId"
            :is-reset="isReset"
            @update-cur-step="updateCurStep"
            @update-success="updateSuccess" />
          <Ldap
            v-if="currentType === 'ldap'"
            :cur-step="curStep"
            :data-source-id="dataSourceId"
            :is-reset="isReset"
            @update-cur-step="updateCurStep"
            @update-success="updateSuccess" />
          <CustomJsonSchema
            v-if="!isNotJsonSchemaIds.includes(currentType)"
            :current-type="currentType"
            :data-source-id="dataSourceId"
            :cur-step="curStep"
            :is-reset="isReset"
            @update-cur-step="updateCurStep"
            @update-success="updateSuccess" />
        </div>
      </template>
    </DataSourceCard>
    <Success v-else :title="successText" />
  </div>
</template>

<script setup lang="ts"> import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import Success from './ConfigSuccess.vue';
import CustomJsonSchema from './CustomJsonSchema.vue';
import Http from './HttpConfig.vue';
import Ldap from './LdapConfig.vue';

import DataSourceCard from '@/components/layouts/DataSourceCard.vue';
import { getDataSourcePlugins } from '@/http';
import { t } from '@/language/index';
import { useMainViewStore, useUser } from '@/store';

const store = useMainViewStore();
store.customBreadcrumbs = false;

const route = useRoute();

const userStore = useUser();

const currentType = ref('');

const isNotJsonSchemaIds = ['general', 'local', 'ldap'];

// 获取数据源类型
watch(() => route.query.type, (val: string) => {
  if (val) {
    currentType.value = val;
  }
}, {
  deep: true,
  immediate: true,
});

const dataSourceId = ref(null);
// 获取数据源类型
watch(() => route.query.id, (val: number) => {
  if (val) {
    dataSourceId.value = val;
  }
}, {
  deep: true,
  immediate: true,
});

const currentPlugins = ref([]);
const isLoading = ref(false);

const curStep = ref(1);
const typeSteps = ref([
  { title: t('服务配置') },
  { title: t('字段设置') },
]);

onMounted(() => {
  initDataSourcePlugins();
});

const initDataSourcePlugins = () => {
  isLoading.value = true;
  getDataSourcePlugins().then((res) => {
    res.data?.forEach((item) => {
      if (item.id === currentType.value) {
        currentPlugins.value = [item];
      }
    });
    isLoading.value = false;
  })
    .catch(() => {
      isLoading.value = false;
    });
};

// 切换步骤
const updateCurStep = (value: number) => {
  curStep.value = value;
};

// 切换展示状态
const showContent = ref(true);
const handleCollapse = () => {
  showContent.value = !showContent.value;
};

// 数据源创建、更新
const successText = ref('新建企业微信数据源成功');
const isSuccess = ref(false);
const updateSuccess = (value: string) => {
  successText.value = `${value}${currentPlugins.value[0].name}${t('成功 ')}`;
  isSuccess.value = true;
};

const isReset = ref(false);
</script>

<style lang="less" scoped>
.has-alert {
  height: calc(100vh - 144px) !important;
}

.data-source-card {
  height: calc(100vh - 92px);
  padding: 16px 24px;

  .steps-wrapper {
    padding: 12px 0;
    text-align: center;
    background: #FAFBFD;
    box-shadow: 0 1px 0 0 #F0F1F5;

    .steps {
      width: 350px;
      margin: auto;
    }
  }
}
</style>
