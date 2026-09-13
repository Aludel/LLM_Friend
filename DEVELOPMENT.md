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

三个脚本定义在 `frontend/package.json` 的 `scripts` 里，本质都是调用 Vite：

| 命令 | 实际执行 | 作用 | 端口 |
| --- | --- | --- | --- |
| `npm run dev` | `vite` | 开发服务器：读 `frontend/src/` 源码，改动即时热更新，**不写任何文件到磁盘** | 5173 |
| `npm run build` | `vite build` | 生产构建：打包压缩、文件名加内容哈希，写入 `backend/static/frontend/` | —— |
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

注意 `emptyOutDir: true`：构建会**先把 `backend/static/frontend/` 整个清空**再写入。旧哈希的文件是被**删除**，不是留着共存——所以构建之后 8000 端口必然失效，直到你把模板同步过来（见下）。

## ⚠️ 陷阱一：构建会打断 8000 端口

`backend/web/templates/index.html` 里**硬编码了构建产物的哈希文件名**：

```django
<script type="module" crossorigin src="{% static 'frontend/assets/index-CuUsnuGI.js' %}"></script>
<link rel="stylesheet" crossorigin href="{% static 'frontend/assets/index-CKT5K5NR.css' %}">
```

而这个模板**不是 Vite 生成的**。Vite 生成的是 `backend/static/frontend/index.html`，两份是不同的文件，内容也不同（后者用 `/assets/...`，前者用 `{% static %}`）。

Vite 的输出文件名带内容哈希，**源码一改、重新构建，哈希就变**。实测一次全新构建的产出：

```
index-BxcJWdw6.js    index-gxaJMinD.css
```

和模板里写死的 `index-CuUsnuGI.js` / `index-CKT5K5NR.css` **两个都对不上**。此时访问 8000 会因脚本和样式表 404 而白屏。

### 怎么改后端的 index

要同步的就是 `backend/web/templates/index.html` 的第 10、11 两行：

```django
<script type="module" crossorigin src="{% static 'frontend/assets/index-CuUsnuGI.js' %}"></script>
<link rel="stylesheet" crossorigin href="{% static 'frontend/assets/index-CKT5K5NR.css' %}">
```

把 `index-XXXX.js` / `index-XXXX.css` 换成 `backend/static/frontend/assets/` 下的**实际文件名**。

注意路径前缀是 `frontend/assets/`，不是 `assets/`。因为模板用的是 Django 的 `{% static %}`，根目录是 `backend/static/`——所以**不能**直接照抄 Vite 自己生成的那份 `backend/static/frontend/index.html` 里的 `/assets/...` 写法。

**手动改**：

```bash
ls backend/static/frontend/assets/     # 看新文件名
# 然后把上面两行改掉
```

**一条命令改完**（在仓库根目录执行）：

```bash
js=$(ls backend/static/frontend/assets/*.js)
css=$(ls backend/static/frontend/assets/*.css)
# 出现多个入口文件时直接报错退出，避免拼出错误的文件名
case "$js$css" in *$'\n'*) echo "assets/ 下有多个入口文件，请手动确认"; exit 1;; esac
js=${js##*/}; css=${css##*/}

sed -i '' -E "s#frontend/assets/index-[A-Za-z0-9_-]+\.js#frontend/assets/$js#"   backend/web/templates/index.html
sed -i '' -E "s#frontend/assets/index-[A-Za-z0-9_-]+\.css#frontend/assets/$css#" backend/web/templates/index.html
```

关于 `-i ''`：这是 macOS 的写法（`sed` 的备份后缀参数），Linux 上要改成 `sed -i -E`。

这条命令是**幂等的**——文件名已经对得上时不会产生任何改动，实测确认。

那三行防护是必要的：当前构建只产出单个 JS 和单个 CSS 入口，但一旦将来做了代码分割产生多个 chunk，`ls` 会返回多行，简单取文件名会拼出一个不存在的路径并**静默**写进模板。加上判断后这种情况会直接报错，而不是坏得不明不白。

### 完整的构建流程

```bash
# 1. 构建（会先清空再重写 backend/static/frontend/）
cd frontend && npm run build

# 2. 回仓库根目录，同步模板里的两个哈希
cd ..
js=$(ls backend/static/frontend/assets/*.js)
css=$(ls backend/static/frontend/assets/*.css)
case "$js$css" in *$'\n'*) echo "assets/ 下有多个入口文件，请手动确认"; exit 1;; esac
js=${js##*/}; css=${css##*/}
sed -i '' -E "s#frontend/assets/index-[A-Za-z0-9_-]+\.js#frontend/assets/$js#"   backend/web/templates/index.html
sed -i '' -E "s#frontend/assets/index-[A-Za-z0-9_-]+\.css#frontend/assets/$css#" backend/web/templates/index.html

# 3. 验证 8000 端口还能正常返回
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/
```

开发阶段走 5173 不会碰到这个问题——Vite 自己管理资源引用，改完源码刷新即可。这个陷阱只影响 8000 端口。

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
