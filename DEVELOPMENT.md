# 开发指南

本项目的环境搭建、日常开发命令，以及几个会把人坑住的陷阱。

## 环境要求

| 依赖 | 版本要求 | 依据 |
| --- | --- | --- |
| Python | >= 3.12 | Django 6.1.1 的 `requires-python` 为 `>=3.12` |
| Node.js | `^22.18.0` 或 `>= 24.12.0` | `frontend/package.json` 的 `engines` 字段 |

本仓库实际验证环境：Python 3.14.7、Django 6.1.1、Node 24.21.0、npm 11.19.0。

## 项目结构

```
backend/                      Django 6.1 后端
├── backend/                  项目配置（settings / urls / wsgi / asgi）
├── web/                      业务 app
│   └── templates/index.html  8000 端口返回的页面模板（注意：不是 Vite 生成的）
├── static/frontend/          前端构建产物（被 git 跟踪）
└── db.sqlite3                开发数据库（未被 git 跟踪）
frontend/                     Vue 3 + Vite 前端
└── src/
    ├── components/navbar/    顶部导航栏与搜索栏
    ├── router/               路由（目前 routes 为空）
    └── stores/               Pinia
```

前后端是**两个独立服务**，职责不同：

| 服务 | 端口 | 读什么 |
| --- | --- | --- |
| Django | 8000 | `backend/web/templates/index.html` + `backend/static/frontend/` 里**上次构建的**产物 |
| Vite | 5173 | `frontend/src/` **实时源码**，改动即时热更新 |

## 首次配置

### 后端

```bash
# 在仓库根目录创建虚拟环境
python3 -m venv .venv

# 安装依赖
.venv/bin/pip install -r requirements.txt

# 建库（db.sqlite3 不在版本控制里，必须自己跑）
cd backend
../.venv/bin/python manage.py migrate
```

### 前端

```bash
cd frontend
npm install
```

## 日常开发

**两个服务都要跑**，开两个终端：

```bash
# 终端 1 —— Django 后端
cd backend
../.venv/bin/python manage.py runserver 8000
```

```bash
# 终端 2 —— Vite 开发服务器
cd frontend
npm run dev
```

**开发时访问 http://localhost:5173**，它读的是源码，改完立刻生效。

http://127.0.0.1:8000 也能打开界面，但它加载的是上次构建的产物，**不反映源码改动**。只有需要验证「构建后的真实表现」时才看它。

### 为什么两个都得跑

`backend/backend/settings.py` 里的 CORS 只放行了 `http://localhost:5173`，即 Vite 的开发地址，所以前端以 5173 为开发入口。

后端认证接口已经就绪，但前端**目前还没有调用任何接口**（`frontend/src` 里没有任何 `fetch` / `axios`）：

| 接口 | 方法 | 用途 |
| --- | --- | --- |
| `/api/token/` | POST | 获取 JWT |
| `/api/token/refresh/` | POST | 刷新 JWT |

## 常用命令

### 后端

```bash
cd backend

../.venv/bin/python manage.py check              # 系统检查
../.venv/bin/python manage.py migrate            # 应用迁移
../.venv/bin/python manage.py makemigrations     # 改过 models.py 后生成迁移
../.venv/bin/python manage.py showmigrations     # 查看迁移状态
../.venv/bin/python manage.py test               # 跑测试（目前 0 个）
../.venv/bin/python manage.py createsuperuser    # 建管理员账号
../.venv/bin/python manage.py shell              # Django shell
```

管理后台：http://127.0.0.1:8000/admin/

### 前端

```bash
cd frontend

npm run dev       # 开发服务器（热更新）
npm run build     # 构建产物 → 输出到 backend/static/frontend/
npm run preview   # Vite 自带的预览服务器（不是 Django）
```

## ⚠️ 陷阱一：构建会打断 8000 端口

`backend/web/templates/index.html` 里**硬编码了构建产物的哈希文件名**：

```django
<script src="{% static 'frontend/assets/index-CuUsnuGI.js' %}"></script>
<link rel="stylesheet" href="{% static 'frontend/assets/index-CKT5K5NR.css' %}">
```

而这个模板**不是 Vite 生成的**。Vite 生成的是 `backend/static/frontend/index.html`，两份是不同的文件，内容也不同（后者用 `/assets/...`，前者用 `{% static %}`）。

Vite 的输出文件名带内容哈希，**源码一改、重新构建，哈希就变**。实测一次全新构建的产出：

```
index-BxcJWdw6.js    index-gxaJMinD.css
```

和模板里写死的 `index-CuUsnuGI.js` / `index-CKT5K5NR.css` **两个都对不上**。此时访问 8000 会因脚本和样式表 404 而白屏。

> **每次 `npm run build` 之后，必须手工把 `backend/web/templates/index.html` 里那两处文件名同步成新哈希。**

开发阶段走 5173 不会碰到这个问题——Vite 自己管理资源引用。这个陷阱只影响 8000 端口。

## ⚠️ 陷阱二：`static/` 是有意保留在版本控制里的

`.gitignore` 里写着 `static/`，但 `backend/static/frontend/` 的 4 个文件**仍被 git 跟踪**，这是有意为之：新克隆的仓库因此可以直接 `runserver` 就在 8000 看到界面，不必先装 Node 再构建。

代价就是陷阱一——哈希不同步的问题会一直在。

## 数据库

开发库是 SQLite，位于 `backend/db.sqlite3`，**未被 git 跟踪**（见 `.gitignore`）。所以：

- 新克隆的仓库里没有这个文件，需要自己跑 `migrate`
- 里面的数据只存在于本机，不同机器之间不会同步
- 它曾经被跟踪过，旧版本仍留在 git 历史里

## 版本控制

- 远端 `origin` 指向 `git@github.com:Aludel/LLM_Friend.git`（SSH）
- 主分支为 `main`
- 以下内容已被移出版本控制：`__pycache__/`、`*.pyc`、`.idea/`、`db.sqlite3`

## 已知的待办

- `frontend/src/router/index.js` 的 `routes` 为空，访问 `/` 会触发 vue-router 的 `No match found` 警告。属于脚手架状态，需要时补路由。
