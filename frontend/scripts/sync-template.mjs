// 构建后把 Vite 产物的哈希同步进 Django 模板。
//
// 背景见 DEVELOPMENT.md「陷阱一」：Vite 输出的文件名带内容哈希，而
// backend/web/templates/index.html 里是写死的文件名。构建又会先清空
// 整个输出目录，旧哈希的文件被删掉，不同步就会 404 白屏。
//
// 注意：改的是 Django 模板（用 {% static %}），不是 Vite 自己生成的
// backend/static/frontend/index.html（用 /assets/）。后者每次构建都会被
// 重写，不需要也不应该手动改。

import { readFileSync, writeFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const assetsDir = path.join(root, 'backend/static/frontend/assets')
const templatePath = path.join(root, 'backend/web/templates/index.html')

// 当前构建只产出单个 JS 和单个 CSS 入口。一旦将来做了代码分割产生多个
// chunk，这里必须报错而不是猜一个——否则会拼出不存在的路径写进模板，
// 坏得不明不白。
function soleEntry(ext) {
  const found = readdirSync(assetsDir).filter((f) => f.endsWith(ext))
  if (found.length !== 1) {
    console.error(`✗ assets/ 下有 ${found.length} 个 ${ext} 文件，预期 1 个：`)
    for (const f of found) console.error(`    ${f}`)
    console.error('  构建产出了多个入口（可能开了代码分割），需要手动确认要加载哪个。')
    process.exit(1)
  }
  return found[0]
}

const js = soleEntry('.js')
const css = soleEntry('.css')

const before = readFileSync(templatePath, 'utf8')
let after = before

for (const [ext, name] of [
  ['js', js],
  ['css', css],
]) {
  const pattern = new RegExp(`frontend/assets/index-[A-Za-z0-9_-]+\\.${ext}`, 'g')
  // 用 match 判断有没有命中。不能拿 replace 的结果和原文比——文件名已经
  // 对得上时替换结果相同，那种情况下是「不需要改」，不是「找不到」。
  if (!after.match(pattern)) {
    console.error(`✗ 模板里找不到 frontend/assets/index-*.${ext}，没动它。`)
    console.error(`  检查 ${path.relative(root, templatePath)} 里那两行是不是被改过。`)
    process.exit(1)
  }
  after = after.replace(pattern, `frontend/assets/${name}`)
}

// 幂等：文件名已经对得上时不写盘，避免无谓地刷新 mtime。
if (after === before) {
  console.log(`✓ 模板已是最新：${js} / ${css}`)
} else {
  writeFileSync(templatePath, after)
  console.log(`✓ 模板已更新：${js} / ${css}`)
}
