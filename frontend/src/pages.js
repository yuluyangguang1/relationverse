/**
 * RelationVerse — 页面逻辑
 */

// ═══════════════════════════════════════════
// 全局状态
// ═══════════════════════════════════════════
let currentCharId = null;
let selectedType = null;
let selectedPersona = null;
let voiceMode = false;

// ═══════════════════════════════════════════
// 首页
// ═══════════════════════════════════════════
async function onPage_home() {
  await Promise.all([
    loadHomeCharacters(),
    loadHomePets(),
    loadHomeMemorials(),
  ]);
}

async function loadHomeCharacters() {
  const lovers = document.getElementById('home-lovers');
  const social = document.getElementById('home-social');
  
  try {
    const data = await api.characters.list();
    
    let loversHtml = '';
    let socialHtml = '';
    
    data.characters.forEach(c => {
      const tc = TYPE_COLORS[c.type] || TYPE_COLORS.friend;
      const emoji = TYPE_EMOJI[c.type] || '🤝';
      const stage = STAGE_NAMES[c.relationship_stage] || c.relationship_stage;
      const color = getIntimacyColor(c.intimacy_level);
      
      const html = `
        <div class="card" onclick="openChat('${c.id}','${c.name}','${c.type}')">
          <div class="card-avatar" style="background:${tc.bg}">${emoji}</div>
          <div class="card-name">${c.name}</div>
          <div class="card-desc">${stage} · ${c.total_messages} 条消息</div>
          <div class="card-tags">
            ${(c.personality || []).slice(0, 2).map(t => `<span class="card-tag">${t}</span>`).join('')}
          </div>
          <div class="card-progress">
            <div class="card-progress-fill" style="width:${c.intimacy_level}%;background:${color}"></div>
          </div>
        </div>
      `;
      
      if (c.type === 'girlfriend' || c.type === 'boyfriend') {
        loversHtml += html;
      } else {
        socialHtml += html;
      }
    });
    
    lovers.innerHTML = loversHtml + createAddCardHtml('lover');
    social.innerHTML = socialHtml + createAddCardHtml('social');
  } catch (e) {
    console.error('加载角色失败:', e);
    lovers.innerHTML = createAddCardHtml('lover');
    social.innerHTML = createAddCardHtml('social');
  }
}

async function loadHomePets() {
  const pets = document.getElementById('home-pets');
  
  try {
    const data = await api.pets.list();
    
    let html = '';
    data.pets.forEach(p => {
      const emoji = PET_EMOJI[p.species] || '🐾';
      const color = getIntimacyColor(p.intimacy);
      
      html += `
        <div class="card" onclick="openPet('${p.id}')">
          <div class="card-avatar" style="background:rgba(251,191,36,0.1)">${emoji}</div>
          <div class="card-name">${p.name}</div>
          <div class="card-desc">Lv.${p.level} · 亲密度 ${p.intimacy.toFixed(0)}%</div>
          <div class="card-tags">
            ${(p.personality_traits || []).slice(0, 2).map(t => `<span class="card-tag">${t}</span>`).join('')}
          </div>
          <div class="card-progress">
            <div class="card-progress-fill" style="width:${p.intimacy}%;background:${color}"></div>
          </div>
        </div>
      `;
    });
    
    pets.innerHTML = html + createAddCardHtml('pet');
  } catch (e) {
    console.error('加载宠物失败:', e);
    pets.innerHTML = createAddCardHtml('pet');
  }
}

async function loadHomeMemorials() {
  const memorials = document.getElementById('home-memorials');
  
  try {
    const data = await api.memorial.list();
    
    let html = '';
    data.memorials.forEach(m => {
      html += `
        <div class="card" onclick="showToast('怀念对话功能开发中')">
          <div class="card-avatar" style="background:rgba(167,139,250,0.1)">🕊️</div>
          <div class="card-name">${m.name}</div>
          <div class="card-desc">${m.relation_type} · ${m.stories_count} 个故事</div>
        </div>
      `;
    });
    
    memorials.innerHTML = html + createAddCardHtml('memorial');
  } catch (e) {
    memorials.innerHTML = createAddCardHtml('memorial');
  }
}

