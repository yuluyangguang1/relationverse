/**
 * Embera API 客户端
 */
const API_BASE = localStorage.getItem('rv_api_base') || 'http://localhost:8000';

const api = {
  base: API_BASE,

  async request(path, options = {}) {
    const url = `${this.base}${path}`;
    const config = {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    };
    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }
    const res = await fetch(url, config);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || '请求失败');
    }
    return res.json();
  },

  // ─── 角色 ───
  characters: {
    list:    () => api.request('/api/characters/list'),
    get:     (id) => api.request(`/api/characters/${id}`),
    create:  (data) => api.request('/api/characters/create', { method: 'POST', body: data }),
    templates: () => api.request('/api/characters/templates'),
  },

  // ─── 对话 ───
  chat: {
    send:    (data) => api.request('/api/chat/send', { method: 'POST', body: data }),
    history: (charId, limit = 50) => api.request(`/api/chat/history/${charId}?limit=${limit}`),
  },

  // ─── 宠物 ───
  pets: {
    list:    () => api.request('/api/pets/list'),
    create:  (data) => api.request('/api/pets/create', { method: 'POST', body: data }),
    action:  (petId, action) => api.request(`/api/pets/${petId}/action`, { method: 'POST', body: { action } }),
    species: () => api.request('/api/pets/species'),
  },

  // ─── 数字怀念 ───
  memorial: {
    list:     () => api.request('/api/memorial/list'),
    create:   (data) => api.request('/api/memorial/create', { method: 'POST', body: data }),
    addStory: (id, data) => api.request(`/api/memorial/${id}/add-story`, { method: 'POST', body: data }),
  },

  // ─── 上传 ───
  upload: {
    photo: async (file) => {
      const fd = new FormData();
      fd.append('file', file);
      const res = await fetch(`${api.base}/api/upload/photo`, { method: 'POST', body: fd });
      return res.json();
    },
    voice: async (file) => {
      const fd = new FormData();
      fd.append('file', file);
      const res = await fetch(`${api.base}/api/upload/voice`, { method: 'POST', body: fd });
      return res.json();
    },
  },
};

// ─── 页面路由 ───
const router = {
  current: 'home',
  
  go(page, params = {}) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tabbar-item').forEach(t => t.classList.remove('active'));

    // 显示目标页面
    const el = document.getElementById(`page-${page}`);
    if (el) {
      el.classList.add('active');
      this.current = page;
    }

    // 高亮 tab
    const tab = document.querySelector(`.tabbar-item[data-page="${page}"]`);
    if (tab) tab.classList.add('active');

    // 触发页面加载
    if (typeof window[`onPage_${page}`] === 'function') {
      window[`onPage_${page}`](params);
    }
  },

  back() {
    history.back();
  }
};

// ─── Toast 通知 ───
function showToast(message, duration = 2000) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// ─── 时间格式化 ───
function formatTime(dateStr) {
  const d = new Date(dateStr);
  const now = new Date();
  const diff = now - d;
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
  if (diff < 86400000) return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  return `${d.getMonth() + 1}月${d.getDate()}日`;
}

// ─── 亲密度颜色 ───
function getIntimacyColor(level) {
  if (level < 20) return '#64748b';
  if (level < 40) return '#60a5fa';
  if (level < 60) return '#34d399';
  if (level < 80) return '#fbbf24';
  return '#f472b6';
}

// ─── 关系阶段中文 ───
const STAGE_NAMES = {
  stranger: '初识',
  friend: '朋友',
  flirting: '暧昧',
  lover: '恋人',
  deep_love: '深爱',
  soulmate: '灵魂伴侣',
};

// ─── 角色头像 ───
const AVATAR_MAP = {
  gf_gentle: 'src/assets/avatars/gf_gentle.jpg',
  gf_bubbly: 'src/assets/avatars/gf_bubbly.jpg',
  gf_tsundere: 'src/assets/avatars/gf_tsundere.jpg',
  gf_intellectual: 'src/assets/avatars/gf_intellectual.jpg',
  bf_sunny: 'src/assets/avatars/bf_sunny.jpg',
  bf_cold: 'src/assets/avatars/bf_cold.jpg',
  bf_steady: 'src/assets/avatars/bf_steady.jpg',
  bf_young: 'src/assets/avatars/bf_young.jpg',
};

// ─── 角色 3D 模型 ───
const MODEL_3D_MAP = {
  // 生成 3D 模型后放到 src/assets/models/ 目录
  // gf_gentle: 'src/assets/models/gf_gentle.glb',
  // gf_bubbly: 'src/assets/models/gf_bubbly.glb',
};

// ─── 角色类型 emoji ───
const TYPE_EMOJI = {
  girlfriend: '💕',
  boyfriend: '💙',
  friend: '🤝',
  family: '👨‍👩‍👧',
  mentor: '🧠',
  fantasy: '🎭',
};

// ─── 宠物 emoji ───
const PET_EMOJI = {
  cat: '🐱', dog: '🐶', rabbit: '🐰',
  panda: '🐼', fox: '🦊', dragon: '🐉', robot: '🤖',
};

// ─── 角色类型颜色 ───
const TYPE_COLORS = {
  girlfriend: { bg: 'rgba(244,114,182,0.1)', color: '#f472b6' },
  boyfriend:  { bg: 'rgba(96,165,250,0.1)', color: '#60a5fa' },
  friend:     { bg: 'rgba(52,211,153,0.1)', color: '#34d399' },
  family:     { bg: 'rgba(251,146,60,0.1)', color: '#fb923c' },
  mentor:     { bg: 'rgba(56,189,248,0.1)', color: '#38bdf8' },
  fantasy:    { bg: 'rgba(232,121,249,0.1)', color: '#e879f9' },
};
