# 3D 角色生成指南

## 流程
```
即梦/生成的 2D 头像 → 上传到 3D 生成平台 → 导出 GLB 文件 → 放到 src/assets/models/
```

## 推荐平台

### 1. Tripo3D（推荐，免费额度最多）
- 网址：https://tripo3d.ai
- 操作：上传图片 → 自动生成 3D → 下载 GLB
- 免费：每天 4 次
- 文件命名：下载后改名为 `gf_gentle.glb` 放入 models 目录

### 2. Meshy
- 网址：https://meshy.ai
- 操作：Image to 3D → 上传 → 下载 GLB
- 免费：每天 4 次

### 3. CSM
- 网址：https://3d.csm.ai
- 操作：上传照片 → 生成 → 下载
- 免费：有免费额度

## 文件放置
生成的 GLB 文件放到：
```
frontend/src/assets/models/gf_gentle.glb
frontend/src/assets/models/gf_bubbly.glb
frontend/src/assets/models/gf_tsundere.glb
frontend/src/assets/models/gf_intellectual.glb
frontend/src/assets/models/bf_sunny.glb
frontend/src/assets/models/bf_cold.glb
frontend/src/assets/models/bf_steady.glb
frontend/src/assets/models/bf_young.glb
```

## 启用 3D
生成 GLB 后，取消 app.js 中 MODEL_3D_MAP 的注释：
```javascript
const MODEL_3D_MAP = {
  gf_gentle: 'src/assets/models/gf_gentle.glb',
  gf_bubbly: 'src/assets/models/gf_bubbly.glb',
  // ... 其他角色
};
```