function createAddCardHtml(type) {
  const labels = { lover: '添加恋人', pet: '领养宠物', memorial: '创建纪念', social: '添加关系' };
  return `
    <div class="card card-add" onclick="router.go('create', {type:'${type}'})">
      <span class="plus">+</span>
      <span>${labels[type] || '添加'}</span>
    </div>
  `;
}

// ═══════════════════════════════════════════
// 聊天页面
// ═══════════════════════════════════════════
function openChat(charId, name, type) {
  currentCharId = charId;
  document.getElementById('chat-char-name').textContent = name;
  const tc = TYPE_COLORS[type] || TYPE_COLORS.friend;
  document.getElementById('chat-char-stage').textContent = TYPE_EMOJI[type] || '🤝';
  router.go('chat');
  loadChatHistory(charId);
}

async function loadChatHistory(charId) {
  const list = document.getElementById('chat-msg-list');
  list.innerHTML = '<div class="loading" style="justify-content:center;padding:40px;"><span class="loading-dots">加载中</span></div>';
  
  try {
    const data = await api.chat.history(charId);
    let html = '';
    
    data.messages.forEach(m => {
      html += createMsgHtml(m.role, m.content, m.created_at);
    });
    
    list.innerHTML = html || '<div class="empty"><div class="empty-icon">💬</div><div class="empty-text">开始你们的第一次对话吧</div></div>';
    scrollToBottom();
  } catch (e) {
    list.innerHTML = '<div class="empty"><div class="empty-icon">⚠️</div><div class="empty-text">加载失败</div></div>';
  }
}

function createMsgHtml(role, content, time) {
  return `
    <div class="chat-msg ${role}">
      <div class="chat-bubble">${escapeHtml(content)}</div>
      <span class="chat-time">${formatTime(time)}</span>
    </div>
  `;
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg || !currentCharId) return;
  
  // 清空输入
  input.value = '';
  autoResize(input);
  
  // 显示用户消息
  const list = document.getElementById('chat-msg-list');
  list.innerHTML += createMsgHtml('user', msg, new Date().toISOString());
  scrollToBottom();
  
  // 显示加载
  const loadingId = 'loading-' + Date.now();
  list.innerHTML += `<div class="chat-msg ai" id="${loadingId}"><div class="chat-bubble"><span class="loading"><span class="loading-dots">思考中</span></span></div></div>`;
  scrollToBottom();
  
  try {
    const data = await api.chat.send({
      character_id: currentCharId,
      message: msg,
    });
    
    // 替换加载为回复
    const loading = document.getElementById(loadingId);
    if (loading) {
      loading.innerHTML = `<div class="chat-bubble">${escapeHtml(data.reply)}</div><span class="chat-time">${formatTime(new Date().toISOString())}</span>`;
    }
    scrollToBottom();
  } catch (e) {
    const loading = document.getElementById(loadingId);
    if (loading) loading.remove();
    list.innerHTML += createMsgHtml('ai', '抱歉，出了点问题，请稍后再试。', new Date().toISOString());
    scrollToBottom();
  }
}

