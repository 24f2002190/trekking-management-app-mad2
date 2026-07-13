import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',        redirect: '/login' },
    { path: '/login',   component: () => import('../views/LoginView.vue') },
    { path: '/register',component: () => import('../views/RegisterView.vue') },
    { path: '/admin',   component: () => import('../views/AdminView.vue'),  meta: { role: 'admin' } },
    { path: '/staff',   component: () => import('../views/StaffView.vue'),  meta: { role: 'trek_staff' } },
    { path: '/trekker', component: () => import('../views/TrekkerView.vue'),meta: { role: 'trekker' } },
  ]
})


router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user  = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.path === '/login' || to.path === '/register') {
    return next()
  }

  if (!token) {
    return next('/login')
  }

  if (to.meta.role && !user?.roles?.includes(to.meta.role)) {
    if (user?.roles?.includes('admin'))      return next('/admin')
    if (user?.roles?.includes('trek_staff')) return next('/staff')
    if (user?.roles?.includes('trekker'))    return next('/trekker')
  }

  next()
})

export default router