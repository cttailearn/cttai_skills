"""
Selector configurations for Toutiao Publisher
Provides fallback selectors for robust element finding
"""

# Title input selectors
TITLE_INPUT_SELECTORS = [
    {"type": "placeholder", "value": "请输入文章标题"},
    {"type": "placeholder", "value": "标题"},
    {"type": "css", "value": "textarea[placeholder*='标题']"},
    {"type": "css", "value": "textarea"},
]

# Content editor selectors (ProseMirror)
CONTENT_EDITOR_SELECTORS = [
    {"type": "css", "value": ".ProseMirror"},
    {"type": "css", "value": "[contenteditable='true']"},
    {"type": "css", "value": ".editor-content"},
]

# Publish button selectors
PUBLISH_BUTTON_SELECTORS = [
    {"type": "text", "value": "预览并发布"},
    {"type": "text", "value": "发布"},
    {"type": "css", "value": ".publish-btn"},
    {"type": "css", "value": "button[data-e2e='publish-btn']"},
]

# Final confirm button selectors
FINAL_CONFIRM_BUTTON_SELECTORS = [
    {"type": "css", "value": ".publish-btn-last"},
    {"type": "text", "value": "确定"},
    {"type": "text", "value": "确认发布"},
    {"type": "text", "value": "发布文章"},
    {"type": "css", "value": ".byte-modal .byte-btn-primary"},
]

# Cover upload selectors
ADD_COVER_SELECTORS = [
    {"type": "css", "value": "div.article-cover-add"},
    {"type": "text", "value": "添加封面"},
]

# Upload local button selectors
UPLOAD_LOCAL_SELECTORS = [
    {"type": "css", "value": "div.btn-upload-handle.upload-handler"},
    {"type": "text", "value": "本地上传"},
]

# File input selectors
FILE_INPUT_SELECTORS = [
    {"type": "css", "value": "input[type='file']"},
]

# Confirm upload button selectors
CONFIRM_UPLOAD_SELECTORS = [
    {"type": "css", "value": "button[data-e2e='imageUploadConfirm-btn']"},
    {"type": "text", "value": "确定"},
    {"type": "css", "value": ".byte-btn-primary"},
]

# No cover option selectors
NO_COVER_SELECTORS = [
    {"type": "text", "value": "无封面"},
    {"type": "css", "value": "input[type='radio'][value='0']"},
]

# Overlay/drawer selectors to dismiss
OVERLAY_SELECTORS = [
    {"type": "css", "value": ".byte-drawer-mask"},
    {"type": "css", "value": ".ai-assistant-drawer"},
    {"type": "css", "value": ".byte-modal-mask"},
]

# Save draft button
SAVE_DRAFT_SELECTORS = [
    {"type": "text", "value": "保存草稿"},
    {"type": "text", "value": "存草稿"},
]

# Success indicator text
SUCCESS_TEXT_SELECTORS = [
    "发布成功",
    "主页查看",
    "查看已发布",
    "已发布",
]

# Login redirect check
LOGIN_REDIRECT_PATTERNS = [
    "auth/page/login",
    "sso.toutiao.com",
]
