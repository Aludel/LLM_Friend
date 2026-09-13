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

脚本定义在 `frontend/package.json` 的 `scripts` 里：

| 命令 | 实际执行 | 作用 | 端口 |
| --- | --- | --- | --- |
| `npm run dev` | `vite` | 开发服务器：读 `frontend/src/` 源码，改动即时热更新，**不写任何文件到磁盘** | 5173 |
| `npm run build` | `vite build && node scripts/sync-template.mjs` | 生产构建：打包压缩、文件名加内容哈希，写入 `backend/static/frontend/`，**并自动把新哈希同步进 Django 模板**（见陷阱一） | —— |
| `npm run sync` | `node scripts/sync-template.mjs` | 只同步不构建：把模板里的哈希改成当前 `assets/` 里的实际文件名 | —— |
| `npm run preview` | `vite preview` | 本地预览**已构建**的产物，用于脱离 Django 单独检查构建结果 | 4173 |

`dev` 和 `build` 的区别是本质性的：

- `dev` **不落盘**，Vite 在内存里编译后直接喂给浏览器，所以启动快、有热更新，但你看到的**不是最终产物**
- `build` 才会真正生成带哈希的静态文件并写入磁盘

构建的输出位置由 `frontend/vite.config.js` 指定，**不是 Vite 默认的 `dist/`**：

```js
build: {
  outDir: path.resolve(import.meta.dirname, '../backend/static/frontend'),
  emptyOutDir: true,   // ← 构建前先清空该目录
}
```

注意 `emptyOutDir: true`：构建会**先把 `backend/static/frontend/` 整个清空**再写入。旧哈希的文件是被**删除**，不是留着共存——所以每次构建后模板都必须重新同步，这一步现在由构建脚本自动完成（见下）。

## ⚠️ 陷阱一：构建会打断 8000 端口（已由构建脚本自动处理）

`backend/web/templates/index.html` 里**硬编码了构建产物的哈希文件名**：

```django
<script type="module" crossorigin src="{% static 'frontend/assets/index-XXXXXXXX.js' %}"></script>
<link rel="stylesheet" crossorigin href="{% static 'frontend/assets/index-XXXXXXXX.css' %}">
```

而这个模板**不是 Vite 生成的**。Vite 生成的是 `backend/static/frontend/index.html`，两份是不同的文件，内容也不同（后者用 `/assets/...`，前者用 `{% static %}`）。

Vite 的输出文件名带内容哈希，**源码一改、重新构建，哈希就变**。模板里那两个名字一旦对不上新哈希，访问 8000 就会因脚本和样式表 404 而白屏。

### 现在由构建脚本自动同步

`npm run build` 的第二段就是 `frontend/scripts/sync-template.mjs`，它会在构建后自动把模板里那两个哈希换成 `assets/` 下的实际文件名。**你不需要知道哈希是什么，也不该手动敲它。**

脚本的行为：

- 只认 `frontend/assets/index-<hash>.{js,css}` 这个形状；在模板里找不到就报错退出，不会静默放过
- `assets/` 下出现**多个** `.js` 或 `.css`（将来做了代码分割）时直接报错——文件名没法猜，必须人工确认加载哪个
- 幂等：文件名已经对得上时不写盘，不刷新 mtime

路径前缀是 `frontend/assets/`，不是 `assets/`。因为模板用的是 Django 的 `{% static %}`，根目录是 `backend/static/`——所以**不能**照抄 Vite 那份产物 `backend/static/frontend/index.html` 里的 `/assets/...` 写法。

**要改的是 Django 模板 `backend/web/templates/index.html`，不是那份 Vite 产物。** 产物每次构建都会被重写，而且 Django 根本不服务它（`backend/backend/urls.py` 只挂了 `/assets/` 和 `/media/`），改了也是白改。

### 完整的构建流程

```bash
cd frontend && npm run build                                              # 构建 + 自动同步模板

cd .. && curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/  # 验证
```

开发阶段走 5173 不会碰到这个问题——Vite 自己管理资源引用，改完源码刷新即可。这个陷阱只影响 8000 端口。

## ⚠️ 陷阱二：构建产物是有意保留在版本控制里的

`backend/static/frontend/` 的构建产物**被 git 跟踪**，这是有意为之：新克隆的仓库因此可以直接 `runserver` 就在 8000 看到界面，不必先装 Node 再构建。

所以 `.gitignore` 里**不能**写 `static/`。这个模式按目录名匹配，会连 `backend/static/` 整个一起挡掉——构建后旧哈希的文件被删、新的又看不见，仓库里一个前端资源都不剩。

改完产物记得和代码一起提交：

```bash
git add backend/static/frontend/
```

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