function scrollToBottom() {
  const container = document.getElementById('chat-messages');
  setTimeout(() => { container.scrollTop = container.scrollHeight; }, 100);
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

function toggleVoiceMode() {
  voiceMode = !voiceMode;
  const btn = document.getElementById('chat-voice-btn');
  btn.textContent = voiceMode ? '📝' : '🔊';
  showToast(voiceMode ? '语音模式已开启' : '文字模式');
}

function toggleRecording() {
  const btn = document.getElementById('chat-mic-btn');
  btn.classList.toggle('recording');
  if (btn.classList.contains('recording')) {
    showToast('正在录音...');
    // TODO: 接入 Whisper 语音识别
  } else {
    showToast('录音结束');
  }
}

function showCharInfo() {
  showToast('角色详情功能开发中');
}

// ═══════════════════════════════════════════
// 消息列表页
// ═══════════════════════════════════════════
async function onPage_chat_list() {
  const content = document.getElementById('chat-list-content');
  content.innerHTML = '<div class="loading" style="justify-content:center;padding:40px;"><span class="loading-dots">加载中</span></div>';
  
  try {
    const data = await api.characters.list();
    
    if (data.characters.length === 0) {
      content.innerHTML = '<div class="empty" style="margin-top:80px;"><div class="empty-icon">💬</div><div class="empty-text">还没有角色<br>快去创建一个吧</div></div>';
      return;
    }
    
    let html = '';
    data.characters.forEach(c => {
      const emoji = TYPE_EMOJI[c.type] || '🤝';
      const time = c.last_active ? formatTime(c.last_active) : '从未聊天';
      
      html += `
        <div style="display:flex;align-items:center;gap:12px;padding:16px;border-bottom:1px solid var(--border);cursor:pointer;" 
             onclick="openChat('${c.id}','${c.name}','${c.type}')">
          <div style="width:48px;height:48px;border-radius:50%;background:var(--card);display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">
            ${emoji}
          </div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;">${c.name}</div>
            <div style="font-size:12px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              ${c.total_messages} 条消息 · ${time}
            </div>
          </div>
          <div style="font-size:11px;color:var(--text-dim);">${time}</div>
        </div>
      `;
    });
    
    content.innerHTML = html;
  } catch (e) {
    content.innerHTML = '<div class="empty"><div class="empty-icon">⚠️</div><div class="empty-text">加载失败</div></div>';
  }
}

// ═══════════════════════════════════════════
// 创建角色页
// ═══════════════════════════════════════════
const CREATE_TYPES = [
  { id: 'girlfriend', emoji: '💕', name: 'AI 女友', desc: '温柔陪伴' },
  { id: 'boyfriend', emoji: '💙', name: 'AI 男友', desc: '守护你的人' },
  { id: 'friend', emoji: '🤝', name: 'AI 朋友', desc: '无话不谈' },
  { id: 'family', emoji: '👨‍👩‍👧', name: 'AI 家人', desc: '温暖的家' },
  { id: 'mentor', emoji: '🧠', name: 'AI 导师', desc: '帮你成长' },
  { id: 'fantasy', emoji: '🎭', name: '幻想角色', desc: '无限可能' },
];

function onPage_create(params) {
  selectedType = null;
  selectedPersona = null;
  document.getElementById('create-step1').classList.remove('hidden');
  document.getElementById('create-step2').classList.add('hidden');
  
  const grid = document.getElementById('create-type-grid');
  grid.innerHTML = CREATE_TYPES.map(t => `
    <div class="persona-option" onclick="selectCreateType('${t.id}')">
      <div class="emoji">${t.emoji}</div>
      <div class="name">${t.name}</div>
      <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">${t.desc}</div>
    </div>
  `).join('');
}

async function selectCreateType(type) {
  selectedType = type;
  document.getElementById('create-step1').classList.add('hidden');
  document.getElementById('create-step2').classList.remove('hidden');
  
  try {
    const data = await api.characters.templates();
    const templates = data.templates.filter(t => t.type === type);
    
    const grid = document.getElementById('create-persona-grid');
    grid.innerHTML = templates.map(t => `
      <div class="persona-option" onclick="selectPersona('${t.id}', this)">
        <div class="name">${t.name}</div>
        <div class="card-tags" style="justify-content:center;margin-top:8px;">
          ${t.personality.map(p => `<span class="card-tag">${p}</span>`).join('')}
        </div>
      </div>
    `).join('');
  } catch (e) {
    showToast('加载人设失败');
  }
}

function selectPersona(id, el) {
  selectedPersona = id;
  document.querySelectorAll('#create-persona-grid .persona-option').forEach(e => e.classList.remove('selected'));
  el.classList.add('selected');
}

async function doCreateCharacter() {
  if (!selectedPersona) {
    showToast('请先选择一个人设');
    return;
  }
  
  const customName = document.getElementById('create-custom-name').value.trim();
  
  try {
    showToast('创建中...');
    const data = await api.characters.create({
      persona_id: selectedPersona,
      custom_name: customName || null,
    });
    
    showToast(`✨ ${data.name} 已创建！`);
    router.go('home');
  } catch (e) {
    showToast('创建失败: ' + e.message);
  }
}

// ═══════════════════════════════════════════
// 宠物互动页
// ═══════════════════════════════════════════
let currentPetId = null;

async function openPet(petId) {
  currentPetId = petId;
  router.go('pet');
  await loadPetDetails(petId);
}

async function loadPetDetails(petId) {
  try {
    const data = await api.pets.list();
    const pet = data.pets.find(p => p.id === petId);
    if (!pet) return;
    
    document.getElementById('pet-name').textContent = pet.name;
    document.getElementById('pet-avatar-display').textContent = PET_EMOJI[pet.species] || '🐾';
    
    // 宠物说话
    const speech = document.getElementById('pet-speech');
    if (pet.intimacy < 20) {
      speech.textContent = pet.species === 'cat' ? '"喵~"' : '"汪！"';
    } else if (pet.intimacy < 50) {
      speech.textContent = '"饿饿...想玩..."';
    } else if (pet.intimacy < 80) {
      speech.textContent = '"今天你回来晚了呢，我等了好久。"';
    } else {
      speech.textContent = '"你最近是不是不太开心？我感觉你叹气变多了。"';
    }
    
    // 属性
    const stats = document.getElementById('pet-stats-grid');
    stats.innerHTML = `
      <div class="pet-stat">
        <div class="pet-stat-icon">🍚</div>
        <div class="pet-stat-value" style="color:${getIntimacyColor(pet.hunger)}">${pet.hunger.toFixed(0)}</div>
        <div class="pet-stat-label">饥饿</div>
      </div>
      <div class="pet-stat">
        <div class="pet-stat-icon">🛁</div>
        <div class="pet-stat-value" style="color:${getIntimacyColor(pet.cleanliness)}">${pet.cleanliness.toFixed(0)}</div>
        <div class="pet-stat-label">清洁</div>
      </div>
      <div class="pet-stat">
        <div class="pet-stat-icon">😊</div>
        <div class="pet-stat-value" style="color:${getIntimacyColor(pet.mood)}">${pet.mood.toFixed(0)}</div>
        <div class="pet-stat-label">心情</div>
      </div>
      <div class="pet-stat">
        <div class="pet-stat-icon">💤</div>
        <div class="pet-stat-value" style="color:${getIntimacyColor(pet.energy)}">${pet.energy.toFixed(0)}</div>
        <div class="pet-stat-label">精力</div>
      </div>
      <div class="pet-stat">
        <div class="pet-stat-icon">❤️</div>
        <div class="pet-stat-value" style="color:${getIntimacyColor(pet.intimacy)}">${pet.intimacy.toFixed(0)}</div>
        <div class="pet-stat-label">亲密度</div>
      </div>
      <div class="pet-stat">
        <div class="pet-stat-icon">🧠</div>
        <div class="pet-stat-value" style="color:${getIntimacyColor(pet.speak_level)}">${pet.speak_level.toFixed(0)}</div>
        <div class="pet-stat-label">说话力</div>
      </div>
    `;
    
    // 操作按钮
    const actions = document.getElementById('pet-actions-grid');
    actions.innerHTML = `
      <div class="pet-action" onclick="petDoAction('feed')">
        <span class="icon">🍚</span><span>喂食</span>
      </div>
      <div class="pet-action" onclick="petDoAction('play')">
        <span class="icon">🎾</span><span>玩耍</span>
      </div>
      <div class="pet-action" onclick="petDoAction('clean')">
        <span class="icon">🛁</span><span>清洁</span>
      </div>
      <div class="pet-action" onclick="petDoAction('talk')">
        <span class="icon">💬</span><span>对话</span>
      </div>
    `;
    
    // 成长信息
    document.getElementById('pet-level').textContent = `Lv.${pet.level}`;
    document.getElementById('pet-intimacy-val').textContent = `${pet.intimacy.toFixed(0)}%`;
    document.getElementById('pet-speak-val').textContent = `${pet.speak_level.toFixed(0)}%`;
    
  } catch (e) {
    showToast('加载宠物详情失败');
  }
}

async function petDoAction(action) {
  if (!currentPetId) return;
  
  try {
    const data = await api.pets.action(currentPetId, action);
    showToast(data.message);
    
    if (data.level_up) {
      setTimeout(() => showToast(`🎉 升级到 Lv.${data.new_level}！`), 1000);
    }
    
    // 刷新宠物状态
    await loadPetDetails(currentPetId);
  } catch (e) {
    showToast('操作失败: ' + e.message);
  }
}

// ═══════════════════════════════════════════
// 个人中心
// ═══════════════════════════════════════════
function onPage_profile() {
  document.getElementById('profile-api-url').textContent = api.base;
}

// ═══════════════════════════════════════════
// 工具函数
// ═══════════════════════════════════════════
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ═══════════════════════════════════════════
// 初始化
// ═══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  router.go('home');
});
