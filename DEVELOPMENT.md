# 开发指南

纯命令速查。**首次部署**看「一」，**每次开发**看「二」「三」。

> 动手前先记住两条 Windows 差异，否则照抄网上 Unix 教程会直接卡住：
>
> - venv 目录是 `.venv\Scripts\`，**不是** `.venv/bin\`
> - PowerShell 5.1 不支持 `&&`，串联命令用 `;` 或分两行
>
> 下面一律用完整路径调 `.venv\Scripts\python.exe`，所以**不需要激活虚拟环境**，也不挑终端（PowerShell / Git Bash 都能跑）。

---

## 一、首次部署

在仓库根目录（`D:\LLM_Friend`）下，按顺序执行这四步。

### 1. 建虚拟环境

```powershell
python -m venv .venv
```

效果：生成 `D:\LLM_Friend\.venv\`，里面是 `Scripts\` 目录。

### 2. 装后端依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

效果：把 Django 6.1.1、DRF、JWT 等装进 venv。

装完自检一下，应打印 `6.1.1`：

```powershell
.\.venv\Scripts\python.exe -c "import django; print(django.get_version())"
```

报 `ModuleNotFoundError: No module named 'django'` 就是这步没成功，别往下走。

### 3. 建数据库

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py migrate
cd ..
```

效果：生成 `backend/db.sqlite3`。这个文件不入库，**每个新克隆的仓库都要跑一次**。

### 4. 装前端依赖

```powershell
cd frontend
npm install
cd ..
```

效果：生成 `frontend/node_modules\`。

---

## 二、启动项目

**每次开发都要开两个终端**，两个服务都得跑。

```powershell
# 终端 1 —— 后端
cd D:\LLM_Friend\backend
..\.venv\Scripts\python.exe manage.py runserver 8000
```

效果：Django 跑在 http://127.0.0.1:8000

```powershell
# 终端 2 —— 前端
cd D:\LLM_Friend\frontend
npm run dev
```

效果：Vite 跑在 http://localhost:5173

**开发时访问 http://localhost:5173** —— 它读 `frontend/src/` 的源码，改完立刻生效。
8000 加载的是上次构建的产物，不反映源码改动，只在验证「构建后的真实表现」时才看它。

---

## 三、日常开发命令

### 后端（在 `D:\LLM_Friend\backend` 下）

| 命令 | 效果 |
| --- | --- |
| `..\.venv\Scripts\python.exe manage.py runserver 8000` | 启动后端服务（8000） |
| `..\.venv\Scripts\python.exe manage.py check` | 系统检查，不写任何东西 |
| `..\.venv\Scripts\python.exe manage.py migrate` | 把迁移应用到数据库 |
| `..\.venv\Scripts\python.exe manage.py makemigrations` | 改过 `models.py` 后生成迁移文件 |
| `..\.venv\Scripts\python.exe manage.py showmigrations` | 查看迁移状态 |
| `..\.venv\Scripts\python.exe manage.py test` | 跑测试（目前 0 个） |
| `..\.venv\Scripts\python.exe manage.py createsuperuser` | 建管理员账号 |
| `..\.venv\Scripts\python.exe manage.py shell` | 进 Django shell |

管理后台：http://127.0.0.1:8000/admin/

### 前端（在 `D:\LLM_Friend\frontend` 下）

| 命令 | 效果 |
| --- | --- |
| `npm run dev` | 启动开发服务器（5173）。读源码、热更新，**不写任何文件到磁盘** |
| `npm run build` | 生产构建：打包压缩、文件名加哈希，写入 `backend/static/frontend/`，并自动同步模板 |
| `npm run preview` | 本地预览**已构建**的产物（4173），脱离 Django 单独检查构建结果 |
| `npm run sync` | 只同步模板哈希，不构建。输入是磁盘现状——**改了源码没构建时，它不会让 8000 更新** |

`dev` 和 `build` 是本质区别：`dev` 在内存里编译直接喂给浏览器，**不落盘**，你看到的不是最终产物；`build` 才真正生成带哈希的文件写进磁盘。

---

## 四、改完前端要发布到 8000

改样式阶段停在 5173 就够了。要让 8000 也更新，多跑一条：

```powershell
cd D:\LLM_Friend\frontend
npm run build
```

效果：重新打包并把新哈希写进 Django 模板。这一步必须做——构建会先清空 `backend/static/frontend/`，不重新构建的话 8000 会白屏（脚本或样式表 404）。

验证 8000 正常（应输出 `200`）：

```powershell
(Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing).StatusCode
```

### 提交时模板和产物必须一起

```powershell
git add backend/static/frontend/ backend/web/templates/index.html
```

效果：把新产物和模板里的新哈希引用一起入库。

**只 add 产物是常见错误** —— 模板改动留在工作区，别人拉下来就是「新产物 + 旧引用」，8000 白屏。

---

## 五、不要做的事

| 不要 | 原因 |
| --- | --- |
| 改 `backend/static/frontend/` 里的文件 | 是压缩过的构建产物，下次构建会被整个清空 |
| 改 `backend/static/frontend/index.html` | 那是 Vite 自己生成的，Django 根本不服务它（只挂了 `/assets/` 和 `/media/`） |
| 在 `.gitignore` 里加 `static/` | 会把 `backend/static/` 整个挡掉，产物全部丢失 |
| 手敲模板里的哈希文件名 | `npm run build` 会自动同步 |

---

## 附：更详细的说明

本文档只保留命令。构建机制的完整推演（哈希同步的触发时机、脚本的提前退出路径、构建失败时目录受损的两种阶段、`sync` 与 `build` 的边界）在 git 历史里：

```powershell
git show HEAD:DEVELOPMENT.md
```
