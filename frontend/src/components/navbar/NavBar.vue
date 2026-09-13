<script setup>

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcons from "@/components/navbar/icons/CreateIcons.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle inline" />
    < <div class="drawer-content">
      <nav class="navbar w-full bg-base-300 shadow-sm">
        <div class="navbar-start">
          <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost drawer-button">
            <MenuIcon/>
          </label>
          <div class="px-2 font-bold text-2xl">AI Friends</div>
        </div>

        <div class="navbar-center w-2/3 max-w-180 flex justify-center">
          <div class="search-ring">
            <div class="search-bar">
              <input class="search-input" placeholder="搜索你感兴趣的内容" />
              <button class="search-btn">
                <SearchIcon />
                <span>搜索</span>
              </button>
            </div>
          </div>
        </div>

        <div class="navbar-end">
          <button class="btn btn-ghost text-base">登录</button>
        </div>
      </nav>

      <!-- Page content here -->
      <slot></slot>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-56">
        <!-- Sidebar content here -->
        <ul class="menu w-full grow">
          <!-- List item -->
          <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-2.5" data-tip="首页">
              <HomepageIcon/>
              <span class="is-drawer-close:hidden table-base ml-2 whitespace-nowrap">首页</span>
            </button>

          </li>
                  <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-2.5" data-tip="好友">
              <FriendIcon/>
              <span class="is-drawer-close:hidden table-base ml-2 whitespace-nowrap">好友</span>
            </button>

          </li>
                  <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-2.5" data-tip="创作">
              <CreateIcons/>
              <span class="is-drawer-close:hidden table-base ml-2 whitespace-nowrap">创作</span>
            </button>
          </li>

          <!-- List item -->
          <li>
            <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Settings">
              <!-- Settings icon -->
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-linejoin="round" stroke-linecap="round" stroke-width="2" fill="none" stroke="currentColor" class="my-1.5 inline-block size-4"><path d="M20 7h-9"></path><path d="M14 17H5"></path><circle cx="17" cy="17" r="3"></circle><circle cx="7" cy="7" r="3"></circle></svg>
              <span class="is-drawer-close:hidden">Settings</span>
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 搜索栏的彩色动态环绕效果。
   用 @property 让自定义属性可插值，从而直接动画 conic-gradient 的起始角，
   这样渐变层本身不需要旋转，也就不需要一个超大的方形子元素去覆盖椭圆。 */
@property --search-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

.search-ring {
  position: relative;
  width: 80%;
  max-width: 45rem;
  padding: 2px; /* 环的粗细 */
  border-radius: 9999px;
  overflow: hidden; /* 把渐变裁成椭圆，只留 padding 那一圈 */
  /* 未聚焦时的静态细边，聚焦后由彩色环取代 */
  background: color-mix(in oklab, var(--color-base-content) 20%, transparent);
}

.search-ring::before {
  content: '';
  position: absolute;
  inset: 0;
  background: conic-gradient(
    from var(--search-angle),
    #4285f4,
    #ea4335,
    #fbbc05,
    #34a853,
    #4285f4
  );
  animation: search-ring-spin 3s linear infinite;
  /* 默认暂停：不聚焦时不产生重绘开销，且保留当前角度让淡出过渡平滑 */
  animation-play-state: paused;
  opacity: 0;
  transition: opacity 0.25s ease;
}

/* 点击或聚焦搜索栏，彩色环才启动 */
.search-ring:focus-within::before {
  opacity: 1;
  animation-play-state: running;
}

@keyframes search-ring-spin {
  to {
    --search-angle: 360deg;
  }
}

.search-bar {
  position: relative;
  display: flex;
  align-items: center;
  border-radius: 9999px;
  background: var(--color-base-300);
}

.search-input {
  flex: 1 1 auto;
  min-width: 0;
  height: 2.75rem;
  padding-inline: 1.25rem;
  background: transparent;
  border: 0;
  outline: none;
  color: var(--color-base-content);
  font-size: 0.9375rem;
}

.search-input::placeholder {
  color: color-mix(in oklab, var(--color-base-content) 45%, transparent);
}

.search-btn {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.75rem;
  padding-inline: 1.25rem;
  background: transparent;
  border: 0;
  color: var(--color-base-content);
  font-size: 0.9375rem;
  cursor: pointer;
}

.search-btn svg {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}
</style>